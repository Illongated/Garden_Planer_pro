from fastapi import APIRouter, Depends

from app.schemas.irrigation import ZoneInput, ZoneOutput, FlowInput, FlowOutput
from app.services import irrigation_planner
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserPublic

router = APIRouter()

@router.post("/zones", response_model=ZoneOutput)
def compute_watering_zones(
    zone_in: ZoneInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Computes optimal watering zones based on plant locations and water needs.
    (Note: The current implementation uses mock logic.)
    """
    return irrigation_planner.calculate_watering_zones(zone_in)


@router.post("/flow", response_model=FlowOutput)
def compute_flow_and_pressure(
    flow_in: FlowInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Computes the required water flow and pressure for a given set of irrigation zones.
    (Note: The current implementation uses mock logic.)
    """
    return irrigation_planner.calculate_flow_and_pressure(flow_in)
