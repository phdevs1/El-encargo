import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { HostQueueEntryResponse } from "../api/types";
import { useNow } from "../hooks/useNow";

interface QueueRowProps {
  entry: HostQueueEntryResponse;
  position: number;
  onCall: (entryId: number) => void;
  onSeat: (entryId: number) => void;
}

function elapsedMinutes(joinedAt: string, now: Date): number {
  const joined = new Date(joinedAt).getTime();
  return Math.max(0, Math.round((now.getTime() - joined) / 60_000));
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function QueueRow({ entry, position, onCall, onSeat }: QueueRowProps) {
  const now = useNow();
  const isCalled = entry.status === "called";

  // Only "waiting" entries can be reordered — the backend rejects reorder
  // attempts on anything else, so disable dragging before that round-trip.
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: entry.id,
    disabled: isCalled,
  });

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`flex items-center gap-3 rounded-lg border border-border px-3 py-3 ${
        isCalled ? "bg-surface" : "bg-transparent"
      } ${isDragging ? "opacity-50" : ""}`}
    >
      <button
        type="button"
        aria-label="Arrastrar para reordenar"
        className="cursor-grab touch-none px-1 text-text-muted active:cursor-grabbing"
        {...attributes}
        {...listeners}
      >
        ⋮⋮
      </button>

      <span className="w-5 shrink-0 text-sm text-text-muted">{position}</span>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate font-medium text-text">{entry.guest_name}</span>
          {entry.is_frequent_guest && (
            <span className="shrink-0 rounded-full bg-pill-bg px-2 py-0.5 text-xs text-pill">
              Frecuente
            </span>
          )}
          {isCalled && entry.called_at && (
            <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-xs text-text-muted">
              Llamado {formatTime(entry.called_at)}
            </span>
          )}
        </div>
        <div className="text-sm text-text-muted">
          {entry.party_size} pers. · {elapsedMinutes(entry.joined_at, now)} min
        </div>
      </div>

      <button
        type="button"
        onClick={() => (isCalled ? onSeat(entry.id) : onCall(entry.id))}
        className="shrink-0 rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-text"
      >
        {isCalled ? "Sentar" : "Llamar"}
      </button>
    </div>
  );
}
