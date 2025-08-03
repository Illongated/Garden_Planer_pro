#!/bin/bash

# Agrotique Garden Planner - Automated Backup Script
# This script performs encrypted backups of the database and application data

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres"
DB_NAME="agrotique"
DB_USER="agrotique_user"
DB_PASSWORD="${POSTGRES_PASSWORD}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="agrotique_backup_${DATE}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if encryption key is set
if [[ -z "${ENCRYPTION_KEY:-}" ]]; then
    error "BACKUP_ENCRYPTION_KEY environment variable is not set"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

log "Starting backup process..."

# Database backup
log "Creating database backup..."
if pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" --verbose --clean --no-owner --no-privileges | gzip > "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz"; then
    log "Database backup completed successfully"
else
    error "Database backup failed"
    exit 1
fi

# Encrypt the backup
log "Encrypting backup..."
if echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 --symmetric "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz"; then
    log "Backup encrypted successfully"
    # Remove unencrypted file
    rm "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz"
else
    error "Backup encryption failed"
    exit 1
fi

# Create backup manifest
log "Creating backup manifest..."
cat > "${BACKUP_DIR}/${BACKUP_NAME}.manifest" << EOF
Backup Date: $(date)
Backend Version: $(cat /app/version.txt 2>/dev/null || echo "unknown")
Database: ${DB_NAME}
Size: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz.gpg" | cut -f1)
Checksum: $(sha256sum "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz.gpg" | cut -d' ' -f1)
EOF

# Clean up old backups
log "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "agrotique_backup_*.sql.gz.gpg" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true
find "${BACKUP_DIR}" -name "agrotique_backup_*.manifest" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Verify backup integrity
log "Verifying backup integrity..."
if echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 --decrypt "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz.gpg" | gunzip | head -n 1 > /dev/null; then
    log "Backup integrity verified"
else
    error "Backup integrity check failed"
    exit 1
fi

# Log backup statistics
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.sql.gz.gpg" | cut -f1)
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "agrotique_backup_*.sql.gz.gpg" | wc -l)

log "Backup completed successfully!"
log "Backup file: ${BACKUP_NAME}.sql.gz.gpg"
log "Backup size: ${BACKUP_SIZE}"
log "Total backups: ${BACKUP_COUNT}"

# Send notification (if configured)
if [[ -n "${BACKUP_NOTIFICATION_WEBHOOK:-}" ]]; then
    log "Sending backup notification..."
    curl -X POST "${BACKUP_NOTIFICATION_WEBHOOK}" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"✅ Agrotique backup completed: ${BACKUP_NAME} (${BACKUP_SIZE})\"}" \
        --silent --fail || warning "Failed to send notification"
fi

log "Backup process completed successfully"
