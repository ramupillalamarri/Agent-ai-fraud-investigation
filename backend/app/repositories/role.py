from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.role import Role


class RoleRepository(BaseRepository[Role]):
    """Repository handling database operations for the Role entity."""

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Fetch a role record by name."""
        result = await self.db.execute(select(Role).filter(Role.name == name))
        return result.scalars().first()
