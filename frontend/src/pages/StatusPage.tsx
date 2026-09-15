import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";
import { usePolling } from "../hooks/usePolling";
import { useGuestWaitlistStore } from "../stores/useGuestWaitlistStore";

const POLL_INTERVAL_MS = 12_000;

export function StatusPage() {
  const { slug = "", token = "" } = useParams<{ slug: string; token: string }>();
  const navigate = useNavigate();

  const publicToken = useGuestWaitlistStore((s) => s.publicToken);
  const status = useGuestWaitlistStore((s) => s.status);
  const currentPosition = useGuestWaitlistStore((s) => s.currentPosition);
  const initialPosition = useGuestWaitlistStore((s) => s.initialPosition);
  const estimatedWaitMinutes = useGuestWaitlistStore((s) => s.estimatedWaitMinutes);
  const loading = useGuestWaitlistStore((s) => s.loading);
  const error = useGuestWaitlistStore((s) => s.error);
  const hydrateFromToken = useGuestWaitlistStore((s) => s.hydrateFromToken);
  const refreshStatus = useGuestWaitlistStore((s) => s.refreshStatus);
  const cancel = useGuestWaitlistStore((s) => s.cancel);

  // The URL is the source of truth: if the store doesn't already hold this
  // exact token (fresh tab, cleared storage, a shared link), fetch it.
  const [hydrating, setHydrating] = useState(publicToken !== token);

  useEffect(() => {
    if (publicToken !== token) {
      setHydrating(true);
      hydrateFromToken(slug, token)
        .catch(() => {})
        .finally(() => setHydrating(false));
    }
  }, [slug, token, publicToken, hydrateFromToken]);

  usePolling(refreshStatus, status === "waiting" ? POLL_INTERVAL_MS : null);

  // No ticket and we're done hydrating: it doesn't exist — either it never
  // did, or a 404 during polling/hydration wiped the stale local copy.
  // The join form is the only sensible place to land, not a dead-end screen.
  useEffect(() => {
    if (!hydrating && !publicToken) {
      navigate(`/l/${slug}`, { replace: true });
    }
  }, [hydrating, publicToken, slug, navigate]);

  if (hydrating || !publicToken) {
    return <Centered>Cargando…</Centered>;
  }

  if (status === "cancelled") {
    return <Centered>Cancelaste tu lugar en la cola.</Centered>;
  }

  if (status === "no_show") {
    return <Centered>Tu lugar en la cola expiró.</Centered>;
  }

  if (status === "seated") {
    return <Centered>¡Tu mesa está lista! Disfruta.</Centered>;
  }

  async function handleCancel() {
    try {
      await cancel();
    } catch {
      // error already surfaced via the store's `error` field
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-8 px-6 py-10 text-center">
      <div>
        <p className="text-sm text-text-muted">Estás en el puesto</p>
        <p className="text-7xl font-semibold text-text">{currentPosition ?? "—"}</p>
      </div>

      <div className="flex flex-col gap-2">
        <p className="text-sm text-text-muted">Tiempo estimado</p>
        <p className="text-lg font-medium text-text">≈ {estimatedWaitMinutes ?? "—"} min</p>
        {initialPosition !== null && currentPosition !== null && (
          <ProgressBar initial={initialPosition} current={currentPosition} />
        )}
      </div>

      <p className="text-sm text-text-muted">Te avisaremos por WhatsApp cuando tu mesa esté lista</p>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="button"
        onClick={handleCancel}
        disabled={loading}
        className="rounded-lg border border-border px-4 py-3 font-medium text-text disabled:opacity-50"
      >
        Ya no voy
      </button>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="flex min-h-screen items-center justify-center text-text-muted">{children}</div>;
}
