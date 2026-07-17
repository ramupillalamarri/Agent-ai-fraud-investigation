import uuid
import logging
from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.timeline_event import TimelineEvent
from app.repositories.investigation_repository import RepositoryException

logger = logging.getLogger("app.repositories.TimelineRepository")

class TimelineRepository(BaseRepository[TimelineEvent]):
    """Repository handling database operations for the TimelineEvent entity."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(TimelineEvent, db_session)

    async def create(self, obj_in: Any) -> TimelineEvent:
        """Creates a new TimelineEvent record."""
        try:
            logger.info("Creating new timeline event record.")
            if isinstance(obj_in, TimelineEvent):
                self.db.add(obj_in)
                await self.db.commit()
                await self.db.refresh(obj_in)
                return obj_in
            return await super().create(obj_in=obj_in)
        except Exception as e:
            logger.error("Error creating timeline event: %s", str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to create timeline event: {str(e)}")

    async def list_by_investigation(self, investigation_id: uuid.UUID) -> List[TimelineEvent]:
        """Fetch all timeline events associated with a specific investigation."""
        try:
            logger.info("Listing timeline events for investigation ID: %s", investigation_id)
            result = await self.db.execute(
                select(TimelineEvent)
                .filter(TimelineEvent.investigation_id == investigation_id)
                .order_by(TimelineEvent.created_at.asc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing timeline events for investigation ID %s: %s", investigation_id, str(e))
            raise RepositoryException(f"Failed to list timeline events: {str(e)}")

    async def list_chronological(self, investigation_id: uuid.UUID) -> List[TimelineEvent]:
        """Fetch all timeline events associated with a specific investigation in chronological order (oldest first)."""
        return await self.list_by_investigation(investigation_id)
