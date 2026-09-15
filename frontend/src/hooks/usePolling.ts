import { useEffect, useRef } from "react";

/**
 * Runs `callback` every `intervalMs` milliseconds. Pass `null` to pause
 * polling entirely (e.g. once a guest's entry leaves "waiting").
 */
export function usePolling(callback: () => void, intervalMs: number | null): void {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    if (intervalMs === null) return;
    const id = setInterval(() => callbackRef.current(), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
}
