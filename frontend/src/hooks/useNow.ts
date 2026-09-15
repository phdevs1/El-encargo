import { useEffect, useState } from "react";

/** Re-renders every `intervalMs` so elapsed-time displays (e.g. "34 min") stay fresh. */
export function useNow(intervalMs = 60_000): Date {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return now;
}
