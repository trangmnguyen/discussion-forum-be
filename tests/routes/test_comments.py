def test_create_and_get_comments(client):
    # User A creates the discussion and top-level comment
    user_a_res = client.post("/users/", json={"username": "a"})
    user_a_id = user_a_res.json()["id"]

    disc_res = client.post("/discussions/", params={"author_id": user_a_id}, json={
        "title": "Test Thread",
        "body": "Let's talk"
    })
    discussion_id = disc_res.json()["id"]

    top_comment_res = client.post(
        f"/comments/discussion/{discussion_id}",
        params={"author_id": user_a_id},
        json={"body": "First top-level comment"}
    )
    top_comment = top_comment_res.json()

    assert top_comment_res.status_code == 200
    assert top_comment["body"] == "First top-level comment"
    assert top_comment["parent_id"] is None # No parent comment
    assert top_comment["author_id"] == user_a_id
    assert top_comment["discussion_id"] == discussion_id

    # User B replies to User A's comment
    user_b_res = client.post("/users/", json={"username": "b"})
    user_b_id = user_b_res.json()["id"]

    reply_res = client.post(
        f"/comments/discussion/{discussion_id}",
        params={"author_id": user_b_id},
        json={"body": "This is a reply", "parent_id": top_comment["id"]}
    )
    reply = reply_res.json()

    assert reply_res.status_code == 200
    assert reply["body"] == "This is a reply"
    assert reply["parent_id"] == top_comment["id"]
    assert reply["author_id"] == user_b_id
    assert reply["discussion_id"] == discussion_id

    # Get comments for the discussion
    response = client.get(f"/comments/discussion/{discussion_id}")
    assert response.status_code == 200
    comments = response.json()

    # Make sure both comments are there
    bodies = [c["body"] for c in comments]
    assert "First top-level comment" in bodies
    assert "This is a reply" in bodies

    # Check parent-child relationship
    top = next(c for c in comments if c["body"] == "First top-level comment")
    reply = next(c for c in comments if c["body"] == "This is a reply")
    assert top["parent_id"] is None
    assert reply["parent_id"] == top["id"]


def test_create_comment_nonexistent_author(client):
    user_res = client.post("/users/", json={"username": "c"})
    user_id = user_res.json()["id"]

    disc_res = client.post("/discussions/", params={"author_id": user_id}, json={
        "title": "Test Thread",
        "body": "Let's talk"
    })
    discussion_id = disc_res.json()["id"]

    nonexistent_user_id = 9999
    comment_res = client.post(
        f"/comments/discussion/{discussion_id}",
        params={"author_id": nonexistent_user_id},
        json={"body": "First top-level comment"}
    )
    assert comment_res.status_code == 404
    assert comment_res.json()["detail"] == "Author not found"


def test_get_comments_for_empty_discussion(client):
    # Create a user and a discussion
    user = client.post("/users/", json={"username": "lonely_user"}).json()

    discussion = client.post("/discussions/", params={"author_id": user["id"]}, json={
        "title": "Quiet Room",
        "body": "Nobody has replied yet"
    }).json()
    discussion_id = discussion["id"]

    # Get comments for this discussion
    res = client.get(f"/comments/discussion/{discussion_id}")
    assert res.status_code == 200

    comments = res.json()
    assert isinstance(comments, list)
    assert comments == []


def test_edit_nonexistent_comment(client):
    user = client.post("/users/", json={"username": "ghost"}).json()

    res = client.patch("/comments/99999", params={"author_id": user["id"]}, json={"body": "Doesn't exist"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Comment not found"


def test_edit_comment_forbidden_unauthorized(client):
    owner = client.post("/users/", json={"username": "owner"}).json()
    intruder = client.post("/users/", json={"username": "intruder"}).json()

    disc = client.post("/discussions/", params={"author_id": owner["id"]}, json={
        "title": "Secure", "body": "testing auth"
    }).json()
    comment = client.post(
        f"/comments/discussion/{disc['id']}",
        params={"author_id": owner["id"]},
        json={"body": "Owner's comment"}
    ).json()

    # Intruder tries to edit comment
    res = client.patch(
        f"/comments/{comment['id']}",
        params={"author_id": intruder["id"]},
        json={"body": "Hacked!"}
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Unauthorized"


def test_edit_comment(client):
    user = client.post("/users/", json={"username": "editor"}).json()
    disc = client.post("/discussions/", params={"author_id": user["id"]}, json={
        "title": "Editing Test", "body": "edit body"
    }).json()

    comment = client.post(
        f"/comments/discussion/{disc['id']}",
        params={"author_id": user["id"]},
        json={"body": "original comment"}
    ).json()

    # Update comment
    res = client.patch(
        f"/comments/{comment['id']}",
        params={"author_id": user["id"]},
        json={"body": "edited comment"}
    )

    assert res.status_code == 200
    assert res.json()["body"] == "edited comment"


def test_soft_delete_comment(client):
    user = client.post("/users/", json={"username": "deleter"}).json()
    disc = client.post("/discussions/", params={"author_id": user["id"]}, json={
        "title": "To Be Deleted", "body": "deletion test"
    }).json()

    comment = client.post(
        f"/comments/discussion/{disc['id']}",
        params={"author_id": user["id"]},
        json={"body": "bye"}
    ).json()

    res = client.delete(
        f"/comments/{comment['id']}",
        params={"author_id": user["id"]}
    )

    assert res.status_code == 200
    assert res.json()["message"] == "Comment marked as deleted"

    # Fetch it again
    res = client.get(f"/comments/discussion/{disc['id']}")
    deleted_comment = next(c for c in res.json() if c["id"] == comment["id"])
    assert deleted_comment["deleted"] is True


def test_delete_nonexistent_comment(client):
    user = client.post("/users/", json={"username": "ghost"}).json()

    res = client.delete("/comments/99999", params={"author_id": user["id"]})
    assert res.status_code == 404
    assert res.json()["detail"] == "Comment not found"


def test_delete_comment_forbidden_unauthorized(client):
    owner = client.post("/users/", json={"username": "owner"}).json()
    intruder = client.post("/users/", json={"username": "intruder"}).json()

    disc = client.post("/discussions/", params={"author_id": owner["id"]}, json={
        "title": "Secure", "body": "testing auth"
    }).json()
    comment = client.post(
        f"/comments/discussion/{disc['id']}",
        params={"author_id": owner["id"]},
        json={"body": "Owner's comment"}
    ).json()

    # Intruder tries to delete comment
    res = client.delete(
        f"/comments/{comment['id']}",
        params={"author_id": intruder["id"]}
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "Unauthorized"
