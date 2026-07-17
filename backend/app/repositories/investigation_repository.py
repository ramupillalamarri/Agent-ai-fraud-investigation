import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc, asc, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.investigation import Investigation

class InvestigationRepository(BaseRepository[Investigation]):
    """Repository handling database operations for the Investigation entity."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Investigation, db_session)

    async def create_investigation(self, investigation: Investigation) -> Investigation:
        """Saves a new investigation record and commits the transaction."""
        self.db.add(investigation)
        await self.db.commit()
        await self.db.refresh(investigation)
        return investigation

    async def update_investigation(self, investigation: Investigation) -> Investigation:
        """Updates an existing investigation record and commits the transaction."""
        self.db.add(investigation)
        await self.db.commit()
        await self.db.refresh(investigation)
        return investigation

    async def get_by_id(self, id: uuid.UUID) -> Optional[Investigation]:
        """Fetch an investigation record by ID, eagerly loading nested children."""
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

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Investigation]:
        """Fetch an investigation record by Transaction ID."""
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

    async def list_investigations(
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
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> Tuple[List[Investigation], int]:
        """Fetch paginated, sorted, and filtered lists of investigations with count.
        
        Args:
            status: Match status exactly.
            priority: Match priority exactly.
            min_risk_score: Minimum risk score.
            max_risk_score: Maximum risk score.
            min_fraud_prob: Minimum fraud probability.
            max_fraud_prob: Maximum fraud probability.
            start_date: Started after this date.
            end_date: Started before this date.
            page: Pagination page (1-indexed).
            page_size: Pagination size.
            sort_by: Column to sort by.
            sort_desc: Sort descending if True.
            
        Returns:
            Tuple[List[Investigation], int]: Paginated investigations list and total count.
        """
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

        if filters:
            clause = and_(*filters)
            query = query.filter(clause)
            count_query = count_query.filter(clause)

        # Sort order validation
        sort_col = getattr(Investigation, sort_by, None)
        if sort_col is None:
            sort_col = Investigation.created_at
            
        if sort_desc:
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))

        # Pagination calculations
        offset = max(0, (page - 1) * page_size)
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        count_res = await self.db.execute(count_query)
        
        return list(result.scalars().all()), count_res.scalar() or 0

    async def delete_investigation(self, id: uuid.UUID) -> Optional[Investigation]:
        """Removes an investigation and cascades deletes."""
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
        return db_obj
