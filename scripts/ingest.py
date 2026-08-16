"""Ingest a PDF: extract, chunk, embed, store. Run from the project root.

    python -m scripts.ingest data/raw/regulations.pdf "Document title"
"""
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
PAGE_SLICE = slice(21, None)  # regulations start on page 22; slice(None) for all


def embed_with_retry(texts: list[str], max_attempts: int = 5) -> list[list[float]]:
    """Embed a batch, backing off and retrying on rate limit errors."""
    for attempt in range(max_attempts):
        try:
            return embed(texts)
        except errors.ClientError as exc:
            if exc.code != 429 or attempt == max_attempts - 1:
                raise
            wait = 30 * (attempt + 1)
            print(f"rate limited, waiting {wait}s")
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
        for page_number, text in extract_pages(Path(pdf_path))[PAGE_SLICE]:
            if text.strip():
                all_chunks.extend(chunk_by_regulation(text, page_number))

        print(f"{len(all_chunks)} chunks extracted")
        if not all_chunks:
            print("Nothing to embed. Check the page slice and the regex.")
            return

        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            vectors = embed_with_retry([c["content"] for c in batch])
            for chunk_data, vector in zip(batch, vectors):
                db.add(Chunk(
                    document_id=document.id,
                    content=chunk_data["content"],
                    source_ref=chunk_data["source_ref"],
                    embedding=vector,
                ))
            db.commit()
            print(f"embedded {i + len(batch)} / {len(all_chunks)}")

            if i + BATCH_SIZE < len(all_chunks):
                time.sleep(PAUSE_SECONDS)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])