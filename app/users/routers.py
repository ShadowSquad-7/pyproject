from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.users import crud, schemas, security, model as user_model
from app.users.security import get_db
from app.parcers.parcer import get_value


router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)


templates = Jinja2Templates(directory="app/templates")

@router.post("/register")
async def reg_form(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    email: str = Form(...),
    password: str = Form(...)
):
    existing_user = await crud.get_user_by_email(db, email=email)
    if existing_user:
        return templates.TemplateResponse("main_page.html", {
            "request": request,
            "register_error": "Email уже зарегистрирован",
            "user": None
        })

    user_in = schemas.UserCreate(email=email, password=password)
    await crud.create_user(db=db, user_data=user_in)
    return RedirectResponse("/", status_code=302)


@router.post("/login")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.pswrd):
        return templates.TemplateResponse("main_page.html", {
            "request": request,
            "login_error": "Неверный email или пароль",
            "user": None
        })

    access_token = security.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/buy")
async def get_buy_page(request : Request, user=Depends(security.get_current_user)):
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("buy.html", {
        "request": request,
        "user": user
    })

@router.post("/buy")
async def buy_currency(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    amount_value: float = Form(...),
    user=Depends(security.get_current_user),
    curr: str = Form(...)
):
    prices = {
        'BTC': get_value(),
        'USD': get_value(),
        'EUR': get_value(),
        'CNY': get_value(),
    }
    price = prices.get(str(curr))
    if user.balance/price < amount_value:
        return templates.TemplateResponse("buy.html", {
            "request": request,
            "user" : user,
            "error": "malo denek",
            "prices": prices
        })
    user.balance -= amount_value*price
    curr_attr = f'{curr.lower()}_balance'
    if not getattr(user, curr_attr):
        setattr(user, curr_attr, 0.0)
    setattr(user, curr_attr, getattr(user, curr_attr)+amount_value)
    await db.commit()
    return RedirectResponse(url="/users/buy", status_code=302)
