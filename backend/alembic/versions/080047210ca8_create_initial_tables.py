"""create initial tables

Revision ID: 080047210ca8
Revises: 
Create Date: 2025-09-06 22:49:09.850874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '080047210ca8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, nullable=False, unique=True, index=True),
        sa.Column('email', sa.String, nullable=False, unique=True, index=True),
        sa.Column('role', sa.String, server_default='operator'),
        sa.Column('hashed_password', sa.String)
    )

    # Orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False, index=True),
        sa.Column('status', sa.String, server_default='Готово к работе'),
        sa.Column('start_time', sa.DateTime, nullable=True),
        sa.Column('end_time', sa.DateTime, nullable=True)
    )

    # OrderFiles table
    op.create_table(
        'order_files',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('orders.id', ondelete='CASCADE')),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('filepath', sa.String, nullable=False)
    )

    # Workstations table
    op.create_table(
        'workstations',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True)
    )

    # RejectReasons table
    op.create_table(
        'reject_reasons',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('description', sa.String, nullable=False)
    )

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, index=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('orders.id')),
        sa.Column('workstation_id', sa.Integer, sa.ForeignKey('workstations.id')),
        sa.Column('operator_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String, server_default='Готово к работе'),
        sa.Column('start_time', sa.DateTime, nullable=True),
        sa.Column('end_time', sa.DateTime, nullable=True),
        sa.Column('reject_reason_id', sa.Integer, sa.ForeignKey('reject_reasons.id'), nullable=True)
    )

    # MaintenanceLogs table
    op.create_table(
        'maintenance_logs',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('workstation_id', sa.Integer, sa.ForeignKey('workstations.id')),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Performance table
    op.create_table(
        'performance',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id')),
        sa.Column('points', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )


def downgrade() -> None:
    op.drop_table('performance')
    op.drop_table('maintenance_logs')
    op.drop_table('tasks')
    op.drop_table('reject_reasons')
    op.drop_table('workstations')
    op.drop_table('order_files')
    op.drop_table('orders')
    op.drop_table('users')