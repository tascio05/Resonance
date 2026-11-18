from datetime import timedelta

import pytest
from core.config import settings
from core.security import create_access_token, get_password_hash, pwd_context
from jose import JWTError, jwt


def test_hashing_password():
    password = "test_password"
    hashed_password = get_password_hash(password)

    assert password != hashed_password
    assert pwd_context.verify(password, hashed_password) is True
    assert pwd_context.verify("wrong_password", hashed_password) is False


def test_create_and_decode_access_token():
    token = create_access_token({"sub": "testuser"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username = payload.get("sub")

    assert username == "testuser"
    assert payload.get("exp") is not None


def test_expired_jwt():
    token = create_access_token(
        {"sub": "testuser"}, expires_delta=timedelta(minutes=-5)
    )
    with pytest.raises(JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_wrong_jwt():
    token = create_access_token({"sub": "testuser"})
    with pytest.raises(JWTError):
        jwt.decode(token, "wrong_key_test", algorithms=[settings.ALGORITHM])
