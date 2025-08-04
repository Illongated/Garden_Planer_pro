import redis.asyncio as redis
from contextlib import asynccontextmanager
import time
import gzip
import json

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi import status

from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import security_manager
from app.api.v1.api import api_router

# --- Performance Monitoring ---
class PerformanceMiddleware:
    """Middleware to track request performance metrics."""
    
    def __init__(self):
        self.request_times = {}
        self.error_counts = {}
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Track request start
        request_id = f"{request.method}_{request.url.path}"
        self.request_times[request_id] = start_time
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Cache-Control"] = "public, max-age=3600"
            
            # Log slow requests
            if process_time > 1.0:  # 1 second threshold
                print(f"Slow request: {request_id} took {process_time:.2f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            
            # Track errors
            if request_id not in self.error_counts:
                self.error_counts[request_id] = 0
            self.error_counts[request_id] += 1
            
            print(f"Error in request: {request_id} after {process_time:.2f}s - {str(e)}")
            raise

# --- Caching Middleware ---
class CacheMiddleware:
    """Middleware for response caching."""
    
    def __init__(self):
        self.cache = {}
    
    async def __call__(self, request: Request, call_next):
        # Skip caching for non-GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Create cache key
        cache_key = f"{request.method}_{request.url.path}_{request.query_params}"
        
        # Check cache
        if cache_key in self.cache:
            cached_response = self.cache[cache_key]
            if time.time() - cached_response["timestamp"] < settings.CACHE_TTL:
                return JSONResponse(
                    content=cached_response["content"],
                    headers=cached_response["headers"]
                )
        
        # Get response
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            try:
                content = await response.body()
                self.cache[cache_key] = {
                    "content": json.loads(content.decode()),
                    "headers": dict(response.headers),
                    "timestamp": time.time()
                }
            except:
                pass  # Skip caching if response can't be serialized
        
        return response

# --- Lifespan Manager for Redis Connection ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown events.
    Connects to Redis on startup and closes the connection on shutdown.
    """
    app.state.redis = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True,
        db=settings.REDIS_DB
    )
    yield
    await app.state.redis.aclose()

# --- App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="A modern, production-ready RESTful API for the Agrotique Garden Planner.",
    lifespan=lifespan
)

# --- Performance Middleware ---
performance_middleware = PerformanceMiddleware()
cache_middleware = CacheMiddleware()

# --- Middleware ---
app.state.limiter = limiter

# Add compression middleware
if settings.ENABLE_COMPRESSION:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add security middleware
SecurityMiddleware = security_manager.get_middleware()
app.add_middleware(SecurityMiddleware)

# Add performance monitoring
app.middleware("http")(performance_middleware)

# Add caching middleware
if settings.ENABLE_CACHING:
    app.middleware("http")(cache_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CSRF Protection ---
@CsrfProtect.load_config
def get_csrf_config():
    return [("secret_key", settings.CSRF_SECRET), ("cookie_samesite", "strict")]

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

# --- Exception Handlers ---
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": " -> ".join(map(str, e["loc"])), "msg": e["msg"]} for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": errors},
    )

# --- Health Check Endpoint ---
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# --- Performance Metrics Endpoints ---
performance_metrics_store = {}
cache_stats_store = {}
database_stats_store = {}

@app.post("/api/v1/performance/metrics", tags=["Performance"])
async def receive_performance_metrics(request: Request):
    """Receive performance metrics from frontend."""
    try:
        metrics = await request.json()
        
        # Store metrics for retrieval
        performance_metrics_store["latest"] = {
            **metrics,
            "timestamp": time.time()
        }
        
        print(f"Performance metrics received: {metrics}")
        return {"status": "received"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid metrics format: {str(e)}"}
        )

@app.get("/api/v1/performance/metrics", tags=["Performance"])
async def get_performance_metrics():
    """Get latest performance metrics."""
    return performance_metrics_store.get("latest", {
        "status": "no_data",
        "message": "No metrics available yet"
    })

@app.get("/api/v1/performance/cache-stats", tags=["Performance"])
async def get_cache_stats():
    """Get cache statistics."""
    # Mock cache stats - in real implementation, get from Redis/cache service
    return {
        "hit_rate": 0.85,
        "miss_rate": 0.15,
        "total_requests": 1000,
        "cache_size": "50MB",
        "memory_usage": 0.6,
        "timestamp": time.time()
    }

@app.get("/api/v1/performance/database-stats", tags=["Performance"])
async def get_database_stats():
    """Get database statistics."""
    # Mock database stats - in real implementation, get from database monitoring
    return {
        "active_connections": 5,
        "max_connections": 100,
        "query_time_avg": 0.05,
        "slow_queries": 2,
        "database_size": "120MB",
        "timestamp": time.time()
    }

# --- API Router ---
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
