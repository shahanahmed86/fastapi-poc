from fastapi import status
from models import Users
from .utils import client, test_user, TestingSessionLocal
from routers.helper import bcrypt_context


def test_get_current_user(test_user):
    response = client.get("/api/users/logged-in")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "shahanahmed86"
    assert response.json()["email"] == "developer.shahan@gmail.com"
    assert response.json()["first_name"] == "shahan ahnmed"
    assert response.json()["last_name"] == "khan"
    assert bcrypt_context.verify("test1234", response.json()["hashed_password"])
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "+923362122588"


def test_admin_change_password_success(test_user):
    request_data = {"old_password": "test1234", "new_password": "test1234!"}
    response = client.put("/api/users/change-password", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.id == test_user.id).first()
    assert bcrypt_context.verify(request_data.get("new_password"), user.hashed_password)


def test_admin_change_password_failed(test_user):
    request_data = {"old_password": "test1234!", "new_password": "test1234"}
    response = client.put("/api/users/change-password", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Old password mismatched"}


def test_admin_phone_number_success(test_user):
    request_data = {"phone_number": "+923131126908"}
    response = client.put("/api/users/phone-number", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.id == test_user.id).first()
    assert user.phone_number == request_data.get("phone_number")
