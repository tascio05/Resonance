import os

from database.models import UserRole
from fastapi.testclient import TestClient
from services.users_services import get_user_by_username

TEST_USER_DATA = {
    "username": "test_song_integration",
    "password": "test_password123",
}


def test_upload_song_forbidden_for_listener(client: TestClient):
    client.post("/api/users/register", json=TEST_USER_DATA)
    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)

    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        response = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mpeg")},
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not a Musician"


def test_upload_song_invalid_audio_file(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.post(
        "/api/songs/",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "Test song", "is_public": "true"},
        files={"audio_file": ("test.mp3", b"not an audio file", "audio/mpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio file"


def test_upload_song_success(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        response = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test song"
    assert data["length_seconds"] == 2

    os.remove(data["audio_url"])
