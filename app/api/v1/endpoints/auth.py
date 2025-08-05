"""
Authentication API Endpoints
Handles user authentication, registration, and session management.
"""
from fastapi import (
    APIRouter, Body, Depends, HTTPException, status, Response, Request, Query
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core import security
from app.core.config import settings
from app.schemas import UserCreate, UserPublic, Token, Message
from app.db.session import get_db
from app.models import User
from app.crud import user as crud_user
from app.api.deps import get_current_active_user, get_current_user
from app.core.limiter import limiter
from app.core.logging import security_logger
from app.services.email_service import email_service

router = APIRouter()

@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def register_user(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    db_user = await crud_user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    user = await crud_user.create(db, obj_in=user_in)
    verification_token = security.generate_verification_token(user.email)
    try:
        await email_service.send_verification_email(
            email_to=user.email,
            token=verification_token
        )
    except Exception as e:
        security_logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
    security_logger.info(f"User registration: {user.email} from IP: {request.client.host}")
    return {"message": "Registration successful. Please check your email to verify your account."}

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Log in a user and return access and refresh tokens.
    """
    user = await crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        security_logger.warning(
            f"Failed login attempt for email: {form_data.username} from IP: {request.client.host}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account."
        )
    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_HOURS * 3600,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    security_logger.info(f"Successful login: {user.email} from IP: {request.client.host}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.get("/me", response_model=UserPublic)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user

@router.get("/verify-email", response_model=Message)
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user email with token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    await crud_user.update(db, db_obj=user, obj_in={"is_verified": True})
    security_logger.info(f"Email verified: {user.email}")
    return {"message": "Email verified successfully. You can now log in."}

@router.post("/request-password-reset", response_model=Message)
@limiter.limit("3/hour")
async def request_password_reset(
    request: Request,
    email: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email.
    """
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent."}
    reset_token = security.generate_password_reset_token(email)
    try:
        await email_service.send_password_reset_email(
            email_to=email,
            token=reset_token
        )
    except Exception as e:
        security_logger.error(f"Failed to send password reset email to {email}: {str(e)}")
    security_logger.info(f"Password reset requested for: {email} from IP: {request.client.host}")
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password", response_model=Message)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password with token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    hashed_password = security.get_password_hash(new_password)
    await crud_user.update(db, db_obj=user, obj_in={"hashed_password": hashed_password})
    security_logger.info(f"Password reset completed for: {user.email}")
    return {"message": "Password has been reset successfully. You can now log in with your new password."}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token from cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        # TODO: Implement Redis denylist check
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    user = await crud_user.get(db, id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    new_access_token = security.create_access_token(subject=user.id)
    new_refresh_token = security.create_refresh_token(subject=user.id)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_HOURS * 3600,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/logout", response_model=Message)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user and invalidate refresh token.
    """
    response.delete_cookie(key="refresh_token")
    # TODO: Add refresh token to denylist in Redis
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            jti = payload.get("jti")
            if jti:
                pass  # TODO: Add to Redis denylist
        except JWTError:
            pass  # Token was invalid anyway
    security_logger.info(f"User logout: {current_user.email} from IP: {request.client.host}")
    return {"message": "Successfully logged out"}
