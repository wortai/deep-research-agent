/**
 * Backend base URL for REST calls (no trailing slash).
 *
 * - Production (Vercel): set `VITE_API_URL` to your Render URL, e.g.
 *   https://deep-research-agent-2-vri8.onrender.com
 * - Local dev: omit it — defaults to http://{current hostname}:8000
 */
export function getApiOrigin(): string {
  const raw = import.meta.env.VITE_API_URL as string | undefined;
  if (raw?.trim()) {
    return raw.trim().replace(/\/$/, "");
  }
  if (typeof window === "undefined") {
    return "http://localhost:8000";
  }
  return `http://${window.location.hostname}:8000`;
}

/** WebSocket origin (ws:// or wss://) matching the API host. */
export function getWebSocketOrigin(): string {
  const http = getApiOrigin();
  if (http.startsWith("https://")) {
    return http.replace(/^https/, "wss");
  }
  return http.replace(/^http/, "ws");
}
