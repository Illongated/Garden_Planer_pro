"""
Security API Endpoints
Handles security monitoring, audit logs, and security management.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.security import security_manager, SecurityEvent
from api.deps import get_current_user
from models.user import User

router = APIRouter()

# Security Models
class SecurityEventResponse(BaseModel):
    timestamp: datetime
    event_type: str
    user_id: Optional[str] = None
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    severity: str
    session_id: Optional[str] = None

class SecurityStatsResponse(BaseModel):
    rate_limits: int
    brute_force_attempts: int
    audit_events: int
    recent_events: int
    blocked_ips: List[str]
    suspicious_requests: int

class SecurityConfigResponse(BaseModel):
    rate_limiting: Dict[str, Any]
    brute_force: Dict[str, Any]
    password: Dict[str, Any]
    session: Dict[str, Any]
    audit: Dict[str, Any]

@router.get("/audit/events", response_model=List[SecurityEventResponse])
async def get_audit_events(
    request: Request,
    current_user: User = Depends(get_current_user),
    hours: int = 24,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Get security audit events.
    Only accessible by authenticated users.
    """
    # Check if user has admin privileges
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    events = security_manager.audit_logger.get_events(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        hours=hours
    )
    
    return events

@router.get("/audit/events/{event_type}", response_model=List[SecurityEventResponse])
async def get_audit_events_by_type(
    event_type: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    hours: int = 24
):
    """
    Get security audit events by type.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    events = security_manager.audit_logger.get_events(
        event_type=event_type,
        hours=hours
    )
    
    return events

@router.get("/stats", response_model=SecurityStatsResponse)
async def get_security_stats(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get security statistics.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    stats = security_manager.get_security_stats()
    
    # Get blocked IPs
    blocked_ips = list(security_manager.rate_limiter.rate_limits.keys())
    
    # Get suspicious requests count
    suspicious_events = security_manager.audit_logger.get_events(
        event_type="suspicious_request",
        hours=24
    )
    
    return SecurityStatsResponse(
        rate_limits=stats["rate_limits"],
        brute_force_attempts=stats["brute_force_attempts"],
        audit_events=stats["audit_events"],
        recent_events=stats["recent_events"],
        blocked_ips=blocked_ips,
        suspicious_requests=len(suspicious_events)
    )

@router.get("/config", response_model=SecurityConfigResponse)
async def get_security_config(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get security configuration.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    from core.security import SECURITY_CONFIG
    
    return SecurityConfigResponse(
        rate_limiting=SECURITY_CONFIG["rate_limiting"],
        brute_force=SECURITY_CONFIG["brute_force"],
        password=SECURITY_CONFIG["password"],
        session=SECURITY_CONFIG["session"],
        audit=SECURITY_CONFIG["audit"]
    )

@router.post("/log")
async def log_security_event(
    request: Request,
    event_data: Dict[str, Any]
):
    """
    Log security event from frontend.
    """
    try:
        event_type = event_data.get("type", "unknown")
        details = event_data.get("details", {})
        severity = event_data.get("severity", "low")
        
        security_manager.log_security_event(
            event_type=event_type,
            request=request,
            details=details,
            severity=severity
        )
        
        return {"status": "logged"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to log event: {str(e)}"
        )

@router.delete("/audit/events")
async def clear_audit_events(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Clear audit events (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    security_manager.audit_logger.events.clear()
    
    return {"status": "cleared", "message": "All audit events cleared"}

@router.post("/rate-limit/reset/{ip_address}")
async def reset_rate_limit(
    ip_address: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Reset rate limit for specific IP (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    if ip_address in security_manager.rate_limiter.rate_limits:
        del security_manager.rate_limiter.rate_limits[ip_address]
    
    security_manager.log_security_event(
        "rate_limit_reset",
        request,
        {"ip_address": ip_address, "reset_by": current_user.id}
    )
    
    return {"status": "reset", "ip_address": ip_address}

@router.post("/brute-force/reset/{identifier}")
async def reset_brute_force(
    identifier: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Reset brute force protection for specific identifier (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    security_manager.brute_force_protector.reset_attempts(identifier)
    
    security_manager.log_security_event(
        "brute_force_reset",
        request,
        {"identifier": identifier, "reset_by": current_user.id}
    )
    
    return {"status": "reset", "identifier": identifier}

@router.get("/health")
async def security_health_check():
    """
    Security system health check.
    """
    try:
        # Check if security components are working
        stats = security_manager.get_security_stats()
        
        return {
            "status": "healthy",
            "components": {
                "rate_limiter": "active",
                "brute_force_protector": "active",
                "audit_logger": "active"
            },
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/alerts")
async def get_security_alerts(
    request: Request,
    current_user: User = Depends(get_current_user),
    hours: int = 24
):
    """
    Get security alerts (high/critical severity events).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    high_events = security_manager.audit_logger.get_events(
        severity="high",
        hours=hours
    )
    
    critical_events = security_manager.audit_logger.get_events(
        severity="critical",
        hours=hours
    )
    
    return {
        "high_alerts": len(high_events),
        "critical_alerts": len(critical_events),
        "high_events": high_events,
        "critical_events": critical_events
    }

@router.get("/dashboard")
async def get_security_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get security dashboard data.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get recent events by type
    event_types = [
        "login_attempt", "login_success", "login_failed", "login_blocked",
        "rate_limit_exceeded", "suspicious_request", "csrf_violation"
    ]
    
    event_counts = {}
    for event_type in event_types:
        events = security_manager.audit_logger.get_events(
            event_type=event_type,
            hours=24
        )
        event_counts[event_type] = len(events)
    
    # Get severity distribution
    low_events = len(security_manager.audit_logger.get_events(severity="low", hours=24))
    medium_events = len(security_manager.audit_logger.get_events(severity="medium", hours=24))
    high_events = len(security_manager.audit_logger.get_events(severity="high", hours=24))
    critical_events = len(security_manager.audit_logger.get_events(severity="critical", hours=24))
    
    return {
        "event_counts": event_counts,
        "severity_distribution": {
            "low": low_events,
            "medium": medium_events,
            "high": high_events,
            "critical": critical_events
        },
        "stats": security_manager.get_security_stats(),
        "blocked_ips": list(security_manager.rate_limiter.rate_limits.keys()),
        "brute_force_attempts": list(security_manager.brute_force_protector.attempts.keys())
    } 