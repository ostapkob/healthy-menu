"""add image_url to dishes

Revision ID: 9dc7bbfb08af
Revises: aaa47cf68445
Create Date: 2025-12-11 23:16:40.991448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dc7bbfb08af'
down_revision: Union[str, Sequence[str], None] = 'aaa47cf68445'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
