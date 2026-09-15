from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.waitlist.infrastructure.websocket.connection_manager import broadcaster

router = APIRouter(tags=["waitlist-host"])


@router.websocket("/ws/locations/{location_id}/waitlist-entries")
async def queue_updates(websocket: WebSocket, location_id: int) -> None:
    """Live push of the host queue snapshot for a location (screen 4).

    Sends the current snapshot immediately on connect, then again every
    time a mutation (join/call/seat/cancel/no-show/reorder) affects this
    location. No auth, matching the rest of the host routes in this pilot.
    """
    await broadcaster.connect(location_id, websocket)
    try:
        while True:
            # The client never sends anything meaningful; this just blocks
            # until the socket closes so we can clean up the connection.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        broadcaster.disconnect(location_id, websocket)
