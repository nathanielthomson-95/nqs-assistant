import pytest

from app.services.ingest import chunk_by_regulation, chunk_text

LONG = "x" * 250  # clears MIN_CHUNK_LENGTH


# --- chunk_text: fixed-size splitting ---

def test_chunks_overlap():
    chunks = chunk_text("a" * 2000, size=800, overlap=150)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)


def test_short_text_is_one_chunk():
    assert len(chunk_text("short text", size=800, overlap=150)) == 1


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("some text", size=100, overlap=100)


# --- chunk_by_regulation: structural splitting ---

def test_heading_is_labelled_with_its_regulation():
    chunks, carry, highest = chunk_by_regulation(f"123 Educator to child ratios\n{LONG}", 134)
    assert chunks[0]["source_ref"] == "Regulation 123, page 134"
    assert carry == "123"
    assert highest == 123


def test_continuation_inherits_the_carried_regulation():
    """A page with no heading continues the regulation from the previous page."""
    chunks, carry, _ = chunk_by_regulation(f"{LONG}\n", 135, carry_reg="123", highest_seen=123)
    assert chunks[0]["source_ref"] == "Regulation 123, page 135"
    assert carry == "123"


def test_text_before_the_first_heading_is_kept():
    """The exact shape of page 135: continuation text, then a new heading."""
    page = f"{LONG}\n124 Number of children who can be educated\n{LONG}"
    chunks, carry, _ = chunk_by_regulation(page, 135, carry_reg="123", highest_seen=123)
    assert len(chunks) == 2
    assert chunks[0]["source_ref"] == "Regulation 123, page 135"
    assert chunks[1]["source_ref"] == "Regulation 124, page 135"
    assert carry == "124"


def test_page_with_no_carry_falls_back_to_page_reference():
    chunks, carry, _ = chunk_by_regulation(f"{LONG}\n", 22)
    assert chunks[0]["source_ref"] == "page 22"
    assert carry is None


def test_number_below_highest_seen_is_not_a_heading():
    """A '2 Fire and other emergencies' line on page 138 is a list item."""
    page = f"2 Fire and other emergencies\n{LONG}"
    chunks, carry, highest = chunk_by_regulation(page, 138, carry_reg="136", highest_seen=136)
    assert chunks[0]["source_ref"] == "Regulation 136, page 138"
    assert carry == "136"
    assert highest == 136


def test_short_title_is_not_treated_as_a_heading():
    """The minimum title length is what rejects list items like '2 Fire.'

    Known trade-off: Regulation 1, titled simply 'Title', is also rejected
    and falls into a page-level chunk.
    """
    chunks, carry, highest = chunk_by_regulation(f"1 Title\n{LONG}", 22)
    assert chunks[0]["source_ref"] == "page 22"
    assert highest == 0


def test_short_fragments_are_dropped():
    """Footers and stray lines should not become chunks."""
    chunks, _, _ = chunk_by_regulation("2011 No 653\n", 40, carry_reg="123", highest_seen=123)
    assert chunks == []


def test_multiple_headings_on_one_page():
    page = (
        f"1 Title of these Regulations\n{LONG}\n"
        f"2 Authorising provisions\n{LONG}\n"
        f"3 Commencement of these Regulations\n{LONG}"
    )
    chunks, carry, highest = chunk_by_regulation(page, 22)
    assert [c["source_ref"] for c in chunks] == [
        "Regulation 1, page 22",
        "Regulation 2, page 22",
        "Regulation 3, page 22",
    ]
    assert carry == "3"
    assert highest == 3