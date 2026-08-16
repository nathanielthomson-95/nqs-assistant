def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_document(client):
    response = client.post("/documents", json={
        "title": "Ratios",
        "body": "One educator to four children for birth to 24 months.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Ratios"
    assert data["id"] > 0
    assert data["created_at"] is not None


def test_list_documents_empty(client):
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_get_document_by_id(client):
    created = client.post("/documents", json={"title": "A", "body": "B"}).json()
    response = client.get(f"/documents/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "A"


def test_delete_document(client):
    created = client.post("/documents", json={"title": "A", "body": "B"}).json()
    assert client.delete(f"/documents/{created['id']}").status_code == 204
    assert client.get(f"/documents/{created['id']}").status_code == 404


def test_rejects_empty_title(client):
    response = client.post("/documents", json={"title": "", "body": "x"})
    assert response.status_code == 422



def test_get_missing_document_returns_404(client):
    response = client.get("/documents/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"



def test_ask_returns_answer(client):
    response = client.post("/ask", json={"text": "What is the ratio for under twos?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Stubbed answer"