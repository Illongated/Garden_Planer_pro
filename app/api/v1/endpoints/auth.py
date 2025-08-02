import uuid
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate, UserPublic
from app.schemas.token import Token, TokenPayload

# --- In-Memory "Database" ---
# In a real application, this would be replaced by a proper database (e.g., PostgreSQL).
# The key is the user's email, and the value is the user object.
fake_users_db: dict[str, Any] = {}

# --- APIRouter ---
router = APIRouter()

# --- Reusable Dependency to get current user ---
async def get_current_user(token: str = Depends(security.oauth2_scheme)) -> UserPublic:
    """
    Dependency to get the current user from a token.
    Raises HTTPException if the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=uuid.UUID(user_id_str))
    except (JWTError, ValueError):
        raise credentials_exception

    # Find user in our fake DB
    user = next((user for user in fake_users_db.values() if user["id"] == token_data.sub), None)

    if user is None:
        raise credentials_exception
    return UserPublic(**user)

# --- API Endpoints ---
@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register_user(user_in: UserCreate):
    """
    Register a new user.
    """
    if user_in.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    hashed_password = security.get_password_hash(user_in.password)
    user_id = uuid.uuid4()
    user_data = user_in.model_dump(exclude={"password"})
    user_data.update({"id": user_id, "hashed_password": hashed_password})
    fake_users_db[user_in.email] = user_data
    return UserPublic(**user_data)

@router.post("/login", response_model=Token, tags=["auth"])
def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Log in a user and return access and refresh tokens.
    """
    user = fake_users_db.get(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(subject=user["id"])
    refresh_token = security.create_refresh_token(subject=user["id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token, tags=["auth"])
def refresh_access_token(refresh_token: str = Body(..., embed=True)):
    """
    Refresh an access token using a refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=uuid.UUID(user_id_str))
    except (JWTError, ValueError):
        raise credentials_exception

    user = next((u for u in fake_users_db.values() if u["id"] == token_data.sub), None)
    if not user:
        raise credentials_exception

    new_access_token = security.create_access_token(subject=user["id"])
    new_refresh_token = security.create_refresh_token(subject=user["id"]) # Issue a new refresh token for rotation

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserPublic, tags=["auth"])
def read_current_user(current_user: UserPublic = Depends(get_current_user)):
    """
    Get the current logged-in user.
    """
    return current_user
