from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import base64
from datetime import datetime

from app.schemas.irrigation import (
    ZoneInput, ZoneOutput, FlowInput, FlowOutput, WateringZone,
    ClusteringInput, ClusteringResult, HydraulicCalculationInput, HydraulicCalculationResult,
    EquipmentSelectionInput, EquipmentSelectionResult, WeatherForecastInput, WeatherForecastResult,
    CostEstimationInput, CostEstimationResult, IrrigationZone, IrrigationPipe, IrrigationProject,
    IrrigationZoneCreate, IrrigationZoneUpdate, IrrigationZone as IrrigationZoneSchema,
    IrrigationEquipmentCreate, IrrigationEquipmentUpdate, IrrigationEquipment as IrrigationEquipmentSchema,
    IrrigationScheduleCreate, IrrigationScheduleUpdate, IrrigationSchedule as IrrigationScheduleSchema,
    WeatherDataCreate, WeatherData as WeatherDataSchema, IrrigationProjectCreate, IrrigationProjectUpdate,
    IrrigationProject as IrrigationProjectSchema
)
from app.services.irrigation_planner import IrrigationPlanner
from app.services.hydraulic_engine import HydraulicEngine
from app.services.clustering_engine import ClusteringEngine
from app.services.weather_service import WeatherService
from app.services.technical_export import TechnicalExportService
from app.api.deps import get_current_user, get_db
from app.schemas.user import UserPublic
from app.crud.irrigation import (
    irrigation_zone_crud, irrigation_equipment_crud, irrigation_schedule_crud,
    weather_data_crud, irrigation_project_crud
)

router = APIRouter()

# Initialize services
irrigation_planner = IrrigationPlanner()
hydraulic_engine = HydraulicEngine()
clustering_engine = ClusteringEngine()
weather_service = WeatherService()
technical_export_service = TechnicalExportService()


# Legacy endpoints for backward compatibility
@router.post("/zones", response_model=ZoneOutput)
def compute_watering_zones(
    zone_in: ZoneInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Computes optimal watering zones based on plant locations and water needs.
    Uses advanced clustering algorithms for optimal zone design.
    """
    return irrigation_planner.calculate_watering_zones(zone_in)


@router.post("/flow", response_model=FlowOutput)
def compute_flow_and_pressure(
    flow_in: FlowInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Computes the required water flow and pressure for a given set of irrigation zones.
    Uses advanced hydraulic calculations with Darcy-Weisbach equations.
    """
    return irrigation_planner.calculate_flow_and_pressure(flow_in)


# Advanced clustering endpoints
@router.post("/clustering", response_model=ClusteringResult)
def perform_plant_clustering(
    clustering_input: ClusteringInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Perform advanced plant clustering for optimal irrigation zone design.
    Uses K-means clustering with multiple features including water needs and spatial distribution.
    """
    return clustering_engine.perform_clustering(clustering_input)


# Hydraulic calculation endpoints
@router.post("/hydraulics", response_model=HydraulicCalculationResult)
def calculate_hydraulics(
    hydraulic_input: HydraulicCalculationInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Perform comprehensive hydraulic calculations for irrigation systems.
    Includes Darcy-Weisbach equations, Reynolds number calculations, and pressure loss analysis.
    """
    return hydraulic_engine.calculate_network_hydraulics(
        zones=hydraulic_input.zones,
        pipes=[],  # Will be generated from zones
        source_pressure_bar=hydraulic_input.source_pressure_bar,
        source_flow_lph=hydraulic_input.source_flow_lph
    )


# Equipment selection endpoints
@router.post("/equipment-selection", response_model=EquipmentSelectionResult)
def select_optimal_equipment(
    equipment_input: EquipmentSelectionInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Select optimal irrigation equipment based on zone requirements and constraints.
    Considers coverage efficiency, cost, and water needs.
    """
    return clustering_engine.optimize_equipment_selection(
        zone_area_m2=equipment_input.zone_area_m2,
        water_needs=equipment_input.water_needs,
        budget_constraint=equipment_input.budget_constraint,
        preferred_equipment_type=equipment_input.preferred_equipment_type
    )


# Weather integration endpoints
@router.post("/weather-forecast", response_model=WeatherForecastResult)
async def get_weather_forecast(
    weather_input: WeatherForecastInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Get weather forecast and irrigation scheduling recommendations.
    Integrates with external weather APIs for real-time data.
    """
    return await weather_service.get_weather_forecast(weather_input)


# Complete system design endpoint
@router.post("/design-system")
def design_complete_irrigation_system(
    garden_id: str,
    plants_data: List[Dict[str, Any]],
    water_source_pressure_bar: float = 2.5,
    water_source_flow_lph: float = 1000,
    max_zones: int = 5,
    budget_constraint: Optional[float] = None,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Design a complete irrigation system for a garden.
    Includes clustering, equipment selection, pipe network design, and cost estimation.
    """
    try:
        system_design = irrigation_planner.design_complete_irrigation_system(
            garden_id=garden_id,
            plants_data=plants_data,
            water_source_pressure_bar=water_source_pressure_bar,
            water_source_flow_lph=water_source_flow_lph,
            max_zones=max_zones,
            budget_constraint=budget_constraint
        )
        return system_design
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"System design failed: {str(e)}")


# Cost estimation endpoint
@router.post("/cost-estimation", response_model=CostEstimationResult)
def estimate_system_costs(
    cost_input: CostEstimationInput,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Estimate comprehensive costs for irrigation system.
    Includes equipment, pipes, installation, and ROI calculations.
    """
    return irrigation_planner.calculate_system_costs(
        zones=cost_input.zones,
        equipment_selections=cost_input.equipment_selections,
        pipe_network=cost_input.pipe_network
    )


# Technical report generation
@router.post("/technical-report")
def generate_technical_report(
    system_design: Dict[str, Any],
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Generate comprehensive technical report for irrigation system.
    Includes hydraulic analysis, cost breakdown, and efficiency metrics.
    """
    return irrigation_planner.generate_technical_report(system_design)


# Irrigation Zone CRUD endpoints
@router.post("/zones", response_model=IrrigationZoneSchema)
def create_irrigation_zone(
    zone_in: IrrigationZoneCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Create a new irrigation zone."""
    return irrigation_zone_crud.create_zone(db=db, zone_in=zone_in)


@router.get("/zones", response_model=List[IrrigationZoneSchema])
def get_irrigation_zones(
    garden_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get irrigation zones with optional filtering."""
    return irrigation_zone_crud.get_zones(
        db=db, garden_id=garden_id, skip=skip, limit=limit
    )


@router.get("/zones/{zone_id}", response_model=IrrigationZoneSchema)
def get_irrigation_zone(
    zone_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get a specific irrigation zone."""
    zone = irrigation_zone_crud.get_zone(db=db, zone_id=zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")
    return zone


@router.put("/zones/{zone_id}", response_model=IrrigationZoneSchema)
def update_irrigation_zone(
    zone_id: UUID,
    zone_in: IrrigationZoneUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Update an irrigation zone."""
    zone = irrigation_zone_crud.update_zone(
        db=db, zone_id=zone_id, zone_in=zone_in
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")
    return zone


@router.delete("/zones/{zone_id}")
def delete_irrigation_zone(
    zone_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Delete an irrigation zone."""
    success = irrigation_zone_crud.delete_zone(db=db, zone_id=zone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Irrigation zone not found")
    return {"message": "Irrigation zone deleted successfully"}


# Irrigation Equipment CRUD endpoints
@router.post("/equipment", response_model=IrrigationEquipmentSchema)
def create_irrigation_equipment(
    equipment_in: IrrigationEquipmentCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Create new irrigation equipment."""
    return irrigation_equipment_crud.create_equipment(db=db, equipment_in=equipment_in)


@router.get("/equipment", response_model=List[IrrigationEquipmentSchema])
def get_irrigation_equipment(
    equipment_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get irrigation equipment with optional filtering."""
    return irrigation_equipment_crud.get_equipment(
        db=db, equipment_type=equipment_type, skip=skip, limit=limit
    )


@router.get("/equipment/{equipment_id}", response_model=IrrigationEquipmentSchema)
def get_irrigation_equipment_by_id(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get specific irrigation equipment."""
    equipment = irrigation_equipment_crud.get_equipment_by_id(
        db=db, equipment_id=equipment_id
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Irrigation equipment not found")
    return equipment


@router.put("/equipment/{equipment_id}", response_model=IrrigationEquipmentSchema)
def update_irrigation_equipment(
    equipment_id: UUID,
    equipment_in: IrrigationEquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Update irrigation equipment."""
    equipment = irrigation_equipment_crud.update_equipment(
        db=db, equipment_id=equipment_id, equipment_in=equipment_in
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Irrigation equipment not found")
    return equipment


@router.delete("/equipment/{equipment_id}")
def delete_irrigation_equipment(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Delete irrigation equipment."""
    success = irrigation_equipment_crud.delete_equipment(db=db, equipment_id=equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Irrigation equipment not found")
    return {"message": "Irrigation equipment deleted successfully"}


# Irrigation Schedule CRUD endpoints
@router.post("/schedules", response_model=IrrigationScheduleSchema)
def create_irrigation_schedule(
    schedule_in: IrrigationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Create new irrigation schedule."""
    return irrigation_schedule_crud.create_schedule(db=db, schedule_in=schedule_in)


@router.get("/schedules", response_model=List[IrrigationScheduleSchema])
def get_irrigation_schedules(
    zone_id: Optional[UUID] = None,
    schedule_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get irrigation schedules with optional filtering."""
    return irrigation_schedule_crud.get_schedules(
        db=db, zone_id=zone_id, schedule_type=schedule_type, skip=skip, limit=limit
    )


@router.get("/schedules/{schedule_id}", response_model=IrrigationScheduleSchema)
def get_irrigation_schedule_by_id(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get specific irrigation schedule."""
    schedule = irrigation_schedule_crud.get_schedule_by_id(
        db=db, schedule_id=schedule_id
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Irrigation schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", response_model=IrrigationScheduleSchema)
def update_irrigation_schedule(
    schedule_id: UUID,
    schedule_in: IrrigationScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Update irrigation schedule."""
    schedule = irrigation_schedule_crud.update_schedule(
        db=db, schedule_id=schedule_id, schedule_in=schedule_in
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Irrigation schedule not found")
    return schedule


@router.delete("/schedules/{schedule_id}")
def delete_irrigation_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Delete irrigation schedule."""
    success = irrigation_schedule_crud.delete_schedule(db=db, schedule_id=schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Irrigation schedule not found")
    return {"message": "Irrigation schedule deleted successfully"}


# Weather Data endpoints
@router.post("/weather-data", response_model=WeatherDataSchema)
def create_weather_data(
    weather_in: WeatherDataCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Create new weather data entry."""
    return weather_data_crud.create_weather_data(db=db, weather_in=weather_in)


@router.get("/weather-data", response_model=List[WeatherDataSchema])
def get_weather_data(
    garden_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get weather data with optional filtering."""
    return weather_data_crud.get_weather_data(
        db=db, garden_id=garden_id, start_date=start_date, 
        end_date=end_date, skip=skip, limit=limit
    )


# Irrigation Project endpoints
@router.post("/projects", response_model=IrrigationProjectSchema)
def create_irrigation_project(
    project_in: IrrigationProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Create new irrigation project."""
    return irrigation_project_crud.create_project(db=db, project_in=project_in)


@router.get("/projects", response_model=List[IrrigationProjectSchema])
def get_irrigation_projects(
    garden_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get irrigation projects with optional filtering."""
    return irrigation_project_crud.get_projects(
        db=db, garden_id=garden_id, is_active=is_active, skip=skip, limit=limit
    )


@router.get("/projects/{project_id}", response_model=IrrigationProjectSchema)
def get_irrigation_project_by_id(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get specific irrigation project."""
    project = irrigation_project_crud.get_project_by_id(
        db=db, project_id=project_id
    )
    if not project:
        raise HTTPException(status_code=404, detail="Irrigation project not found")
    return project


@router.put("/projects/{project_id}", response_model=IrrigationProjectSchema)
def update_irrigation_project(
    project_id: UUID,
    project_in: IrrigationProjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Update irrigation project."""
    project = irrigation_project_crud.update_project(
        db=db, project_id=project_id, project_in=project_in
    )
    if not project:
        raise HTTPException(status_code=404, detail="Irrigation project not found")
    return project


@router.delete("/projects/{project_id}")
def delete_irrigation_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
):
    """Delete irrigation project."""
    success = irrigation_project_crud.delete_project(db=db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Irrigation project not found")
    return {"message": "Irrigation project deleted successfully"}


# Advanced analysis endpoints
@router.post("/optimize-schedule")
def optimize_irrigation_schedule(
    zones: List[IrrigationZone],
    weather_forecast: WeatherForecastResult,
    water_availability_hours: int = 6,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Optimize irrigation schedule based on weather forecast and water availability.
    """
    return irrigation_planner.optimize_irrigation_schedule(
        zones=zones,
        weather_forecast=weather_forecast,
        water_availability_hours=water_availability_hours
    )


@router.post("/validate-system")
def validate_irrigation_system(
    zones: List[IrrigationZone],
    pipes: List[IrrigationPipe],
    source_pressure_bar: float,
    source_flow_lph: float,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Validate irrigation system design for viability and efficiency.
    """
    return hydraulic_engine.validate_system_design(
        zones=zones,
        pipes=pipes,
        source_pressure_bar=source_pressure_bar,
        source_flow_lph=source_flow_lph
    )


@router.post("/optimize-pipe-diameter")
def optimize_pipe_diameter(
    flow_rate_lph: float,
    length_m: float,
    material: str = "pvc",
    max_pressure_loss_bar: float = 0.5,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Optimize pipe diameter for minimum cost while meeting pressure constraints.
    """
    return hydraulic_engine.optimize_pipe_diameter(
        flow_rate_lph=flow_rate_lph,
        length_m=length_m,
        material=material,
        max_pressure_loss_bar=max_pressure_loss_bar
    )


# Technical Export endpoints
@router.post("/export/pdf")
def export_pdf_technical_report(
    garden_id: str,
    system_design: Dict[str, Any],
    project_name: str = "Irrigation System Design",
    include_drawings: bool = True,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Generate a comprehensive PDF technical report for an irrigation system.
    Includes executive summary, hydraulic calculations, equipment specifications,
    cost analysis, installation guidelines, and maintenance schedule.
    """
    try:
        pdf_content = technical_export_service.generate_pdf_technical_report(
            garden_id=garden_id,
            system_design=system_design,
            project_name=project_name,
            include_drawings=include_drawings
        )
        
        return {
            "pdf_content": base64.b64encode(pdf_content).decode('utf-8'),
            "filename": f"irrigation_technical_report_{garden_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "content_type": "application/pdf",
            "size_bytes": len(pdf_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/export/svg/layout")
def export_svg_system_layout(
    system_design: Dict[str, Any],
    width: int = 800,
    height: int = 600,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Generate an SVG technical drawing of the irrigation system layout.
    Shows zones, equipment placement, and system overview.
    """
    try:
        svg_content = technical_export_service.generate_svg_technical_drawing(
            system_design=system_design,
            width=width,
            height=height
        )
        
        return {
            "svg_content": svg_content,
            "filename": f"irrigation_system_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
            "content_type": "image/svg+xml",
            "width": width,
            "height": height
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")


@router.post("/export/svg/pipe-network")
def export_svg_pipe_network(
    system_design: Dict[str, Any],
    width: int = 800,
    height: int = 600,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Generate a detailed SVG of the pipe network with flow directions.
    Shows main and secondary pipes, valves, and flow arrows.
    """
    try:
        svg_content = technical_export_service.generate_svg_pipe_network(
            system_design=system_design,
            width=width,
            height=height
        )
        
        return {
            "svg_content": svg_content,
            "filename": f"irrigation_pipe_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
            "content_type": "image/svg+xml",
            "width": width,
            "height": height
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")


@router.post("/export/technical-plans")
def export_complete_technical_plans(
    garden_id: str,
    system_design: Dict[str, Any],
    project_name: str = "Irrigation System Design",
    include_pdf: bool = True,
    include_svg_layout: bool = True,
    include_svg_pipe_network: bool = True,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Generate complete technical plans including PDF report and SVG drawings.
    Returns all requested formats in a single response.
    """
    try:
        exports = {}
        
        if include_pdf:
            pdf_content = technical_export_service.generate_pdf_technical_report(
                garden_id=garden_id,
                system_design=system_design,
                project_name=project_name,
                include_drawings=True
            )
            exports["pdf"] = {
                "content": base64.b64encode(pdf_content).decode('utf-8'),
                "filename": f"irrigation_technical_report_{garden_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "content_type": "application/pdf",
                "size_bytes": len(pdf_content)
            }
        
        if include_svg_layout:
            svg_layout = technical_export_service.generate_svg_technical_drawing(
                system_design=system_design,
                width=800,
                height=600
            )
            exports["svg_layout"] = {
                "content": svg_layout,
                "filename": f"irrigation_system_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                "content_type": "image/svg+xml"
            }
        
        if include_svg_pipe_network:
            svg_pipe_network = technical_export_service.generate_svg_pipe_network(
                system_design=system_design,
                width=800,
                height=600
            )
            exports["svg_pipe_network"] = {
                "content": svg_pipe_network,
                "filename": f"irrigation_pipe_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                "content_type": "image/svg+xml"
            }
        
        return {
            "garden_id": garden_id,
            "project_name": project_name,
            "exports": exports,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Technical plan generation failed: {str(e)}")
