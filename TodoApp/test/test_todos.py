from fastapi import status
from ..models import Todos
from .utils import test_todo, client, TestingSessionLocal


def test_read_all_todos(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Learn to code",
            "description": "Need to learn everyday",
            "priority": 5,
            "complete": False,
            "owner_id": 1,
        }
    ]


def test_read_todo_by_id(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "title": "Learn to code",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
        "owner_id": 1,
    }


def test_read_todo_by_id_not_found(test_todo):
    response = client.get("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found!"}


def test_create_todo(test_todo):
    request_data = {
        "title": "new todo",
        "description": "new todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/todos", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()

    todo = db.query(Todos).filter(Todos.id == 2).first()
    assert todo is not None

    assert todo.title == request_data.get("title")
    assert todo.description == request_data.get("description")
    assert todo.priority == request_data.get("priority")
    assert todo.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "new todo - update",
        "description": "new todo description - update",
        "priority": 1,
        "complete": True,
    }

    response = client.put("/todos/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.id == 1).first()

    assert todo.title == request_data.get("title")
    assert todo.description == request_data.get("description")
    assert todo.priority == request_data.get("priority")
    assert todo.complete == request_data.get("complete")


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "new todo - update",
        "description": "new todo description - update",
        "priority": 1,
        "complete": True,
    }

    response = client.put("/todos/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found!"}


def test_delete_todo(test_todo):
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos == 1).first()

    assert todo is None


def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found!"}
