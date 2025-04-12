
from datetime import datetime, timedelta
from typing import Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf import settings
from app.users import crud, model as user_model
from app.database import asession_generator
from app.conf import settings

async def get_db():
    async with asession_generator() as session:
        yield session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password): #верификация (из FastAPI OAuth2 doc)
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password): #хеширование (из FastAPI OAuth2 doc)
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None ):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_TIME))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    reqest: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token = reqest.cookies.get("access_token")
    if token is None:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = await crud.get_user_by_email(db, email=email)
    if user is None:
        return None
    
    return user
