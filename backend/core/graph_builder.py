"""
core/graph_builder.py

Dos responsabilidades separadas y deliberadamente NO mezcladas aquí:

1. load_master_graph(): carga G_db (el grafo maestro de la empresa) desde
   nodes.json + edges.json a un nx.DiGraph. Es la fuente de verdad.

2. build_from_extraction(): convierte el GraphExtractionResult que produce
   el SLM (services/graph_extractor.py) en un nx.DiGraph *candidato*,
   standalone, SIN cruzarlo todavía contra G_db.

El cruce/matching entre ambos (fuzzy matching de ids, acotar el fragmento
relevante de G_db en vez de cargarlo completo al contexto) es
responsabilidad de services/normalizer.py, no de este archivo. Este builder
se mantiene puramente estructural: JSON/objetos -> nx.DiGraph.
"""

import json
from pathlib import Path

import networkx as nx

from schemas.graph_schema import GraphExtractionResult

# --- Grafo maestro (G_db) ---


def load_master_graph(
    nodes_path: str | Path,
    edges_path: str | Path,
) -> nx.DiGraph:
    """
    Carga el grafo maestro G_db desde dos archivos JSON locales:

    nodes.json -> lista de objetos:
        {"id": str, "label": str, "cluster_id": str}

    edges.json -> lista de objetos:
        {"source": str, "target": str, "edge_type": "PROCEDURAL"|"INFORMATIVE", "cost": 1}

    Lanza ValueError si una arista referencia un nodo inexistente, o si hay
    ids de nodo duplicados -- preferimos fallar temprano y explícito antes
    de dejar que G_db quede en un estado inconsistente silenciosamente.
    """
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)

    with nodes_path.open("r", encoding="utf-8") as f:
        raw_nodes = json.load(f)
    with edges_path.open("r", encoding="utf-8") as f:
        raw_edges = json.load(f)

    graph = nx.DiGraph()

    seen_ids: set[str] = set()
    for node in raw_nodes:
        node_id = node["id"]
        if node_id in seen_ids:
            raise ValueError(f"Nodo duplicado en nodes.json: '{node_id}'")
        seen_ids.add(node_id)
        graph.add_node(
            node_id,
            label=node["label"],
            cluster_id=node.get("cluster_id"),
        )

    for edge in raw_edges:
        source, target = edge["source"], edge["target"]
        if source not in graph or target not in graph:
            raise ValueError(
                f"Arista {source}->{target} referencia un nodo que no "
                f"existe en nodes.json"
            )
        graph.add_edge(
            source,
            target,
            edge_type=edge.get("edge_type", "PROCEDURAL"),
            cost=edge.get("cost", 1),
        )

    return graph


# --- Subgrafo candidato (G_extraido, viene del SLM) ---


def build_from_extraction(extraction: GraphExtractionResult) -> nx.DiGraph:
    """
    Convierte el subgrafo candidato validado por Pydantic (salida del SLM)
    en un nx.DiGraph. No valida contra G_db -- este grafo es "crudo", tal
    como lo propuso el modelo, todavía con ids que pueden no coincidir con
    los canónicos de G_db (eso lo resuelve normalizer.py con RapidFuzz).
    """
    graph = nx.DiGraph()

    for node in extraction.nodes:
        graph.add_node(
            node.id,
            label=node.label,
            cluster_id=node.cluster_id,
        )

    for edge in extraction.edges:
        graph.add_edge(
            edge.source,
            edge.target,
            edge_type=edge.edge_type.value,
            cost=edge.cost,
        )

    return graph


def graph_to_dict(graph: nx.DiGraph) -> dict:
    """
    Serializa un nx.DiGraph de vuelta a la forma {nodes: [...], edges: [...]}
    compatible con el Node/Edge Schema. Útil para depurar o para el contrato
    de salida del endpoint (subgrafo_ejecutado, inspector visual del front).
    """
    nodes = [
        {"id": n, **{k: v for k, v in data.items()}}
        for n, data in graph.nodes(data=True)
    ]
    edges = [
        {"source": u, "target": v, **{k: val for k, val in data.items()}}
        for u, v, data in graph.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges}