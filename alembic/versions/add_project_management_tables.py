"""Add project management tables

Revision ID: add_project_management_tables
Revises: a1b2c3d4e5f6_add_plant_catalog_table
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_project_management_tables'
down_revision = 'a1b2c3d4e5f6_add_plant_catalog_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create project_management tables
    
    # Projects table
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('planning', 'in_progress', 'review', 'testing', 'deployed', 'archived', name='projectstatus'), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)

    # Tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'review', 'testing', 'done', 'blocked', name='taskstatus'), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='taskpriority'), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)

    # Bugs table
    op.create_table('bugs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='bugseverity'), nullable=True),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'review', 'testing', 'done', 'blocked', name='taskstatus'), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('reported_by', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('steps_to_reproduce', sa.Text(), nullable=True),
        sa.Column('expected_behavior', sa.Text(), nullable=True),
        sa.Column('actual_behavior', sa.Text(), nullable=True),
        sa.Column('environment', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bugs_id'), 'bugs', ['id'], unique=False)
    op.create_index(op.f('ix_bugs_severity'), 'bugs', ['severity'], unique=False)
    op.create_index(op.f('ix_bugs_status'), 'bugs', ['status'], unique=False)

    # Project collaborators table
    op.create_table('project_collaborators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_collaborators_id'), 'project_collaborators', ['id'], unique=False)

    # Project metrics table
    op.create_table('project_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('lines_of_code', sa.Integer(), nullable=True),
        sa.Column('test_coverage', sa.Float(), nullable=True),
        sa.Column('code_quality_score', sa.Float(), nullable=True),
        sa.Column('build_success_rate', sa.Float(), nullable=True),
        sa.Column('api_response_time_avg', sa.Float(), nullable=True),
        sa.Column('api_response_time_p95', sa.Float(), nullable=True),
        sa.Column('frontend_load_time', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        sa.Column('active_users', sa.Integer(), nullable=True),
        sa.Column('new_users', sa.Integer(), nullable=True),
        sa.Column('feature_adoption_rate', sa.Float(), nullable=True),
        sa.Column('bugs_total', sa.Integer(), nullable=True),
        sa.Column('bugs_open', sa.Integer(), nullable=True),
        sa.Column('bugs_resolved', sa.Integer(), nullable=True),
        sa.Column('bugs_critical', sa.Integer(), nullable=True),
        sa.Column('tasks_total', sa.Integer(), nullable=True),
        sa.Column('tasks_completed', sa.Integer(), nullable=True),
        sa.Column('tasks_in_progress', sa.Integer(), nullable=True),
        sa.Column('tasks_overdue', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_metrics_id'), 'project_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_project_metrics_date'), 'project_metrics', ['date'], unique=False)

    # User activities table
    op.create_table('user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('activity_data', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_activities_id'), 'user_activities', ['id'], unique=False)
    op.create_index(op.f('ix_user_activities_timestamp'), 'user_activities', ['timestamp'], unique=False)

    # Feedback table
    op.create_table('feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_id'), 'feedback', ['id'], unique=False)

    # Releases table
    op.create_table('releases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('release_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_releases_id'), 'releases', ['id'], unique=False)

    # Code reviews table
    op.create_table('code_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('pull_request_url', sa.String(length=500), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_reviews_id'), 'code_reviews', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_code_reviews_id'), table_name='code_reviews')
    op.drop_table('code_reviews')
    
    op.drop_index(op.f('ix_releases_id'), table_name='releases')
    op.drop_table('releases')
    
    op.drop_index(op.f('ix_feedback_id'), table_name='feedback')
    op.drop_table('feedback')
    
    op.drop_index(op.f('ix_user_activities_timestamp'), table_name='user_activities')
    op.drop_index(op.f('ix_user_activities_id'), table_name='user_activities')
    op.drop_table('user_activities')
    
    op.drop_index(op.f('ix_project_metrics_date'), table_name='project_metrics')
    op.drop_index(op.f('ix_project_metrics_id'), table_name='project_metrics')
    op.drop_table('project_metrics')
    
    op.drop_index(op.f('ix_project_collaborators_id'), table_name='project_collaborators')
    op.drop_table('project_collaborators')
    
    op.drop_index(op.f('ix_bugs_status'), table_name='bugs')
    op.drop_index(op.f('ix_bugs_severity'), table_name='bugs')
    op.drop_index(op.f('ix_bugs_id'), table_name='bugs')
    op.drop_table('bugs')
    
    op.drop_index(op.f('ix_tasks_priority'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_status'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS projectstatus')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS taskpriority')
    op.execute('DROP TYPE IF EXISTS bugseverity') 