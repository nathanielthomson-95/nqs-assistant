def test_create_centre(client):
    response = client.post("/centres", json={"name": "Rhodes ELC", "state": "NSW"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rhodes ELC"
    assert data["state"] == "NSW"
    assert data["id"] > 0


def test_list_centres_empty(client):
    response = client.get("/centres")
    assert response.status_code == 200
    assert response.json() == []


def test_list_centres_returns_created(client):
    client.post("/centres", json={"name": "Rhodes ELC", "state": "NSW"})
    client.post("/centres", json={"name": "Ermington ELC", "state": "NSW"})
    response = client.get("/centres")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_centre_by_id(client):
    created = client.post("/centres", json={"name": "Rhodes ELC", "state": "NSW"}).json()
    response = client.get(f"/centres/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Rhodes ELC"


def test_get_missing_centre_returns_404(client):
    response = client.get("/centres/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Centre not found"


def test_rejects_invalid_state(client):
    response = client.post("/centres", json={"name": "X", "state": "NEWSOUTHWALES"})
    assert response.status_code == 422


def test_rejects_empty_name(client):
    response = client.post("/centres", json={"name": "", "state": "NSW"})
    assert response.status_code == 422