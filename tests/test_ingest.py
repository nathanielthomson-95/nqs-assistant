from app.services.ingest import chunk_text



def test_chunks_overlap():
    text = "a" * 2000
    chunks = chunk_text(text, size=800, overlap=150)
    assert len(chunks) > 1
    assert all(len(c) <= 800 for c in chunks)

def test_short_text_is_one_chunk():
    text = "short text"
    chunks = chunk_text(text, size=800, overlap=150)
    assert len(chunks) == 1