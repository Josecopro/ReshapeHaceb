"""
config.py

Constantes y configuración de entorno del proyecto. No poner valores
sensibles hardcodeados aquí -- todo viene de variables de entorno.
"""

import os

from dotenv import load_dotenv

# Carga el .env ANTES de leer cualquier os.environ.get de abajo. Sin esto,
# las variables definidas en .env nunca llegan al proceso: os.environ.get
# solo ve variables realmente exportadas en la shell, no las de un archivo
# .env que nadie cargó explícitamente.
load_dotenv()

# --- Groq ---
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

# --- CORS (front en Vercel, backend en host aparte: Render/Railway/Fly) ---
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# --- Límites de exploración topológica (usado más adelante en core/topology.py) ---
MAX_EXPLORATION_DEPTH = int(os.environ.get("MAX_EXPLORATION_DEPTH", "8"))  # D_max

# --- Grafo maestro (G_db) ---
GRAPH_DB_NODES_PATH = os.environ.get("GRAPH_DB_NODES_PATH", "./data/nodes.json")
GRAPH_DB_EDGES_PATH = os.environ.get("GRAPH_DB_EDGES_PATH", "./data/edges.json")