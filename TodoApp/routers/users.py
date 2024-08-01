from pydantic import BaseModel, Field
from starlette import status
from fastapi import APIRouter, HTTPException
from ..models import Users
from .helper import db_dependency, user_dependency, bcrypt_context

router = APIRouter()


class ChangePassword(BaseModel):
    old_password: str = Field()
    new_password: str = Field(min_length=6, max_length=16)

    model_config = {
        "json_schema_extra": {
            "example": {"old_password": "test1234", "new_password": "1234test"}
        }
    }


class UpdatePhoneNumber(BaseModel):
    phone_number: str = Field(min_length=10, max_length=15)

    model_config = {"json_schema_extra": {"example": {"phone_number": "+923362122588"}}}


@router.get("/logged-in", status_code=status.HTTP_200_OK)
async def get_logged_in_user(user: user_dependency, db: db_dependency):
    user_info = (
        db.query(Users)
        .filter(Users.id == user.get("id") and Users.role == user.get("role"))
        .first()
    )
    if user_info is None:
        raise HTTPException(401, "Not Authenticated!")

    return user_info


@router.put("/phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(
    user: user_dependency, db: db_dependency, data: UpdatePhoneNumber
):
    user_info = (
        db.query(Users)
        .filter(Users.id == user.get("id") and Users.role == user.get("role"))
        .first()
    )
    if user_info is None:
        raise HTTPException(401, "Not Authenticated!")

    user_info.phone_number = data.phone_number
    db.add(user_info)
    db.commit()


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency, db: db_dependency, data: ChangePassword
):
    user_info = (
        db.query(Users)
        .filter(Users.id == user.get("id") and Users.role == user.get("role"))
        .first()
    )
    if user_info is None:
        raise HTTPException(401, "Not Authenticated!")

    is_valid = bcrypt_context.verify(data.old_password, user_info.hashed_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Old password mismatched"
        )

    user_info.hashed_password = bcrypt_context.hash(
        data.new_password,
    )
    db.add(user_info)
    db.commit()
