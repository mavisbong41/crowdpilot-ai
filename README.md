# CrowdPilot AI

### Turning Operational Data into Actionable Decisions for Large-Scale Events

CrowdPilot AI is a multi-agent operational planning platform that helps event organizers anticipate crowd risks, retrieve incident response procedures, evaluate available resources, and generate actionable operation plans before problems occur.

Built for the Google Cloud Rapid Agent Hackathon, CrowdPilot demonstrates how Gemini-powered agents can move beyond answering questions and actively support operational decision-making through MongoDB-powered intelligence retrieval.

---

## Problem

Large-scale events generate huge amounts of operational information:

- Historical crowd incidents
- Emergency response procedures
- Resource availability
- Venue risk assessments
- Operational playbooks

Unfortunately, this information is often scattered across documents, spreadsheets, reports, and disconnected systems.

During critical situations, operators waste valuable time searching for information instead of making decisions.

CrowdPilot AI solves this by allowing multiple AI agents to retrieve operational intelligence directly from MongoDB Atlas through MongoDB MCP and transform data into actionable plans.

---

## Architecture

```mermaid
flowchart TD

A[Operations Dashboard]

A --> B[FastAPI Backend]

B --> C[Google ADK Multi-Agent System]

C --> D[Forecast Agent]
C --> E[Incident Agent]
C --> F[Resource Agent]
C --> G[Operation Planning Agent]

D --> H[Gemini 3]
E --> H
F --> H
G --> H

H --> I[MongoDB MCP Server]

I --> J[(MongoDB Atlas)]

J --> K[Historical Events]
J --> L[Incident Playbooks]
J --> M[Resource Inventory]
J --> N[Operation Plans]

G --> O[Operational Recommendations]

O --> A
```

---

## Multi-Agent Workflow

### Forecast Agent

Evaluates event risk levels using:

- Attendance forecasts
- Venue capacity
- Historical event intelligence
- Crowd density indicators

Outputs:

- Risk classification
- Congestion prediction
- Monitoring recommendations

---

### Incident Agent

Retrieves operational response procedures from MongoDB Atlas.

Outputs:

- Relevant incident playbooks
- Escalation procedures
- Emergency actions

---

### Resource Agent

Analyzes available operational resources.

Outputs:

- Staffing recommendations
- Equipment allocation
- Coverage analysis

---

### Operation Planning Agent

Combines outputs from all agents and generates:

- Deployment plans
- Risk mitigation actions
- Monitoring priorities
- Operational recommendations

---

## MongoDB MCP Integration

MongoDB serves as the operational intelligence backbone of CrowdPilot AI.

Agents access MongoDB through MongoDB MCP to retrieve:

- Historical event records
- Incident response playbooks
- Resource inventories
- Operational plans
- Risk classifications

Instead of hardcoding knowledge into prompts, agents dynamically retrieve operational intelligence at runtime.

This enables:

- Better decision making
- Scalable knowledge management
- Real-time operational grounding

---

## Technology Stack

### AI & Agents

- google-gemini-3
- google-adk
- model-context-protocol
- mongodb-mcp-server

### Backend

- python
- fastapi
- pydantic
- motor

### Database

- mongodb-atlas

### Frontend

- react
- vite
- tailwindcss

### Cloud

- google-cloud-run
- google-container-registry

---

## Project Structure

```text
crowdpilot-ai/

├── frontend/
│   ├── dashboard
│   └── visualization
│
├── backend/
│   ├── agents/
│   │   ├── forecast_agent
│   │   ├── incident_agent
│   │   ├── resource_agent
│   │   └── planning_agent
│   │
│   ├── services/
│   ├── routes/
│   ├── database/
│   └── mcp_tools/
│
└── deployment/
```

---

## Example Operational Scenario

Input:

- Event Attendance: 18,000
- Venue Capacity: 20,000

CrowdPilot AI will:

1. Assess crowd risk
2. Retrieve similar historical events
3. Analyze available resources
4. Retrieve emergency playbooks
5. Generate deployment recommendations

Output:

- Risk level
- Monitoring zones
- Staffing plan
- Resource allocation
- Incident response guidance

---

## Why CrowdPilot AI

Most AI systems answer questions.

CrowdPilot helps operators make decisions.

By combining Gemini reasoning with MongoDB operational intelligence through MCP, CrowdPilot demonstrates how AI agents can support real-world operational planning rather than simply generating text.

---

## License

MIT License
