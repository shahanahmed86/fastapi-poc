from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from starlette import status
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database import SessionLocal
from jose import jwt
from passlib.context import CryptContext
from models import Users


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "rEEC6iWOFDfaGKrIido5oM1FqKkBE67Y+sYGQ+R1P9A1/b8qWEGGarg1xBLs35NIJSJwrhv/sBfL20NIAi3IGg=="
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated"
        )

    is_valid = bcrypt_context.verify(password, user.hashed_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated"
        )

    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: Optional[str] = payload.get("sub")
    user_id: Optional[int] = payload.get("id")
    role: Optional[int] = payload.get("role")

    if username is None or user_id is None or role is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Couldn't validate user.")

    return {"id": user_id, "username": username, "role": role}


templates = Jinja2Templates(directory="templates")


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
