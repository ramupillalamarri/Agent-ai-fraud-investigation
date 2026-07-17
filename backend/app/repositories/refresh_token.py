from typing import Optional
from datetime import datetime
from sqlalchemy import select, update
from app.repositories.base import BaseRepository
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository handling database operations for active sessions refresh tokens."""

    async def get_by_token_hash(
        self, token_hash: str, *, for_update: bool = False
    ) -> Optional[RefreshToken]:
        """Fetch a refresh token record by its non-reversible lookup value."""
        query = select(RefreshToken).filter(RefreshToken.token_hash == token_hash)
        if for_update:
            query = query.with_for_update()
        result = await self.db.execute(
            query
        )
        return result.scalars().first()

    async def revoke_family(self, family_id, revoked_at: datetime) -> None:
        """Invalidate all tokens in a session family after refresh-token replay."""
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
