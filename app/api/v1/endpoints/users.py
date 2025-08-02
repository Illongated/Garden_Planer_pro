from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.schemas import UserCreate, UserPublic, Token, Message
from app.db.session import get_db
from app.models import User
from app.crud import user as crud_user
from app.api.deps import get_current_active_user, get_current_user
from app.core.limiter import limiter
from app.core.logging import security_logger

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
    return {"message": f"User {user.email} registered successfully."}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Log in a user and return an access token.
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": "not_implemented"}


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Get the current logged-in user.
    """
    return current_user
