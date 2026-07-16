from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create the asynchronous database engine
# configured with standard enterprise connection pool settings
async_engine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # checks connection liveness before checking it out
    echo=settings.DEBUG,  # prints sql queries in debug/development mode
)

# AsyncSession factory configured to avoid auto-commit and expiring instances
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection generator yielding an active AsyncSession.

    Ensures the connection is correctly returned to the pool or closed
    upon request finalization, even when exceptions are raised.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error, rolling back: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_database_health() -> bool:
    """Checks the database health by executing a simple SELECT 1 query.

    Returns True if the database is reachable and responsive, False otherwise.
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
