# CrowdPilot AI

Multi-agent event operations platform for the **Google Cloud Rapid Agent Hackathon**. CrowdPilot helps organizers predict crowd surges, allocate resources, and generate operational response plans for large-scale events.

## Architecture

```
crowdpilot-ai/
├── frontend/          # React + Vite + Tailwind dashboard
└── backend/           # FastAPI + MongoDB Atlas
    ├── agents/        # Gemini-powered Forecast, Resource, Incident + Coordinator
    ├── services/      # Business logic & orchestration
    ├── models/        # Pydantic schemas
    ├── routes/        # REST API endpoints
    └── database/      # MongoDB connection (Motor)
```

### Core workflow

1. User submits event information (dashboard).
2. **Forecast Agent** — crowd risk assessment (stub).
3. **Resource Agent** — staffing & equipment (stub).
4. **Incident Agent** — contingency actions (stub).
5. **Coordinator Agent** — merged operation plan (stub).
6. Plan persisted in **MongoDB Atlas**.
7. Results displayed on the dashboard.

> Agents use the **Gemini API** for analysis with rule-based fallback when the API is unavailable.

## Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **MongoDB Atlas** cluster (or local MongoDB for development)

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MONGODB_URI

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env

npm run dev
```

Dashboard: [http://localhost:5173](http://localhost:5173)

## Environment variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB_NAME` | Database name (default: `crowdpilot`) |
| `API_HOST` | Bind host (default: `0.0.0.0`) |
| `API_PORT` | Port (default: `8000`) |
| `CORS_ORIGINS` | Comma-separated frontend origins |
| `GEMINI_API_KEY` | API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Model id (default: `gemini-2.0-flash`) |
| `GEMINI_TEMPERATURE` | Sampling temperature (default: `0.2`) |
| `AGENTS_USE_GEMINI` | Enable Gemini agents (`true` / `false`) |
| `AGENT_FALLBACK_TO_RULES` | Fall back to rules if Gemini fails (`true` / `false`) |
| `LOG_LEVEL` | Python log level (`INFO`, `DEBUG`, etc.) |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend URL (leave empty to use Vite proxy) |

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST/GET/PUT/DELETE` | `/api/events` | CRUD for `events` collection |
| `POST/GET/PUT/DELETE` | `/api/incidents` | CRUD for `incidents` collection |
| `POST/GET/PUT/DELETE` | `/api/plans` | CRUD for `operation_plans` collection |
| `POST` | `/api/agents/forecast` | Run ForecastAgent (standalone) |
| `POST` | `/api/agents/resources` | Run ResourceAgent (standalone) |
| `POST` | `/api/agents/incidents` | Run IncidentAgent (standalone) |
| `POST` | `/api/agents/coordinate` | Full multi-agent pipeline |
| `POST` | `/api/agents/coordinate/save` | Pipeline + save plan to MongoDB |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Example: coordinate workflow

```bash
curl -X POST http://localhost:8000/api/agents/coordinate \
  -H "Content-Type: application/json" \
  -d '{
    "expected_attendance": 42000,
    "venue_capacity": 50000,
    "event_name": "Fan Zone",
    "incident_data": [
      {
        "location": "Gate A",
        "severity": "high",
        "description": "Crowd queue exceeding safe depth",
        "status": "open"
      }
    ]
  }'
```

## Project status

- [x] Monorepo skeleton (frontend + backend)
- [x] FastAPI routes & MongoDB service
- [x] Multi-agent orchestration (Gemini + rule fallback)
- [x] React operations dashboard (mock data)
- [x] Gemini API integration with structured JSON outputs
- [ ] Real-time crowd data ingestion
- [ ] Authentication & multi-tenant orgs

## License

Hackathon project — MIT (adjust as needed).
