import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ApiError } from "../api/client";
import { cancelEntry, getEntryStatus, joinWaitlist } from "../api/waitlistApi";
import type { WaitlistStatus } from "../api/types";

interface GuestWaitlistState {
  slug: string | null;
  publicToken: string | null;
  guestName: string | null;
  partySize: number | null;
  /** Position at join time — stable denominator for the progress bar, since
   * the status endpoint only ever returns the current position. */
  initialPosition: number | null;
  currentPosition: number | null;
  estimatedWaitMinutes: number | null;
  status: WaitlistStatus | null;
  loading: boolean;
  error: string | null;
}

interface GuestWaitlistActions {
  join: (slug: string, name: string, phone: string, partySize: number) => Promise<void>;
  hydrateFromToken: (slug: string, token: string) => Promise<void>;
  refreshStatus: () => Promise<void>;
  cancel: () => Promise<void>;
  clear: () => void;
}

const initialState: GuestWaitlistState = {
  slug: null,
  publicToken: null,
  guestName: null,
  partySize: null,
  initialPosition: null,
  currentPosition: null,
  estimatedWaitMinutes: null,
  status: null,
  loading: false,
  error: null,
};

export const useGuestWaitlistStore = create<GuestWaitlistState & GuestWaitlistActions>()(
  persist(
    (set, get) => ({
      ...initialState,

      join: async (slug, name, phone, partySize) => {
        set({ loading: true, error: null });
        try {
          const result = await joinWaitlist(slug, { name, phone, party_size: partySize });
          set({
            slug,
            publicToken: result.public_token,
            guestName: name,
            partySize,
            initialPosition: result.position,
            currentPosition: result.position,
            estimatedWaitMinutes: result.estimated_wait_minutes,
            status: result.status,
            loading: false,
          });
        } catch (err) {
          set({ loading: false, error: err instanceof ApiError ? err.detail : "No se pudo unir a la cola" });
          throw err;
        }
      },

      hydrateFromToken: async (slug, token) => {
        set({ loading: true, error: null });
        try {
          const result = await getEntryStatus(token);
          set({
            slug,
            publicToken: result.public_token,
            guestName: result.guest_name,
            partySize: result.party_size,
            initialPosition: result.position ?? get().initialPosition,
            currentPosition: result.position,
            estimatedWaitMinutes: result.estimated_wait_minutes,
            status: result.status,
            loading: false,
          });
        } catch (err) {
          // A 404 means this ticket no longer exists server-side (expired,
          // DB reset, etc). Wipe it instead of leaving stale frozen data
          // around — otherwise a future visit would keep "resuming" a ticket
          // that's gone, never showing the join form again.
          if (err instanceof ApiError && err.status === 404) {
            set({ ...initialState });
          } else {
            set({ loading: false, error: err instanceof ApiError ? err.detail : "Ticket no encontrado" });
          }
          throw err;
        }
      },

      refreshStatus: async () => {
        const { publicToken } = get();
        if (!publicToken) return;
        try {
          const result = await getEntryStatus(publicToken);
          set({
            currentPosition: result.position,
            estimatedWaitMinutes: result.estimated_wait_minutes,
            status: result.status,
            error: null,
          });
        } catch (err) {
          if (err instanceof ApiError && err.status === 404) {
            set({ ...initialState });
          } else {
            set({ error: err instanceof ApiError ? err.detail : "No se pudo actualizar el estado" });
          }
        }
      },

      cancel: async () => {
        const { publicToken } = get();
        if (!publicToken) return;
        set({ loading: true, error: null });
        try {
          const result = await cancelEntry(publicToken);
          set({ status: result.status, loading: false });
        } catch (err) {
          set({ loading: false, error: err instanceof ApiError ? err.detail : "No se pudo cancelar" });
          throw err;
        }
      },

      clear: () => set({ ...initialState }),
    }),
    {
      name: "guest-waitlist",
      partialize: (state) => ({
        slug: state.slug,
        publicToken: state.publicToken,
        guestName: state.guestName,
        partySize: state.partySize,
        initialPosition: state.initialPosition,
        currentPosition: state.currentPosition,
        estimatedWaitMinutes: state.estimatedWaitMinutes,
        status: state.status,
      }),
    },
  ),
);
