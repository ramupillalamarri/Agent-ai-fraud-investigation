import uuid
import logging
from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.recommendation import Recommendation
from app.repositories.investigation_repository import RepositoryException

logger = logging.getLogger("app.repositories.RecommendationRepository")

class RecommendationRepository(BaseRepository[Recommendation]):
    """Repository handling database operations for the Recommendation entity."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Recommendation, db_session)

    async def create(self, obj_in: Any) -> Recommendation:
        """Creates a new Recommendation record."""
        try:
            logger.info("Creating new recommendation record.")
            if isinstance(obj_in, Recommendation):
                self.db.add(obj_in)
                await self.db.commit()
                await self.db.refresh(obj_in)
                return obj_in
            return await super().create(obj_in=obj_in)
        except Exception as e:
            logger.error("Error creating recommendation: %s", str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to create recommendation: {str(e)}")

    async def list_by_investigation(self, investigation_id: uuid.UUID) -> List[Recommendation]:
        """Fetch all actionable recommendations associated with a specific investigation."""
        try:
            logger.info("Listing recommendations for investigation ID: %s", investigation_id)
            result = await self.db.execute(
                select(Recommendation)
                .filter(Recommendation.investigation_id == investigation_id)
                .order_by(Recommendation.created_at.asc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing recommendations for investigation ID %s: %s", investigation_id, str(e))
            raise RepositoryException(f"Failed to list recommendations: {str(e)}")
