"""
core/topology.py

Motor puramente determinista de evaluación topológica (Paso 2 del pipeline).

LÓGICA VIGENTE (reemplaza el enfoque anterior basado en cluster_id "sol_"):

1. Nodo origen: el nodo sin predecesores dentro de G_extraido (orden causal
   del prompt).
2. Nodo hoja: cualquier nodo sin sucesores PROCEDURAL dentro de la vecindad
   ya acotada (normalizer.py) -- ya no existe un marcador especial de
   "cierre"; una hoja es simplemente el final de una cadena procedimental.
3. Se calculan TODOS los caminos simples PROCEDURAL desde el origen hasta
   cada hoja alcanzable (respetando D_max), y se PODAN a las 5 rutas MÁS
   CORTAS (self-consistency acotado: no se evalúan todas las ramas, solo
   las más directas/probables).
4. Sobre esas <=5 rutas podadas, se agrupa por el id EXACTO del nodo hoja
   (no por cluster_id).
5. Regla de mayoría (self-consistency):
   - Si la hoja más frecuente representa >70% de las rutas podadas ->
     CONVERGENTE. Se responde de forma autónoma, pero la respuesta debe
     incluir una nota de supuesto (ej. "Supuse X. Si no es así, indícame
     si es por A o por B") -- eso lo redacta el LLM final, aquí solo se
     deja la señal (hoja_mayoritaria + alternativas_descartadas).
   - Si ninguna hoja supera 70% -> DIVERGENTE. Se bloquea la respuesta
     autónoma y se enumeran las opciones vistas como pregunta de
     aclaración obligatoria.
   - Si no hay ningún camino -> SIN_CAMINO.

No genera texto ni llama al LLM -- es lógica de grafos pura (NetworkX).
"""

from dataclasses import dataclass, field
from enum import Enum

import networkx as nx

from config import MAX_EXPLORATION_DEPTH

MAX_PRUNED_PATHS = 5
CONVERGENCE_THRESHOLD = 0.70  # > 70%, estrictamente mayor


class TopologicalState(str, Enum):
    DIVERGENTE = "DIVERGENTE"
    CONVERGENTE = "CONVERGENTE"
    SIN_CAMINO = "SIN_CAMINO"


@dataclass
class LeafOption:
    """Una opción de destino vista entre las rutas podadas."""

    leaf_id: str
    leaf_label: str
    leaf_why: list[str]
    count: int
    ratio: float
    paths: list[list[str]] = field(default_factory=list)


@dataclass
class TopologyResult:
    estado: TopologicalState
    origen: str | None
    rutas_podadas: list[list[str]] = field(default_factory=list)
    opciones: list[LeafOption] = field(default_factory=list)  # ordenadas por count desc
    hoja_mayoritaria: LeafOption | None = None  # solo si CONVERGENTE
    camino_seleccionado: list[str] | None = None  # solo si CONVERGENTE


def find_origin_node(extracted_graph: nx.DiGraph) -> str | None:
    """
    El nodo origen es aquel sin predecesores DENTRO del subgrafo extraído
    (el punto de partida del orden causal que produjo el SLM).

    Si hay más de un nodo sin predecesores, se toma el primero en orden de
    inserción como criterio determinista y estable. Si hay ciclo (no
    debería, pero el SLM puede fallar), cae al primer nodo insertado.
    """
    if extracted_graph.number_of_nodes() == 0:
        return None

    roots = [n for n, indeg in extracted_graph.in_degree() if indeg == 0]
    if roots:
        node_order = list(extracted_graph.nodes)
        roots.sort(key=lambda n: node_order.index(n))
        return roots[0]

    return next(iter(extracted_graph.nodes))


def _procedural_view(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Subgrafo que conserva SOLO las aristas PROCEDURAL. Las INFORMATIVE se
    descartan para la exploración del árbol de decisiones.
    """
    procedural_edges = [
        (u, v)
        for u, v, data in graph.edges(data=True)
        if data.get("edge_type") == "PROCEDURAL"
    ]
    view = nx.DiGraph()
    view.add_nodes_from(graph.nodes(data=True))
    view.add_edges_from(
        (u, v, graph.get_edge_data(u, v)) for u, v in procedural_edges
    )
    return view


def _is_leaf(full_db_procedural_view: nx.DiGraph, node: str) -> bool:
    """
    Una hoja es un nodo sin sucesores PROCEDURAL, evaluado contra el grafo
    maestro COMPLETO (no contra la vecindad recortada por normalizer.py).

    Esto es crítico: si evaluáramos "hoja" solo dentro de la vecindad
    acotada, un nodo intermedio que en realidad tiene más pasos después
    (pero esos pasos cayeron fuera de la vecindad K-hop) se confundiría
    con un final de proceso real, y rutas cortas-pero-truncadas le
    ganarían en la poda a rutas más largas pero verdaderamente completas.
    """
    if node not in full_db_procedural_view:
        # Nodo fuera de G_db (no debería pasar tras el matching, pero por
        # seguridad lo tratamos como hoja para no romper la búsqueda).
        return True
    return full_db_procedural_view.out_degree(node) == 0


def find_all_procedural_paths(
    neighborhood_graph: nx.DiGraph,
    origin: str,
    full_db_graph: nx.DiGraph,
    max_depth: int = MAX_EXPLORATION_DEPTH,
) -> list[list[str]]:
    """
    Encuentra todos los caminos simples PROCEDURAL desde `origin` hasta
    cualquier hoja alcanzable DENTRO de `neighborhood_graph` (la vecindad
    ya acotada), pero usando `full_db_graph` (G_db completo) para decidir
    qué nodos son realmente hojas -- ver _is_leaf().
    """
    if origin not in neighborhood_graph:
        return []

    proc_view = _procedural_view(neighborhood_graph)
    if origin not in proc_view:
        return []

    full_proc_view = _procedural_view(full_db_graph)
    leaf_nodes = [n for n in proc_view.nodes if _is_leaf(full_proc_view, n)]

    all_paths: list[list[str]] = []
    for target in leaf_nodes:
        if target == origin:
            continue
        try:
            paths = nx.all_simple_paths(
                proc_view, source=origin, target=target, cutoff=max_depth
            )
            all_paths.extend(paths)
        except nx.NodeNotFound:
            continue

    return all_paths


def prune_shortest_paths(
    paths: list[list[str]], limit: int = MAX_PRUNED_PATHS
) -> list[list[str]]:
    """
    Poda la lista de caminos a las `limit` rutas más cortas (por número de
    nodos). Empates se resuelven por orden de aparición (determinismo).
    """
    return sorted(paths, key=len)[:limit]


def evaluate_topology(
    neighborhood_graph: nx.DiGraph,
    extracted_graph: nx.DiGraph,
    db_graph: nx.DiGraph,
    max_depth: int = MAX_EXPLORATION_DEPTH,
    max_pruned_paths: int = MAX_PRUNED_PATHS,
    convergence_threshold: float = CONVERGENCE_THRESHOLD,
) -> TopologyResult:
    """
    Punto de entrada principal del motor topológico.

    neighborhood_graph: fragmento de G_db ya acotado (normalizer.py), los
        nodos deben traer 'label', 'cluster_id' y 'why' (lista de str).
    extracted_graph: G_extraido crudo (para determinar el nodo origen).
    db_graph: G_db COMPLETO (para decidir qué nodos son hojas reales,
        independiente de qué tanto recortó la vecindad K-hop).
    """
    origin = find_origin_node(extracted_graph)
    if origin is None or origin not in neighborhood_graph:
        return TopologyResult(estado=TopologicalState.SIN_CAMINO, origen=origin)

    all_paths = find_all_procedural_paths(
        neighborhood_graph, origin, db_graph, max_depth
    )
    if not all_paths:
        return TopologyResult(estado=TopologicalState.SIN_CAMINO, origen=origin)

    pruned = prune_shortest_paths(all_paths, limit=max_pruned_paths)
    total = len(pruned)

    paths_by_leaf: dict[str, list[list[str]]] = {}
    for path in pruned:
        leaf = path[-1]
        paths_by_leaf.setdefault(leaf, []).append(path)

    opciones = []
    for leaf_id, leaf_paths in paths_by_leaf.items():
        data = neighborhood_graph.nodes[leaf_id]
        count = len(leaf_paths)
        opciones.append(
            LeafOption(
                leaf_id=leaf_id,
                leaf_label=data.get("label", leaf_id),
                leaf_why=data.get("why") or [],
                count=count,
                ratio=count / total,
                paths=leaf_paths,
            )
        )
    opciones.sort(key=lambda o: o.count, reverse=True)

    top = opciones[0]
    if top.ratio > convergence_threshold:
        shortest_of_top = min(top.paths, key=len)
        return TopologyResult(
            estado=TopologicalState.CONVERGENTE,
            origen=origin,
            rutas_podadas=pruned,
            opciones=opciones,
            hoja_mayoritaria=top,
            camino_seleccionado=shortest_of_top,
        )

    return TopologyResult(
        estado=TopologicalState.DIVERGENTE,
        origen=origin,
        rutas_podadas=pruned,
        opciones=opciones,
    )