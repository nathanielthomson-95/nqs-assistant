import re
from pathlib import Path

from pypdf import PdfReader

# Regulation heading: number at line start, then a title starting like a heading.
# [ \t] rather than \s so it never matches across a line break.
REG_PATTERN = re.compile(r"^[ \t]*(\d{1,3}[A-Z]?)[ \t]+([A-Z][a-z][^\n]{8,110})$", re.MULTILINE)

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


def chunk_by_regulation(
    page_text: str,
    page_number: int,
    carry_reg: str | None = None,
    highest_seen: int = 0,
) -> tuple[list[dict], str | None, int]:
    """Split a page on regulation headings.

    Text before the first heading continues the regulation that started on an
    earlier page, so it inherits that number rather than a bare page reference.

    Regulation numbers ascend through the document, so a heading numbered below
    the highest already seen is a numbered list item inside another regulation,
    not a heading.

    Returns (chunks, regulation to carry forward, highest number seen).
    """
    page_text = clean_page(page_text)

    matches = []
    for m in REG_PATTERN.finditer(page_text):
        number = int(re.sub(r"[A-Z]", "", m.group(1)))
        if number < highest_seen:
            continue
        matches.append(m)
        highest_seen = number

    chunks = []

    lead_end = matches[0].start() if matches else len(page_text)
    lead = page_text[:lead_end].strip()
    if lead:
        ref = f"Regulation {carry_reg}, page {page_number}" if carry_reg else f"page {page_number}"
        chunks.append({"content": lead, "source_ref": ref})

    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(page_text)
        chunks.append({
            "content": page_text[match.start():end].strip(),
            "source_ref": f"Regulation {match.group(1)}, page {page_number}",
        })

    next_carry = matches[-1].group(1) if matches else carry_reg
    kept = [c for c in chunks if len(c["content"].strip()) >= MIN_CHUNK_LENGTH]
    return kept, next_carry, highest_seen