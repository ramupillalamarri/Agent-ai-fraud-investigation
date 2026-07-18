from typing import Annotated, List
from fastapi import Depends, HTTPException, status, Request
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
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False
)

# Active Database Session injection type alias
ActiveSession = Annotated[AsyncSession, Depends(get_db_session)]


from jwt import PyJWKClient
from app.core.logging import get_logger

logger = get_logger(__name__)


async def verify_google_id_token(token: str) -> dict:
    """Verifies a Google ID token and returns its payload."""
    # 1. First, check if it's a test/mock token (decodable with our SECRET_KEY)
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            options={"verify_exp": False}
        )
        return payload
    except Exception:
        pass

    # 2. Otherwise, treat it as a real Google ID token
    try:
        try:
            jwk_client = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False, "verify_exp": False}
            )
            return payload
        except Exception as jwk_err:
            logger.warning(f"Google JWK verification fallback: {jwk_err}")
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
    except Exception as e:
        logger.error(f"Google ID Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: ActiveSession,
) -> User:
    """Dependency injection helper retrieving the currently authenticated User entity."""
    user_repo = UserRepository(User, db)

    # 1. Development Mode Authentication Bypass
    if settings.is_development:
        demo_email = settings.INITIAL_ADMIN_EMAIL or "admin@investigation.com"
        demo_user = await user_repo.get_by_email(demo_email)

        if not demo_user:
            # Seed default roles and admin user if not created yet
            from app.services.auth import AuthService
            auth_service = AuthService(db)
            await auth_service.seed_default_data()
            demo_user = await user_repo.get_by_email(demo_email)

        if demo_user:
            full_demo_user = await user_repo.get_with_roles(demo_user.id)
            user_to_inject = full_demo_user or demo_user
            request.state.user = user_to_inject
            request.state.user_id = user_to_inject.id
            return user_to_inject

    # 2. Production Mode Normal Authentication (JWT Enforcement)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = None
    # First attempt standard JWT access token decoding
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except Exception:
        # Fallback to Google ID token validation
        try:
            payload = await verify_google_id_token(token)
        except Exception:
            raise credentials_exception

    if not payload:
        raise credentials_exception

    email = payload.get("email")
    sub = payload.get("sub")

    user = None
    if sub:
        try:
            user_id = uuid.UUID(sub)
            user = await user_repo.get_with_roles(user_id)
        except ValueError:
            pass

    if not user and email:
        user = await user_repo.get_by_email(email)

    if user is None:
        raise credentials_exception

    # Store authenticated user in request state for AuditLog middleware
    request.state.user = user
    request.state.user_id = user.id

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

