from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.conf import settings


DB_URL=settings.DATABASE_URL

engine = create_async_engine(DB_URL)

asession_generator = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class DATA_BASE(DeclarativeBase):
    pass