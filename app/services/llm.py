import logging
import time

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger("nqs")

SYSTEM_PROMPT = (
    "You are an expert on the Australian National Quality Standard and the "
    "Education and Care Services National Regulations. Answer only from the "
    "context provided. If the context does not contain the answer, say so "
    "plainly rather than guessing."
)

client = genai.Client(api_key=settings.gemini_api_key)


def answer_question(question: str, context: str = "") -> str:
    prompt = f"Context:\n{context}\n\nQuestion: {question}" if context else question

    started = time.perf_counter()
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            max_output_tokens=800,
        ),
    )
    elapsed = time.perf_counter() - started

    usage = response.usage_metadata
    logger.info(
        "ask latency=%.2fs in_tokens=%s out_tokens=%s",
        elapsed,
        usage.prompt_token_count,
        usage.candidates_token_count,
    )

    return response.text