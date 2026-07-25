"""
services/response_generator.py

Generación de respuestas del asistente adaptativas e interactivas.
Cuando la evaluación topológica devuelve SIN_CAMINO (o DIVERGENTE),
utiliza el LLM de Groq (o una estrategia estructurada con fallback)
para contrapreguntar al usuario/técnico con preguntas de aclaración
diagnósticas precisas en lugar de un mensaje estático de error.
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
    Construye la respuesta final del asistente.
    Para CONVERGENTE / DIVERGENTE, formatea la salida estructurada.
    Para SIN_CAMINO, genera contrapreguntas diagnósticas específicas.
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
    Genera contrapreguntas para guiar al usuario cuando no hay un camino directo en G_db.
    """
    api_key = get_groq_api_key() or GROQ_API_KEY
    if api_key:
        try:
            llm_text = _call_llm_for_clarification(user_message, extracted_labels, db_graph)
            if llm_text and len(llm_text.strip()) > 30:
                return llm_text
        except Exception:
            pass  # Fallback a plantilla determinista abajo

    return _build_fallback_clarification(user_message, extracted_labels, matches, db_graph)


def _call_llm_for_clarification(
    user_message: str,
    extracted_labels: list[str],
    db_graph: nx.DiGraph,
) -> str:
    client = get_groq_client()

    sample_nodes = []
    for node_id, data in db_graph.nodes(data=True):
        label = data.get("label", node_id)
        why = data.get("why") or []
        why_str = f" ({', '.join(why[:2])})" if why else ""
        sample_nodes.append(f"- {label}{why_str}")

    context_str = "\n".join(sample_nodes[:15])

    system_prompt = (
        "Eres un asistente de soporte técnico experto en electrodomésticos y refrigeradores Haceb. "
        "Tu objetivo es ayudar al técnico a diagnosticar una falla cuando la consulta inicial "
        "no es lo suficientemente específica para seguir una ruta procedimental exacta en la base de conocimiento.\n\n"
        "REGLAS:\n"
        "1. Inicia reconociendo amablemente los detalles que el usuario proporcionó.\n"
        "2. Explica de forma concisa que se necesitan más detalles específicos para trazar la ruta de solución ideal.\n"
        "3. Formula exactamente entre 3 y 4 CONTRAPREGUNTAS diagnósticas muy concretas, técnicas y relevantes "
        "(ej. ruidos/clics del compresor, funcionamiento de ventiladores, presencia de escarcha/hielo, códigos de error en display, etc.).\n"
        "4. Usa formato Markdown limpio con viñetas o números para que las preguntas sean claras y destacadas.\n"
        "5. Sé profesional y mantén un excelente tono de servicio técnico."
    )

    user_prompt = (
        f"Consulta del usuario: \"{user_message}\"\n"
        f"Conceptos o síntomas identificados: {extracted_labels if extracted_labels else 'Ninguno específico'}\n\n"
        f"Procedimientos/Diagnósticos disponibles en la base de conocimiento:\n{context_str}\n\n"
        "Genera una respuesta con contrapreguntas oportunas y claras para este caso."
    )

    completion = client.chat.completions.create(
        model=LLM_RESPONSE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
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
    lines.append("")
    lines.append("Con tu respuesta identificaremos la ruta precisa en el grafo de conocimiento.")

    return "\n".join(lines)
