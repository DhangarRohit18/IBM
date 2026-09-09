"""
LEGACYX — Test Configuration.

Provides pytest fixtures for the backend test suite, including an in-memory
SQLite database session override for isolated API testing.
"""

import pytest
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import get_async_session
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(autouse=True)
async def prepare_database():
    """Create in-memory database schema before each test and drop after."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Override FastAPI get_async_session dependency to use in-memory SQLite."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated AsyncSession for database operations in tests."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def settings():
    """Return the application settings."""
    return get_settings()


@pytest.fixture
async def async_client():
    """Async HTTPX test client that calls FastAPI endpoints in-memory."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture
async def sample_user(async_session: AsyncSession):
    """Provide a persisted test User record."""
    from app.models.user import User
    user = User(email="test@legacyx.dev", display_name="Test User", hashed_password="hashed_pw")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def sample_project(async_session: AsyncSession, sample_user):
    """Provide a persisted test Project record."""
    from app.models.project import Project
    project = Project(name="Sample Legacy Bank", description="Test Project", owner_id=sample_user.id)
    async_session.add(project)
    await async_session.commit()
    await async_session.refresh(project)
    return project


@pytest.fixture
async def sample_repository(async_session: AsyncSession, sample_project):
    """Provide a persisted test Repository record."""
    from app.models.repository import Repository, RepositoryStatus
    repo = Repository(
        project_id=sample_project.id,
        original_filename="valid-legacybank-app.zip",
        artifact_size=1024,
        sha256="0" * 64,
        storage_key="repositories/test.zip",
        status=RepositoryStatus.COMPLETED,
    )
    async_session.add(repo)
    await async_session.commit()
    await async_session.refresh(repo)
    return repo
