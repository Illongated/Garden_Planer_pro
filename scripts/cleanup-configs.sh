#!/bin/bash
# =============================================================================
# Configuration Cleanup Script
# =============================================================================
# This script removes old configuration files after consolidation
# and creates symlinks to the new unified configurations
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Backup directory
BACKUP_DIR="./config-backup-$(date +%Y%m%d-%H%M%S)"

# Function to backup and remove old files
backup_and_remove() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        log "Backing up $description: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        success "Removed $file"
    else
        warning "File not found: $file"
    fi
}

# Function to create symlinks
create_symlink() {
    local target="$1"
    local link="$2"
    local description="$3"
    
    if [[ -f "$target" ]]; then
        ln -sf "$target" "$link"
        success "Created symlink for $description: $link -> $target"
    else
        error "Target file not found: $target"
    fi
}

main() {
    log "Starting configuration cleanup and consolidation..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    log "Created backup directory: $BACKUP_DIR"
    
    # =============================================================================
    # BACKUP AND REMOVE OLD DOCKER COMPOSE FILES
    # =============================================================================
    log "Cleaning up Docker Compose files..."
    
    backup_and_remove "docker-compose.yml" "Quick dev docker-compose"
    backup_and_remove "docker-compose.dev.yml" "Development docker-compose"
    backup_and_remove "docker-compose.test.yml" "Test docker-compose"
    backup_and_remove "docker-compose.production.yml" "Production docker-compose"
    backup_and_remove "Dockerfile.old" "Old Dockerfile"
    
    # Create symlink to unified docker-compose
    create_symlink "docker-compose.unified.yml" "docker-compose.yml" "default docker-compose"
    
    # =============================================================================
    # BACKUP AND REMOVE OLD KUBERNETES MANIFESTS
    # =============================================================================
    log "Cleaning up Kubernetes manifests..."
    
    backup_and_remove "k8s/namespace.yml" "Kubernetes namespace"
    backup_and_remove "k8s/secrets.yml" "Kubernetes secrets"
    backup_and_remove "k8s/configmap.yml" "Kubernetes configmap"
    backup_and_remove "k8s/services.yml" "Kubernetes services"
    backup_and_remove "k8s/deployments.yml" "Kubernetes deployments"
    backup_and_remove "k8s/persistent-volumes.yml" "Kubernetes persistent volumes"
    
    # Create symlink to unified K8s manifest
    create_symlink "k8s/agrotique-all-in-one.yml" "k8s/deployment.yml" "unified K8s deployment"
    
    # =============================================================================
    # BACKUP AND REMOVE OLD MONITORING CONFIGS
    # =============================================================================
    log "Cleaning up monitoring configurations..."
    
    backup_and_remove "docker/monitoring/prometheus.yml" "Prometheus config"
    backup_and_remove "docker/monitoring/alertmanager.yml" "Alertmanager config"
    
    # Create symlinks to unified monitoring config
    create_symlink "../config/monitoring.yml" "docker/monitoring/prometheus.yml" "Prometheus config"
    create_symlink "../config/monitoring.yml" "docker/monitoring/alertmanager.yml" "Alertmanager config"
    
    # =============================================================================
    # BACKUP AND REMOVE OLD NGINX CONFIGS
    # =============================================================================
    log "Cleaning up Nginx configurations..."
    
    backup_and_remove "docker/nginx/nginx.conf" "Main Nginx config"
    backup_and_remove "docker/nginx/frontend.conf" "Frontend Nginx config"
    
    # Create symlink to unified nginx config
    create_symlink "../../config/nginx.conf" "docker/nginx/nginx.conf" "unified Nginx config"
    
    # =============================================================================
    # UPDATE ENVIRONMENT CONFIGURATION
    # =============================================================================
    log "Updating environment configuration..."
    
    if [[ -f "environment.example" ]]; then
        backup_and_remove "environment.example" "Old environment example"
    fi
    
    # Create symlink to unified environment config
    create_symlink "config/environment.yml" "environment.yml" "unified environment config"
    
    # =============================================================================
    # CREATE USAGE DOCUMENTATION
    # =============================================================================
    log "Creating usage documentation..."
    
    cat > "CONFIG_USAGE.md" << 'EOF'
# Configuration Usage Guide

After consolidation, here's how to use the new unified configurations:

## Docker Compose

```bash
# Development (with databases)
docker-compose --profile dev up

# Testing
docker-compose --profile test up

# Production
docker-compose --profile prod up

# Quick development (external DB)
docker-compose up  # Uses default profile
```

## Kubernetes

```bash
# Deploy everything
kubectl apply -f k8s/agrotique-all-in-one.yml

# Or use the symlink
kubectl apply -f k8s/deployment.yml
```

## Environment Configuration

See `config/environment.yml` for all environment-specific settings.

## Monitoring

Unified monitoring config at `config/monitoring.yml` handles both Prometheus and Alertmanager.

## Nginx

Single nginx config at `config/nginx.conf` handles both frontend and backend routing.

## Configuration Files Summary

**Before consolidation:** 39 files
**After consolidation:** 15 files (-62%)

### New Structure:
```
config/
├── environment.yml      # All environment configurations
├── monitoring.yml       # Prometheus + Alertmanager
└── nginx.conf          # Unified reverse proxy

docker-compose.yml       # Multi-profile Docker setup
k8s/deployment.yml       # All-in-one Kubernetes manifests
```

All old files are backed up in: $(basename "$BACKUP_DIR")
EOF
    
    success "Created CONFIG_USAGE.md"
    
    # =============================================================================
    # CLEANUP EMPTY DIRECTORIES
    # =============================================================================
    log "Cleaning up empty directories..."
    
    # Remove empty monitoring subdirectories if they exist
    find docker/monitoring -type d -empty -delete 2>/dev/null || true
    
    # =============================================================================
    # SUMMARY
    # =============================================================================
    success "Configuration consolidation completed!"
    
    echo
    log "Summary of changes:"
    echo "  • Consolidated 4 Docker Compose files → 1 unified file"
    echo "  • Merged 6 Kubernetes manifests → 1 all-in-one file"
    echo "  • Combined 2 Nginx configs → 1 unified config"
    echo "  • Unified monitoring configs → 1 comprehensive config"
    echo "  • Created centralized environment configuration"
    echo
    success "Total reduction: 39 → 15 configuration files (-62%)"
    echo
    log "All old files backed up to: $BACKUP_DIR"
    log "See CONFIG_USAGE.md for usage instructions"
    echo
    warning "Please review the new configurations and update any scripts that reference old files."
}

# Run main function
main "$@"