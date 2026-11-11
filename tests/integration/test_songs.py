import os

from database.models import UserRole
from fastapi.testclient import TestClient
from services.users_services import get_user_by_username

TEST_USER_DATA = {
    "username": "test_song_integration",
    "password": "test_password123",
}

TEST_USER_DATA_2 = {
    "username": "test_song_integration_2",
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


def test_read_song_success(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.get("/api/songs/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == []

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        new_song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = new_song.json()

    response2 = client.get("/api/songs/", headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == 200
    assert response2.json()[0]["title"] == "Test song"

    os.remove(data["audio_url"])


def test_read_song_by_id(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = song.json()

    response = client.get("/api/songs/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    bad_response = client.get(
        "/api/songs/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert bad_response.status_code == 404
    assert bad_response.json()["detail"] == "Song not found"

    os.remove(data["audio_url"])


def test_delete_song_succes(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = song.json()

    response = client.delete(
        f"/api/songs/{data['id']}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    os.remove(data["audio_url"])


def test_delete_not_existing_song(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    response = client.delete(
        "/api/songs/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Song not found"


def test_delete_song_not_owner(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = song.json()

    client.post("/api/users/register", json=TEST_USER_DATA_2)
    new_user2 = get_user_by_username(db_session, username=TEST_USER_DATA_2["username"])
    new_user2.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA_2)
    token2 = logged_user.json()["access_token"]

    response = client.delete(
        f"/api/songs/{data['id']}", headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only the owner of this song can delete it"

    os.remove(data["audio_url"])


def test_add_song_to_favourite(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = song.json()

    client.post("/api/users/register", json=TEST_USER_DATA_2)
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA_2)
    token2 = logged_user.json()["access_token"]

    response = client.post(
        f"/api/songs/{data['id']}/favourites",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 201

    response2 = client.post(
        f"/api/songs/{data['id']}/favourites",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response2.status_code == 409
    assert response2.json()["detail"] == "This song is already in favourites"
    os.remove(data["audio_url"])


def test_remove_song_from_favourite(client: TestClient, db_session):
    client.post("/api/users/register", json=TEST_USER_DATA)
    new_user = get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    new_user.role = UserRole.Musician
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA)
    token = logged_user.json()["access_token"]

    file_path_test = "tests/integration/dummy.mp3"

    with open(file_path_test, "rb") as f:
        song = client.post(
            "/api/songs/",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test song", "is_public": "true"},
            files={"audio_file": ("test.mp3", f, "audio/mp3")},
        )
    data = song.json()

    client.post("/api/users/register", json=TEST_USER_DATA_2)
    db_session.commit()

    logged_user = client.post("/api/users/login", data=TEST_USER_DATA_2)
    token2 = logged_user.json()["access_token"]

    client.post(
        f"/api/songs/{data['id']}/favourites",
        headers={"Authorization": f"Bearer {token2}"},
    )

    response = client.delete(
        f"/api/songs/{data['id']}/favourites",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 200

    response2 = client.delete(
        f"/api/songs/{data['id']}/favourites",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response2.status_code == 404
    assert response2.json()["detail"] == "This song isn't already in favourites"
    os.remove(data["audio_url"])
