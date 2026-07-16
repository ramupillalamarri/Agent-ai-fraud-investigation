from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.role import Role


class RoleRepository(BaseRepository[Role]):
    """Repository handling database operations for the Role entity."""

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Fetch a role record by name, including associated permissions."""
        result = await self.db.execute(
            select(Role)
            .filter(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        return result.scalars().first()
