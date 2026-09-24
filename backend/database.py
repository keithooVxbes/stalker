"""
STALKER - Database Configuration
SQLAlchemy async engine & session setup.
"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "STALKER_DATABASE_URL",
    "sqlite+aiosqlite:///./stalker.db",
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        from backend.models import (  # noqa: F401 – ensure models are imported
            User,
            Campaign,
            Participant,
            ConsentLog,
            TrainingEvent,
            LocationEvent,
            BrowserInfo,
            Report,
        )
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        yield session
