from typing import Any, Optional
from sqlalchemy import select, func, or_
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

    async def get_users_paginated(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> tuple[list[User], int]:
        """Fetch a list of users matching query filters with sorting and pagination."""
        query = select(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        count_query = select(func.count()).select_from(User)

        # Filters
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
            count_query = count_query.filter(User.is_active == is_active)

        # Search matching email or full name
        if search:
            search_clause = or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_clause)
            count_query = count_query.filter(search_clause)

        # Sorting
        sort_col = getattr(User, sort_by, None)
        if sort_col is None:
            sort_col = User.created_at

        if sort_desc:
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        # Pagination
        query = query.offset(skip).limit(limit)

        # Execute
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return users, total
