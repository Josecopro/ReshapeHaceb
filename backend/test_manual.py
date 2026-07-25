"""
test_manual.py

Script de prueba manual para el pipeline hasta donde llevamos:
  prompt (texto) -> graph_extractor (SLM/Groq) -> normalizer (RapidFuzz +
  vecindad K-hop) -> topology (divergencia/convergencia)

No requiere FastAPI ni front -- simula la llamada directamente por consola.
Requiere GROQ_API_KEY configurada en el entorno (o en un .env cargado con
python-dotenv, ver instrucciones abajo).

USO:
    python test_manual.py "<prompt>"
    python test_manual.py "<prompt>" --nodes ../db/nodes.json --edges ../db/edges.json

    python test_manual.py "el compresor no enfría, no sé si es inverter o no"
    python test_manual.py "hay un problema de voltaje de entrada"
"""

import argparse
import sys

from core.graph_builder import build_from_extraction, load_master_graph
from core.topology import evaluate_topology
from services.graph_extractor import GraphExtractionError, extract_graph_from_prompt
from services.normalizer import normalize_and_extract_neighborhood


def run(prompt: str, nodes_path: str, edges_path: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"PROMPT: {prompt}")
    print("=" * 70)

    # 1. Cargar G_db (grafo maestro)
    db_graph = load_master_graph(nodes_path, edges_path)
    print(f"\n[G_db] {db_graph.number_of_nodes()} nodos, "
          f"{db_graph.number_of_edges()} aristas cargadas.")

    # 2. Extraer subgrafo candidato del prompt (SLM vía Groq)
    try:
        extraction = extract_graph_from_prompt(prompt)
    except GraphExtractionError as exc:
        print(f"\n[ERROR extracción] {exc}")
        return

    print(f"\n[SLM extrajo] {len(extraction.nodes)} nodos, "
          f"{len(extraction.edges)} aristas:")
    for n in extraction.nodes:
        print(f"    - {n.id}  (label='{n.label}', cluster='{n.cluster_id}')")
    for e in extraction.edges:
        print(f"    - {e.source} -> {e.target}  ({e.edge_type.value})")

    extracted_graph = build_from_extraction(extraction)

    # 3. Normalizar contra G_db (fuzzy matching) + extraer vecindad K-hop
    norm_result = normalize_and_extract_neighborhood(extracted_graph, db_graph)

    print("\n[Matching contra G_db]")
    for m in norm_result.matches:
        status = "OK" if m.matched_id else "SIN MATCH"
        print(f"    - '{m.extracted_id}' -> '{m.matched_id}' "
              f"(score={m.score:.1f}, por={m.matched_by}) [{status}]")

    print(f"\n[Vecindad extraída de G_db] "
          f"{norm_result.neighborhood_subgraph.number_of_nodes()} nodos: "
          f"{list(norm_result.neighborhood_subgraph.nodes)}")

    # 4. Evaluar topología (divergencia/convergencia por mayoría >70%)
    topo_result = evaluate_topology(
        norm_result.neighborhood_subgraph, extracted_graph, db_graph
    )

    print(f"\n[TOPOLOGÍA] estado={topo_result.estado.value}  "
          f"origen='{topo_result.origen}'")
    print(f"    Rutas podadas (max 5, más cortas): {len(topo_result.rutas_podadas)}")

    if topo_result.opciones:
        print("    Opciones vistas entre las rutas podadas:")
        for opt in topo_result.opciones:
            print(f"      * {opt.leaf_id}  (label='{opt.leaf_label}')  "
                  f"count={opt.count}/{len(topo_result.rutas_podadas)}  "
                  f"ratio={opt.ratio:.0%}")
            if opt.leaf_why:
                print(f"          why: {opt.leaf_why}")
            for p in opt.paths:
                print(f"          {' -> '.join(p)}")

    if topo_result.estado.value == "CONVERGENTE":
        top = topo_result.hoja_mayoritaria
        print(f"\n    >70% converge en: {top.leaf_id} ({top.ratio:.0%})")
        print(f"    Camino seleccionado (mínimo): "
              f"{' -> '.join(topo_result.camino_seleccionado)}")
        descartadas = [o for o in topo_result.opciones if o.leaf_id != top.leaf_id]
        if descartadas:
            print(f"    Nota que debería agregar el LLM: 'Supuse {top.leaf_label}. "
                  f"Si no es así, indícame si es por "
                  f"{' o por '.join(o.leaf_label for o in descartadas)}.'")
    elif topo_result.estado.value == "DIVERGENTE":
        print(f"\n    Ninguna opción supera 70% -> pregunta de aclaración bloqueante:")
        opciones_txt = " / ".join(
            f"{o.leaf_label} ({o.ratio:.0%})" for o in topo_result.opciones
        )
        print(f"    '¿Cuál de estas opciones aplica: {opciones_txt}?'")
    else:
        print("    No se encontró ningún camino hacia una hoja.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt del usuario en lenguaje natural")
    parser.add_argument(
        "--nodes", default="data/nodes.json", help="Ruta a nodes.json (default: data/nodes.json)"
    )
    parser.add_argument(
        "--edges", default="data/edges.json", help="Ruta a edges.json (default: data/edges.json)"
    )
    args = parser.parse_args()
    run(args.prompt, args.nodes, args.edges)