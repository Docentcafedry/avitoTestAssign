import aiosqlite
import pytest
from db import get_db_connection
from main import app
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
from sqlalchemy import text
from utils import generate_random_slug
from db import ShortURL

client = TestClient(app)

engine_test = create_async_engine("sqlite+aiosqlite:///./test.db")

session_test = sessionmaker(
    bind=engine_test,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_connection_test():
    db = session_test()
    try:
        yield db
    finally:
        await db.close()


app.dependency_overrides[get_db_connection] = get_db_connection_test


@pytest.fixture(scope="session", autouse=True)
async def fake_db():

    db = session_test()
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield db
    finally:
        await db.close()


@pytest.fixture(scope="function")
async def session():
    session = session_test()
    yield session
    # Remove any data from database (even data not created by this session)
    await session.rollback()  # rollback the transactions

    # truncate all tables
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(text(f"DELETE FROM {table.name};"))
        await session.commit()

    await session.close()
