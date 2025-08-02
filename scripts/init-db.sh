#!/bin/bash
set -e

# This script is executed when the PostgreSQL container is first started.
# It connects to the database specified by the POSTGRES_DB environment variable
# and creates the necessary extensions.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable the uuid-ossp extension for UUID generation
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL
