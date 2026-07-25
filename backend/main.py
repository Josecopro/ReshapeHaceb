"""
main.py

FastAPI server that connects the frontend to the backend pipeline:
  - GET /api/health         → health check
  - GET /api/graph          → full G_db master graph (25-node refrigerator repair)
  - POST /api/chat          → user message → SLM extraction → fuzzy match →
                              K-hop neighborhood → topology evaluation → response
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import (
    GROQ_API_KEY,
    get_groq_api_key,
    GRAPH_DB_NODES_PATH,
    GRAPH_DB_EDGES_PATH,
    MAX_EXPLORATION_DEPTH,
)
from core.graph_builder import load_master_graph, build_from_extraction, graph_to_dict
from core.topology import evaluate_topology, TopologicalState
from services.graph_extractor import extract_graph_from_prompt, GraphExtractionError
from services.normalizer import normalize_and_extract_neighborhood
from services.response_generator import generate_assistant_response

app = FastAPI(title="ReshapeHck Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_gdb() -> "nx.DiGraph":
    return load_master_graph(GRAPH_DB_NODES_PATH, GRAPH_DB_EDGES_PATH)


# ─── Endpoints ────────────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/graph")
async def get_graph():
    try:
        gdb = _load_gdb()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return graph_to_dict(gdb)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    assistant_message: str
    neighborhood_graph: dict
    extracted_graph: dict
    topology: dict


@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = get_groq_api_key() or GROQ_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY no está configurada. El chat requiere una clave de API.",
        )

    try:
        extraction = extract_graph_from_prompt(req.message)
    except GraphExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    extracted_digraph = build_from_extraction(extraction)

    try:
        db_digraph = _load_gdb()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al cargar G_db: {exc}")

    try:
        norm_result = normalize_and_extract_neighborhood(
            extracted_digraph, db_digraph,
            threshold=70, hops=2,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en normalización: {exc}")

    topology_result = evaluate_topology(
        norm_result.neighborhood_subgraph,
        extracted_digraph,
        db_digraph,
        max_depth=MAX_EXPLORATION_DEPTH,
    )

    assistant_message = generate_assistant_response(
        user_message=req.message,
        topology_result=topology_result,
        extracted_nodes=extraction.nodes,
        norm_result=norm_result,
        db_graph=db_digraph,
    )

    return {
        "assistant_message": assistant_message,
        "neighborhood_graph": graph_to_dict(norm_result.neighborhood_subgraph),
        "extracted_graph": graph_to_dict(extracted_digraph),
        "topology": {
            "estado": topology_result.estado.value,
            "origen": topology_result.origen,
            "camino_seleccionado": topology_result.camino_seleccionado,
            "hoja_mayoritaria": (
                {
                    "leaf_id": topology_result.hoja_mayoritaria.leaf_id,
                    "leaf_label": topology_result.hoja_mayoritaria.leaf_label,
                    "leaf_why": topology_result.hoja_mayoritaria.leaf_why,
                    "count": topology_result.hoja_mayoritaria.count,
                    "ratio": topology_result.hoja_mayoritaria.ratio,
                }
                if topology_result.hoja_mayoritaria
                else None
            ),
            "opciones": [
                {
                    "leaf_id": o.leaf_id,
                    "leaf_label": o.leaf_label,
                    "leaf_why": o.leaf_why,
                    "count": o.count,
                    "ratio": o.ratio,
                }
                for o in topology_result.opciones
            ],
        },
    }
