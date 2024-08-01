from fastapi import FastAPI
from starlette import status
from .models import Base
from .database import engine
from .routers import admin, auth, todos, users

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy", status_code=status.HTTP_200_OK)
def health_check() -> dict:
    return {"status": "Healthy"}


app.include_router(prefix="/admin", tags=["admin"], router=admin.router)
app.include_router(prefix="/auth", tags=["auth"], router=auth.router)
app.include_router(prefix="/todos", tags=["todos"], router=todos.router)
app.include_router(prefix="/users", tags=["users"], router=users.router)
