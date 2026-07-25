"""
services/llm_client.py

Cliente centralizado para Groq. Cualquier otro servicio (graph_extractor.py,
y más adelante el generador de respuesta técnica) debe pasar por aquí en
lugar de instanciar su propio cliente Groq.
"""

import json
from functools import lru_cache
from typing import Any, Optional

from groq import Groq

from config import GROQ_API_KEY, get_groq_api_key


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    """Cliente Groq singleton (cacheado por proceso)."""
    api_key = get_groq_api_key() or GROQ_API_KEY
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY no está configurada. Define la variable de entorno."
        )
    return Groq(api_key=api_key)


def call_with_json_schema(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    json_schema: dict[str, Any],
    schema_name: str,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> dict[str, Any]:
    """
    Llama a Groq forzando structured outputs (response_format json_schema).

    Devuelve el dict ya parseado desde JSON. No hace la validación Pydantic
    del contrato de dominio -- eso es responsabilidad del caller (mantiene
    este cliente agnóstico del schema de negocio).

    temperature=0.0 por defecto: para extracción determinista queremos la
    menor variabilidad posible entre corridas, dado que el objetivo del
    proyecto es reducir alucinaciones, no creatividad.
    """
    client = get_groq_client()

    kwargs: dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": json_schema,
            },
        },
    )
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    completion = client.chat.completions.create(**kwargs)
    raw_content = completion.choices[0].message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"El modelo '{model}' no devolvió JSON válido pese a json_schema "
            f"forzado. Contenido crudo: {raw_content!r}"
        ) from exc