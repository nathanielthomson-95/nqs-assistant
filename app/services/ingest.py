import re
from pathlib import Path

from pypdf import PdfReader

# Regulation heading: number at line start, then a title starting like a heading.
# [ \t] rather than \s so it never matches across a line break.
REG_PATTERN = re.compile(r"^[ \t]*(\d{1,3}[A-Z]?)[ \t]+([A-Z][a-z].{3,110})$", re.MULTILINE)

# Noise to strip before chunking
FOOTER = re.compile(r"^\s*2011 No 653\s*$", re.MULTILINE)
BARE_NUMBER = re.compile(r"^\s*\d{1,4}\s*$", re.MULTILINE)

MIN_CHUNK_LENGTH = 200


def extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    """Return (page_number, text) for each page, one-indexed."""
    reader = PdfReader(pdf_path)
    return [
        (i + 1, page.extract_text() or "")
        for i, page in enumerate(reader.pages)
    ]


def clean_page(text: str) -> str:
    """Remove running footers and bare page numbers."""
    text = FOOTER.sub("", text)
    return BARE_NUMBER.sub("", text)


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def chunk_by_regulation(page_text: str, page_number: int) -> list[dict]:
    """Split on regulation headings, keeping a source reference with each chunk."""
    page_text = clean_page(page_text)
    matches = list(REG_PATTERN.finditer(page_text))

    if not matches:
        chunks = [{"content": page_text, "source_ref": f"page {page_number}"}]
    else:
        chunks = []
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
            chunks.append({
                "content": page_text[match.start():end].strip(),
                "source_ref": f"Regulation {match.group(1)}, page {page_number}",
            })

    return [c for c in chunks if len(c["content"].strip()) >= MIN_CHUNK_LENGTH]