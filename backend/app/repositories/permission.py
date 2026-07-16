from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.permission import Permission


class PermissionRepository(BaseRepository[Permission]):
    """Repository handling database operations for the Permission entity."""

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Fetch a permission record by name."""
        result = await self.db.execute(
            select(Permission).filter(Permission.name == name)
        )
        return result.scalars().first()
