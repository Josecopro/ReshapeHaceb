# ReshapeHaceb — Knowledge-Graph-Driven AI Diagnostic Agent

> **An explainable AI assistant for Haceb refrigerator technical support**, powered by a procedural knowledge graph, LLM-driven subgraph extraction, topological self-consistency reasoning, and an interactive 3D visualization frontend.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
  - [4. Environment Variables](#4-environment-variables)
- [Running the Application](#running-the-application)
- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Knowledge Graph (G_db)](#knowledge-graph-g_db)
- [How It Works — Detailed Pipeline](#how-it-works--detailed-pipeline)
- [Frontend — UI Components](#frontend--ui-components)
- [Contributing](#contributing)
- [License](#license)


---

## Prerequisites

- **Python** ≥ 3.11
- **Node.js** ≥ 18.x
- **npm** ≥ 9.x
- A **Groq API key** ([Get one here](https://console.groq.com/))

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Josecopro/ReshapeHaceb.git
cd ReshapeHaceb
```

### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```dotenv
# Required — Groq API key for LLM inference
GROQ_API_KEY=gsk_your_api_key_here

# Optional — Override default models
SLM_EXTRACTION_MODEL=openai/gpt-oss-20b       # Must support json_schema on Groq
LLM_RESPONSE_MODEL=llama-3.3-70b-versatile    # For final response generation

# Optional — Topology exploration
MAX_EXPLORATION_DEPTH=8

# Optional — Custom paths to knowledge graph files
GRAPH_DB_NODES_PATH=../db/nodes.json
GRAPH_DB_EDGES_PATH=../db/edges.json
```

> **Note on SLM model:** The extraction model **must** support Groq's `response_format: json_schema` (constrained decoding). Currently only `openai/gpt-oss-20b` and `openai/gpt-oss-120b` support this. Llama models will return `400 Bad Request`.

---

## Running the Application

You need to run **both** the backend and frontend simultaneously.

### Start the Backend (Terminal 1)

```bash
# From the project root, with venv activated
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`.

### Verify the Setup

```bash
# Health check
curl http://localhost:8000/api/health
# Expected: {"status": "ok"}

# Fetch the full knowledge graph
curl http://localhost:8000/api/graph
```

---

## API Reference

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

--- 

## Overview

**ReshapeHaceb** is a full-stack AI diagnostic agent designed for **Haceb appliance technical support**. Instead of relying solely on a Large Language Model (which can hallucinate), it constrains the LLM's output through a **curated procedural knowledge graph** of refrigerator repair workflows.

The system:

1. **Extracts** structured intent from a user's natural-language query using a Small Language Model (SLM).
2. **Matches** the extracted intent against a master knowledge graph (`G_db`) using fuzzy matching (RapidFuzz).
3. **Evaluates** the topological structure of the matched neighborhood using self-consistency path analysis (NetworkX).
4. **Generates** a transparent, explainable response — either a converging diagnosis or targeted clarification questions.
5. **Visualizes** the entire Chain of Thought (CoT) reasoning on an interactive 3D force-directed graph (Three.js).

---

## Key Features

| Feature | Description |
|---|---|
|  **Explainable AI (XAI)** | Every diagnostic node can be inspected for its causal reasoning chain — predecessors, successors, and symptom justifications. |
|  **Topological Self-Consistency** | Up to 5 shortest paths are explored and aggregated by leaf-node majority voting (>70% convergence threshold). |
|  **Interactive 3D Graph** | Real-time 3D force-directed visualization with click-to-inspect nodes, edge filtering, dark/light themes, and chat-driven highlighting. |
|  **Conversational Chat Sidebar** | Natural-language chat interface that highlights the relevant graph neighborhood in real-time as you converse. |
|  **Fuzzy Matching** | RapidFuzz `WRatio` matching against node symptoms (`why`), labels, and IDs — gracefully handles misspellings and paraphrasing. |
|  **Divergence Detection** | When the query maps to multiple possible diagnoses, the system blocks autonomous response and asks targeted clarification questions. |
|  **Structured Outputs** | Groq's `json_schema` constrained decoding ensures the SLM extraction follows the exact Pydantic contract. |


---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Runtime |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **NetworkX** | Graph data structure and path algorithms |
| **Pydantic v2** | Schema validation and structured output contracts |
| **Groq SDK** | LLM inference (SLM extraction + response generation) |
| **RapidFuzz** | Fuzzy string matching |
| **python-dotenv** | Environment variable management |

### Frontend

| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework (App Router) |
| **React 19** | UI library |
| **TypeScript 6** | Type safety |
| **react-force-graph-3d** | Interactive 3D graph visualization (Three.js) |
| **SCSS** | Styling |
| **Atomic Design** | Component architecture (atoms → molecules → organisms → templates → pages) |


---

### `GET /api/graph`

Returns the complete master knowledge graph (`G_db`).

**Response:**
```json
{
  "nodes": [
    { "id": "identifyModel", "label": "Identificar modelo...", "cluster_id": "identification", "why": [...], "source_url": "..." }
  ],
  "edges": [
    { "source": "identifyModel", "target": "locateServiceManual", "edge_type": "PROCEDURAL", "cost": 1 }
  ]
}
```

---

### `POST /api/chat`

Send a user message through the full diagnostic pipeline.

**Request:**
```json
{ "message": "My refrigerator compressor is not starting" }
```

**Response:**
```json
{
  "assistant_message": "✅ **Resultado: CONVERGENTE** — ...",
  "neighborhood_graph": { "nodes": [...], "edges": [...] },
  "extracted_graph": { "nodes": [...], "edges": [...] },
  "topology": {
    "estado": "CONVERGENTE",
    "origen": "inspectCompressor",
    "camino_seleccionado": ["inspectCompressor", "testCompressorWindings"],
    "hoja_mayoritaria": { "leaf_id": "...", "leaf_label": "...", "count": 4, "ratio": 0.8 },
    "opciones": [...]
  }
}
```

---

### `POST /api/node-reasoning`

Get the Chain of Thought (causal reasoning) explanation for a specific node.

**Request:**
```json
{
  "node_id": "inspectCompressor",
  "user_context": "The compressor is buzzing but not starting"
}
```

**Response:**
```json
{
  "node_id": "inspectCompressor",
  "label": "Inspeccionar motocompresor",
  "reasoning": "🧠 **Modelo de Pensamiento:** ...",
  "why": ["El compresor no arranca.", "Se escucha zumbido..."],
  "source_url": "https://...",
  "predecessors": ["Diagnosticar falla de enfriamiento"],
  "successors": ["Probar devanados del compresor"]
}
```

---

## Knowledge Graph (G_db)

The master graph is stored in `db/nodes.json` and `db/edges.json` and contains **25 nodes** representing the diagnostic workflow for Haceb refrigerator repair.

### Node Schema

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique camelCase identifier |
| `label` | `string` | Human-readable description |
| `cluster_id` | `string` | Thematic grouping (e.g., `compressor`, `defrost`, `power`) |
| `why` | `string[]` | User-facing symptoms/reasons that lead to this node |
| `source_url` | `string` | Technical evidence source URL |

### Edge Schema

| Field | Type | Description |
|---|---|---|
| `source` | `string` | Origin node ID |
| `target` | `string` | Target node ID |
| `edge_type` | `PROCEDURAL \| INFORMATIVE` | Procedural = causal flow, Informative = metadata |
| `cost` | `int` | Fixed at 1 |

### Cluster Overview

| Cluster | Nodes | Domain |
|---|---|---|
| `identification` | Model identification | Entry point |
| `documentation` | Service manual lookup | Reference |
| `power` | Electrical supply verification | Power system |
| `diagnosis` | Generic cooling failure diagnosis | Triage |
| `compressor` | Compressor, windings, start relay/capacitor | Sealed system |
| `sealed_system` | Refrigerant leak detection | Sealed system |
| `defrost` | Sensor, heater, timer, ADC board | Defrost cycle |
| `electronics` | Control board, self-diagnostic, error codes | Electronics |
| `ventilation` | Evaporator fan, condenser fan | Air circulation |
| `mechanical` | Door seal / magnetic sensor | Mechanical |
| `icemaker` | Ice maker diagnosis and module testing | Ice maker |
| `parts` | Part identification and compatibility | Replacement |
| `closure` | Repair ticket closure | Workflow end |

---

## How It Works — Detailed Pipeline

### 1. SLM Graph Extraction

The user's natural-language message is sent to a Small Language Model (via Groq) with a strict system prompt and **constrained JSON output** (`response_format: json_schema`). The SLM converts the message into a minimal subgraph with:
- **Nodes:** `id` (camelCase infinitive), `label` (faithful to user's wording), `cluster_id` (loose grouping).
- **Edges:** Causal/procedural order reflecting the user's intent.

### 2. Fuzzy Normalization & Neighborhood Extraction

Each extracted node is matched against `G_db` using a 3-priority strategy:
1. **`why` symptoms** — Best for natural-language matching (e.g., "the compressor doesn't start" → `inspectCompressor`).
2. **`label`** — Semantic label matching.
3. **`id`** — Structural ID matching.

Matching uses `RapidFuzz.WRatio` with a configurable threshold (default: 60). For each matched node, a **K-hop bidirectional neighborhood** (default K=4) is extracted from `G_db`.

### 3. Topological Self-Consistency

The topology engine (pure NetworkX, no LLM):
1. Identifies the **origin node** (no predecessors in the extracted graph).
2. Identifies **leaf nodes** (no PROCEDURAL successors in the **full** `G_db`, not just the neighborhood).
3. Finds **all simple PROCEDURAL paths** from origin → leaves within the neighborhood.
4. **Prunes** to the **5 shortest paths** (self-consistency acotado).
5. **Aggregates** by leaf node ID:
   - **>70% convergence** → `CONVERGENTE` — Autonomous response with assumption note.
   - **≤70%** → `DIVERGENTE` — Blocks autonomous response, enumerates options as clarification questions.
   - **No paths** → `SIN_CAMINO` — Asks for more information.

### 4. Response Generation

- **CONVERGENT:** Presents the winning diagnosis path, confidence percentage, associated symptoms, and a note like *"I assumed X. If that's not the case, let me know if it's A or B."*
- **DIVERGENT:** Lists the competing diagnoses with their probabilities and asks the user to select the best fit.
- **NO_PATH:** Uses the LLM (or a deterministic fallback) to generate 3–4 targeted diagnostic counter-questions based on `G_db`'s symptom vocabulary.

---

## Frontend — UI Components

The frontend follows **Atomic Design** methodology:

| Layer | Components | Role |
|---|---|---|
| **Atoms** | `Badge`, `Icon`, `Overlay` | Smallest reusable UI elements |
| **Molecules** | `ChatMessage`, `ModalField` | Composed atoms with specific behavior |
| **Organisms** | `ChatSidebar`, `FloatingModal`, `Legend`, `Toolbar`, `ThemeTransition` | Complex UI sections |
| **Templates** | `GraphViewTemplate` | Page layout composition |
| **Pages** | `AgentGraphPage` | Full-page smart component with state management |

### UI Features

- **3D Force-Directed Graph:** Interactive Three.js visualization of the entire knowledge graph.
- **Node Click → CoT Modal:** Click any node to see its Chain of Thought reasoning, predecessors, successors, and source URL.
- **Chat Sidebar:** Send natural-language queries; the graph highlights the relevant neighborhood in real-time.
- **Edge Filtering:** Toggle between showing all edges or only PROCEDURAL edges.
- **Dark/Light Theme:** Smooth animated theme transitions.
- **Divergence UI:** When multiple paths are detected, the chat surfaces options for the user to select.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a Pull Request.

---

## License

This project is provided as-is for educational and research purposes. See the repository for license details.
