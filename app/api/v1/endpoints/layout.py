from fastapi import APIRouter, Depends

from schemas.layout import LayoutInput, LayoutOutput
from services import layout_optimizer
from api.v1.endpoints.auth import get_current_user
from schemas.user import UserPublic

router = APIRouter()

@router.post("/optimize", response_model=LayoutOutput)
def optimize_garden_layout(
    layout_in: LayoutInput,
    current_user: UserPublic = Depends(get_current_user), # Ensures the endpoint is protected
):
    """
    Receives garden dimensions and plant positions, and returns an optimized layout.

    The optimization considers plant spacing and companion/antagonist relationships.
    (Note: The current implementation uses mock logic.)
    """
    # In a real app, you might associate the layout with a user's project
    # and pass the current_user to the service layer.
    optimized_layout = layout_optimizer.optimize_layout(layout_in)
    return optimized_layout
