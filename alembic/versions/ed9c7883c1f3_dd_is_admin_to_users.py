"""dd is_admin to users

Revision ID: ed9c7883c1f3
Revises: eaceab316b9b
Create Date: 2025-05-02 13:06:07.985652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed9c7883c1f3'
down_revision: Union[str, None] = 'eaceab316b9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_comments_task_id', table_name='comments')
    op.drop_index('idx_statuses_status', table_name='statuses')
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_admin')
    op.create_index('idx_statuses_status', 'statuses', ['status'], unique=False)
    op.create_index('idx_comments_task_id', 'comments', ['task_id'], unique=False)
    # ### end Alembic commands ###
