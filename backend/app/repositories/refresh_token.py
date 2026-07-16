from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository handling database operations for active sessions refresh tokens."""

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Fetch a refresh token record by token string."""
        result = await self.db.execute(
            select(RefreshToken).filter(RefreshToken.token == token)
        )
        return result.scalars().first()
