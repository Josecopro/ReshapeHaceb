"""
services/normalizer.py

Responsabilidad: dado un G_extraido (subgrafo candidato crudo del SLM,
core/graph_builder.build_from_extraction) y el G_db (grafo maestro cargado
con load_master_graph), este módulo:

1. Hace fuzzy matching (RapidFuzz) de cada nodo extraído contra los ids/
   labels canónicos de G_db, para resolver a qué nodo real corresponde
   (ej. "verificarCompresor" del SLM -> "comprobarTipoCompresor" en G_db).

2. Para cada nodo matcheado, extrae su VECINDAD K-hop en G_db (K=2 por
   defecto, navegando en ambas direcciones -- se trata el grafo como no
   dirigido solo para el cálculo de distancia, conservando la dirección
   real de las aristas en el subgrafo resultante).

   Esto es lo que evita mandar G_db completo al LLM grande: solo se
   extrae y se pasa el fragmento relevante alrededor de la intención
   del usuario.

Este módulo NO decide divergencia/convergencia (eso es core/topology.py).
Solo resuelve "qué nodos son estos" y "qué fragmento de G_db es relevante".
"""

from dataclasses import dataclass, field

import networkx as nx
from rapidfuzz import fuzz, process

DEFAULT_FUZZY_THRESHOLD = 60
DEFAULT_NEIGHBORHOOD_HOPS = 4


@dataclass
class NodeMatch:
    """Resultado del matching de un nodo extraído contra G_db."""

    extracted_id: str
    matched_id: str | None  # None si no hubo match por encima del umbral
    score: float
    matched_by: str  # "id" | "label" | "none"


@dataclass
class NormalizationResult:
    """Salida completa de la normalización."""

    matches: list[NodeMatch] = field(default_factory=list)
    neighborhood_subgraph: nx.DiGraph = field(default_factory=nx.DiGraph)

    @property
    def matched_ids(self) -> list[str]:
        return [m.matched_id for m in self.matches if m.matched_id is not None]

    @property
    def unmatched_extracted_ids(self) -> list[str]:
        return [m.extracted_id for m in self.matches if m.matched_id is None]


def _match_single_node(
    extracted_id: str,
    extracted_label: str,
    db_graph: nx.DiGraph,
    threshold: int,
) -> NodeMatch:
    """
    Intenta matchear primero por id (más barato y más preciso cuando el SLM
    acierta el formato canónico), y si no supera el umbral, cae a matchear
    por label (más tolerante a que el SLM haya usado otras palabras).
    """
    db_ids = list(db_graph.nodes)
    db_labels = {n: data.get("label", n) for n, data in db_graph.nodes(data=True)}

    # 1. Intento por id
    id_result = process.extractOne(
        extracted_id, db_ids, scorer=fuzz.WRatio
    )
    if id_result is not None:
        matched_id, score, _ = id_result
        if score >= threshold:
            return NodeMatch(
                extracted_id=extracted_id,
                matched_id=matched_id,
                score=score,
                matched_by="id",
            )

    # 2. Intento por label
    label_result = process.extractOne(
        extracted_label, db_labels, scorer=fuzz.WRatio
    )
    if label_result is not None:
        matched_label, score, matched_id = label_result
        if score >= threshold:
            return NodeMatch(
                extracted_id=extracted_id,
                matched_id=matched_id,
                score=score,
                matched_by="label",
            )

    # 3. Sin match aceptable
    best_score = max(
        id_result[1] if id_result else 0,
        label_result[1] if label_result else 0,
    )
    return NodeMatch(
        extracted_id=extracted_id,
        matched_id=None,
        score=best_score,
        matched_by="none",
    )


def match_nodes_to_db(
    extracted_graph: nx.DiGraph,
    db_graph: nx.DiGraph,
    threshold: int = DEFAULT_FUZZY_THRESHOLD,
) -> list[NodeMatch]:
    """Matchea cada nodo del subgrafo extraído contra G_db."""
    matches = []
    for node_id, data in extracted_graph.nodes(data=True):
        label = data.get("label", node_id)
        matches.append(_match_single_node(node_id, label, db_graph, threshold))
    return matches


def extract_k_hop_neighborhood(
    db_graph: nx.DiGraph,
    matched_ids: list[str],
    k: int = DEFAULT_NEIGHBORHOOD_HOPS,
) -> nx.DiGraph:
    """
    Extrae el subgrafo de G_db correspondiente a la vecindad K-hop de cada
    nodo en matched_ids, navegando en ambas direcciones (predecesores y
    sucesores) para no perder contexto causal previo (ej. síntomas que
    "requieren" cierta evaluación antes del nodo matcheado).

    La distancia se calcula tratando el grafo como no dirigido (para no
    ignorar predecesores), pero el subgrafo devuelto conserva las aristas
    dirigidas originales de G_db.
    """
    if not matched_ids:
        return nx.DiGraph()

    undirected_view = db_graph.to_undirected(as_view=True)

    relevant_nodes: set[str] = set()
    for node_id in matched_ids:
        if node_id not in db_graph:
            continue
        # ego_graph sobre la vista no dirigida nos da todos los nodos a
        # distancia <= k en cualquier dirección.
        ego = nx.ego_graph(undirected_view, node_id, radius=k)
        relevant_nodes.update(ego.nodes)

    # Conservamos direccionalidad real tomando el subgrafo inducido sobre
    # el DiGraph original, no sobre la vista no dirigida.
    return db_graph.subgraph(relevant_nodes).copy()


def normalize_and_extract_neighborhood(
    extracted_graph: nx.DiGraph,
    db_graph: nx.DiGraph,
    *,
    threshold: int = DEFAULT_FUZZY_THRESHOLD,
    hops: int = DEFAULT_NEIGHBORHOOD_HOPS,
) -> NormalizationResult:
    """
    Punto de entrada principal: matchea los nodos extraídos contra G_db y
    devuelve el fragmento de vecindad relevante ya acotado, listo para que
    core/topology.py lo use en vez de operar sobre G_db completo.
    """
    matches = match_nodes_to_db(extracted_graph, db_graph, threshold=threshold)

    result = NormalizationResult(matches=matches)
    result.neighborhood_subgraph = extract_k_hop_neighborhood(
        db_graph, result.matched_ids, k=hops
    )
    return result