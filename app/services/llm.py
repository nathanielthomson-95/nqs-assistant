import json
import logging
import time
from functools import lru_cache

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.config import settings
from app.schemas import ComplianceAnswer
from app.services.prompts import load

logger = logging.getLogger("nqs")


@lru_cache
def get_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _call_model(prompt: str, system: str) -> str:
    started = time.perf_counter()
    response = get_client().models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=800,
        ),
    )
    elapsed = time.perf_counter() - started

    usage = response.usage_metadata
    logger.info(
        "call latency=%.2fs in_tokens=%s out_tokens=%s",
        elapsed,
        usage.prompt_token_count,
        usage.candidates_token_count,
    )
    return response.text


def _build_prompt(question: str, context: str) -> str:
    return f"Context:\n{context}\n\nQuestion: {question}" if context else question


def _strip_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()


def answer_question(question: str, context: str = "") -> str:
    return _call_model(_build_prompt(question, context), load("system"))


def structured_answer(question: str, context: str = "", attempts: int = 2) -> ComplianceAnswer:
    prompt = _build_prompt(question, context)
    system = load("system") + "\n\n" + load("answer_json")

    last_error: Exception | None = None
    for attempt in range(attempts):
        raw = _call_model(prompt, system)
        try:
            return ComplianceAnswer.model_validate(json.loads(_strip_fences(raw)))
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            logger.warning("structured output invalid on attempt %d: %s", attempt + 1, exc)

    raise ValueError(f"Model did not return valid JSON after {attempts} attempts") from last_error