# Agrotique Garden Planner - Production Deployment Guide

## Overview

This document provides comprehensive guidance for deploying and operating the Agrotique Garden Planner in a production environment. The system is designed for high availability, scalability, and reliability with automated monitoring, backup, and disaster recovery capabilities.

## Architecture

### Components

1. **Frontend**: React/TypeScript application served by Nginx
2. **Backend**: FastAPI Python application with async support
3. **Database**: PostgreSQL 15 with high availability
4. **Cache**: Redis 7 with persistence
5. **Reverse Proxy**: Nginx with SSL/TLS termination
6. **Monitoring**: Prometheus + Grafana + Alertmanager
7. **Backup**: Automated encrypted backups

### Network Architecture

```
Internet → Load Balancer → Nginx (SSL/TLS) → Frontend/Backend
                                    ↓
                              PostgreSQL + Redis
                                    ↓
                              Monitoring Stack
```

## Prerequisites

### System Requirements

- **CPU**: Minimum 4 cores, recommended 8+ cores
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: Minimum 100GB SSD, recommended 500GB+
- **Network**: Stable internet connection for updates and monitoring

### Software Requirements

- Docker 20.10+ and Docker Compose 2.0+
- OR Kubernetes 1.24+ with kubectl
- Git for version control
- curl for health checks

## Deployment Options

### Option 1: Docker Compose (Recommended for small-medium deployments)

```bash
# Clone the repository
git clone https://github.com/your-org/agrotique-garden-planner.git
cd agrotique-garden-planner

# Configure environment
cp env.production.example .env.production
# Edit .env.production with your values

# Deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh docker
```

### Option 2: Kubernetes (Recommended for large-scale deployments)

```bash
# Deploy to Kubernetes
./scripts/deploy.sh kubernetes

# Or manually apply manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml -n agrotique
kubectl apply -f k8s/secrets.yml -n agrotique
kubectl apply -f k8s/persistent-volumes.yml -n agrotique
kubectl apply -f k8s/services.yml -n agrotique
kubectl apply -f k8s/deployments.yml -n agrotique
```

## Configuration

### Environment Variables

Copy `env.production.example` to `.env.production` and configure:

```bash
# Database
POSTGRES_PASSWORD=your-secure-password
POSTGRES_USER=agrotique_user
POSTGRES_DB=agrotique

# Redis
REDIS_PASSWORD=your-secure-password

# Security
SECRET_KEY=your-very-long-secret-key-minimum-32-characters
ENVIRONMENT=production

# Backup
BACKUP_ENCRYPTION_KEY=your-backup-encryption-key
BACKUP_NOTIFICATION_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK

# Monitoring
GRAFANA_PASSWORD=your-grafana-password

# SSL/TLS
DOMAIN=agrotique.example.com
EMAIL=admin@agrotique.example.com
```

### SSL/TLS Configuration

#### Automatic (Let's Encrypt)

The system is configured to automatically obtain and renew SSL certificates using Let's Encrypt.

#### Manual SSL Certificates

1. Place your certificates in `docker/nginx/ssl/`
2. Update the Nginx configuration if needed
3. For Kubernetes, create a TLS secret:

```bash
kubectl create secret tls ssl-certificates \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  -n agrotique
```

## Monitoring and Alerting

### Accessing Monitoring Dashboards

- **Grafana**: http://your-domain:3000 (admin / your-grafana-password)
- **Prometheus**: http://your-domain:9090
- **Alertmanager**: http://your-domain:9093

### Key Metrics to Monitor

1. **Application Health**
   - Response time (target: < 200ms)
   - Error rate (target: < 1%)
   - Request rate

2. **Infrastructure Health**
   - CPU usage (target: < 80%)
   - Memory usage (target: < 80%)
   - Disk usage (target: < 85%)
   - Network I/O

3. **Database Health**
   - Connection count
   - Query performance
   - Replication lag (if applicable)

### Alerting Rules

The system includes pre-configured alerts for:
- Service down
- High error rates
- Resource exhaustion
- Backup failures
- Security events

## Backup and Recovery

### Automated Backups

Backups run automatically:
- **Daily**: Full database backup
- **Weekly**: Full system backup
- **Retention**: 30 days by default

### Manual Backup

```bash
# Docker
docker-compose -f docker-compose.production.yml exec backup /backup.sh

# Kubernetes
kubectl exec -n agrotique deployment/backup -- /backup.sh
```

### Restore from Backup

```bash
# List available backups
./scripts/restore.sh list

# Restore specific backup
./scripts/restore.sh restore /backups/agrotique_backup_20240101_120000.sql.gz.gpg
```

### Backup Verification

```bash
# Verify backup integrity
echo "your-encryption-key" | gpg --batch --yes --passphrase-fd 0 \
  --decrypt backup_file.sql.gz.gpg | gunzip | head -n 1
```

## Maintenance Procedures

### Regular Maintenance

#### Daily
- Check monitoring dashboards
- Review error logs
- Verify backup completion

#### Weekly
- Review performance metrics
- Update security patches
- Clean up old logs

#### Monthly
- Review and update SSL certificates
- Update system packages
- Review backup retention policy

### Scaling Operations

#### Horizontal Scaling (Kubernetes)

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n agrotique

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n agrotique
```

#### Vertical Scaling (Docker Compose)

Update resource limits in `docker-compose.production.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2Gi
          cpus: '1.0'
```

### Updates and Upgrades

#### Application Updates

```bash
# Pull latest images
docker pull ghcr.io/your-org/agrotique:latest
docker pull ghcr.io/your-org/agrotique-frontend:latest

# Deploy with zero downtime
./scripts/deploy.sh docker
```

#### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services if needed
docker-compose -f docker-compose.production.yml restart
```

## Troubleshooting

### Common Issues

#### Service Won't Start

1. Check logs:
```bash
# Docker
docker-compose -f docker-compose.production.yml logs service_name

# Kubernetes
kubectl logs deployment/service_name -n agrotique
```

2. Check resource usage:
```bash
docker stats
# or
kubectl top pods -n agrotique
```

#### Database Connection Issues

1. Verify PostgreSQL is running:
```bash
docker-compose -f docker-compose.production.yml exec postgres pg_isready
```

2. Check connection string in environment variables

#### High Memory Usage

1. Check for memory leaks:
```bash
docker stats --no-stream
```

2. Restart services if needed:
```bash
docker-compose -f docker-compose.production.yml restart backend
```

### Log Analysis

#### Application Logs

```bash
# Docker
docker-compose -f docker-compose.production.yml logs -f backend

# Kubernetes
kubectl logs -f deployment/backend -n agrotique
```

#### System Logs

```bash
# Docker
docker system df
docker system prune -f

# Kubernetes
kubectl get events -n agrotique --sort-by='.lastTimestamp'
```

## Security

### Security Best Practices

1. **Regular Updates**: Keep all components updated
2. **Access Control**: Use strong passwords and rotate regularly
3. **Network Security**: Use firewalls and VPNs
4. **Monitoring**: Monitor for suspicious activity
5. **Backups**: Test backup restoration regularly

### Security Monitoring

The system includes:
- Rate limiting
- Brute force protection
- Input validation
- XSS protection
- CSRF protection
- Audit logging

### Incident Response

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve evidence
   - Notify stakeholders

2. **Investigation**
   - Review logs and monitoring data
   - Identify root cause
   - Document findings

3. **Recovery**
   - Restore from backup if needed
   - Apply security patches
   - Update procedures

## Performance Optimization

### Application Performance

1. **Database Optimization**
   - Monitor slow queries
   - Add appropriate indexes
   - Optimize connection pooling

2. **Caching Strategy**
   - Use Redis for session storage
   - Implement application-level caching
   - Configure CDN for static assets

3. **Code Optimization**
   - Profile application performance
   - Optimize database queries
   - Implement async operations

### Infrastructure Performance

1. **Resource Monitoring**
   - Monitor CPU, memory, disk usage
   - Set up alerts for resource thresholds
   - Scale resources as needed

2. **Network Optimization**
   - Use CDN for global distribution
   - Optimize SSL/TLS configuration
   - Implement connection pooling

## Disaster Recovery

### Recovery Procedures

#### Complete System Failure

1. **Assess Damage**
   - Determine scope of failure
   - Identify affected components
   - Document incident

2. **Recovery Steps**
   - Restore from latest backup
   - Verify data integrity
   - Test system functionality

3. **Post-Recovery**
   - Update monitoring
   - Review procedures
   - Document lessons learned

#### Partial System Failure

1. **Isolate Affected Components**
2. **Restore from Backup**
3. **Verify System Health**
4. **Resume Operations**

### Recovery Time Objectives (RTO)

- **Critical Systems**: 15 minutes
- **Non-Critical Systems**: 1 hour
- **Full System**: 4 hours

### Recovery Point Objectives (RPO)

- **Database**: 1 hour (daily backups)
- **Application Data**: 24 hours
- **Configuration**: 1 hour

## Support and Contact

### Getting Help

1. **Documentation**: Check this guide and other documentation
2. **Logs**: Review application and system logs
3. **Monitoring**: Check Grafana dashboards
4. **Community**: GitHub issues and discussions

### Emergency Contacts

- **System Administrator**: [Contact Information]
- **Database Administrator**: [Contact Information]
- **Security Team**: [Contact Information]

### Escalation Procedures

1. **Level 1**: System administrator (immediate response)
2. **Level 2**: Senior administrator (within 1 hour)
3. **Level 3**: Management team (within 4 hours)

## Appendix

### Useful Commands

```bash
# Check system status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Execute commands in containers
docker-compose -f docker-compose.production.yml exec backend python manage.py shell

# Backup database
docker-compose -f docker-compose.production.yml exec backup /backup.sh

# Update images
docker-compose -f docker-compose.production.yml pull

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### Configuration Files

- `docker-compose.production.yml`: Production Docker Compose configuration
- `k8s/`: Kubernetes manifests
- `docker/nginx/`: Nginx configuration
- `docker/monitoring/`: Monitoring configuration
- `scripts/`: Deployment and maintenance scripts

### Monitoring Queries

```promql
# Application response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"4..|5.."}[5m])

# Database connections
pg_stat_database_numbackends

# Redis memory usage
redis_memory_used_bytes
```

This documentation should be updated regularly as the system evolves and new procedures are developed. 