import { create } from "zustand";
import { ApiError } from "../api/client";
import { callEntry, listHostQueue, markNoShow, reorderEntry, seatEntry } from "../api/waitlistApi";
import type { HostQueueEntryResponse } from "../api/types";

interface HostQueueState {
  locationId: number | null;
  entries: HostQueueEntryResponse[];
  loading: boolean;
  error: string | null;
}

interface HostQueueActions {
  fetchQueue: (locationId: number) => Promise<void>;
  setEntries: (entries: HostQueueEntryResponse[]) => void;
  call: (entryId: number) => Promise<void>;
  seat: (entryId: number) => Promise<void>;
  markNoShow: (entryId: number) => Promise<void>;
  reorder: (entryId: number, afterEntryId: number | null) => Promise<void>;
}

export const useHostQueueStore = create<HostQueueState & HostQueueActions>((set, get) => ({
  locationId: null,
  entries: [],
  loading: false,
  error: null,

  fetchQueue: async (locationId) => {
    if (get().entries.length === 0) set({ loading: true });
    try {
      const result = await listHostQueue(locationId);
      set({ locationId, entries: result.entries, loading: false, error: null });
    } catch (err) {
      set({ loading: false, error: err instanceof ApiError ? err.detail : "No se pudo cargar la cola" });
    }
  },

  /** Used by the WebSocket hook — a push from the server is already the source of truth. */
  setEntries: (entries) => set({ entries, loading: false, error: null }),

  call: async (entryId) => {
    try {
      await callEntry(entryId);
      const { locationId } = get();
      if (locationId) await get().fetchQueue(locationId);
    } catch (err) {
      set({ error: err instanceof ApiError ? err.detail : "No se pudo llamar" });
    }
  },

  seat: async (entryId) => {
    try {
      await seatEntry(entryId);
      const { locationId } = get();
      if (locationId) await get().fetchQueue(locationId);
    } catch (err) {
      set({ error: err instanceof ApiError ? err.detail : "No se pudo sentar" });
    }
  },

  markNoShow: async (entryId) => {
    try {
      await markNoShow(entryId);
      const { locationId } = get();
      if (locationId) await get().fetchQueue(locationId);
    } catch (err) {
      set({ error: err instanceof ApiError ? err.detail : "No se pudo marcar como no-show" });
    }
  },

  reorder: async (entryId, afterEntryId) => {
    const previous = get().entries;
    const oldIndex = previous.findIndex((e) => e.id === entryId);
    if (oldIndex === -1) return;

    const newIndex = afterEntryId === null ? 0 : previous.findIndex((e) => e.id === afterEntryId) + 1;
    const reordered = [...previous];
    const [moved] = reordered.splice(oldIndex, 1);
    reordered.splice(newIndex > oldIndex ? newIndex - 1 : newIndex, 0, moved);

    // Optimistic update: snappy UI first, reconciled by the next poll tick.
    set({ entries: reordered, error: null });

    try {
      await reorderEntry(entryId, afterEntryId);
    } catch (err) {
      set({
        entries: previous,
        error: err instanceof ApiError ? err.detail : "No se pudo reordenar",
      });
      const { locationId } = get();
      if (locationId) await get().fetchQueue(locationId);
    }
  },
}));
