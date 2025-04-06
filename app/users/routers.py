from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post(
    "/register",
    response_model=schemas.UserRead, 
    status_code=status.HTTP_201_CREATED, 
    summary="Регистрация нового пользователя"
)
async def register_user(
    user_in: schemas.UserCreate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' уже зарегистрирован.",
        )
    new_user = await crud.create_user(db=db, user_data=user_in)
    return new_user


@router.post(
    "/token",
    response_model=schemas.Token,
    summary="Получение JWT токена доступа"
)
async def login_for_access_token(
    
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.pswrd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    access_token = security.create_access_token(
        data={"sub": user.email}
    )

    return schemas.Token(access_token=access_token, token_type="bearer")

@router.get(
    "/me",
    response_model=schemas.UserRead,
    summary="Получить информацию о текущем пользователе"
)
async def read_users_me(
    current_user: Annotated[user_model.User, Depends(security.get_current_user)]
):
    return current_user
