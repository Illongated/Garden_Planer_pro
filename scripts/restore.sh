#!/bin/bash

# This script restores a PostgreSQL database from a .sql backup file into a Docker container.

# --- Configuration ---
# Load environment variables from .env.dev
if [ -f .env.dev ]; then
  export $(grep -v '^#' .env.dev | xargs)
fi

DB_CONTAINER_NAME="agrotique_db"
DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
BACKUP_DIR="backups"

# Find the most recent backup file, or use one provided as an argument
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/*.sql | head -n 1)
BACKUP_FILE=${1:-${LATEST_BACKUP}}

# --- Pre-flight Checks ---
# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker does not seem to be running, start it first."
  exit 1
fi

# Check if a backup file exists
if [ -z "${BACKUP_FILE}" ] || [ ! -f "${BACKUP_FILE}" ]; then
  echo "Error: No backup file found."
  echo "Please create a backup first or specify the path to a .sql file."
  echo "Usage: $0 [path_to_backup.sql]"
  exit 1
fi

# Check if the container is running
if ! docker ps | grep -q "${DB_CONTAINER_NAME}"; then
  echo "Database container '${DB_CONTAINER_NAME}' is not running."
  echo "Please start it with 'docker compose up -d db'"
  exit 1
fi

# --- Main Restore Logic ---
echo "Starting database restore for '${DB_NAME}' from file '${BACKUP_FILE}'..."

# Warning and confirmation
read -p "WARNING: This will overwrite the current database '${DB_NAME}'. Are you sure? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Restore cancelled."
  exit 1
fi

# The restore process:
# 1. Drop the existing database.
# 2. Create a new, empty database.
# 3. Restore the backup into the new database.

echo "Restoring..."
docker compose exec -T "${DB_CONTAINER_NAME}" psql -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
docker compose exec -T "${DB_CONTAINER_NAME}" psql -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"
cat "${BACKUP_FILE}" | docker compose exec -T "${DB_CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}"

# --- Verification ---
if [ $? -eq 0 ]; then
  echo "Restore successful!"
else
  echo "Restore failed!"
  exit 1
fi

echo "Restore process finished."
