from pathlib import Path

from pypdf import PdfReader

import re

REG_PATTERN = re.compile(r"^\s*(\d+[A-Z]?)\s+(.{5,120})$", re.MULTILINE)



def extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (page_number, text) for each page, one-indexed."""
    reader = PdfReader(pdf_path)
    return [
        (i + 1, page.extract_text() or "")
        for i, page in enumerate(reader.pages)
    ]    

def chunk_text(text: str, size: int - 800, overlap: int = 150) -> list[str]:
    chunks, start - [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
    return chunks

def chunk_by_regulation(page_text: str, page_number: int) -> list[dict]:
    """Split on regulation headings, keeping the source reference with each chunk."""
    matches = list(REG_PATTERN.finditer(page_text))
    if not matches:
        return [{"content": page_text, "source_ref": f"page {page_number}"}]

    chunks = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
        chunks.append({
            "content": page_text[match.start():end].strip(),
            "source_ref": f"Regulation {match.group(1)}, page {page_number}",
        })
    return chunks