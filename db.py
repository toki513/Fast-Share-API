
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker,create_async_engine


DATABASE_URL = "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session