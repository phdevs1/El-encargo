import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { getLocationSummary } from "../api/waitlistApi";
import type { LocationSummaryResponse } from "../api/types";
import { PartySizeStepper } from "../components/PartySizeStepper";
import { useGuestWaitlistStore } from "../stores/useGuestWaitlistStore";

export function JoinPage() {
  const { slug = "" } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const [location, setLocation] = useState<LocationSummaryResponse | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [loadingLocation, setLoadingLocation] = useState(true);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [partySize, setPartySize] = useState(2);

  const join = useGuestWaitlistStore((s) => s.join);
  const loading = useGuestWaitlistStore((s) => s.loading);
  const error = useGuestWaitlistStore((s) => s.error);

  // Re-entry: if this browser already has an active ticket for this slug, skip the form.
  useEffect(() => {
    const s = useGuestWaitlistStore.getState();
    if (s.slug === slug && s.publicToken && (s.status === "waiting" || s.status === "called")) {
      navigate(`/l/${slug}/status/${s.publicToken}`, { replace: true });
    }
  }, [slug, navigate]);

  useEffect(() => {
    let cancelled = false;
    setLoadingLocation(true);
    getLocationSummary(slug)
      .then((loc) => {
        if (!cancelled) setLocation(loc);
      })
      .catch((err) => {
        if (!cancelled) {
          setLocationError(err instanceof ApiError ? err.detail : "No se pudo cargar el local");
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingLocation(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await join(slug, name, phone, partySize);
      const token = useGuestWaitlistStore.getState().publicToken;
      if (token) navigate(`/l/${slug}/status/${token}`);
    } catch {
      // error already surfaced via the store's `error` field
    }
  }

  if (loadingLocation) {
    return <Centered>Cargando…</Centered>;
  }

  if (locationError || !location) {
    return <Centered>Ubicación no encontrada</Centered>;
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-6 px-6 py-10">
      <header>
        <h1 className="text-xl font-semibold text-text">{location.name}</h1>
        <p className="text-sm text-text-muted">Lista de espera · hoy</p>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-sm text-text-muted">Nombre</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="rounded-lg border border-border bg-surface px-3 py-2 text-text outline-none"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm text-text-muted">Teléfono</span>
          <input
            required
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+51 987 654 321"
            className="rounded-lg border border-border bg-surface px-3 py-2 text-text outline-none"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm text-text-muted">¿Cuántos son?</span>
          <PartySizeStepper value={partySize} onChange={setPartySize} />
        </label>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-accent px-4 py-3 font-medium text-accent-text disabled:opacity-50"
        >
          {loading ? "Uniendo…" : "Unirme a la cola"}
        </button>
      </form>

      <p className="text-xs text-text-muted">↳ se abre al escanear el QR de la puerta</p>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="flex min-h-screen items-center justify-center text-text-muted">{children}</div>;
}
