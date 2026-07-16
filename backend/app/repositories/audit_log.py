from app.repositories.base import BaseRepository
from app.models.audit_log import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository handling database operations for audit logging traces."""

    pass
