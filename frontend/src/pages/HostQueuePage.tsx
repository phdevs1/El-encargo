import { useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { QueueList } from "../components/QueueList";
import { useQueueSocket } from "../hooks/useQueueSocket";
import { useHostQueueStore } from "../stores/useHostQueueStore";

export function HostQueuePage() {
  const { locationId } = useParams<{ locationId: string }>();
  const id = Number(locationId);

  const entries = useHostQueueStore((s) => s.entries);
  const loading = useHostQueueStore((s) => s.loading);
  const error = useHostQueueStore((s) => s.error);
  const fetchQueue = useHostQueueStore((s) => s.fetchQueue);
  const setEntries = useHostQueueStore((s) => s.setEntries);
  const call = useHostQueueStore((s) => s.call);
  const seat = useHostQueueStore((s) => s.seat);
  const reorder = useHostQueueStore((s) => s.reorder);

  // Fast first paint via REST; live updates (from this tablet, the other
  // one, or a guest joining) arrive over the WebSocket from here on.
  useEffect(() => {
    if (!Number.isNaN(id)) fetchQueue(id);
  }, [id, fetchQueue]);

  const socketStatus = useQueueSocket(id, (message) => setEntries(message.entries));

  const stats = useMemo(() => {
    const waiting = entries.filter((e) => e.status === "waiting");
    const withEstimate = entries.filter((e) => e.estimated_wait_minutes_at_join !== null);
    const avgWait = withEstimate.length
      ? Math.round(
          withEstimate.reduce((sum, e) => sum + (e.estimated_wait_minutes_at_join ?? 0), 0) /
            withEstimate.length,
        )
      : null;
    return { waitingCount: waiting.length, avgWait };
  }, [entries]);

  if (Number.isNaN(id)) {
    return <Centered>Local inválido</Centered>;
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-4 px-6 py-8">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h1 className="text-lg font-semibold text-text">Cola · local {id}</h1>
          <span
            title={socketStatus === "open" ? "En vivo" : "Reconectando…"}
            className={`h-2 w-2 rounded-full ${socketStatus === "open" ? "bg-emerald-400" : "bg-amber-400"}`}
          />
        </div>
        <p className="text-sm text-text-muted">
          {stats.waitingCount} en cola{stats.avgWait !== null && ` · espera media ${stats.avgWait} min`}
        </p>
      </header>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {loading && entries.length === 0 ? (
        <Centered>Cargando…</Centered>
      ) : entries.length === 0 ? (
        <Centered>No hay nadie en la cola todavía</Centered>
      ) : (
        <QueueList entries={entries} onReorder={reorder} onCall={call} onSeat={seat} />
      )}

      <p className="text-xs text-text-muted">↳ arrastrar ⋮⋮ para reordenar · «Llamar» envía el WhatsApp</p>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="flex min-h-[40vh] items-center justify-center text-text-muted">{children}</div>;
}
