#!/bin/bash

# This script creates a backup of the PostgreSQL database running in a Docker container.

# --- Configuration ---
# Load environment variables from .env.dev
if [ -f .env.dev ]; then
  export $(grep -v '^#' .env.dev | xargs)
fi

DB_CONTAINER_NAME="agrotique_db"
DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${TIMESTAMP}.sql"

# --- Pre-flight Checks ---
# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker does not seem to be running, start it first."
  exit 1
fi

# Check if the container is running
if ! docker ps | grep -q "${DB_CONTAINER_NAME}"; then
  echo "Database container '${DB_CONTAINER_NAME}' is not running."
  echo "Please start it with 'docker compose up -d db'"
  exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# --- Main Backup Logic ---
echo "Starting database backup for '${DB_NAME}'..."

docker compose exec -T "${DB_CONTAINER_NAME}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" > "${BACKUP_FILE}"

# --- Verification ---
if [ $? -eq 0 ]; then
  echo "Backup successful!"
  echo "File created at: ${BACKUP_FILE}"
  # Optional: List files to show the new backup
  ls -lh "${BACKUP_FILE}"
else
  echo "Backup failed!"
  # Optional: remove failed backup file
  rm "${BACKUP_FILE}"
  exit 1
fi

# Optional: Prune old backups (e.g., keep the last 7)
# find "${BACKUP_DIR}" -type f -name "*.sql" -mtime +7 -delete
# echo "Old backups (older than 7 days) have been pruned."

echo "Backup process finished."
