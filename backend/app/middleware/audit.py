import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

from app.core.logging import get_logger

logger = get_logger(__name__)


async def write_audit_log_to_db(
    session_maker,
    user_id: Optional[uuid.UUID],
    action: str,
    entity_name: str,
    entity_id: Optional[uuid.UUID],
    old_values: Optional[dict],
    new_values: Optional[dict],
    ip_address: Optional[str],
    user_agent: Optional[str],
):
    """Asynchronous worker executing database insertions for audit logs in the background."""
    from app.models.audit_log import AuditLog

    try:
        async with session_maker() as db:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                entity_name=entity_name,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(log_entry)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log asynchronously: {e}")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """ASGI Middleware dynamically tracking API access and security actions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Initialize default audit log state parameters
        request.state.audit_action = None
        request.state.audit_user_id = None
        request.state.audit_status = None
        request.state.audit_entity_name = "api"
        request.state.audit_entity_id = None
        request.state.audit_old_values = None
        request.state.audit_new_values = None

        # Execute Request Pipeline
        response = await call_next(request)

        # Retrieve paths & attributes to determine if we should write trace
        path = request.url.path
        is_api = path.startswith("/api/v1")
        is_health = path == "/api/v1/health" or path == "/health"

        # Check if audit logging is required
        audit_action = getattr(request.state, "audit_action", None)
        authenticated_user = getattr(request.state, "user", None)

        if is_api and not is_health and (audit_action or authenticated_user):
            # Resolve the database session maker from app state
            session_maker = getattr(request.app.state, "db_session_maker", None)
            if not session_maker:
                from app.database.database import AsyncSessionLocal
                session_maker = AsyncSessionLocal

            # Extract client properties
            # IP (check headers first if behind reverse proxies)
            ip_address = request.headers.get(
                "x-forwarded-for",
                request.client.host if request.client else "unknown"
            )
            # Take the first IP if forwarded list exists
            if "," in ip_address:
                ip_address = ip_address.split(",")[0].strip()

            user_agent = request.headers.get("user-agent", "unknown")

            # Determine log properties
            if not audit_action:
                # Default API Access log
                action = f"api_access:get:{path}" if request.method.lower() == "get" else f"api_access:{request.method.lower()}:{path}"
                entity_name = "api"
                entity_id = None
                user_id = getattr(request.state, "user_id", None)
                old_values = None
                new_values = {
                    "method": request.method,
                    "path": path,
                    "status_code": response.status_code,
                }
            else:
                action = audit_action
                entity_name = getattr(request.state, "audit_entity_name", "api")
                entity_id = getattr(request.state, "audit_entity_id", None)
                user_id = getattr(request.state, "audit_user_id", None)
                if not user_id:
                    user_id = getattr(request.state, "user_id", None)
                old_values = getattr(request.state, "audit_old_values", None)
                new_values = getattr(request.state, "audit_new_values", None)
                if new_values is None:
                    new_values = {}
                # Ensure status is captured
                new_values["status_code"] = response.status_code
                status_str = getattr(request.state, "audit_status", None)
                if not status_str:
                    status_str = "success" if response.status_code < 400 else "failed"
                new_values["status"] = status_str

            # Attach audit log worker as background task
            original_task = response.background
            async def run_combined():
                await write_audit_log_to_db(
                    session_maker=session_maker,
                    user_id=user_id,
                    action=action,
                    entity_name=entity_name,
                    entity_id=entity_id,
                    old_values=old_values,
                    new_values=new_values,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                if original_task:
                    await original_task()

            response.background = BackgroundTask(run_combined)

        return response
