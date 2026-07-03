from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from .config import settings

connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}
    engine = create_async_engine(
        settings.database_url,
        echo=(settings.environment == "development"),
        connect_args=connect_args,
    )
else:
    engine = create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=settings.db_pool_recycle,
        echo=(settings.environment == "development"),
    )
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()