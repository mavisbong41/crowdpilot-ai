const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  createEvent: (payload) =>
    request("/api/events", { method: "POST", body: JSON.stringify(payload) }),
  listEvents: () => request("/api/events"),
  getPlan: (planId) => request(`/api/plans/${planId}`),
  listPlansForEvent: (eventId) => request(`/api/plans/event/${eventId}`),
  coordinate: (payload) =>
    request("/api/agents/coordinate", { method: "POST", body: JSON.stringify(payload) }),
  coordinateAndSave: (payload) =>
    request("/api/agents/coordinate/save", { method: "POST", body: JSON.stringify(payload) }),
  startMission: (payload) =>
    request("/api/mission/start", { method: "POST", body: JSON.stringify(payload) }),
  getMission: (missionId) => request(`/api/mission/${missionId}`),
  decideAction: (missionId, actionIndex, decision) =>
    request(`/api/mission/${missionId}/actions/${actionIndex}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision }),
    }),
};

export function missionWebSocketUrl(missionId) {
  const configuredBase = import.meta.env.VITE_API_BASE_URL;
  if (configuredBase) {
    const url = new URL(configuredBase, window.location.origin);
    const protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${url.host}/api/mission/ws/${missionId}`;
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/mission/ws/${missionId}`;
}
