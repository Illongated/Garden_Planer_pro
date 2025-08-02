from fastapi import APIRouter, Depends
from .... import models, schemas
from ..deps import get_current_active_user

router = APIRouter()

@router.get("/users/me", response_model=schemas.User)
def read_users_me(
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user
