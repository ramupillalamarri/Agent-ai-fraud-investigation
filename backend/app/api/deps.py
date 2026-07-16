from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.database.database import get_db_session
from app.schemas.auth import TokenPayload

# OAuth2 Password flow scheme pointing to a hypothetical auth token route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# Active Database Session injection type alias
ActiveSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: ActiveSession,
) -> dict:
    """Dependency injection helper retrieving the currently authenticated user.

    Provides a clean placeholder matching JWT standard conventions.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodes the JWT token claims
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(sub=username)
    except PyJWTError:
        raise credentials_exception

    # Placeholder return object (should look up in database in a real flow)
    return {
        "id": "usr_placeholder_001",
        "email": token_data.sub,
        "role": "investigator",
        "is_active": True,
    }


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Dependency injection helper checking that the user is active."""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
