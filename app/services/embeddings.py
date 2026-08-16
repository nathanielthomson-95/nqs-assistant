import logging

from app.services.llm import get_client
from google.genai import types

logger = logging.getLogger("nqs")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns one vector per input, in order."""
    if not texts:
        return []

    response = get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
    )
    logger.info("embedded %d texts", len(texts))
    return [e.values for e in response.embeddings]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]



def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    logger.info("embedded %d texts", len(texts))
    return [e.values for e in response.embeddings]