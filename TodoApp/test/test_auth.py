import pytest
from fastapi import HTTPException, status
from .utils import test_user, TestingSessionLocal
from ..routers.helper import (
    authenticate_user,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)
from jose import jwt
from datetime import timedelta


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, "test1234", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    try:
        authenticate_user("wronguser", "wrongpassword", db)
    except HTTPException as error:
        assert error.status_code == status.HTTP_401_UNAUTHORIZED
        assert error.detail == "Not Authenticated"

    try:
        authenticate_user(test_user.username, "wrongpassword", db)
    except HTTPException as error:
        assert error.status_code == status.HTTP_401_UNAUTHORIZED
        assert error.detail == "Not Authenticated"


def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )

    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token)

    assert user == {
        "username": encode.get("sub"),
        "id": encode.get("id"),
        "role": encode.get("role"),
    }


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Couldn't validate user."
