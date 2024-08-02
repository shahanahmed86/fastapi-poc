from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse, HTMLResponse
from typing import Annotated, Optional
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
    Path,
)
from jose import jwt
from .helper import (
    authenticate_user,
    create_access_token,
    templates,
    db_dependency,
    SECRET_KEY,
    ALGORITHM,
    bcrypt_context,
)
from models import Todos, Users

router = APIRouter()


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        return None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: Optional[str] = payload.get("sub")
    user_id: Optional[int] = payload.get("id")
    role: Optional[int] = payload.get("role")

    if username is None or user_id is None or role is None:
        logout(request)

    return {"id": user_id, "username": username, "role": role}


@router.get("/", response_class=HTMLResponse)
async def get_all_todos(request: Request, db: db_dependency):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse(
        "home.html", {"request": request, "todos": todos, "user": user}
    )


@router.get("/add-todo", response_class=HTMLResponse)
async def add_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    db: db_dependency,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    todo = Todos()
    todo.title = title
    todo.description = description
    todo.priority = priority
    todo.complete = False
    todo.owner_id = user.get("id")

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(
    db: db_dependency,
    request: Request,
    todo_id: int = Path(gt=0),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found!")

    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo, "user": user}
    )


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo(
    db: db_dependency,
    request: Request,
    todo_id: int = Path(gt=0),
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )
    if todo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found!")

    todo.title = title
    todo.description = description
    todo.priority = priority

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/delete-todo/{todo_id}", response_class=HTMLResponse)
async def delete_todo_by_id(
    db: db_dependency, request: Request, todo_id: int = Path(gt=0)
):
    try:
        user = await get_current_user(request)
        if user is None:
            return RedirectResponse("/login", status.HTTP_302_FOUND)

        todo = (
            db.query(Todos)
            .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
            .first()
        )
        db.delete(todo)
        db.commit()
    finally:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/complete-todo/{todo_id}", response_class=HTMLResponse)
async def complete_todo(db: db_dependency, request: Request, todo_id: int = Path(gt=0)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id and Todos.owner_id == user.get("id"))
        .first()
    )

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


class LoginForm:
    def __init__(self, request: Request):
        self.request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth2_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=60)
    )

    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    user = await get_current_user(request)
    if user is not None:
        return RedirectResponse("/", status.HTTP_302_FOUND)

    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_api(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request)
        if user is not None:
            return RedirectResponse("/", status.HTTP_302_FOUND)

        form = LoginForm(request)
        await form.create_oauth2_form()
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response, form, db)
        if not validate_user_cookie:
            message = "Incorrect username or password!"
            return templates.TemplateResponse(
                "login.html", {"request": request, "message": message}
            )
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "message": e or "Unknown error"}
        )


@router.get("/logout")
async def logout(request: Request):
    message = "Logout Successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "message": message}
    )

    response.delete_cookie(key="access_token", httponly=True)

    return response


@router.get("/change-password", response_class=HTMLResponse)
async def change_password(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    return templates.TemplateResponse("change-password.html", {"request": request})


@router.post("/change-password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    db: db_dependency,
    old_password: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        logout(request)
        return RedirectResponse("/login", status.HTTP_302_FOUND)

    is_matched = bcrypt_context.verify(old_password, user_model.hashed_password)
    if not is_matched:
        message = "Password mismatched"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "message": message}
        )

    if password != password2:
        message = "Confirm password mismatched"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "message": message}
        )

    if len(password) < 6:
        message = "New password must be atleast six characters long"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "message": message}
        )

    if bcrypt_context.verify(password, user_model.hashed_password):
        message = "You haven't changed the password"
        return templates.TemplateResponse(
            "change-password.html", {"request": request, "message": message}
        )

    user_model.hashed_password = bcrypt_context.hash(password)

    db.add(user_model)
    db.commit()

    return templates.TemplateResponse(
        "change-password.html", {"request": request, "message": "Password updated"}
    )


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    user = await get_current_user(request)
    if user is not None:
        return RedirectResponse("/", status.HTTP_302_FOUND)

    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    db: db_dependency,
    email: str = Form(...),
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    user = await get_current_user(request)
    if user is not None:
        return RedirectResponse("/", status.HTTP_302_FOUND)

    validation = (
        db.query(Users)
        .filter(Users.username == username or Users.email == email)
        .first()
    )

    if password != password2 or validation is not None:
        message = "Invalid registration request"
        return templates.TemplateResponse(
            "register.html", {"request": request, "message": message}
        )

    user_model = Users()
    user_model.email = email
    user_model.username = username
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.phone_number = phone_number
    user_model.is_active = True
    user_model.hashed_password = bcrypt_context.hash(password)

    db.add(user_model)
    db.commit()

    message = "User successfully created"

    return templates.TemplateResponse(
        "login.html", {"request": request, "message": message}
    )
