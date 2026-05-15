from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DATABASE_URL
from database.models import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(url: str | None = None) -> AsyncEngine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_async_engine(url or DATABASE_URL, echo=False)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def async_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


async def create_tables() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = async_session_factory()
    async with factory() as session:
        yield session
