from fastapi import status
from models import Todos
from .utils import client, test_todo, TestingSessionLocal


def test_admin_get_all_todos(test_todo):
    response = client.get("/api/admin/todos")
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


def test_admin_delete_todo(test_todo):
    response = client.delete("/api/admin/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todos).filter(Todos.id == 1).first()

    assert todo is None


def test_admin_delete_todo_not_found(test_todo):
    response = client.delete("/api/admin/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found!"}
