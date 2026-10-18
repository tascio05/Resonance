from fastapi.testclient import TestClient

TEST_USER_DATA = {
    "username": "test_user_integration",
    "password": "test_password123",
}

TEST_WRONG_USER_DATA = {
    "username": "wrong_user_integration",
    "password": "wrong_password123",
}


def test_register_user(client: TestClient):
    response = client.post("/api/users/register", json=TEST_USER_DATA)
    assert response.status_code == 201
    assert response.json()["username"] == TEST_USER_DATA["username"]

    bad_response = client.post("/api/users/register", json=TEST_USER_DATA)
    assert bad_response.status_code == 409


def test_login_user(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)

    response = client.post("/api/users/login", data=TEST_USER_DATA)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    bad_response = client.post("/api/users/login", data=TEST_WRONG_USER_DATA)
    assert bad_response.status_code == 401
