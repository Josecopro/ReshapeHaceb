"""
config.py

Constantes y configuración de entorno del proyecto. No poner valores
sensibles hardcodeados aquí -- todo viene de variables de entorno.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths relative to this file's location (backend/)
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent

# Cargar variables de entorno desde .env (raíz del proyecto o directorio backend)
load_dotenv(_PROJECT_ROOT / ".env")
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv()


def get_groq_api_key() -> str:
    """Obtiene GROQ_API_KEY del entorno, forzando lectura actualizada."""
    return os.environ.get("GROQ_API_KEY", "").strip()


GROQ_API_KEY = get_groq_api_key()

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

_DEFAULT_NODES = _PROJECT_ROOT / "db" / "nodes.json"
_DEFAULT_EDGES = _PROJECT_ROOT / "db" / "edges.json"


def _resolve_db_path(env_var: str, default_path: Path) -> str:
    raw_val = os.environ.get(env_var, "").strip()
    if not raw_val:
        return str(default_path)
    p = Path(raw_val)
    if p.is_absolute() and p.exists():
        return str(p)
    if (_PROJECT_ROOT / p).exists():
        return str((_PROJECT_ROOT / p).resolve())
    if (_BACKEND_DIR / p).exists():
        return str((_BACKEND_DIR / p).resolve())
    if (_PROJECT_ROOT / "db" / p.name).exists():
        return str((_PROJECT_ROOT / "db" / p.name).resolve())
    return str(default_path)


GRAPH_DB_NODES_PATH = _resolve_db_path("GRAPH_DB_NODES_PATH", _DEFAULT_NODES)
GRAPH_DB_EDGES_PATH = _resolve_db_path("GRAPH_DB_EDGES_PATH", _DEFAULT_EDGES)


