from fastapi import FastAPI
from starlette import status
from starlette.staticfiles import StaticFiles
from models import Base
from database import engine
from routers import admin, auth, todos, users, todos_templates

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthy", status_code=status.HTTP_200_OK, tags=["healthcheck"])
def health_check() -> dict:
    return {"status": "Healthy"}


app.include_router(prefix="/api/admins", tags=["api/admins"], router=admin.router)
app.include_router(prefix="/api/auth", tags=["api/auth"], router=auth.router)
app.include_router(prefix="/api/todos", tags=["api/todos"], router=todos.router)
app.include_router(prefix="/api/users", tags=["api/users"], router=users.router)

app.include_router(router=todos_templates.router)
