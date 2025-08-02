import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app.core.config import settings

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# --- Password Hashing Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Timed Serializer for Tokens (Email Verification, Password Reset) ---
# This uses a different secret than JWTs for better security separation.
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# --- JWT Creation ---
def create_token(subject: Union[str, Any], expires_delta: timedelta, token_type: str, jti: str | None = None) -> str:
    """
    Creates a JWT token with a specified subject, expiration, type, and optional JTI.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,
    }
    if jti:
        to_encode["jti"] = jti

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_access_token(subject: Union[str, Any]) -> str:
    """
    Creates a new access token.
    """
    return create_token(
        subject,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )

def create_refresh_token(subject: Union[str, Any]) -> tuple[str, str]:
    """
    Creates a new refresh token and its JTI.
    """
    jti = str(uuid.uuid4())
    token = create_token(
        subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
        jti=jti
    )
    return token, jti

# --- Password and Token Verification ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.
    """
    return pwd_context.hash(password)

def generate_verification_token(email: str) -> str:
    """
    Generates a time-limited token for email verification.
    """
    return serializer.dumps(email, salt='email-verification-salt')

def verify_verification_token(token: str, max_age_seconds: int = 3600) -> str | None:
    """
    Verifies a time-limited token and returns the email if valid.
    """
    try:
        return serializer.loads(
            token,
            salt='email-verification-salt',
            max_age=max_age_seconds
        )
    except (SignatureExpired, BadTimeSignature):
        return None
