def test_create_user_success(client):
    response = client.post("/users/", json={"username": "alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data

def test_create_user_duplicate(client):
    client.post("/users/", json={"username": "bob"})
    response = client.post("/users/", json={"username": "bob"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"

def test_create_user_validation(client):
    response = client.post("/users/", json={})
    assert response.status_code == 422
