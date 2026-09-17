"""create users devices loans tables

Revision ID: 20260917_create_users_devices_loans
Revises: 
Create Date: 2026-09-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260917_create_users_devices_loans'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())

    if not inspector.has_table('users'):
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=150), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    elif 'phone' not in {column['name'] for column in inspector.get_columns('users')}:
        op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))

    if not inspector.has_table('devices'):
        op.create_table(
            'devices',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('serial_number', sa.String(length=100), nullable=False),
            sa.Column('device_type', sa.String(length=50), nullable=False),
            sa.Column('brand', sa.String(length=100), nullable=True),
            sa.Column('is_available', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('serial_number')
        )
        op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
        op.create_index(op.f('ix_devices_serial_number'), 'devices', ['serial_number'], unique=True)

    if not inspector.has_table('loans'):
        op.create_table(
            'loans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('device_id', sa.Integer(), nullable=False),
            sa.Column('loan_date', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('return_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.ForeignKeyConstraint(['device_id'], ['devices.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_loans_id'), 'loans', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_loans_id'), table_name='loans')
    op.drop_table('loans')
    op.drop_index(op.f('ix_devices_serial_number'), table_name='devices')
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
