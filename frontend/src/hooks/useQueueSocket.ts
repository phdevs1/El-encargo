import { useEffect, useRef, useState } from "react";
import { WS_BASE_URL } from "../api/client";
import type { QueueUpdateMessage } from "../api/types";

const RECONNECT_DELAY_MS = 3_000;

export type QueueSocketStatus = "connecting" | "open" | "reconnecting";

/**
 * Subscribes to live host-queue updates for a location. Pushes a fresh
 * snapshot on connect and again after every mutation that affects this
 * location (from any client — another tablet, a guest joining, etc).
 * Reconnects automatically (fixed delay) if the connection drops.
 */
export function useQueueSocket(
  locationId: number,
  onMessage: (message: QueueUpdateMessage) => void,
): QueueSocketStatus {
  const [status, setStatus] = useState<QueueSocketStatus>("connecting");
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (Number.isNaN(locationId)) return;

    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let stopped = false;

    function connect() {
      setStatus((prev) => (prev === "open" ? "reconnecting" : "connecting"));
      socket = new WebSocket(`${WS_BASE_URL}/ws/locations/${locationId}/waitlist-entries`);

      socket.onopen = () => setStatus("open");

      socket.onmessage = (event) => {
        try {
          onMessageRef.current(JSON.parse(event.data) as QueueUpdateMessage);
        } catch {
          // ignore malformed frames
        }
      };

      socket.onclose = () => {
        if (stopped) return;
        setStatus("reconnecting");
        reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
      };

      socket.onerror = () => {
        socket?.close();
      };
    }

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [locationId]);

  return status;
}
