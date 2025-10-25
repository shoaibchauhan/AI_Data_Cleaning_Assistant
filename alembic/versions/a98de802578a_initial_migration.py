"""Initial migration

Revision ID: a98de802578a
Revises: 665a6b94cad5
Create Date: 2025-10-23 13:11:00.404212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a98de802578a'
down_revision: Union[str, Sequence[str], None] = '665a6b94cad5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
