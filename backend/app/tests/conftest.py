import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database.database import get_db_session
from app.models.base import Base

# Use an in-memory SQLite database for testing, or a test PostgreSQL instance.
# Here we use an in-memory SQLite for self-contained, rapid testing.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Create schema tables in the test database on setup; drop on teardown."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Overrides the database session dependency with a test transaction session."""
    async with TestSessionLocal() as session:
        yield session


# Override the dependency inside app
app.dependency_overrides[get_db_session] = override_get_db_session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing an async HTTP client to make requests to the API."""
    async with AsyncClient(
        transport=ASGITransport(app=app), # type: ignore
        base_url="http://test",
    ) as ac:
        yield ac
