from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database import asession_generator
from app.users import crud, schemas, security, model as user_model 


router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)


async def get_db():
    async with asession_generator() as session:
        yield session

templates = Jinja2Templates(directory="app/templates")

@router.get("/register")
async def get_register(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request})

@router.post("/register-page")
async def reg_form(
    db : Annotated[AsyncSession, Depends(get_db)],
    email : str = Form(...),
    password : str = Form(...)
):
    exiting_user = await crud.get_user_by_email(db, email=email)
    if exiting_user:
        raise HTTPException(status_code=400, detail="You are already registred, try log in pls")
    
    user_in = schemas.UserCreate(email=email, password=password)
    await crud.create_user(db=db, user_data=user_in)
    return RedirectResponse("/", status_code=302)


@router.post("/register", summary="Reg new user")
async def register_user(
    request: Request, 
    user_in: schemas.UserCreate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        return templates.TemplateResponse("reg.html", {
            "request": request,
            "error_message": f"Email '{user_in.email}' уже зарегистрирован."
        })
    
    new_user = await crud.create_user(db=db, user_data=user_in)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.pswrd):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": "Неверный email или пароль"
        })

    access_token = security.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/users/profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)


    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
