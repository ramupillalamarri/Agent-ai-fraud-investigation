from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.database.database import get_db_session
from app.core import security
from app.models.user import User
from app.repositories.user import UserRepository

# OAuth2 Password flow scheme pointing to the Swagger form token route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# Active Database Session injection type alias
ActiveSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: ActiveSession,
) -> User:
    """Dependency injection helper retrieving the currently authenticated User entity."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodes the JWT token claims
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")  # type: ignore
        token_type: str = payload.get("type")  # type: ignore
        if user_id_str is None or token_type != "access":
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user_repo = UserRepository(User, db)
    user = await user_repo.get_with_roles(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency injection helper checking that the user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )
    return current_user


class RoleChecker:
    """Reusable role authorization dependency checker."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        user_role_names = [role.name for role in current_user.roles]
        if not any(role in user_role_names for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role privileges to access this endpoint.",
            )
        return current_user


class PermissionChecker:
    """Reusable permission authorization dependency checker."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        user_permissions = {
            perm.name for role in current_user.roles for perm in role.permissions
        }
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have the required permission privileges ('{self.required_permission}') to access this endpoint.",
            )
        return current_user


def has_permission(permission: str):
    """Reusable endpoint dependency wrapper to enforce specific permission requirements."""
    return Depends(PermissionChecker(permission))

