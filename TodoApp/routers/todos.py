from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from .helper import db_dependency, user_dependency
from ..models import Todos

router = APIRouter()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new todo",
                "description": "A new description",
                "priority": 5,
                "complete": False,
            }
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    return todo


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, data: TodoRequest):
    todo = Todos(**data.model_dump(), owner_id=user.get("id"))

    db.add(todo)
    db.commit()

    return todo


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    data: TodoRequest,
    todo_id: int = Path(gt=0),
):
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    todo.title = data.title
    todo.description = data.description
    todo.priority = data.priority
    todo.complete = data.complete

    db.add(todo)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    db.delete(todo)
    db.commit()
