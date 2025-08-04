from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import UserPublic, UserUpdate
from app.db.session import get_db
from models import User
from crud import user as crud_user
from app.api.deps import get_current_active_user

router = APIRouter()

# Authentication endpoints have been moved to auth.py
# This file now only contains user management endpoints (CRUD operations)

@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific user by ID (admin only or own profile).
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile.
    """
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await crud_user.update(db, db_obj=user, obj_in=user_update)
    return updated_user
