import {
  DndContext,
  type DragEndEvent,
  PointerSensor,
  TouchSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, arrayMove, verticalListSortingStrategy } from "@dnd-kit/sortable";
import type { HostQueueEntryResponse } from "../api/types";
import { QueueRow } from "./QueueRow";

interface QueueListProps {
  entries: HostQueueEntryResponse[];
  onReorder: (entryId: number, afterEntryId: number | null) => void;
  onCall: (entryId: number) => void;
  onSeat: (entryId: number) => void;
}

export function QueueList({ entries, onReorder, onCall, onSeat }: QueueListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 150, tolerance: 5 } }),
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = entries.findIndex((e) => e.id === active.id);
    const newIndex = entries.findIndex((e) => e.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    const reordered = arrayMove(entries, oldIndex, newIndex);
    const movedIndex = reordered.findIndex((e) => e.id === active.id);
    const afterEntryId = movedIndex === 0 ? null : reordered[movedIndex - 1].id;

    onReorder(Number(active.id), afterEntryId);
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={entries.map((e) => e.id)} strategy={verticalListSortingStrategy}>
        <div className="flex flex-col gap-2">
          {entries.map((entry, index) => (
            <QueueRow
              key={entry.id}
              entry={entry}
              position={index + 1}
              onCall={onCall}
              onSeat={onSeat}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
