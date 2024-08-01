from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status
from ..models import Users
from .helper import (
    authenticate_user,
    db_dependency,
    create_access_token,
    bcrypt_context,
)

router = APIRouter()


class UserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    role: str
    phone_number: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "developer.shahan@gmail.com",
                "username": "shahanahmed86",
                "first_name": "shahan ahnmed",
                "last_name": "khan",
                "hashed_password": "test1234",
                "role": "admin",
                "phone_number": "+923362122588",
            }
        }
    }


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, data: UserRequest):
    user = Users(
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=bcrypt_context.hash(data.hashed_password),
        role=data.role,
        phone_number=data.phone_number,
    )

    db.add(user)
    db.commit()


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}
