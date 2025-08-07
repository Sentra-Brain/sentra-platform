"""Extend system settings and add chat settings

Revision ID: extend_settings_add_chat
Revises: add_user_profile_fields
Create Date: 2025-01-08 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'extend_settings_add_chat'
down_revision: Union[str, Sequence[str], None] = 'add_user_profile_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new system settings fields and create chat settings table."""
    
    # Add new system settings fields
    op.add_column('system_settings', sa.Column('enable_web_search', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('system_settings', sa.Column('web_search_region', sa.String(length=64), nullable=False, server_default='España'))
    op.add_column('system_settings', sa.Column('max_web_results', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('system_settings', sa.Column('cache_results', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('system_settings', sa.Column('cache_expiration_hours', sa.Integer(), nullable=False, server_default='6'))
    op.add_column('system_settings', sa.Column('context_limit_chars', sa.Integer(), nullable=False, server_default='1500'))
    op.add_column('system_settings', sa.Column('default_timezone', sa.String(length=64), nullable=False, server_default='Europe/Madrid'))
    
    # Create chat settings table
    op.create_table('chat_settings',
        sa.Column('max_tokens', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('top_p', sa.Float(), nullable=False),
        sa.Column('top_k', sa.Integer(), nullable=False),
        sa.Column('system_prompt', sa.String(), nullable=False),
        sa.Column('stop_sequences', sa.String(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Remove new system settings fields and drop chat settings table."""
    
    # Drop chat settings table
    op.drop_table('chat_settings')
    
    # Remove new system settings fields
    op.drop_column('system_settings', 'default_timezone')
    op.drop_column('system_settings', 'context_limit_chars')
    op.drop_column('system_settings', 'cache_expiration_hours')
    op.drop_column('system_settings', 'cache_results')
    op.drop_column('system_settings', 'max_web_results')
    op.drop_column('system_settings', 'web_search_region')
    op.drop_column('system_settings', 'enable_web_search')