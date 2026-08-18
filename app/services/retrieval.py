import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embeddings import embed_one

logger = logging.getLogger("nqs")

TOP_K = 8
MIN_SIMILARITY = 0.55


@dataclass
class RetrievedChunk:
    content: str
    source_ref: str
    similarity: float


def retrieve(db: Session, question: str, k: int = TOP_K) -> list[RetrievedChunk]:
    vector = embed_one(question)

    stmt = text("""
        SELECT content, source_ref,
               1 - (embedding <=> CAST(:vec AS vector)) AS similarity
        FROM chunks
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :k
    """)

    rows = db.execute(stmt, {"vec": str(vector), "k": k}).fetchall()
    results = [RetrievedChunk(r.content, r.source_ref, r.similarity) for r in rows]

    logger.info(
        "retrieved %d chunks, top similarity %.3f",
        len(results),
        results[0].similarity if results else 0.0,
    )
    return [r for r in results if r.similarity >= MIN_SIMILARITY]



def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    return "\n\n".join(
        f"[{c.source_ref}]\n{c.content}" for c in chunks
    )