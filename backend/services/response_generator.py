"""
services/response_generator.py

Generación de respuestas del asistente adaptativas e interactivas.
Cuando la evaluación topológica devuelve SIN_CAMINO (o DIVERGENTE),
utiliza el LLM de Groq (o una estrategia estructurada con fallback)
para contrapreguntar al usuario/técnico con preguntas de aclaración
diagnósticas precisas en lenguaje natural accesible, sin exponer bloques
JSON al usuario.
"""

from typing import Any
import networkx as nx

from config import LLM_RESPONSE_MODEL, GROQ_API_KEY, get_groq_api_key
from core.topology import TopologicalState, TopologyResult
from services.llm_client import get_groq_client


def generate_assistant_response(
    user_message: str,
    topology_result: TopologyResult,
    extracted_nodes: list,
    norm_result: Any,
    db_graph: nx.DiGraph,
) -> str:
    """
    Construye la respuesta final del asistente limpia en Markdown.
    No incluye bloques ```json en el mensaje de salida.
    """
    estado = topology_result.estado
    extracted_labels = [getattr(n, "label", str(n)) for n in extracted_nodes]

    if estado == TopologicalState.SIN_CAMINO:
        return _generate_sin_camino_response(
            user_message=user_message,
            extracted_labels=extracted_labels,
            matches=norm_result.matches if norm_result else [],
            db_graph=db_graph,
        )

    lines = []
    if extracted_labels:
        lines.append("📋 **Nodos identificados en tu consulta:**")
        for lbl in extracted_labels:
            lines.append(f"  - {lbl}")
        lines.append("")

    if estado == TopologicalState.CONVERGENTE:
        hoja = topology_result.hoja_mayoritaria
        lines.append("✅ **Resultado: CONVERGENTE** — El análisis converge en un camino principal.")
        lines.append("")
        if hoja:
            lines.append(f"**Destino más probable:** _{hoja.leaf_label}_")
            lines.append(f"  - Confianza: {hoja.ratio:.0%}")
            if topology_result.camino_seleccionado:
                lines.append(f"  - Ruta: {' → '.join(topology_result.camino_seleccionado)}")
            if hoja.leaf_why:
                lines.append(f"  - Síntomas asociados: {', '.join(hoja.leaf_why)}")
        lines.append("")
        if len(topology_result.opciones) > 1:
            lines.append(f"*También se consideraron {len(topology_result.opciones) - 1} ruta(s) alternativa(s).*")
    else:
        # DIVERGENTE
        lines.append("❓ **Resultado: DIVERGENTE** — Tu consulta abarca múltiples caminos de diagnóstico.")
        lines.append("")
        lines.append("**Opciones principales identificadas en la base de conocimiento:**")
        for opt in topology_result.opciones:
            lines.append(f"  - _{opt.leaf_label}_ ({opt.ratio:.0%} de probabilidad)")
        lines.append("")
        lines.append("🔍 **Para continuar con la solución ideal, por favor aclárame:**")
        lines.append("¿Cuál de estas situaciones o síntomas se ajusta mejor al estado actual del equipo?")

    return "\n".join(lines)


def _generate_sin_camino_response(
    user_message: str,
    extracted_labels: list[str],
    matches: list[Any],
    db_graph: nx.DiGraph,
) -> str:
    """
    Genera contrapreguntas en lenguaje natural limpio sin JSON.
    """
    api_key = get_groq_api_key() or GROQ_API_KEY
    if api_key:
        try:
            llm_text = _call_llm_for_clarification(user_message, extracted_labels, db_graph)
            if llm_text and len(llm_text.strip()) > 30:
                # Limpiar cualquier bloque json accidental si el modelo lo generara
                cleaned = llm_text.split("```json")[0].strip()
                return cleaned if cleaned else llm_text
        except Exception:
            pass  # Fallback determinista abajo

    return _build_fallback_clarification(user_message, extracted_labels, matches, db_graph)


def _call_llm_for_clarification(
    user_message: str,
    extracted_labels: list[str],
    db_graph: nx.DiGraph,
) -> str:
    client = get_groq_client()

    nodes_info = []
    for node_id, data in db_graph.nodes(data=True):
        label = data.get("label", node_id)
        why = data.get("why") or []
        why_str = f" [Síntomas/Whys: {'; '.join(why)}]" if why else ""
        nodes_info.append(f"- ID: '{node_id}' | Label: '{label}'{why_str}")

    nodes_context = "\n".join(nodes_info)

    system_prompt = (
        "Eres un asistente de soporte técnico experto en electrodomésticos Haceb.\n"
        "Tu tarea es generar contrapreguntas de aclaración en lenguaje natural fluido y Markdown limpio cuando la consulta inicial "
        "no contiene información suficiente para trazar una ruta procedimental única en el grafo de conocimiento.\n\n"
        "REGLAS OBLIGATORIAS:\n"
        "1. Inicia reconociendo los detalles que el usuario proporcionó.\n"
        "2. Formula entre 3 y 4 CONTRAPREGUNTAS diagnósticas concretas basándote en los síntomas ('whys') y nodos de G_db.\n"
        "3. NO incluyas código JSON, ni bloques de código ```json, ni explicaciones técnicas internas en la respuesta. Debe ser puramente texto y viñetas en Markdown limpio."
    )

    user_prompt = (
        f"Consulta del usuario: \"{user_message}\"\n"
        f"Síntomas/Conceptos identificados: {extracted_labels if extracted_labels else 'No especificado'}\n\n"
        f"Nodos canónicos de G_db (ID, Label y Whys asociados):\n{nodes_context}\n\n"
        "Genera únicamente la respuesta con las contrapreguntas en Markdown sin ningún bloque JSON."
    )

    completion = client.chat.completions.create(
        model=LLM_RESPONSE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return completion.choices[0].message.content


def _build_fallback_clarification(
    user_message: str,
    extracted_labels: list[str],
    matches: list[Any],
    db_graph: nx.DiGraph,
) -> str:
    lines = []
    lines.append("🔍 **Diagnóstico en progreso — Necesitamos un poco más de detalle**")
    lines.append("")
    if extracted_labels:
        lines.append(f"Identifiqué en tu consulta: *{', '.join(extracted_labels)}*.")
        lines.append("Para trazar el procedimiento exacto de reparación, se requieren algunas precisiones técnicas adicionales.")
    else:
        lines.append("Para trazar el procedimiento exacto de reparación, se requieren algunas precisiones sobre el estado del equipo.")

    lines.append("")
    lines.append("**Por favor respóndeme las siguientes contrapreguntas para ofrecerte la respuesta ideal:**")
    lines.append("")
    lines.append("1. ⚡ **Comportamiento del compresor**: ¿Escuchas algún 'clic' repetido, un zumbido al intentar arrancar, o el motor permanece en silencio?")
    lines.append("2. ❄️ **Estado de enfriamiento**: ¿El congelador enfría mientras la parte inferior (conservador) no enfría, o ambos compartimentos están tibios?")
    lines.append("3. 💨 **Ventiladores e higiene térmica**: ¿Se escucha el ventilador interno del evaporador o el ventilador trasero del condensador?")
    lines.append("4. 🖥️ **Códigos de error**: ¿El panel de control muestra algún código de error o patrón de luces parpadeantes?")

    return "\n".join(lines)
