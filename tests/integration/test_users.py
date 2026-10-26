from fastapi.testclient import TestClient
from services.users_services import get_user_by_username

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


def test_register_invalid_input(client: TestClient):
    response = client.post(
        "/api/users/register", json={"username": "1", "password": "123"}
    )
    assert response.status_code == 422


def test_login_user(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)

    response = client.post("/api/users/login", data=TEST_USER_DATA)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    bad_response = client.post("/api/users/login", data=TEST_WRONG_USER_DATA)
    assert bad_response.status_code == 401


def test_login_inactive_user(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)

    user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    user.is_active = False
    db_session.commit()

    response = client.post("/api/users/login", data=TEST_USER_DATA)
    assert response.status_code == 403


def test_update_user_role_to_musician_success(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)
    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.patch(
        "/api/users/me/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "Musician"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "Musician"


def test_update_user_role_to_admin_forbidden(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)
    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.patch(
        "/api/users/me/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "Admin"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot self assign Admin role"


def test_update_wrong_user_role(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)
    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.patch(
        "/api/users/me/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "Test"},
    )
    assert response.status_code == 422
