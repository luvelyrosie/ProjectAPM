from fastapi import APIRouter, Form, Path, status
from fastapi.responses import HTMLResponse
from ..dependencies import *
from ..schemas import UserRequest, Token
from fastapi.security import OAuth2PasswordRequestForm


router=APIRouter(
    prefix="/users",
    tags=["users"]
)


# Pages
@router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# API
@router.post("/create-user")
async def create_register_user(
    db: db_dependency,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("user")
):
    user_exists = db.query(User).filter(User.username == username, User.email == email).first()
    if user_exists:
        return templates.TemplateResponse("register.html", {"request": {}, "error": "User already exists!"})

    user_model = User(
        username=username,
        email=email,
        role=role,
        hashed_password=bcrypt_context.hash(password)
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    token = create_access_token(
        username=user_model.username,
        user_id=user_model.id,
        role=user_model.role,
        expires_delta=timedelta(minutes=20)
    )

    response = RedirectResponse(url="/orders/page", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.post("/login")
async def login_html(request: Request, db: db_dependency, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password, db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    response = RedirectResponse(url="/orders/page", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response



@router.post("/api/login", response_model=Token)
async def login_api(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/logout")
async def logout_user():
    response = RedirectResponse(url="/users/login-page", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")  # Clear the token cookie
    return response