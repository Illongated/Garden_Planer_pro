BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 31b11de043d7

CREATE TYPE sunpreference AS ENUM ('full_sun', 'partial_shade', 'full_shade');

CREATE TABLE plant_catalog (
    species_name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    description VARCHAR,
    space_m2 FLOAT NOT NULL,
    sun_preference sunpreference NOT NULL,
    water_liters_per_week FLOAT NOT NULL,
    rich_metadata JSON,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_plant_catalog PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_plant_catalog_species_name ON plant_catalog (species_name);

CREATE TABLE users (
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TYPE companiontype AS ENUM ('friend', 'enemy', 'neutral');

CREATE TABLE companion_rules (
    source_plant_id UUID NOT NULL,
    target_plant_id UUID NOT NULL,
    relationship_type companiontype NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_companion_rules PRIMARY KEY (id),
    CONSTRAINT fk_companion_rules_source_plant_id_plant_catalog FOREIGN KEY(source_plant_id) REFERENCES plant_catalog (id),
    CONSTRAINT fk_companion_rules_target_plant_id_plant_catalog FOREIGN KEY(target_plant_id) REFERENCES plant_catalog (id),
    CONSTRAINT uq_companion_rule_pair UNIQUE (source_plant_id, target_plant_id)
);

CREATE INDEX ix_companion_rules_source_plant_id ON companion_rules (source_plant_id);

CREATE INDEX ix_companion_rules_target_plant_id ON companion_rules (target_plant_id);

CREATE TABLE garden_projects (
    name VARCHAR(255) NOT NULL,
    description VARCHAR,
    location VARCHAR,
    width_m FLOAT NOT NULL,
    depth_m FLOAT NOT NULL,
    sun_angle_deg FLOAT,
    settings JSON,
    owner_id UUID NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_garden_projects PRIMARY KEY (id),
    CONSTRAINT fk_garden_projects_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id)
);

CREATE TYPE changetype AS ENUM ('create', 'update', 'delete');

CREATE TABLE audit_logs (
    user_id UUID,
    project_id UUID,
    target_entity VARCHAR(100) NOT NULL,
    target_id VARCHAR NOT NULL,
    change_type changetype NOT NULL,
    change_diff JSONB NOT NULL,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_audit_logs PRIMARY KEY (id),
    CONSTRAINT fk_audit_logs_project_id_garden_projects FOREIGN KEY(project_id) REFERENCES garden_projects (id),
    CONSTRAINT fk_audit_logs_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_audit_logs_project_id ON audit_logs (project_id);

CREATE INDEX ix_audit_logs_target_entity ON audit_logs (target_entity);

CREATE INDEX ix_audit_logs_target_id ON audit_logs (target_id);

CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);

CREATE TABLE irrigation_zones (
    name VARCHAR(255) NOT NULL,
    project_id UUID NOT NULL,
    settings JSON,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_irrigation_zones PRIMARY KEY (id),
    CONSTRAINT fk_irrigation_zones_project_id_garden_projects FOREIGN KEY(project_id) REFERENCES garden_projects (id)
);

CREATE INDEX ix_irrigation_zones_project_id ON irrigation_zones (project_id);

CREATE TYPE plantstatus AS ENUM ('planning', 'planted', 'growing', 'harvested', 'inactive');

CREATE TABLE plant_instances (
    project_id UUID NOT NULL,
    catalog_id UUID NOT NULL,
    x_coord INTEGER NOT NULL,
    y_coord INTEGER NOT NULL,
    status plantstatus NOT NULL,
    is_manual_placement BOOLEAN NOT NULL,
    irrigation_zone_id UUID,
    id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_plant_instances PRIMARY KEY (id),
    CONSTRAINT fk_plant_instances_catalog_id_plant_catalog FOREIGN KEY(catalog_id) REFERENCES plant_catalog (id),
    CONSTRAINT fk_plant_instances_irrigation_zone_id_irrigation_zones FOREIGN KEY(irrigation_zone_id) REFERENCES irrigation_zones (id),
    CONSTRAINT fk_plant_instances_project_id_garden_projects FOREIGN KEY(project_id) REFERENCES garden_projects (id)
);

CREATE INDEX ix_plant_instances_catalog_id ON plant_instances (catalog_id);

CREATE INDEX ix_plant_instances_project_id ON plant_instances (project_id);

INSERT INTO alembic_version (version_num) VALUES ('31b11de043d7') RETURNING alembic_version.version_num;

COMMIT;
