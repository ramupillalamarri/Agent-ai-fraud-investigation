from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.user import User
from app.models.role import Role


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for the User entity."""

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user record by email, including associated roles and permissions."""
        result = await self.db.execute(
            select(User)
            .filter(User.email == email)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalars().first()

    async def get_with_roles(self, user_id: Any) -> Optional[User]:
        """Fetch a user by primary key, eagerly loading their assigned roles and permissions."""
        result = await self.db.execute(
            select(User)
            .filter(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalars().first()
