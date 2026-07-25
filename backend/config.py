"""
config.py

Constantes y configuración de entorno del proyecto. No poner valores
sensibles hardcodeados aquí -- todo viene de variables de entorno.
"""

import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SLM_EXTRACTION_MODEL = os.environ.get("SLM_EXTRACTION_MODEL", "llama-3.1-8b-instant")

LLM_RESPONSE_MODEL = os.environ.get("LLM_RESPONSE_MODEL", "llama-3.3-70b-versatile")

# --- Límites de exploración topológica ---
MAX_EXPLORATION_DEPTH = int(os.environ.get("MAX_EXPLORATION_DEPTH", "4")) 

GRAPH_DB_NODES_PATH = os.environ.get("GRAPH_DB_NODES_PATH", "./data/nodes.json")
GRAPH_DB_EDGES_PATH = os.environ.get("GRAPH_DB_EDGES_PATH", "./data/edges.json")