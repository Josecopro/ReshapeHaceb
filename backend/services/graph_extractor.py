"""
services/graph_extractor.py

Convierte el prompt en lenguaje natural del usuario en un subgrafo candidato
(GraphExtractionResult) usando un SLM (Small Language Model) vía Groq con
structured outputs (json_schema).

Este servicio NO valida contra G_db (grafo maestro) ni hace fuzzy matching
de ids -- eso ocurre después, en services/normalizer.py (RapidFuzz) y en
core/topology.py. Aquí únicamente se transforma texto libre en la forma
mínima Node/Edge que el resto del pipeline necesita.

Prioridad de campos (por decisión de negocio):
  - label y relaciones (edges) son lo importante -> instrucciones estrictas.
  - cluster_id es secundario/genérico -> instrucciones laxas, puede ser
    aproximado, la normalización posterior no depende de que sea exacto.
"""

from pydantic import ValidationError

from config import SLM_EXTRACTION_MODEL
from schemas.graph_schema import GraphExtractionResult
from services.llm_client import call_with_json_schema

SYSTEM_PROMPT = """\
Eres un extractor de grafos de conocimiento para un sistema de soporte \
técnico de electrodomésticos Haceb. Tu única tarea es convertir la consulta \
del usuario en un subgrafo mínimo (nodos y aristas) que represente su \
intención y las relaciones procedimentales implícitas.

REGLAS ESTRICTAS:
1. id de cada nodo: camelCase, en infinitivo (verbo base), sin espacios, \
sin guiones, sin tildes. Ejemplos válidos: "verificarSaldo", \
"comprobarTipoCompresor", "despacharRepuesto". Ejemplos inválidos: \
"verificando_saldo", "Verificar Saldo", "VerificarSaldo".
2. label: texto legible, lo más fiel posible a como lo expresó el usuario. \
Este es el campo más importante para el matching posterior, prioriza \
fidelidad semántica sobre elegancia.
3. cluster_id: agrupador temático laxo (puede ser genérico, ej. \
"FALLA_TECNICA", "CONSULTA_GENERAL"). No te preocupes por precisión aquí.
4. Las aristas (edges) deben reflejar el orden causal/procedimental real \
de la consulta: si el usuario dice "el compresor no enfría y no sé si es \
inverter", el flujo procedimental es síntoma -> evaluación -> posible \
estado, no al revés.
5. edge_type: usa "PROCEDURAL" para relaciones causales/de flujo (la \
inmensa mayoría). Usa "INFORMATIVE" solo para atributos o metadatos que \
no forman parte de un flujo de decisión (ej. mención de fecha, cliente, \
prioridad).
6. cost: siempre 1.
7. Nunca inventes nodos que no se desprendan directa o razonablemente del \
texto del usuario. Si el usuario da una sola idea sin relación, devuelve \
un único nodo y una lista de edges vacía.
8. No agregues explicaciones, texto adicional, ni markdown. Solo el JSON \
que cumple el schema entregado.
"""


class GraphExtractionError(Exception):
    """Error al extraer o validar el subgrafo candidato desde el prompt."""


def extract_graph_from_prompt(
    user_prompt: str,
    *,
    model: str = SLM_EXTRACTION_MODEL,
) -> GraphExtractionResult:
    """
    Punto de entrada principal. Toma el texto del usuario y devuelve un
    GraphExtractionResult validado (nodos + aristas).

    Lanza GraphExtractionError si el SLM devuelve algo que no cumple el
    contrato Pydantic, incluso después del structured output de Groq
    (defensa en profundidad: json_schema reduce pero no elimina al 100%
    la posibilidad de una salida mal formada).
    """
    if not user_prompt or not user_prompt.strip():
        raise GraphExtractionError("El prompt del usuario está vacío.")

    json_schema = GraphExtractionResult.model_json_schema()

    try:
        raw_result = call_with_json_schema(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt.strip(),
            json_schema=json_schema,
            schema_name="graph_extraction_result",
        )
    except ValueError as exc:
        raise GraphExtractionError(f"Fallo en la llamada al SLM: {exc}") from exc

    try:
        return GraphExtractionResult.model_validate(raw_result)
    except ValidationError as exc:
        raise GraphExtractionError(
            f"El subgrafo extraído no cumple el schema esperado: {exc}"
        ) from exc