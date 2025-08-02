import uuid
from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_csrf_protect import CsrfProtect

from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate, UserPublic, PasswordReset
from app.schemas.token import Token, TokenPayload
from app.schemas.message import Message
from app.db.session import get_db
from app.models.user import User
from app.crud import user as crud_user
from app.services.redis_service import RedisService
from app.services.email_service import send_verification_email, send_password_reset_email
from app.core.limiter import limiter
from app.core.logging import security_logger

router = APIRouter()

# --- Dependencies ---

async def get_redis_service(request: Request) -> RedisService:
    return RedisService(request.app.state.redis)

async def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from a token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=uuid.UUID(user_id_str))
    except JWTError:
        raise credentials_exception

    user = await crud_user.get_user_by_id(db, user_id=token_data.sub)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_active_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to get the current active and verified user.
    """
    if not current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified. Please check your inbox.")
    return current_user


@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def register_user(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and send a verification email.
    """
    db_user = await crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    user = await crud_user.create_user(db, user_in=user_in)

    # Send verification email
    token = security.generate_verification_token(user.email)
    await send_verification_email(email_to=user.email, token=token)

    return {"message": "Registration successful. Please check your email to verify your account."}

@router.get("/verify-email", response_model=Message)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify a user's email address from the token sent to them.
    """
    email = security.verify_verification_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")

    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if user.is_verified:
        return {"message": "Email already verified."}

    user.is_verified = True
    await db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login")
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    csrf_protect: CsrfProtect = Depends()
):
    """
    Log in a user and return tokens.
    Access token is in the response body.
    Refresh token is in an HttpOnly cookie.
    """
    user = await crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        security_logger.warning(
            f"Failed login attempt for email: {form_data.username} from IP: {request.client.host}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified. Please check your inbox.")

    access_token = security.create_access_token(subject=user.id)
    refresh_token, jti = security.create_refresh_token(subject=user.id)

    content = {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    response = JSONResponse(content=content)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", response_model=Message)
async def logout(
    response: Response,
    request: Request,
    redis_service: RedisService = Depends(get_redis_service),
):
    """
    Log out a user by invalidating their refresh token.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            jti = payload.get("jti")
            if jti:
                await redis_service.add_jti_to_denylist(jti, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        except JWTError:
            # If token is invalid, we can just ignore it.
            pass

    # Clear the cookie
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
    csrf_protect: CsrfProtect = Depends()
):
    """
    Refresh the access token using the refresh token from the cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        jti = payload.get("jti")

        if token_type != "refresh" or not jti:
            raise credentials_exception

        if await redis_service.is_jti_in_denylist(jti):
            raise credentials_exception

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=uuid.UUID(user_id_str))
    except JWTError:
        raise credentials_exception

    user = await crud_user.get_user_by_id(db, user_id=token_data.sub)
    if not user or not user.is_active:
        raise credentials_exception

    new_access_token = security.create_access_token(subject=user.id)

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/request-password-reset", response_model=Message)
@limiter.limit("5/minute")
async def request_password_reset(
    request: Request,
    email_body: dict = Body(..., example={"email": "user@example.com"}),
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset. Sends an email with a reset link.
    """
    email = email_body.get("email")
    user = await crud_user.get_user_by_email(db, email=email)
    if user:
        # To prevent user enumeration, we don't reveal if the user was found.
        # We just send the email if they exist.
        token = security.generate_verification_token(email)
        await send_password_reset_email(email_to=email, token=token)

    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password", response_model=Message)
async def reset_password(body: PasswordReset, db: AsyncSession = Depends(get_db)):
    """
    Reset a user's password using the token from the reset link.
    """
    email = security.verify_verification_token(body.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")

    user = await crud_user.get_user_by_email(db, email=email)
    if not user:
        # This case should ideally not be reached if the token is valid, but as a safeguard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.hashed_password = security.get_password_hash(body.new_password)
    await db.commit()

    return {"message": "Password has been reset successfully."}

@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: User = Depends(get_current_active_verified_user)):
    """
    Get the current logged-in, active, and verified user.
    """
    return current_user
