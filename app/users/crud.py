from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.users import model, schemas
from app.users.security import hash_password

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(model.User).where(model.User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: schemas.UserCreate):
    hashed_password = hash_password(user_data.password)
    new_user = model.User(email=user_data.email, pswrd=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
