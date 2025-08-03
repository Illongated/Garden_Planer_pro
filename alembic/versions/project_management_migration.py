"""Project Management System Migration

Revision ID: project_management_001
Revises: a1b2c3d4e5f6
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'project_management_001'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('climate_zone', sa.String(length=50), nullable=True),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.Column('garden_size', sa.Float(), nullable=True),
        sa.Column('layout_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('plant_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('irrigation_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('current_version', sa.Integer(), nullable=False),
        sa.Column('last_modified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('allow_comments', sa.Boolean(), nullable=False),
        sa.Column('allow_forking', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['last_modified_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)
    op.create_index('idx_project_owner_status', 'projects', ['owner_id', 'status'], unique=False)

    # Create project_members table
    op.create_table('project_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission', sa.String(length=50), nullable=False),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invited_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)
    op.create_index('idx_project_member_user', 'project_members', ['user_id', 'project_id'], unique=False)

    # Create project_versions table
    op.create_table('project_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('plant_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('irrigation_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_tagged', sa.Boolean(), nullable=False),
        sa.Column('tag_name', sa.String(length=100), nullable=True),
        sa.Column('parent_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_version_id'], ['project_versions.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_versions_project_id'), 'project_versions', ['project_id'], unique=False)
    op.create_index('idx_project_version_number', 'project_versions', ['project_id', 'version_number'], unique=False)

    # Create project_comments table
    op.create_table('project_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_comment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('position_x', sa.Float(), nullable=True),
        sa.Column('position_y', sa.Float(), nullable=True),
        sa.Column('element_id', sa.String(length=100), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['project_comments.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_comments_project_id'), 'project_comments', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_comments_author_id'), 'project_comments', ['author_id'], unique=False)

    # Create project_activities table
    op.create_table('project_activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_activities_project_id'), 'project_activities', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_activities_user_id'), 'project_activities', ['user_id'], unique=False)
    op.create_index('idx_project_activity_project', 'project_activities', ['project_id', 'created_at'], unique=False)

    # Add project_id to gardens table
    op.add_column('gardens', sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_gardens_project_id'), 'gardens', ['project_id'], unique=False)
    op.create_foreign_key(None, 'gardens', 'projects', ['project_id'], ['id'])


def downgrade() -> None:
    # Remove project_id from gardens table
    op.drop_constraint(None, 'gardens', type_='foreignkey')
    op.drop_index(op.f('ix_gardens_project_id'), table_name='gardens')
    op.drop_column('gardens', 'project_id')

    # Drop project_activities table
    op.drop_index('idx_project_activity_project', table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_user_id'), table_name='project_activities')
    op.drop_index(op.f('ix_project_activities_project_id'), table_name='project_activities')
    op.drop_table('project_activities')

    # Drop project_comments table
    op.drop_index(op.f('ix_project_comments_author_id'), table_name='project_comments')
    op.drop_index(op.f('ix_project_comments_project_id'), table_name='project_comments')
    op.drop_table('project_comments')

    # Drop project_versions table
    op.drop_index('idx_project_version_number', table_name='project_versions')
    op.drop_index(op.f('ix_project_versions_project_id'), table_name='project_versions')
    op.drop_table('project_versions')

    # Drop project_members table
    op.drop_index('idx_project_member_user', table_name='project_members')
    op.drop_index(op.f('ix_project_members_user_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_project_id'), table_name='project_members')
    op.drop_table('project_members')

    # Drop projects table
    op.drop_index('idx_project_owner_status', table_name='projects')
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_table('projects') 