def test_create_discussion(client):
    # First create a user
    user_res = client.post("/users/", json={"username": "test_author"})
    user_id = user_res.json()["id"]

    # Now create a discussion
    response = client.post("/discussions/", params={"author_id": user_id}, json={
        "title": "First Post",
        "body": "This is the first discussion."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "First Post"
    assert data["body"] == "This is the first discussion."
    assert data["author_id"] == user_id
    assert "id" in data

def test_create_discussion_nonexistent_author(client):
    user_id = 99999
    response = client.post("/discussions/", params={"author_id": user_id}, json={
        "title": "Fake Author Post",
        "body": "This is the first discussion."
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"

def test_create_discussion_missing_title(client):
    user_res = client.post("/users/", json={"username": "missing_title_user"})
    user_id = user_res.json()["id"]

    response = client.post("/discussions/", params={"author_id": user_id}, json={
        "body": "Body"
    })
    assert response.status_code == 422

def test_list_discussions(client):
    # First create a user
    user_res = client.post("/users/", json={"username": "test_author"})
    user_id = user_res.json()["id"]

    # Now create a few discussions
    for i in range(5):
        client.post("/discussions/", params={"author_id": user_id}, json={
        "title": f"Post number {i}",
        "body": f"This is the discussion number {i}."
    })

    response = client.get("/discussions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5


def test_edit_nonexistent_discussion(client):
    user = client.post("/users/", json={"username": "ghost"}).json()

    res = client.patch("/discussions/99999", params={"author_id": user["id"]}, json={"body": "Doesn't exist"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Discussion not found"


def test_delete_nonexistent_discussion(client):
    user = client.post("/users/", json={"username": "ghost"}).json()

    res = client.delete("/discussions/99999", params={"author_id": user["id"]})
    assert res.status_code == 404
    assert res.json()["detail"] == "Discussion not found"


def test_delete_discussion_forbidden_unauthorized(client):
    owner = client.post("/users/", json={"username": "owner"}).json()
    intruder = client.post("/users/", json={"username": "intruder"}).json()

    disc = client.post("/discussions/", params={"author_id": owner["id"]}, json={
        "title": "Secure", "body": "testing auth"
    }).json()

    # Intruder tries to delete discussion
    res = client.delete(
        f"/discussions/{disc['id']}",
        params={"author_id": intruder["id"]}
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Unauthorized"


def test_edit_and_delete_discussion(client):
    user = client.post("/users/", json={"username": "author_disc"}).json()

    disc = client.post("/discussions/", params={"author_id": user["id"]}, json={
        "title": "Initial Title",
        "body": "Initial Body"
    }).json()

    # Edit discussion
    res = client.patch(
        f"/discussions/{disc['id']}",
        params={"author_id": user["id"]},
        json={"title": "Updated Title"}
    )

    assert res.status_code == 200
    assert res.json()["title"] == "Updated Title"

    # Delete discussion
    res = client.delete(
        f"/discussions/{disc['id']}",
        params={"author_id": user["id"]}
    )

    assert res.status_code == 200
    assert res.json()["message"] == "Discussion marked as deleted"
