def test_profile_returns_200_for_valid_user(client):
    r = client.get("/api/users/profile/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "created_at" in data


def test_profile_returns_404_for_missing_user(client):
    r = client.get("/api/users/profile/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_response_header_contains_failure_mode(client):
    r = client.get("/api/users/profile/1")
    assert "x-failure-mode" in r.headers
    assert r.headers["x-failure-mode"] == "none"
