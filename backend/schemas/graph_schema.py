"""
schemas/graph_schema.py

Contratos Pydantic para el subgrafo candidato que extrae el SLM (Small Language
Model, vía Groq) a partir del prompt en lenguaje natural del usuario.

Este NO es el esquema del grafo maestro completo (G_db) -- es el subconjunto
mínimo que el SLM debe poblar para que core/graph_builder.py y core/topology.py
puedan trabajar con él como subgrafo candidato (G_respuesta / G_extraido).

Reglas de negocio reflejadas aquí (ver contexto del proyecto):
- id: camelCase, raíz en infinitivo (ej. "verificarSaldo", no "verificando").
- label: lo más fiel posible al lenguaje del usuario, es el campo de mayor
  peso semántico para luego hacer fuzzy matching (RapidFuzz) contra G_db.
- cluster_id: campo secundario. El SLM puede generarlo de forma laxa/genérica;
  no se exige que coincida exactamente con los cluster_id reales de G_db,
  eso lo resuelve la normalización posterior, no la extracción.
- edge_type: solo dos valores permitidos, PROCEDURAL es lo único que se usa
  para exploración topológica (ver topology.py).
- cost: entero fijo en 1 por diseño (no ponderado en esta fase).
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EdgeType(str, Enum):
    PROCEDURAL = "PROCEDURAL"
    INFORMATIVE = "INFORMATIVE"


class NodeExtracted(BaseModel):
    """Nodo candidato extraído del prompt del usuario por el SLM."""

    id: str = Field(
        ...,
        description=(
            "Identificador camelCase en infinitivo, ej. 'verificarSaldo', "
            "'cancelarSuscripcion'."
        ),
    )
    label: str = Field(
        ...,
        description="Etiqueta legible, lo más fiel posible al texto del usuario.",
    )
    cluster_id: Optional[str] = Field(
        default=None,
        description=(
            "Agrupador semántico laxo. Puede ser genérico; no necesita "
            "coincidir con los cluster_id de G_db (eso se resuelve después)."
        ),
    )

    @field_validator("id")
    @classmethod
    def validate_camel_case_infinitive(cls, v: str) -> str:
        if not v:
            raise ValueError("id no puede estar vacío")
        if " " in v or "_" in v or "-" in v:
            raise ValueError(
                f"id '{v}' debe estar en camelCase sin espacios/guiones"
            )
        if not v[0].islower():
            raise ValueError(f"id '{v}' debe iniciar en minúscula (camelCase)")
        return v


class EdgeExtracted(BaseModel):
    """Arista candidata entre dos nodos extraídos del prompt del usuario."""

    source: str = Field(..., description="id de NodeExtracted origen")
    target: str = Field(..., description="id de NodeExtracted destino")
    edge_type: EdgeType = Field(
        default=EdgeType.PROCEDURAL,
        description="PROCEDURAL para exploración topológica, INFORMATIVE para metadatos.",
    )
    cost: int = Field(default=1, description="Costo fijo, siempre 1 en esta fase.")

    @field_validator("cost")
    @classmethod
    def validate_fixed_cost(cls, v: int) -> int:
        if v != 1:
            raise ValueError("cost debe ser siempre 1 (costo fijo por diseño)")
        return v


class GraphExtractionResult(BaseModel):
    """
    Salida completa que debe devolver el SLM (Groq, JSON mode) al procesar
    el prompt del usuario. Es el contrato exacto que se le fuerza al modelo.
    """

    nodes: list[NodeExtracted] = Field(default_factory=list)
    edges: list[EdgeExtracted] = Field(default_factory=list)

    @field_validator("edges")
    @classmethod
    def validate_edges_reference_known_nodes(
        cls, edges: list[EdgeExtracted], info
    ) -> list[EdgeExtracted]:
        nodes = info.data.get("nodes", [])
        node_ids = {n.id for n in nodes}
        for e in edges:
            if e.source not in node_ids or e.target not in node_ids:
                raise ValueError(
                    f"Arista {e.source}->{e.target} referencia un nodo "
                    f"que no está en 'nodes'"
                )
        return edges