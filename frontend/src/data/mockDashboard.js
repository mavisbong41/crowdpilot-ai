/** Mock operations data — replace with API calls when backend is wired. */

export const mockEvent = {
  event_name: "FIFA World Cup 2026 — Downtown Fan Zone",
  venue: "Metropolitan Plaza, Sector A",
  expected_attendance: 42_500,
  venue_capacity: 50_000,
  attendance_forecast: 48_200,
  forecast_delta_percent: 13.4,
  event_date: "2026-07-12",
  event_time: "16:00 – 23:30",
  weather: {
    condition: "Partly Cloudy",
    temperature_c: 31,
    precipitation_chance: 20,
  },
};

export const mockRisk = {
  risk_level: "high",
  score: 78,
  surge_probability: 0.74,
  peak_window: "18:30 – 19:45",
  summary:
    "Post-match arrival wave expected to exceed safe density at Gates A and B. Weather remains favorable; monitor exit choke points.",
  factors: [
    { label: "Density index", value: "Critical", trend: "up" },
    { label: "Ingress rate", value: "2.4k/min", trend: "up" },
    { label: "Exit capacity", value: "82%", trend: "stable" },
    { label: "Medical standby", value: "Ready", trend: "ok" },
  ],
};

export const mockIncidents = [
  {
    id: "INC-1042",
    location: "Gate A — Main Ingress",
    severity: "high",
    description: "Queue depth exceeds 400m; estimated wait 35+ minutes.",
    status: "in_progress",
    timestamp: "2026-07-12T18:12:00Z",
    assignee: "Team Alpha",
  },
  {
    id: "INC-1041",
    location: "Stage Front — Zone 2",
    severity: "medium",
    description: "Crowd density approaching 4.5 persons/m² threshold.",
    status: "acknowledged",
    timestamp: "2026-07-12T17:58:00Z",
    assignee: "Team Bravo",
  },
  {
    id: "INC-1039",
    location: "Medical Tent — East",
    severity: "low",
    description: "Heat-related assist requests up 18% vs. baseline.",
    status: "open",
    timestamp: "2026-07-12T17:41:00Z",
    assignee: "Med Unit 3",
  },
  {
    id: "INC-1035",
    location: "Parking Lot C",
    severity: "medium",
    description: "Vehicle ingress backlog affecting pedestrian flow.",
    status: "resolved",
    timestamp: "2026-07-12T16:22:00Z",
    assignee: "Traffic Ops",
  },
];

export const mockOperationPlan = {
  risk_level: "high",
  generated_at: "2026-07-12T18:05:00Z",
  recommendations: [
    "Open auxiliary exit lanes at Gates C and D within 10 minutes.",
    "Throttle main ingress at Gate A to 1,200 persons/minute until density normalizes.",
    "Deploy 6 additional crowd-control staff to Stage Front Zone 2.",
    "Activate PA loop with shelter and hydration wayfinding every 8 minutes.",
    "Pre-position medical rapid response at Gate A queue terminus.",
    "Coordinate with transit authority for staggered post-match departures.",
  ],
};

export const mockConsoleHistory = [
  {
    id: "msg-1",
    role: "system",
    content: "CrowdPilot Operations Console ready. Agent integrations coming soon.",
    time: "18:00",
  },
  {
    id: "msg-2",
    role: "user",
    content: "Summarize current risk at Gate A.",
    time: "18:04",
  },
  {
    id: "msg-3",
    role: "assistant",
    content:
      "Gate A shows HIGH severity incident INC-1042. Queue depth >400m with 35+ min wait. Recommend throttling ingress and opening auxiliary exits per active operation plan.",
    time: "18:04",
  },
];
