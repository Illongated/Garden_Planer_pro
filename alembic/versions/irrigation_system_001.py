"""Create irrigation system tables

Revision ID: irrigation_system_001
Revises: project_management_001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'irrigation_system_001'
down_revision = 'project_management_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create irrigation_equipment table
    op.create_table('irrigation_equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('equipment_type', sa.String(length=50), nullable=False),
        sa.Column('manufacturer', sa.String(length=255), nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('flow_rate_lph', sa.Float(), nullable=False),
        sa.Column('pressure_range_min', sa.Float(), nullable=False),
        sa.Column('pressure_range_max', sa.Float(), nullable=False),
        sa.Column('coverage_radius_m', sa.Float(), nullable=False),
        sa.Column('spacing_m', sa.Float(), nullable=False),
        sa.Column('cost_per_unit', sa.Float(), nullable=False),
        sa.Column('specifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_equipment_name'), 'irrigation_equipment', ['name'], unique=False)
    op.create_index('idx_equipment_type_active', 'irrigation_equipment', ['equipment_type', 'is_active'], unique=False)

    # Create irrigation_zones table
    op.create_table('irrigation_zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('garden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('required_flow_lph', sa.Float(), nullable=False),
        sa.Column('operating_pressure_bar', sa.Float(), nullable=False),
        sa.Column('total_area_m2', sa.Float(), nullable=False),
        sa.Column('cluster_center_x', sa.Float(), nullable=False),
        sa.Column('cluster_center_y', sa.Float(), nullable=False),
        sa.Column('plant_ids', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_zones_name'), 'irrigation_zones', ['name'], unique=False)
    op.create_index('idx_zone_garden_status', 'irrigation_zones', ['garden_id', 'status'], unique=False)

    # Create irrigation_zone_equipment table
    op.create_table('irrigation_zone_equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('spacing_m', sa.Float(), nullable=False),
        sa.Column('layout_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['irrigation_equipment.id'], ),
        sa.ForeignKeyConstraint(['zone_id'], ['irrigation_zones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_zone_equipment_zone', 'irrigation_zone_equipment', ['zone_id'], unique=False)
    op.create_index('idx_zone_equipment_equipment', 'irrigation_zone_equipment', ['equipment_id'], unique=False)

    # Create irrigation_pipes table
    op.create_table('irrigation_pipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipe_name', sa.String(length=255), nullable=False),
        sa.Column('pipe_type', sa.String(length=50), nullable=False),
        sa.Column('material', sa.String(length=50), nullable=False),
        sa.Column('diameter_mm', sa.Float(), nullable=False),
        sa.Column('length_m', sa.Float(), nullable=False),
        sa.Column('flow_rate_lph', sa.Float(), nullable=False),
        sa.Column('velocity_ms', sa.Float(), nullable=False),
        sa.Column('pressure_loss_bar', sa.Float(), nullable=False),
        sa.Column('start_x', sa.Float(), nullable=False),
        sa.Column('start_y', sa.Float(), nullable=False),
        sa.Column('end_x', sa.Float(), nullable=False),
        sa.Column('end_y', sa.Float(), nullable=False),
        sa.Column('cost_per_meter', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['zone_id'], ['irrigation_zones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_pipes_pipe_name'), 'irrigation_pipes', ['pipe_name'], unique=False)
    op.create_index('idx_pipe_zone_type', 'irrigation_pipes', ['zone_id', 'pipe_type'], unique=False)

    # Create irrigation_schedules table
    op.create_table('irrigation_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('schedule_type', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('days_of_week', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('interval_days', sa.Integer(), nullable=True),
        sa.Column('min_temperature_c', sa.Float(), nullable=True),
        sa.Column('max_temperature_c', sa.Float(), nullable=True),
        sa.Column('min_humidity_percent', sa.Float(), nullable=True),
        sa.Column('max_humidity_percent', sa.Float(), nullable=True),
        sa.Column('min_rainfall_mm', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['zone_id'], ['irrigation_zones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_schedules_name'), 'irrigation_schedules', ['name'], unique=False)
    op.create_index('idx_schedule_zone_type', 'irrigation_schedules', ['zone_id', 'schedule_type'], unique=False)

    # Create weather_data table
    op.create_table('weather_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('garden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('temperature_c', sa.Float(), nullable=False),
        sa.Column('humidity_percent', sa.Float(), nullable=False),
        sa.Column('rainfall_mm', sa.Float(), nullable=False),
        sa.Column('wind_speed_kmh', sa.Float(), nullable=False),
        sa.Column('solar_radiation_mj_m2', sa.Float(), nullable=False),
        sa.Column('evapotranspiration_mm', sa.Float(), nullable=False),
        sa.Column('irrigation_need_mm', sa.Float(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_weather_garden_date', 'weather_data', ['garden_id', 'date'], unique=True)
    op.create_index('idx_weather_date', 'weather_data', ['date'], unique=False)

    # Create irrigation_projects table
    op.create_table('irrigation_projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('garden_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('water_source_type', sa.String(length=50), nullable=False),
        sa.Column('source_pressure_bar', sa.Float(), nullable=False),
        sa.Column('source_flow_lph', sa.Float(), nullable=False),
        sa.Column('total_equipment_cost', sa.Float(), nullable=True),
        sa.Column('total_pipe_cost', sa.Float(), nullable=True),
        sa.Column('total_installation_cost', sa.Float(), nullable=True),
        sa.Column('total_project_cost', sa.Float(), nullable=True),
        sa.Column('hydraulic_calculations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('network_layout', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('equipment_selection', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['garden_id'], ['gardens.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_irrigation_projects_name'), 'irrigation_projects', ['name'], unique=False)
    op.create_index('idx_project_garden_active', 'irrigation_projects', ['garden_id', 'is_active'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_project_garden_active', table_name='irrigation_projects')
    op.drop_index(op.f('ix_irrigation_projects_name'), table_name='irrigation_projects')
    op.drop_table('irrigation_projects')

    op.drop_index('idx_weather_date', table_name='weather_data')
    op.drop_index('idx_weather_garden_date', table_name='weather_data')
    op.drop_table('weather_data')

    op.drop_index('idx_schedule_zone_type', table_name='irrigation_schedules')
    op.drop_index(op.f('ix_irrigation_schedules_name'), table_name='irrigation_schedules')
    op.drop_table('irrigation_schedules')

    op.drop_index('idx_pipe_zone_type', table_name='irrigation_pipes')
    op.drop_index(op.f('ix_irrigation_pipes_pipe_name'), table_name='irrigation_pipes')
    op.drop_table('irrigation_pipes')

    op.drop_index('idx_zone_equipment_equipment', table_name='irrigation_zone_equipment')
    op.drop_index('idx_zone_equipment_zone', table_name='irrigation_zone_equipment')
    op.drop_table('irrigation_zone_equipment')

    op.drop_index('idx_zone_garden_status', table_name='irrigation_zones')
    op.drop_index(op.f('ix_irrigation_zones_name'), table_name='irrigation_zones')
    op.drop_table('irrigation_zones')

    op.drop_index('idx_equipment_type_active', table_name='irrigation_equipment')
    op.drop_index(op.f('ix_irrigation_equipment_name'), table_name='irrigation_equipment')
    op.drop_table('irrigation_equipment') 