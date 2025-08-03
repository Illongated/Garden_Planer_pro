// Frontend Security Utilities
// Version: 1.0.0

import DOMPurify from 'dompurify';
import { z } from 'zod';

// Security Configuration
const SECURITY_CONFIG = {
  // CSP Configuration
  csp: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'", "https://api.agrotique.com"],
    'frame-src': ["'none'"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  },
  
  // Rate limiting configuration
  rateLimit: {
    maxRequests: 100,
    windowMs: 15 * 60 * 1000, // 15 minutes
    delayMs: 1000
  },
  
  // Input validation schemas
  validation: {
    strict: true,
    maxLength: 10000,
    allowedTags: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
  }
};

// XSS Protection Class
class XSSProtection {
  private static instance: XSSProtection;
  private sanitizer: typeof DOMPurify;

  constructor() {
    this.sanitizer = DOMPurify;
    this.configureSanitizer();
  }

  static getInstance(): XSSProtection {
    if (!XSSProtection.instance) {
      XSSProtection.instance = new XSSProtection();
    }
    return XSSProtection.instance;
  }

  private configureSanitizer(): void {
    // Configure DOMPurify with strict settings
    this.sanitizer.setConfig({
      ALLOWED_TAGS: SECURITY_CONFIG.validation.allowedTags,
      ALLOWED_ATTR: ['class', 'id', 'style'],
      FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form'],
      FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'],
      KEEP_CONTENT: false,
      RETURN_DOM: false,
      RETURN_DOM_FRAGMENT: false,
      RETURN_TRUSTED_TYPE: false
    });
  }

  sanitizeInput(input: string): string {
    if (typeof input !== 'string') {
      return '';
    }
    
    // Remove null bytes and control characters
    let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
    
    // Basic XSS pattern detection
    const xssPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /javascript:/gi,
      /vbscript:/gi,
      /on\w+\s*=/gi,
      /<iframe/gi,
      /<object/gi,
      /<embed/gi
    ];
    
    xssPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });
    
    // Use DOMPurify for final sanitization
    return this.sanitizer.sanitize(sanitized);
  }

  sanitizeHTML(html: string): string {
    return this.sanitizer.sanitize(html, {
      ALLOWED_TAGS: SECURITY_CONFIG.validation.allowedTags,
      ALLOWED_ATTR: ['class', 'id', 'style'],
      KEEP_CONTENT: true
    });
  }

  validateAndSanitizeObject(obj: any): any {
    if (typeof obj !== 'object' || obj === null) {
      return obj;
    }

    const sanitized: any = Array.isArray(obj) ? [] : {};

    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string') {
        sanitized[key] = this.sanitizeInput(value);
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = this.validateAndSanitizeObject(value);
      } else {
        sanitized[key] = value;
      }
    }

    return sanitized;
  }
}

// Input Validation Class
class InputValidator {
  private static instance: InputValidator;
  private schemas: Map<string, z.ZodSchema> = new Map();

  constructor() {
    this.initializeSchemas();
  }

  static getInstance(): InputValidator {
    if (!InputValidator.instance) {
      InputValidator.instance = new InputValidator();
    }
    return InputValidator.instance;
  }

  private initializeSchemas(): void {
    // User input schemas
    this.schemas.set('userProfile', z.object({
      full_name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
      email: z.string().email(),
      bio: z.string().max(500).optional(),
      location: z.string().max(100).optional()
    }));

    // Garden input schemas
    this.schemas.set('garden', z.object({
      name: z.string().min(1).max(100).regex(/^[a-zA-Z0-9\s\-_]+$/),
      description: z.string().max(1000).optional(),
      width: z.number().positive().max(1000),
      height: z.number().positive().max(1000),
      location: z.string().max(200).optional()
    }));

    // Plant input schemas
    this.schemas.set('plant', z.object({
      name: z.string().min(1).max(100).regex(/^[a-zA-Z0-9\s\-_]+$/),
      species: z.string().min(1).max(100),
      position_x: z.number().min(0).max(1000),
      position_y: z.number().min(0).max(1000),
      notes: z.string().max(1000).optional()
    }));

    // Search input schemas
    this.schemas.set('search', z.object({
      query: z.string().min(1).max(200).regex(/^[a-zA-Z0-9\s\-_]+$/),
      filters: z.record(z.string(), z.any()).optional(),
      page: z.number().int().min(1).max(1000).optional(),
      limit: z.number().int().min(1).max(100).optional()
    }));
  }

  validateInput(schemaName: string, data: any): { success: boolean; data?: any; errors?: string[] } {
    const schema = this.schemas.get(schemaName);
    if (!schema) {
      return { success: false, errors: [`Unknown schema: ${schemaName}`] };
    }

    try {
      const validated = schema.parse(data);
      return { success: true, data: validated };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors = error.errors.map(err => `${err.path.join('.')}: ${err.message}`);
        return { success: false, errors };
      }
      return { success: false, errors: ['Validation failed'] };
    }
  }

  sanitizeAndValidate(schemaName: string, data: any): { success: boolean; data?: any; errors?: string[] } {
    // First sanitize the input
    const xssProtection = XSSProtection.getInstance();
    const sanitizedData = xssProtection.validateAndSanitizeObject(data);
    
    // Then validate
    return this.validateInput(schemaName, sanitizedData);
  }
}

// API Security Class
class APISecurity {
  private static instance: APISecurity;
  private requestCounts: Map<string, number> = new Map();
  private blockedIPs: Set<string> = new Set();
  private lastRequestTimes: Map<string, number> = new Map();

  constructor() {
    this.startCleanupInterval();
  }

  static getInstance(): APISecurity {
    if (!APISecurity.instance) {
      APISecurity.instance = new APISecurity();
    }
    return APISecurity.instance;
  }

  private getClientId(): string {
    // In a real implementation, this would get the actual client IP
    // For now, we'll use a combination of user agent and session
    return `${navigator.userAgent}-${sessionStorage.getItem('sessionId') || 'anonymous'}`;
  }

  private startCleanupInterval(): void {
    setInterval(() => {
      const now = Date.now();
      const windowMs = SECURITY_CONFIG.rateLimit.windowMs;
      
      // Clean up old request counts
      for (const [clientId, lastTime] of this.lastRequestTimes.entries()) {
        if (now - lastTime > windowMs) {
          this.requestCounts.delete(clientId);
          this.lastRequestTimes.delete(clientId);
        }
      }
    }, 60000); // Clean up every minute
  }

  checkRateLimit(): { allowed: boolean; delay?: number } {
    const clientId = this.getClientId();
    const now = Date.now();
    
    // Check if IP is blocked
    if (this.blockedIPs.has(clientId)) {
      return { allowed: false };
    }

    const requestCount = this.requestCounts.get(clientId) || 0;
    const lastRequestTime = this.lastRequestTimes.get(clientId) || 0;
    const windowMs = SECURITY_CONFIG.rateLimit.windowMs;

    // Reset count if window has passed
    if (now - lastRequestTime > windowMs) {
      this.requestCounts.set(clientId, 1);
      this.lastRequestTimes.set(clientId, now);
      return { allowed: true };
    }

    // Check rate limit
    if (requestCount >= SECURITY_CONFIG.rateLimit.maxRequests) {
      // Block for 15 minutes
      this.blockedIPs.add(clientId);
      setTimeout(() => {
        this.blockedIPs.delete(clientId);
      }, 15 * 60 * 1000);
      
      return { allowed: false };
    }

    // Increment count
    this.requestCounts.set(clientId, requestCount + 1);
    this.lastRequestTimes.set(clientId, now);

    // Add delay for high-frequency requests
    const delay = requestCount > 50 ? SECURITY_CONFIG.rateLimit.delayMs : 0;
    
    return { allowed: true, delay };
  }

  secureAPIRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const rateLimitCheck = this.checkRateLimit();
    
    if (!rateLimitCheck.allowed) {
      return Promise.reject(new Error('Rate limit exceeded'));
    }

    // Add security headers
    const secureOptions: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Client-Version': '1.0.0',
        ...options.headers
      },
      credentials: 'include' // Include cookies for CSRF protection
    };

    // Add delay if needed
    if (rateLimitCheck.delay) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          fetch(url, secureOptions).then(resolve).catch(reject);
        }, rateLimitCheck.delay);
      });
    }

    return fetch(url, secureOptions);
  }
}

// CSP Header Generator
class CSPGenerator {
  static generateCSPHeader(): string {
    const csp = SECURITY_CONFIG.csp;
    const directives = Object.entries(csp).map(([directive, sources]) => {
      if (Array.isArray(sources)) {
        return `${directive} ${sources.join(' ')}`;
      }
      return directive;
    });
    
    return directives.join('; ');
  }

  static validateCSPHeader(header: string): boolean {
    const requiredDirectives = [
      'default-src',
      'script-src',
      'style-src',
      'frame-ancestors'
    ];

    const directives = header.split(';').map(d => d.trim().split(' ')[0]);
    
    return requiredDirectives.every(directive => 
      directives.includes(directive)
    );
  }
}

// Security Event Logger
class SecurityLogger {
  private static instance: SecurityLogger;
  private events: Array<{
    timestamp: number;
    type: string;
    details: any;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }> = [];

  constructor() {
    this.setupErrorHandling();
  }

  static getInstance(): SecurityLogger {
    if (!SecurityLogger.instance) {
      SecurityLogger.instance = new SecurityLogger();
    }
    return SecurityLogger.instance;
  }

  private setupErrorHandling(): void {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.logSecurityEvent('javascript_error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack
      }, 'medium');
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.logSecurityEvent('unhandled_promise_rejection', {
        reason: event.reason
      }, 'medium');
    });
  }

  logSecurityEvent(type: string, details: any, severity: 'low' | 'medium' | 'high' | 'critical' = 'low'): void {
    const event = {
      timestamp: Date.now(),
      type,
      details,
      severity
    };

    this.events.push(event);

    // Keep only last 1000 events
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[SECURITY] ${type}:`, details);
    }

    // Send to backend for critical events
    if (severity === 'high' || severity === 'critical') {
      this.sendToBackend(event);
    }
  }

  private async sendToBackend(event: any): Promise<void> {
    try {
      const apiSecurity = APISecurity.getInstance();
      await apiSecurity.secureAPIRequest('/api/v1/security/log', {
        method: 'POST',
        body: JSON.stringify(event)
      });
    } catch (error) {
      console.error('Failed to send security event to backend:', error);
    }
  }

  getEvents(severity?: string): any[] {
    if (severity) {
      return this.events.filter(event => event.severity === severity);
    }
    return [...this.events];
  }

  clearEvents(): void {
    this.events = [];
  }
}

// Export security utilities
export const xssProtection = XSSProtection.getInstance();
export const inputValidator = InputValidator.getInstance();
export const apiSecurity = APISecurity.getInstance();
export const securityLogger = SecurityLogger.getInstance();
export const cspGenerator = CSPGenerator;

// Security middleware for React components
export const withSecurity = <P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> => {
  return (props: P) => {
    // Log component access
    securityLogger.logSecurityEvent('component_access', {
      component: Component.name,
      props: Object.keys(props)
    }, 'low');

    return <Component {...props} />;
  };
};

// Secure input component
export const SecureInput: React.FC<{
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  className?: string;
}> = ({ value, onChange, placeholder, type = 'text', className }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const sanitized = xssProtection.sanitizeInput(e.target.value);
    onChange(sanitized);
  };

  return (
    <input
      type={type}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      className={className}
      maxLength={SECURITY_CONFIG.validation.maxLength}
    />
  );
};

// Secure textarea component
export const SecureTextarea: React.FC<{
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  rows?: number;
}> = ({ value, onChange, placeholder, className, rows = 3 }) => {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const sanitized = xssProtection.sanitizeInput(e.target.value);
    onChange(sanitized);
  };

  return (
    <textarea
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      className={className}
      rows={rows}
      maxLength={SECURITY_CONFIG.validation.maxLength}
    />
  );
}; 