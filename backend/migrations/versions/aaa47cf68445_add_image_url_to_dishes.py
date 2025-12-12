"""add image_url to dishes

Revision ID: aaa47cf68445
Revises: ed429413838e
Create Date: 2025-12-11 23:13:55.302179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaa47cf68445'
down_revision: Union[str, Sequence[str], None] = 'ed429413838e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
