import asyncio
import logging
from typing import Callable

import anyio
from fastapi import WebSocket

from app.waitlist.infrastructure.http.schemas import HostQueueListResponse

logger = logging.getLogger(__name__)

SnapshotFetcher = Callable[[int], HostQueueListResponse]


class QueueBroadcaster:
    """In-process WebSocket fan-out of host queue snapshots, keyed by location_id.

    A single instance only — if this ever runs on more than one Cloud Run
    instance, a client connected to instance A won't see a change committed
    on instance B. Fine for this pilot's scale; would need a shared pub/sub
    (Redis, etc.) to scale past one instance.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None
        self._fetch_snapshot: SnapshotFetcher | None = None

    def configure(self, fetch_snapshot: SnapshotFetcher) -> None:
        self._fetch_snapshot = fetch_snapshot

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, location_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(location_id, set()).add(websocket)
        await self._send_to(websocket, location_id)

    def disconnect(self, location_id: int, websocket: WebSocket) -> None:
        conns = self._connections.get(location_id)
        if conns is None:
            return
        conns.discard(websocket)
        if not conns:
            self._connections.pop(location_id, None)

    def notify(self, location_id: int) -> None:
        """Sync-callable — safe to call from a sync HTTP route (threadpool).

        Only schedules the broadcast; must be called after the triggering
        transaction has committed, or the broadcast may read stale data
        (it opens its own DB session).
        """
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self._broadcast(location_id), self._loop)

    async def _broadcast(self, location_id: int) -> None:
        conns = self._connections.get(location_id)
        if not conns:
            return
        for websocket in list(conns):
            await self._send_to(websocket, location_id)

    async def _send_to(self, websocket: WebSocket, location_id: int) -> None:
        if self._fetch_snapshot is None:
            return
        try:
            snapshot = await anyio.to_thread.run_sync(self._fetch_snapshot, location_id)
            await websocket.send_text(snapshot.model_dump_json())
        except Exception:
            logger.exception("queue_broadcaster: failed to send snapshot, dropping connection")
            self.disconnect(location_id, websocket)


broadcaster = QueueBroadcaster()
