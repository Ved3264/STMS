from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.responses import HTMLResponse
from jose import JWTError
from app.error.auth_exception import email_check, get_user_except
from app.dto.auth_schema import Token, UserRequest, LoginRequest
from app.services.auth_service import authentication_user, create_access_token, get_current_user
from app.vo.auth_vo import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

template = Jinja2Templates("templates")

router = APIRouter(prefix='/auth', tags=['auth'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/user/", response_class=HTMLResponse)
async def auth(request: Request):
    return template.TemplateResponse('loginpageees.html', {"request": request})


@router.post("/adduser/", response_class=HTMLResponse)
async def register_user(reques: Request, request: UserRequest, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(Users).filter(Users.email == request.email).first()
    if existing_user:
        raise email_check

    # Create a new user
    new_user = Users(
        name=request.name,
        email=request.email,
        password=bcrypt_context.hash(request.password),
        is_active=request.is_active,
        is_admin=request.is_admin,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return template.TemplateResponse('home.html', {"request": reques})


@router.post("/logintoken")
async def login_for_access_token(form_data: LoginRequest, db: db_dependency):
    user = authentication_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(user.name, user.id, timedelta(minutes=240))

    response = JSONResponse(content={"access_token": token})
    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


@router.get("/home", response_class=HTMLResponse)
async def redirected_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/user")
    try:
        user = get_current_user(token)
        print("success")
    except JWTError:
        return RedirectResponse(url="/auth/user")
    return template.TemplateResponse("home.html", {"request": request, "username": user["username"], "id": user["id"]})

