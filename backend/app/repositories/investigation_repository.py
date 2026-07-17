import uuid
import logging
from datetime import datetime
from typing import Optional, List, Tuple, Any
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.investigation import Investigation

logger = logging.getLogger("app.repositories.InvestigationRepository")

class RepositoryException(Exception):
    """Base exception for all repository-related failures."""
    pass

class InvestigationRepository(BaseRepository[Investigation]):
    """Repository handling database operations for the Investigation entity."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Investigation, db_session)

    async def create(self, obj_in: Any) -> Investigation:
        """Creates a new Investigation record."""
        try:
            logger.info("Creating new investigation record.")
            if isinstance(obj_in, Investigation):
                self.db.add(obj_in)
                await self.db.commit()
                await self.db.refresh(obj_in)
                return obj_in
            return await super().create(obj_in=obj_in)
        except Exception as e:
            logger.error("Error creating investigation: %s", str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to create investigation: {str(e)}")

    async def create_investigation(self, investigation: Investigation) -> Investigation:
        """Backward compatibility alias for create."""
        return await self.create(investigation)

    async def update(self, db_obj: Investigation, obj_in: Any) -> Investigation:
        """Updates an existing Investigation record."""
        try:
            logger.info("Updating investigation ID: %s", db_obj.id)
            if isinstance(obj_in, Investigation):
                self.db.add(obj_in)
                await self.db.commit()
                await self.db.refresh(obj_in)
                return obj_in
            return await super().update(db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            logger.error("Error updating investigation ID %s: %s", db_obj.id, str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to update investigation: {str(e)}")

    async def update_investigation(self, investigation: Investigation) -> Investigation:
        """Backward compatibility alias for update."""
        return await self.update(investigation, investigation)

    async def delete(self, id: uuid.UUID) -> Optional[Investigation]:
        """Removes an investigation and cascades deletes."""
        try:
            logger.info("Deleting investigation ID: %s", id)
            db_obj = await self.get(id)
            if db_obj:
                await self.db.delete(db_obj)
                await self.db.commit()
            return db_obj
        except Exception as e:
            logger.error("Error deleting investigation ID %s: %s", id, str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to delete investigation: {str(e)}")

    async def delete_investigation(self, id: uuid.UUID) -> Optional[Investigation]:
        """Backward compatibility alias for delete."""
        return await self.delete(id)

    async def soft_delete(self, id: uuid.UUID) -> Optional[Investigation]:
        """Soft deletes an investigation by changing its status to DELETED."""
        try:
            logger.info("Soft deleting investigation ID: %s", id)
            db_obj = await self.get(id)
            if db_obj:
                db_obj.status = "DELETED"
                db_obj.completed_at = datetime.utcnow()
                self.db.add(db_obj)
                await self.db.commit()
                await self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error("Error soft deleting investigation ID %s: %s", id, str(e))
            await self.db.rollback()
            raise RepositoryException(f"Failed to soft delete investigation: {str(e)}")

    async def get(self, id: uuid.UUID) -> Optional[Investigation]:
        """Fetch an investigation record by ID, eagerly loading nested children."""
        try:
            logger.info("Fetching investigation ID: %s", id)
            result = await self.db.execute(
                select(Investigation)
                .filter(Investigation.id == id)
                .options(
                    selectinload(Investigation.agent_results),
                    selectinload(Investigation.evidence),
                    selectinload(Investigation.recommendations),
                    selectinload(Investigation.timeline)
                )
            )
            return result.scalars().first()
        except Exception as e:
            logger.error("Error fetching investigation ID %s: %s", id, str(e))
            raise RepositoryException(f"Failed to fetch investigation: {str(e)}")

    async def get_by_id(self, id: uuid.UUID) -> Optional[Investigation]:
        """Backward compatibility alias for get."""
        return await self.get(id)

    async def get_by_case_number(self, case_number: str) -> Optional[Investigation]:
        """Fetch an investigation record by human-readable unique case number."""
        try:
            logger.info("Fetching investigation by case_number: %s", case_number)
            result = await self.db.execute(
                select(Investigation)
                .filter(Investigation.case_number == case_number)
                .options(
                    selectinload(Investigation.agent_results),
                    selectinload(Investigation.evidence),
                    selectinload(Investigation.recommendations),
                    selectinload(Investigation.timeline)
                )
            )
            return result.scalars().first()
        except Exception as e:
            logger.error("Error fetching investigation by case_number %s: %s", case_number, str(e))
            raise RepositoryException(f"Failed to fetch investigation: {str(e)}")

    async def get_by_transaction(self, transaction_id: str) -> Optional[Investigation]:
        """Fetch an investigation record by Transaction ID."""
        try:
            logger.info("Fetching investigation by transaction ID: %s", transaction_id)
            result = await self.db.execute(
                select(Investigation)
                .filter(Investigation.transaction_id == transaction_id)
                .options(
                    selectinload(Investigation.agent_results),
                    selectinload(Investigation.evidence),
                    selectinload(Investigation.recommendations),
                    selectinload(Investigation.timeline)
                )
            )
            return result.scalars().first()
        except Exception as e:
            logger.error("Error fetching investigation by transaction ID %s: %s", transaction_id, str(e))
            raise RepositoryException(f"Failed to fetch investigation: {str(e)}")

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Investigation]:
        """Backward compatibility alias for get_by_transaction."""
        return await self.get_by_transaction(transaction_id)

    async def list(
        self,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
        min_fraud_prob: Optional[float] = None,
        max_fraud_prob: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        created_by: Optional[uuid.UUID] = None,
        assigned_to: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> Tuple[List[Investigation], int]:
        """Fetch paginated, sorted, and filtered lists of investigations with count."""
        try:
            logger.info("Listing investigations with filters.")
            query = select(Investigation).options(
                selectinload(Investigation.agent_results),
                selectinload(Investigation.evidence),
                selectinload(Investigation.recommendations),
                selectinload(Investigation.timeline)
            )
            count_query = select(func.count()).select_from(Investigation)

            filters = []
            if status:
                filters.append(Investigation.status == status)
            if priority:
                filters.append(Investigation.priority == priority)
            if min_risk_score is not None:
                filters.append(Investigation.risk_score >= min_risk_score)
            if max_risk_score is not None:
                filters.append(Investigation.risk_score <= max_risk_score)
            if min_fraud_prob is not None:
                filters.append(Investigation.fraud_probability >= min_fraud_prob)
            if max_fraud_prob is not None:
                filters.append(Investigation.fraud_probability <= max_fraud_prob)
            if start_date:
                filters.append(Investigation.started_at >= start_date)
            if end_date:
                filters.append(Investigation.started_at <= end_date)
            if created_by:
                filters.append(Investigation.created_by == created_by)
            if assigned_to:
                filters.append(Investigation.assigned_to == assigned_to)

            if filters:
                clause = and_(*filters)
                query = query.filter(clause)
                count_query = count_query.filter(clause)

            sort_col = getattr(Investigation, sort_by, None)
            if sort_col is None:
                sort_col = Investigation.created_at
                
            if sort_desc:
                query = query.order_by(desc(sort_col))
            else:
                query = query.order_by(asc(sort_col))

            offset = max(0, (page - 1) * page_size)
            query = query.offset(offset).limit(page_size)

            result = await self.db.execute(query)
            count_res = await self.db.execute(count_query)
            
            return list(result.scalars().all()), count_res.scalar() or 0
        except Exception as e:
            logger.error("Error listing investigations: %s", str(e))
            raise RepositoryException(f"Failed to list investigations: {str(e)}")

    async def list_investigations(self, **kwargs: Any) -> Tuple[List[Investigation], int]:
        """Backward compatibility alias for list."""
        return await self.list(**kwargs)

    async def search(self, query_str: str, page: int = 1, page_size: int = 10) -> Tuple[List[Investigation], int]:
        """Searches across transaction IDs, case numbers, predictions, or summaries."""
        try:
            logger.info("Searching investigations with query: '%s'", query_str)
            clause = or_(
                Investigation.transaction_id.ilike(f"%{query_str}%"),
                Investigation.case_number.ilike(f"%{query_str}%"),
                Investigation.prediction.ilike(f"%{query_str}%"),
                Investigation.summary.ilike(f"%{query_str}%")
            )
            query = select(Investigation).filter(clause).options(
                selectinload(Investigation.agent_results),
                selectinload(Investigation.evidence),
                selectinload(Investigation.recommendations),
                selectinload(Investigation.timeline)
            ).order_by(desc(Investigation.created_at))

            count_query = select(func.count()).select_from(Investigation).filter(clause)

            offset = max(0, (page - 1) * page_size)
            query = query.offset(offset).limit(page_size)

            result = await self.db.execute(query)
            count_res = await self.db.execute(count_query)

            return list(result.scalars().all()), count_res.scalar() or 0
        except Exception as e:
            logger.error("Error searching investigations: %s", str(e))
            raise RepositoryException(f"Failed to search investigations: {str(e)}")
