from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import settings
from app.core.config import API_DESCRIPTION, API_TITLE, API_VERSION
from app.core.logging import get_logger, setup_logging
from app.database.database import async_engine, check_database_health
from app.middleware.logging import LoggingMiddleware

# 1. Initialize structured logging
setup_logging()
logger = get_logger(__name__)


# 2. Configure lifespan events (managing startup and shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing database connections...")
    db_ok = await check_database_health()
    if not db_ok:
        logger.critical("Failed to connect to database during startup.")
        if settings.APP_ENV == "production":
            raise RuntimeError("Database connection could not be established.")
    else:
        logger.info("Database connection successfully established.")

    logger.info(f"Starting {API_TITLE} version {API_VERSION} [{settings.APP_ENV}]")
    yield
    # Shutdown tasks
    logger.info("Closing database engine connections...")
    await async_engine.dispose()
    logger.info("Application shutdown complete.")


# 3. Instantiate FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 4. Register HTTP Middlewares
# CORS Middleware
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request-Response Correlation & Logging Middleware
app.add_middleware(LoggingMiddleware)


# 5. Define Basic Health Route
@app.get(
    "/health",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="Retrieve system status details",
)
async def health_check() -> dict:
    """Returns application status details.

    Verifies connection sanity to external dependencies such as databases.
    """
    db_ok = await check_database_health()

    return {
        "status": "healthy" if db_ok else "degraded",
        "environment": settings.APP_ENV,
        "database": "connected" if db_ok else "disconnected",
    }


# 6. Include API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
