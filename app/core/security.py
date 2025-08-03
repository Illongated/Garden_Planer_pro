"""
Backend Security Module
Comprehensive security implementation for FastAPI backend.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urlparse

import bcrypt
import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

# Configure security logging
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Security Configuration
SECURITY_CONFIG = {
    "rate_limiting": {
        "requests_per_minute": 60,
        "burst_limit": 100,
        "window_size": 60,  # seconds
        "block_duration": 900,  # 15 minutes
    },
    "brute_force": {
        "max_attempts": 5,
        "lockout_duration": 1800,  # 30 minutes
        "progressive_delay": True,
        "delay_base": 2,  # seconds
    },
    "password": {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digits": True,
        "require_special": True,
        "max_age_days": 90,
    },
    "session": {
        "max_age_hours": 24,
        "refresh_threshold_minutes": 30,
        "max_concurrent_sessions": 5,
    },
    "audit": {
        "log_level": "INFO",
        "retention_days": 365,
        "sensitive_fields": ["password", "token", "secret", "key"],
    }
}

# Security Models
class SecurityEvent(BaseModel):
    timestamp: datetime
    event_type: str
    user_id: Optional[str] = None
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    severity: str = "low"
    session_id: Optional[str] = None

class RateLimitInfo(BaseModel):
    ip_address: str
    requests: int
    window_start: datetime
    blocked_until: Optional[datetime] = None

class BruteForceInfo(BaseModel):
    identifier: str  # IP or username
    attempts: int
    first_attempt: datetime
    last_attempt: datetime
    blocked_until: Optional[datetime] = None

# Security Utilities
class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """Validate password strength."""
        errors = []
        config = SECURITY_CONFIG["password"]
        
        if len(password) < config["min_length"]:
            errors.append(f"Password must be at least {config['min_length']} characters")
        
        if config["require_uppercase"] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if config["require_lowercase"] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if config["require_digits"] and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if config["require_special"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Sanitize input data to prevent injection attacks."""
        if isinstance(data, str):
            # Remove null bytes and control characters
            data = data.replace('\x00', '').replace('\x0d', '').replace('\x0a', '')
            # Basic XSS protection
            data = data.replace('<script', '').replace('javascript:', '')
            return data
        elif isinstance(data, dict):
            return {k: SecurityUtils.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [SecurityUtils.sanitize_input(item) for item in data]
        return data
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token."""
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """Verify CSRF token using constant-time comparison."""
        return hmac.compare_digest(token, stored_token)
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    @staticmethod
    def is_suspicious_request(request: Request) -> bool:
        """Detect suspicious request patterns."""
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_patterns = [
            "sqlmap", "nikto", "nmap", "w3af", "burp", "zap",
            "scanner", "crawler", "bot", "spider"
        ]
        
        return any(pattern in user_agent for pattern in suspicious_patterns)

# Rate Limiting
class RateLimiter:
    def __init__(self):
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.config = SECURITY_CONFIG["rate_limiting"]
    
    def is_allowed(self, ip_address: str) -> Tuple[bool, Optional[datetime]]:
        """Check if request is allowed based on rate limiting."""
        now = datetime.utcnow()
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = RateLimitInfo(
                ip_address=ip_address,
                requests=1,
                window_start=now
            )
            return True, None
        
        limit_info = self.rate_limits[ip_address]
        
        # Check if blocked
        if limit_info.blocked_until and now < limit_info.blocked_until:
            return False, limit_info.blocked_until
        
        # Reset window if expired
        if (now - limit_info.window_start).seconds > self.config["window_size"]:
            limit_info.requests = 1
            limit_info.window_start = now
            return True, None
        
        # Check rate limit
        if limit_info.requests >= self.config["requests_per_minute"]:
            limit_info.blocked_until = now + timedelta(seconds=self.config["block_duration"])
            return False, limit_info.blocked_until
        
        limit_info.requests += 1
        return True, None
    
    def cleanup_expired(self):
        """Clean up expired rate limit entries."""
        now = datetime.utcnow()
        expired_ips = []
        
        for ip, limit_info in self.rate_limits.items():
            if (now - limit_info.window_start).seconds > self.config["window_size"] * 2:
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del self.rate_limits[ip]

# Brute Force Protection
class BruteForceProtector:
    def __init__(self):
        self.attempts: Dict[str, BruteForceInfo] = {}
        self.config = SECURITY_CONFIG["brute_force"]
    
    def check_attempt(self, identifier: str) -> Tuple[bool, Optional[datetime], int]:
        """Check if login attempt is allowed."""
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            self.attempts[identifier] = BruteForceInfo(
                identifier=identifier,
                attempts=1,
                first_attempt=now,
                last_attempt=now
            )
            return True, None, 1
        
        attempt_info = self.attempts[identifier]
        
        # Check if blocked
        if attempt_info.blocked_until and now < attempt_info.blocked_until:
            return False, attempt_info.blocked_until, attempt_info.attempts
        
        # Reset if lockout period expired
        if attempt_info.blocked_until and now >= attempt_info.blocked_until:
            attempt_info.attempts = 1
            attempt_info.first_attempt = now
            attempt_info.last_attempt = now
            attempt_info.blocked_until = None
            return True, None, 1
        
        # Check attempt limit
        if attempt_info.attempts >= self.config["max_attempts"]:
            block_until = now + timedelta(seconds=self.config["lockout_duration"])
            attempt_info.blocked_until = block_until
            return False, block_until, attempt_info.attempts
        
        attempt_info.attempts += 1
        attempt_info.last_attempt = now
        return True, None, attempt_info.attempts
    
    def reset_attempts(self, identifier: str):
        """Reset attempts for successful login."""
        if identifier in self.attempts:
            del self.attempts[identifier]
    
    def cleanup_expired(self):
        """Clean up expired attempt records."""
        now = datetime.utcnow()
        expired_identifiers = []
        
        for identifier, attempt_info in self.attempts.items():
            if (now - attempt_info.last_attempt).days > 1:
                expired_identifiers.append(identifier)
        
        for identifier in expired_identifiers:
            del self.attempts[identifier]

# Audit Logger
class AuditLogger:
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.config = SECURITY_CONFIG["audit"]
    
    def log_event(self, event_type: str, request: Request, details: Dict[str, Any], 
                  user_id: Optional[str] = None, severity: str = "low"):
        """Log security event."""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            ip_address=SecurityUtils.get_client_ip(request),
            user_agent=request.headers.get("User-Agent", ""),
            details=self.sanitize_details(details),
            severity=severity,
            session_id=request.headers.get("X-Session-ID")
        )
        
        self.events.append(event)
        
        # Log to file
        security_logger.info(
            f"SECURITY_EVENT: {event_type} | "
            f"IP: {event.ip_address} | "
            f"User: {user_id or 'anonymous'} | "
            f"Severity: {severity} | "
            f"Details: {json.dumps(details)}"
        )
        
        # Keep only recent events in memory
        if len(self.events) > 10000:
            self.events = self.events[-5000:]
    
    def sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive information from audit details."""
        sanitized = details.copy()
        
        for field in self.config["sensitive_fields"]:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        return sanitized
    
    def get_events(self, user_id: Optional[str] = None, 
                   event_type: Optional[str] = None,
                   severity: Optional[str] = None,
                   hours: int = 24) -> List[SecurityEvent]:
        """Get filtered security events."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        events = [e for e in self.events if e.timestamp >= cutoff]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        return events

# Security Middleware
class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.brute_force_protector = BruteForceProtector()
        self.audit_logger = AuditLogger()
        
        # Start cleanup tasks
        asyncio.create_task(self._cleanup_task())
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = time.time()
        
        # Get client IP
        client_ip = SecurityUtils.get_client_ip(request)
        
        # Check for suspicious requests
        if SecurityUtils.is_suspicious_request(request):
            self.audit_logger.log_event(
                "suspicious_request", request, 
                {"user_agent": request.headers.get("User-Agent")},
                severity="high"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )
        
        # Rate limiting
        allowed, blocked_until = self.rate_limiter.is_allowed(client_ip)
        if not allowed:
            self.audit_logger.log_event(
                "rate_limit_exceeded", request,
                {"blocked_until": blocked_until.isoformat() if blocked_until else None},
                severity="medium"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": int((blocked_until - datetime.utcnow()).total_seconds()) if blocked_until else None
                }
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.agrotique.com; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # HSTS header (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Log request
        duration = time.time() - start_time
        self.audit_logger.log_event(
            "request_processed", request,
            {
                "method": request.method,
                "path": str(request.url.path),
                "duration": duration,
                "status_code": response.status_code
            }
        )
        
        return response
    
    async def _cleanup_task(self):
        """Periodic cleanup of expired data."""
        while True:
            try:
                self.rate_limiter.cleanup_expired()
                self.brute_force_protector.cleanup_expired()
                await asyncio.sleep(300)  # Clean up every 5 minutes
            except Exception as e:
                security_logger.error(f"Cleanup task error: {e}")

# Authentication Security
class AuthSecurity:
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.brute_force_protector = BruteForceProtector()
    
    async def validate_login_attempt(self, request: Request, username: str) -> bool:
        """Validate login attempt and apply brute force protection."""
        identifier = f"{SecurityUtils.get_client_ip(request)}:{username}"
        
        allowed, blocked_until, attempts = self.brute_force_protector.check_attempt(identifier)
        
        if not allowed:
            self.audit_logger.log_event(
                "login_blocked", request,
                {
                    "username": username,
                    "attempts": attempts,
                    "blocked_until": blocked_until.isoformat() if blocked_until else None
                },
                severity="high"
            )
            return False
        
        self.audit_logger.log_event(
            "login_attempt", request,
            {"username": username, "attempts": attempts}
        )
        
        return True
    
    def record_successful_login(self, request: Request, username: str, user_id: str):
        """Record successful login."""
        identifier = f"{SecurityUtils.get_client_ip(request)}:{username}"
        self.brute_force_protector.reset_attempts(identifier)
        
        self.audit_logger.log_event(
            "login_success", request,
            {"username": username},
            user_id=user_id
        )
    
    def record_failed_login(self, request: Request, username: str, reason: str):
        """Record failed login."""
        self.audit_logger.log_event(
            "login_failed", request,
            {"username": username, "reason": reason},
            severity="medium"
        )
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength."""
        return SecurityUtils.validate_password_strength(password)
    
    def hash_password(self, password: str) -> str:
        """Hash password securely."""
        return SecurityUtils.hash_password(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return SecurityUtils.verify_password(password, hashed)

# CSRF Protection
class CSRFProtection:
    def __init__(self):
        self.audit_logger = AuditLogger()
    
    def generate_token(self) -> str:
        """Generate CSRF token."""
        return SecurityUtils.generate_csrf_token()
    
    def verify_token(self, token: str, stored_token: str) -> bool:
        """Verify CSRF token."""
        return SecurityUtils.verify_csrf_token(token, stored_token)
    
    def log_csrf_violation(self, request: Request, details: Dict[str, Any]):
        """Log CSRF violation."""
        self.audit_logger.log_event(
            "csrf_violation", request, details, severity="high"
        )

# Input Validation
class InputValidator:
    def __init__(self):
        self.audit_logger = AuditLogger()
    
    def validate_and_sanitize(self, data: Any, schema: Optional[BaseModel] = None) -> Any:
        """Validate and sanitize input data."""
        # Sanitize input
        sanitized = SecurityUtils.sanitize_input(data)
        
        # Validate against schema if provided
        if schema:
            try:
                validated = schema.parse_obj(sanitized)
                return validated
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(e)}"
                )
        
        return sanitized
    
    def validate_file_upload(self, filename: str, content_type: str, max_size: int = 10 * 1024 * 1024) -> bool:
        """Validate file upload."""
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return False
        
        # Check content type
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif', 
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        if content_type not in allowed_types:
            return False
        
        return True

# Security Manager (Main interface)
class SecurityManager:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.brute_force_protector = BruteForceProtector()
        self.audit_logger = AuditLogger()
        self.auth_security = AuthSecurity()
        self.csrf_protection = CSRFProtection()
        self.input_validator = InputValidator()
    
    def get_middleware(self):
        """Get security middleware."""
        return SecurityMiddleware
    
    def log_security_event(self, event_type: str, request: Request, details: Dict[str, Any],
                          user_id: Optional[str] = None, severity: str = "low"):
        """Log security event."""
        self.audit_logger.log_event(event_type, request, details, user_id, severity)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            "rate_limits": len(self.rate_limiter.rate_limits),
            "brute_force_attempts": len(self.brute_force_protector.attempts),
            "audit_events": len(self.audit_logger.events),
            "recent_events": len(self.audit_logger.get_events(hours=1))
        }

# Global security manager instance
security_manager = SecurityManager()
