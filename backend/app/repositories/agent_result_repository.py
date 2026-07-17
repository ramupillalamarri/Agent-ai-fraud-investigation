import uuid
import logging
from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.agent_result import AgentResult
from app.repositories.investigation_repository import RepositoryException

logger = logging.getLogger("app.repositories.AgentResultRepository")

class AgentResultRepository(BaseRepository[AgentResult]):
    """Repository handling database operations for the AgentResult entity."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(AgentResult, db_session)

    async def create(self, obj_in: Any) -> AgentResult:
        """Creates a new AgentResult record."""
        try:
            logger.info("Creating new agent result record.")
            if isinstance(obj_in, AgentResult):
                self.db.add(obj_in)
                await self.db.commit()
                await self.db.refresh(obj_in)
                return obj_in
            return await super().create(obj_in=obj_in)
        except Exception as e:
            logger.error("Error creating agent result: %s", str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to create agent result: {str(e)}")

    async def get(self, id: uuid.UUID) -> Optional[AgentResult]:
        """Fetch an AgentResult by primary key ID."""
        try:
            logger.info("Fetching agent result ID: %s", id)
            return await super().get(id)
        except Exception as e:
            logger.error("Error fetching agent result ID %s: %s", id, str(e))
            raise RepositoryException(f"Failed to fetch agent result: {str(e)}")

    async def delete(self, id: uuid.UUID) -> Optional[AgentResult]:
        """Removes an agent result from database."""
        try:
            logger.info("Deleting agent result ID: %s", id)
            return await super().remove(id=id)
        except Exception as e:
            logger.error("Error deleting agent result ID %s: %s", id, str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to delete agent result: {str(e)}")

    async def list_by_investigation(self, investigation_id: uuid.UUID) -> List[AgentResult]:
        """Fetch all agent results associated with a specific investigation."""
        try:
            logger.info("Listing agent results for investigation ID: %s", investigation_id)
            result = await self.db.execute(
                select(AgentResult)
                .filter(AgentResult.investigation_id == investigation_id)
                .order_by(AgentResult.created_at.asc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing agent results for investigation ID %s: %s", investigation_id, str(e))
            raise RepositoryException(f"Failed to list agent results: {str(e)}")
