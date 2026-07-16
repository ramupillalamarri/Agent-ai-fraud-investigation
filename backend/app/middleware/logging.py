import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enterprise middleware for tracking API request execution times and correlation IDs.

    Ensures every log trace has an associated request trace identifier.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Resolve or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Track start time
        start_time = time.perf_counter()

        # Attach correlation ID to request state so controllers can read it
        request.state.correlation_id = correlation_id

        # Process the request
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"Duration: {process_time:.2f}ms. Error: {e}",
                extra={"correlation_id": correlation_id},
            )
            raise e

        # Calculate duration
        process_time = (time.perf_counter() - start_time) * 1000

        # Inject correlation ID into response headers for client debugging
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

        # Structured request complete log
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} "
            f"completed in {process_time:.2f}ms",
            extra={
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )

        return response
