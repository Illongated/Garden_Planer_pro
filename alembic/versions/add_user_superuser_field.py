"""Add is_superuser field to users table

Revision ID: user_superuser_001
Revises: d1b2b3a4a5a6
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'user_superuser_001'
down_revision = 'd1b2b3a4a5a6_initial_migration_with_users_gardens_and_plants'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_superuser column to users table
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')))

def downgrade():
    # Remove is_superuser column from users table
    op.drop_column('users', 'is_superuser')