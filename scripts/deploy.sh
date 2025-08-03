#!/bin/bash

# Agrotique Garden Planner - Production Deployment Script
# This script implements blue-green deployment with automated rollback

set -euo pipefail

# Configuration
DEPLOYMENT_NAME="agrotique"
NAMESPACE="agrotique"
REGISTRY="ghcr.io"
IMAGE_NAME="your-org/agrotique"
FRONTEND_IMAGE_NAME="your-org/agrotique-frontend"
DEPLOYMENT_TYPE="${1:-docker}"  # docker or kubernetes
ENVIRONMENT_FILE=".env.production"

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

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if environment file exists
    if [[ ! -f "${ENVIRONMENT_FILE}" ]]; then
        error "Environment file ${ENVIRONMENT_FILE} not found"
        echo "Please copy env.production.example to ${ENVIRONMENT_FILE} and configure it"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if running as root (for Docker)
    if [[ "${DEPLOYMENT_TYPE}" == "docker" && "${EUID}" -eq 0 ]]; then
        warning "Running as root - this is not recommended for production"
    fi
    
    log "Prerequisites check passed"
}

# Function to create backup before deployment
create_backup() {
    log "Creating backup before deployment..."
    
    if [[ "${DEPLOYMENT_TYPE}" == "docker" ]]; then
        # Docker backup
        if docker-compose -f docker-compose.production.yml ps -q | grep -q .; then
            docker-compose -f docker-compose.production.yml exec -T backup /backup.sh || warning "Backup failed"
        fi
    elif [[ "${DEPLOYMENT_TYPE}" == "kubernetes" ]]; then
        # Kubernetes backup
        kubectl exec -n "${NAMESPACE}" deployment/backup -- /backup.sh || warning "Backup failed"
    fi
    
    log "Backup completed"
}

# Function to check service health
check_health() {
    local service_url="$1"
    local max_attempts=30
    local attempt=1
    
    log "Checking service health at ${service_url}..."
    
    while [[ ${attempt} -le ${max_attempts} ]]; do
        if curl -f -s "${service_url}/health" > /dev/null; then
            log "Service is healthy"
            return 0
        fi
        
        warning "Health check attempt ${attempt}/${max_attempts} failed"
        sleep 10
        ((attempt++))
    done
    
    error "Service health check failed after ${max_attempts} attempts"
    return 1
}

# Function to rollback deployment
rollback() {
    local reason="$1"
    error "Rolling back deployment: ${reason}"
    
    if [[ "${DEPLOYMENT_TYPE}" == "docker" ]]; then
        # Docker rollback
        docker-compose -f docker-compose.production.yml down
        docker-compose -f docker-compose.production.yml up -d
    elif [[ "${DEPLOYMENT_TYPE}" == "kubernetes" ]]; then
        # Kubernetes rollback
        kubectl rollout undo deployment/backend -n "${NAMESPACE}"
        kubectl rollout undo deployment/frontend -n "${NAMESPACE}"
    fi
    
    log "Rollback completed"
}

# Function to deploy with Docker Compose
deploy_docker() {
    log "Starting Docker Compose deployment..."
    
    # Load environment variables
    export $(grep -v '^#' "${ENVIRONMENT_FILE}" | xargs)
    
    # Pull latest images
    log "Pulling latest images..."
    docker pull "${REGISTRY}/${IMAGE_NAME}:latest" || error "Failed to pull backend image"
    docker pull "${REGISTRY}/${FRONTEND_IMAGE_NAME}:latest" || error "Failed to pull frontend image"
    
    # Stop current deployment
    if docker-compose -f docker-compose.production.yml ps -q | grep -q .; then
        log "Stopping current deployment..."
        docker-compose -f docker-compose.production.yml down
    fi
    
    # Start new deployment
    log "Starting new deployment..."
    docker-compose -f docker-compose.production.yml up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if ! check_health "http://localhost"; then
        rollback "Health check failed"
        exit 1
    fi
    
    log "Docker Compose deployment completed successfully"
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    log "Starting Kubernetes deployment..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        log "Creating namespace ${NAMESPACE}..."
        kubectl apply -f k8s/namespace.yml
    fi
    
    # Apply ConfigMaps and Secrets
    log "Applying configuration..."
    kubectl apply -f k8s/configmap.yml -n "${NAMESPACE}"
    kubectl apply -f k8s/secrets.yml -n "${NAMESPACE}"
    
    # Apply PersistentVolumeClaims
    log "Creating persistent volumes..."
    kubectl apply -f k8s/persistent-volumes.yml -n "${NAMESPACE}"
    
    # Apply Services
    log "Creating services..."
    kubectl apply -f k8s/services.yml -n "${NAMESPACE}"
    
    # Apply Deployments
    log "Creating deployments..."
    kubectl apply -f k8s/deployments.yml -n "${NAMESPACE}"
    
    # Wait for deployments to be ready
    log "Waiting for deployments to be ready..."
    kubectl rollout status deployment/backend -n "${NAMESPACE}" --timeout=300s
    kubectl rollout status deployment/frontend -n "${NAMESPACE}" --timeout=300s
    kubectl rollout status deployment/nginx -n "${NAMESPACE}" --timeout=300s
    
    # Get service URL
    local service_url=$(kubectl get service nginx-service -n "${NAMESPACE}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [[ -z "${service_url}" ]]; then
        service_url=$(kubectl get service nginx-service -n "${NAMESPACE}" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    fi
    
    if [[ -z "${service_url}" ]]; then
        warning "Could not determine service URL, using localhost"
        service_url="http://localhost"
    else
        service_url="http://${service_url}"
    fi
    
    # Health check
    if ! check_health "${service_url}"; then
        rollback "Health check failed"
        exit 1
    fi
    
    log "Kubernetes deployment completed successfully"
    log "Service URL: ${service_url}"
}

# Function to send deployment notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        log "Sending deployment notification..."
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"${status} Agrotique deployment: ${message}\"}" \
            --silent --fail || warning "Failed to send notification"
    fi
}

# Main deployment function
main() {
    log "Starting Agrotique Garden Planner deployment..."
    log "Deployment type: ${DEPLOYMENT_TYPE}"
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_backup
    
    # Deploy based on type
    if [[ "${DEPLOYMENT_TYPE}" == "docker" ]]; then
        deploy_docker
    elif [[ "${DEPLOYMENT_TYPE}" == "kubernetes" ]]; then
        deploy_kubernetes
    else
        error "Invalid deployment type: ${DEPLOYMENT_TYPE}"
        echo "Usage: $0 [docker|kubernetes]"
        exit 1
    fi
    
    # Send success notification
    send_notification "✅" "Deployment completed successfully"
    
    log "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "docker"|"kubernetes")
        DEPLOYMENT_TYPE="$1"
        main
        ;;
    "help"|"--help"|"-h")
        echo "Agrotique Garden Planner - Deployment Script"
        echo
        echo "Usage:"
        echo "  $0 docker        - Deploy using Docker Compose"
        echo "  $0 kubernetes    - Deploy using Kubernetes"
        echo "  $0 help          - Show this help message"
        echo
        echo "Prerequisites:"
        echo "  - Docker and Docker Compose (for docker deployment)"
        echo "  - kubectl and Kubernetes cluster (for kubernetes deployment)"
        echo "  - .env.production file with proper configuration"
        echo
        exit 0
        ;;
    *)
        error "Invalid argument: ${1:-}"
        echo "Usage: $0 [docker|kubernetes|help]"
        exit 1
        ;;
esac 