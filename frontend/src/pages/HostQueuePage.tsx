import { useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import { QueueList } from "../components/QueueList";
import { usePolling } from "../hooks/usePolling";
import { useHostQueueStore } from "../stores/useHostQueueStore";

const POLL_INTERVAL_MS = 4_000;

export function HostQueuePage() {
  const { locationId } = useParams<{ locationId: string }>();
  const id = Number(locationId);

  const entries = useHostQueueStore((s) => s.entries);
  const loading = useHostQueueStore((s) => s.loading);
  const error = useHostQueueStore((s) => s.error);
  const fetchQueue = useHostQueueStore((s) => s.fetchQueue);
  const call = useHostQueueStore((s) => s.call);
  const seat = useHostQueueStore((s) => s.seat);
  const reorder = useHostQueueStore((s) => s.reorder);

  useEffect(() => {
    if (!Number.isNaN(id)) fetchQueue(id);
  }, [id, fetchQueue]);

  usePolling(() => fetchQueue(id), Number.isNaN(id) ? null : POLL_INTERVAL_MS);

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
        <h1 className="text-lg font-semibold text-text">Cola · local {id}</h1>
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
