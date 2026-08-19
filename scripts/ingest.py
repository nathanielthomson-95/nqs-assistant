"""Ingest a PDF: extract, chunk, embed, store. Run from the project root.

    python -m scripts.ingest data/raw/regulations.pdf "Document title"

Embeddings are cached by content hash in data/embedding_cache.json, so
re-ingesting after a chunking change only embeds what actually changed.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

from google.genai import errors

from app.database import SessionLocal
from app.models import Chunk, Document
from app.services.embeddings import embed
from app.services.ingest import chunk_by_regulation, extract_pages

BATCH_SIZE = 25
PAUSE_SECONDS = 20
PAGE_SLICE = slice(21, None)  # regulations start on page 22
CACHE_PATH = Path("data/embedding_cache.json")
RETRYABLE_SERVER_CODES = (500, 502, 503, 504)


def key_for(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache() -> dict[str, list[float]]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache), encoding="utf-8")


def merge_by_regulation(chunks: list[dict]) -> list[dict]:
    """Rejoin a regulation that was split across pages into a single chunk."""
    merged: list[dict] = []
    for chunk in chunks:
        ref = chunk["source_ref"]
        reg = ref.split(",")[0] if ref.startswith("Regulation") else None
        prev_ref = merged[-1]["source_ref"] if merged else ""
        prev_reg = prev_ref.split(",")[0] if prev_ref.startswith("Regulation") else None

        if reg and reg == prev_reg:
            merged[-1]["content"] += "\n" + chunk["content"]
        else:
            merged.append(dict(chunk))
    return merged


def embed_with_retry(texts: list[str], max_attempts: int = 5) -> list[list[float]]:
    """Embed a batch, backing off on transient rate limits and server errors.

    A per-day quota is not transient, so it is raised immediately rather
    than slept through.
    """
    for attempt in range(max_attempts):
        try:
            return embed(texts)
        except errors.ClientError as exc:
            if exc.code != 429:
                raise
            if "PerDay" in str(exc):
                print("Daily quota exhausted. Cached progress saved, resume after 6pm.")
                raise
            if attempt == max_attempts - 1:
                raise
            wait = 30 * (attempt + 1)
            print(f"rate limited, waiting {wait}s")
            time.sleep(wait)
        except errors.ServerError as exc:
            if exc.code not in RETRYABLE_SERVER_CODES or attempt == max_attempts - 1:
                raise
            wait = 10 * (attempt + 1)
            print(f"server error {exc.code}, waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def main(pdf_path: str, title: str) -> None:
    db = SessionLocal()
    try:
        document = Document(title=title, body="", source_url=str(pdf_path))
        db.add(document)
        db.commit()
        db.refresh(document)

        all_chunks = []
        carry = None
        highest = 0
        for page_number, text in extract_pages(Path(pdf_path))[PAGE_SLICE]:
            if text.strip():
                page_chunks, carry, highest = chunk_by_regulation(
                    text, page_number, carry, highest
                )
                all_chunks.extend(page_chunks)

        print(f"{len(all_chunks)} chunks extracted")
        all_chunks = merge_by_regulation(all_chunks)
        print(f"{len(all_chunks)} chunks after merging")

        if not all_chunks:
            print("Nothing to embed. Check the page slice and the regex.")
            return

        cache = load_cache()
        print(f"{len(cache)} embeddings cached")

        pending = [c for c in all_chunks if key_for(c["content"]) not in cache]
        print(f"{len(pending)} chunks need embedding")

        for i in range(0, len(pending), BATCH_SIZE):
            batch = pending[i:i + BATCH_SIZE]
            vectors = embed_with_retry([c["content"] for c in batch])
            for chunk_data, vector in zip(batch, vectors):
                cache[key_for(chunk_data["content"])] = vector
            save_cache(cache)
            print(f"embedded {i + len(batch)} / {len(pending)}")

            if i + BATCH_SIZE < len(pending):
                time.sleep(PAUSE_SECONDS)

        for chunk_data in all_chunks:
            db.add(Chunk(
                document_id=document.id,
                content=chunk_data["content"],
                source_ref=chunk_data["source_ref"],
                embedding=cache[key_for(chunk_data["content"])],
            ))
        db.commit()
        print(f"stored {len(all_chunks)} chunks")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])