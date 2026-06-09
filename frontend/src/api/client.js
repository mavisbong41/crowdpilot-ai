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
};
