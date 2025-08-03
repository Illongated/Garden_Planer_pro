#!/bin/bash

# Agrotique Garden Planner - Automated Restore Script
# This script restores encrypted backups with validation and safety checks

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres"
DB_NAME="agrotique"
DB_USER="agrotique_user"
DB_PASSWORD="${POSTGRES_PASSWORD}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"
TEMP_DIR="/tmp/restore"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if encryption key is set
if [[ -z "${ENCRYPTION_KEY:-}" ]]; then
    error "BACKUP_ENCRYPTION_KEY environment variable is not set"
    exit 1
fi

# Function to list available backups
list_backups() {
    log "Available backups:"
    if [[ -d "${BACKUP_DIR}" ]]; then
        find "${BACKUP_DIR}" -name "agrotique_backup_*.sql.gz.gpg" -printf "%T@ %p\n" | sort -n | while read timestamp file; do
            date=$(date -d "@${timestamp%.*}" '+%Y-%m-%d %H:%M:%S')
            size=$(du -h "$file" | cut -f1)
            echo "  $date - $size - $(basename "$file")"
        done
    else
        warning "Backup directory not found"
    fi
}

# Function to validate backup file
validate_backup() {
    local backup_file="$1"
    
    if [[ ! -f "${backup_file}" ]]; then
        error "Backup file not found: ${backup_file}"
        return 1
    fi
    
    log "Validating backup file: $(basename "${backup_file}")"
    
    # Check if file is encrypted
    if ! file "${backup_file}" | grep -q "PGP"; then
        error "File does not appear to be a valid encrypted backup"
        return 1
    fi
    
    # Test decryption
    if ! echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 --decrypt "${backup_file}" | gunzip | head -n 1 > /dev/null 2>&1; then
        error "Failed to decrypt backup file"
        return 1
    fi
    
    log "Backup file validation successful"
    return 0
}

# Function to create database backup before restore
create_pre_restore_backup() {
    local pre_backup_name="pre_restore_backup_$(date +%Y%m%d_%H%M%S)"
    
    log "Creating pre-restore backup..."
    if pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" --verbose --clean --no-owner --no-privileges | gzip > "${BACKUP_DIR}/${pre_backup_name}.sql.gz"; then
        echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 --symmetric "${BACKUP_DIR}/${pre_backup_name}.sql.gz"
        rm "${BACKUP_DIR}/${pre_backup_name}.sql.gz"
        log "Pre-restore backup created: ${pre_backup_name}.sql.gz.gpg"
    else
        warning "Failed to create pre-restore backup"
    fi
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    local temp_file="${TEMP_DIR}/restore.sql"
    
    # Create temp directory
    mkdir -p "${TEMP_DIR}"
    
    log "Decrypting and extracting backup..."
    if echo "${ENCRYPTION_KEY}" | gpg --batch --yes --passphrase-fd 0 --decrypt "${backup_file}" | gunzip > "${temp_file}"; then
        log "Backup decrypted successfully"
    else
        error "Failed to decrypt backup"
        return 1
    fi
    
    log "Restoring database..."
    
    # Drop and recreate database
    log "Dropping existing database..."
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME};"
    
    # Restore from backup
    log "Restoring from backup..."
    if PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" < "${temp_file}"; then
        log "Database restore completed successfully"
    else
        error "Database restore failed"
        return 1
    fi
    
    # Clean up temp file
    rm -f "${temp_file}"
}

# Main restore function
main_restore() {
    local backup_file="$1"
    
    log "Starting restore process..."
    
    # Validate backup file
    if ! validate_backup "${backup_file}"; then
        exit 1
    fi
    
    # Create pre-restore backup
    create_pre_restore_backup
    
    # Confirm restore
    echo
    warning "This will completely replace the current database with the backup."
    warning "A pre-restore backup has been created."
    echo
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [[ "${confirm}" != "yes" ]]; then
        log "Restore cancelled by user"
        exit 0
    fi
    
    # Perform restore
    if restore_database "${backup_file}"; then
        log "Restore completed successfully!"
        
        # Send notification (if configured)
        if [[ -n "${BACKUP_NOTIFICATION_WEBHOOK:-}" ]]; then
            log "Sending restore notification..."
            curl -X POST "${BACKUP_NOTIFICATION_WEBHOOK}" \
                -H "Content-Type: application/json" \
                -d "{\"text\":\"🔄 Agrotique database restored from: $(basename "${backup_file}")\"}" \
                --silent --fail || warning "Failed to send notification"
        fi
    else
        error "Restore failed"
        exit 1
    fi
}

# Main script logic
case "${1:-}" in
    "list")
        list_backups
        ;;
    "restore")
        if [[ -z "${2:-}" ]]; then
            error "Please specify a backup file to restore"
            echo "Usage: $0 restore <backup_file>"
            echo "Use '$0 list' to see available backups"
            exit 1
        fi
        main_restore "$2"
        ;;
    *)
        echo "Agrotique Garden Planner - Restore Script"
        echo
        echo "Usage:"
        echo "  $0 list                    - List available backups"
        echo "  $0 restore <backup_file>   - Restore from backup file"
        echo
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 restore /backups/agrotique_backup_20240101_120000.sql.gz.gpg"
        echo
        exit 1
        ;;
esac
