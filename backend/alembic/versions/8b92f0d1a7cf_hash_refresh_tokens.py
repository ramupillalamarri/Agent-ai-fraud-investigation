"""Hash persisted refresh tokens and add session-family tracking.

Revision ID: 8b92f0d1a7cf
Revises: 5fe88867e838
Create Date: 2026-07-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b92f0d1a7cf"
down_revision: Union[str, Sequence[str], None] = "5fe88867e838"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Invalidate legacy plaintext sessions before switching to hashed lookups."""
    op.add_column("refresh_tokens", sa.Column("token_hash", sa.String(length=64), nullable=True))
    op.add_column("refresh_tokens", sa.Column("family_id", sa.UUID(), nullable=True))
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"], unique=False)
    # Existing rows contain bearer material in plaintext. Invalidate and remove
    # them rather than carrying that exposure into the new schema.
    op.execute("DELETE FROM refresh_tokens")
    op.alter_column("refresh_tokens", "token_hash", nullable=False)
    op.alter_column("refresh_tokens", "family_id", nullable=False)
    op.drop_index("ix_refresh_tokens_token", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "token")


def downgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("token", sa.String(length=512), nullable=True))
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)
    op.drop_index("ix_refresh_tokens_family_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "family_id")
    op.drop_column("refresh_tokens", "token_hash")
