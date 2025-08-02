import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.v1.api import api_router

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per minute"])

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="A modern, production-ready RESTful API for the Agrotique Garden Planner.",
)

# Add Rate Limiter state and handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from contextlib import asynccontextmanager

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

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="A modern, production-ready RESTful API for the Agrotique Garden Planner.",
    lifespan=lifespan
)

# --- Middleware ---
# In a production environment, you should restrict origins to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Custom Exception Handler for Pydantic Validation Errors ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    A custom exception handler to provide more detailed validation error messages.
    """
    # You can customize the error response format here
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": " -> ".join(map(str, error["loc"])),
            "msg": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "errors": errors},
    )

# --- API Router ---
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
