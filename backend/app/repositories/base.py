from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

# Generic types for SQLAlchemy Model
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository pattern interface implementing async CRUD operations.

    Separates storage detail implementations from high-level business services.
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db = db_session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        result = await self.db.execute(
            select(self.model).filter(self.model.id == id) # type: ignore
        )
        return result.scalars().first()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Fetch multiple records with offset and limit pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, *, obj_in: Any) -> ModelType:
        """Create and commit a new model instance."""
        # Accepts dictionary or schema representations
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)
            
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, *, db_obj: ModelType, obj_in: Any
    ) -> ModelType:
        """Update an existing model instance with partial changes."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, *, id: Any) -> Optional[ModelType]:
        """Delete an existing model instance by primary key."""
        db_obj = await self.get(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
        return db_obj
