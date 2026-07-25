"""
config.py

Constantes y configuración de entorno del proyecto. No poner valores
sensibles hardcodeados aquí -- todo viene de variables de entorno.
"""

import os
from pathlib import Path

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Modelo SLM usado exclusivamente para la extracción prompt -> subgrafo.
# IMPORTANTE: en Groq, response_format json_schema (constrained decoding)
# SOLO está soportado por openai/gpt-oss-20b y openai/gpt-oss-120b (ver
# https://console.groq.com/docs/structured-outputs#supported-models).
# Ningún modelo Llama (3.1, 3.3) lo soporta -- devuelven 400 Bad Request.
# Usamos el 20b: es el más liviano de los dos que garantizan schema.
SLM_EXTRACTION_MODEL = os.environ.get("SLM_EXTRACTION_MODEL", "openai/gpt-oss-20b")

# Modelo grande reservado para generación de respuesta técnica final
# (Paso 3 del engine, agent_engine.py). Se define aquí para no mezclar
# configuración de modelos en distintos archivos.
LLM_RESPONSE_MODEL = os.environ.get("LLM_RESPONSE_MODEL", "llama-3.3-70b-versatile")

# --- Límites de exploración topológica ---
MAX_EXPLORATION_DEPTH = int(os.environ.get("MAX_EXPLORATION_DEPTH", "4"))

# Resolve paths relative to this file's location (backend/)
_BACKEND_DIR = Path(__file__).resolve().parent
_DEFAULT_NODES = str(_BACKEND_DIR.parent / "db" / "nodes.json")
_DEFAULT_EDGES = str(_BACKEND_DIR.parent / "db" / "edges.json")

GRAPH_DB_NODES_PATH = os.environ.get("GRAPH_DB_NODES_PATH", _DEFAULT_NODES)
GRAPH_DB_EDGES_PATH = os.environ.get("GRAPH_DB_EDGES_PATH", _DEFAULT_EDGES)
