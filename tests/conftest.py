import asyncio
from typing import AsyncGenerator, Final

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_uow
from app.core.config import settings
from app.database import metadata
from app.main import app
from app.utils.uow import UnitOfWork

engine_test: Final[AsyncEngine] = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), poolclass=NullPool)
async_session_maker_test: Final[async_sessionmaker[AsyncSession]] = async_sessionmaker(
    engine_test, expire_on_commit=False, autoflush=False, autocommit=False)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session


def override_get_uow():
    return UnitOfWork(session_maker=async_session_maker_test)


app.dependency_overrides[get_uow] = override_get_uow


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        yield async_client


@pytest.fixture(scope='session')
async def api() -> FastAPI:
    return app


@pytest.fixture(scope='session')
async def uow() -> UnitOfWork:
    return UnitOfWork(session_maker=async_session_maker_test)
