from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..models import Todos
from .helper import db_dependency, user_dependency

router = APIRouter()


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed!")

    return db.query(Todos).all()


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed!")

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    db.delete(todo)
    db.commit()
