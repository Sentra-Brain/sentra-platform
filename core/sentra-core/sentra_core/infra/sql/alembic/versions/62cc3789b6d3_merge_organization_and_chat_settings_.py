"""merge organization and chat settings migrations

Revision ID: 62cc3789b6d3
Revises: add_organizations_table, extend_settings_add_chat
Create Date: 2025-08-07 19:27:33.923844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData 


# revision identifiers, used by Alembic.
revision: str = '62cc3789b6d3'
down_revision: Union[str, Sequence[str], None] = ('add_organizations_table', 'extend_settings_add_chat')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
