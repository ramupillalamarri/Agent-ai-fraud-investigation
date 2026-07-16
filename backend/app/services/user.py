import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models.user import User
from app.models.role import Role
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.schemas.user import UserAdminCreate, UserAdminUpdate


class UserService:
    """Service class managing User CRUD operations and administrative user updates."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(User, db)
        self.role_repo = RoleRepository(Role, db)

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> tuple[list[User], int]:
        """Retrieve a paginated, sorted, and filtered list of user accounts."""
        return await self.user_repo.get_users_paginated(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

    async def get_user(self, user_id: uuid.UUID) -> User:
        """Fetch a single user account by primary key, or raise 404."""
        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    async def create_user(self, user_in: UserAdminCreate) -> User:
        """Create a new user account with hashed password and explicit roles."""
        # 1. Verify email uniqueness
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        # 2. Hash password
        hashed_password = security.get_password_hash(user_in.password)

        # 3. Create user entity
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
        )

        # 4. Bind roles
        for role_name in user_in.role_names:
            role = await self.role_repo.get_by_name(role_name)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{role_name}' does not exist.",
                )
            db_user.roles.append(role)

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        # Re-fetch with eager loaded relationships to ensure nested attributes resolve
        return await self.user_repo.get_with_roles(db_user.id)

    async def update_user(self, user_id: uuid.UUID, user_in: UserAdminUpdate) -> User:
        """Perform a partial update on an existing user account."""
        db_user = await self.get_user(user_id)

        # 1. Email uniqueness check if changed
        if user_in.email is not None and user_in.email != db_user.email:
            existing_user = await self.user_repo.get_by_email(user_in.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email address already exists.",
                )
            db_user.email = user_in.email

        # 2. Update basic fields
        if user_in.full_name is not None:
            db_user.full_name = user_in.full_name
        if user_in.is_active is not None:
            db_user.is_active = user_in.is_active

        # 3. Hash new password if changed
        if user_in.password is not None:
            db_user.hashed_password = security.get_password_hash(user_in.password)

        # 4. Update roles mapping if explicitly provided
        if user_in.role_names is not None:
            db_user.roles.clear()
            for role_name in user_in.role_names:
                role = await self.role_repo.get_by_name(role_name)
                if not role:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Role '{role_name}' does not exist.",
                    )
                db_user.roles.append(role)

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        # Re-fetch with eager loaded relationships to ensure nested attributes resolve
        return await self.user_repo.get_with_roles(db_user.id)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Deletes a user account from the database."""
        db_user = await self.get_user(user_id)
        await self.user_repo.remove(id=db_user.id)
