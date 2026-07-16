import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import ActiveSession, has_permission
from app.schemas.user import (
    UserResponse,
    UserAdminCreate,
    UserAdminUpdate,
    PaginatedUserResponse,
)
from app.services.user import UserService

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedUserResponse,
    summary="List and search user accounts",
    dependencies=[has_permission("dashboard:view")],
)
async def list_users(
    db: ActiveSession,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> dict:
    """Retrieve a paginated list of user accounts with optional filtering, sorting, and name/email search."""
    user_service = UserService(db)
    users, total = await user_service.list_users(
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )
    return {"users": users, "total": total}


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user account details by ID",
    dependencies=[has_permission("dashboard:view")],
)
async def get_user(user_id: uuid.UUID, db: ActiveSession) -> UserResponse:
    """Fetch profile details of a single investigator user by their primary key ID."""
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    return UserResponse.model_validate(user)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investigator user account",
    dependencies=[has_permission("users:create")],
)
async def create_user(
    user_in: UserAdminCreate, db: ActiveSession
) -> UserResponse:
    """Create a new user account with hashed credentials, operational status, and explicit roles mapping."""
    user_service = UserService(db)
    user = await user_service.create_user(user_in)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Modify an existing user account",
    dependencies=[has_permission("users:create")],
)
async def update_user(
    user_id: uuid.UUID, user_in: UserAdminUpdate, db: ActiveSession
) -> UserResponse:
    """Update profile attributes, credentials, status, or role assignments of a user account."""
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_in)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user account",
    dependencies=[has_permission("users:delete")],
)
async def delete_user(user_id: uuid.UUID, db: ActiveSession) -> None:
    """Delete or deactivate an investigator user account by ID."""
    user_service = UserService(db)
    await user_service.delete_user(user_id)
