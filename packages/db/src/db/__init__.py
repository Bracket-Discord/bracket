from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from configs import settings

engine = create_async_engine(str(settings.database_url), echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
