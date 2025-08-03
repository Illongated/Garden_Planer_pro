import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio

from app.schemas.irrigation import (
    ZoneInput, ZoneOutput, FlowInput, FlowOutput, WateringZone,
    ClusteringInput, ClusteringResult, HydraulicCalculationInput, HydraulicCalculationResult,
    EquipmentSelectionInput, EquipmentSelectionResult, WeatherForecastInput, WeatherForecastResult,
    CostEstimationInput, CostEstimationResult, IrrigationZone, IrrigationPipe, IrrigationProject
)
from app.services.hydraulic_engine import HydraulicEngine
from app.services.clustering_engine import ClusteringEngine
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class IrrigationPlanner:
    """Comprehensive irrigation planning and design system."""
    
    def __init__(self):
        """Initialize the irrigation planner with all required engines."""
        self.logger = logging.getLogger(__name__)
        self.hydraulic_engine = HydraulicEngine()
        self.clustering_engine = ClusteringEngine()
        self.weather_service = WeatherService()
    
    def calculate_watering_zones(self, zone_input: ZoneInput) -> ZoneOutput:
        """
        Calculate optimal watering zones using advanced clustering.
        
        Args:
            zone_input: Input data with plant locations and water needs
            
        Returns:
            Zone output with optimized zones
        """
        try:
            # Convert to clustering input format
            plants_data = []
            for plant in zone_input.plants:
                plants_data.append({
                    "plant_id": plant.plant_id,
                    "x": plant.x,
                    "y": plant.y,
                    "water_needs": plant.water_needs,
                    "area_m2": 1.0,  # Default area
                    "growth_stage": "vegetative",
                    "crop_coefficient": 0.8
                })
            
            # Perform clustering
            clustering_input = ClusteringInput(
                plants=plants_data,
                max_zones=min(5, len(zone_input.plants)),  # Max 5 zones or number of plants
                min_plants_per_zone=1
            )
            
            clustering_result = self.clustering_engine.perform_clustering(clustering_input)
            
            # Convert to legacy format for backward compatibility
            zones = []
            for i, zone in enumerate(clustering_result.zones):
                watering_zone = WateringZone(
                    zone_id=i + 1,
                    water_needs=zone.status,  # Use status as water needs
                    plant_ids=zone.plant_ids
                )
                zones.append(watering_zone)
            
            return ZoneOutput(zones=zones)
            
        except Exception as e:
            self.logger.error(f"Error calculating watering zones: {e}")
            # Fallback to simple grouping by water needs
            zones_by_needs = {}
            for plant in zone_input.plants:
                if plant.water_needs not in zones_by_needs:
                    zones_by_needs[plant.water_needs] = []
                zones_by_needs[plant.water_needs].append(plant.plant_id)
            
            zones = [
                WateringZone(zone_id=i + 1, water_needs=needs, plant_ids=plant_ids)
                for i, (needs, plant_ids) in enumerate(zones_by_needs.items())
            ]
            
            return ZoneOutput(zones=zones)
    
    def calculate_flow_and_pressure(self, flow_input: FlowInput) -> FlowOutput:
        """
        Calculate flow and pressure using advanced hydraulic calculations.
        
        Args:
            flow_input: Input data with zones and pipe specifications
            
        Returns:
            Flow output with calculated values
        """
        try:
            # Convert to hydraulic calculation input
            zones = []
            for zone in flow_input.zones:
                # Create mock zone for hydraulic calculations
                mock_zone = IrrigationZone(
                    id=f"zone_{zone.zone_id}",
                    name=f"Zone {zone.zone_id}",
                    description="",
                    status="active",
                    required_flow_lph=150,  # Default flow rate
                    operating_pressure_bar=1.5,
                    total_area_m2=10.0,  # Default area
                    cluster_center_x=0.0,
                    cluster_center_y=0.0,
                    plant_ids=zone.plant_ids,
                    estimated_cost=0.0,
                    garden_id=None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                zones.append(mock_zone)
            
            # Create mock pipes for hydraulic calculations
            pipes = []
            for i, zone in enumerate(flow_input.zones):
                mock_pipe = IrrigationPipe(
                    id=f"pipe_{i}",
                    zone_id=f"zone_{zone.zone_id}",
                    pipe_name=f"Pipe {i+1}",
                    pipe_type="lateral",
                    material="pvc",
                    diameter_mm=flow_input.pipe_diameter_mm,
                    length_m=20.0,  # Default length
                    flow_rate_lph=150,
                    velocity_ms=1.0,
                    pressure_loss_bar=0.1,
                    start_x=0.0,
                    start_y=0.0,
                    end_x=10.0,
                    end_y=0.0,
                    cost_per_meter=2.5,
                    total_cost=50.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                pipes.append(mock_pipe)
            
            # Perform hydraulic calculations
            hydraulic_input = HydraulicCalculationInput(
                zones=zones,
                source_pressure_bar=flow_input.source_pressure_bar,
                source_flow_lph=1000,  # Default source flow
                pipe_material="pvc",
                pipe_diameter_mm=flow_input.pipe_diameter_mm
            )
            
            result = self.hydraulic_engine.calculate_network_hydraulics(
                zones=zones,
                pipes=pipes,
                source_pressure_bar=flow_input.source_pressure_bar,
                source_flow_lph=1000
            )
            
            return FlowOutput(
                required_flow_lph=result.total_flow_lph,
                pressure_at_end_bar=result.final_pressure_bar,
                warnings=result.warnings
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating flow and pressure: {e}")
            # Fallback to simple calculations
            num_zones = len(flow_input.zones)
            required_flow = num_zones * 150
            pressure_drop = num_zones * 0.2
            final_pressure = flow_input.source_pressure_bar - pressure_drop
            
            warnings = []
            if final_pressure < 1.0:
                warnings.append("Warning: Pressure at the end of the system is very low.")
            
            return FlowOutput(
                required_flow_lph=required_flow,
                pressure_at_end_bar=final_pressure,
                warnings=warnings
            )
    
    def design_complete_irrigation_system(
        self, 
        garden_id: str,
        plants_data: List[Dict[str, Any]],
        water_source_pressure_bar: float = 2.5,
        water_source_flow_lph: float = 1000,
        max_zones: int = 5,
        budget_constraint: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Design a complete irrigation system for a garden.
        
        Args:
            garden_id: Garden ID
            plants_data: List of plant data with coordinates and water needs
            water_source_pressure_bar: Source pressure in bar
            water_source_flow_lph: Source flow rate in liters per hour
            max_zones: Maximum number of zones
            budget_constraint: Budget constraint in USD
            
        Returns:
            Complete irrigation system design
        """
        try:
            # Step 1: Perform clustering to create zones
            clustering_input = ClusteringInput(
                plants=plants_data,
                max_zones=max_zones,
                min_plants_per_zone=1
            )
            
            clustering_result = self.clustering_engine.perform_clustering(clustering_input)
            
            # Step 2: Optimize equipment selection for each zone
            equipment_selections = []
            for zone in clustering_result.zones:
                equipment_input = EquipmentSelectionInput(
                    zone_area_m2=zone.total_area_m2,
                    water_needs=zone.status,
                    budget_constraint=budget_constraint / len(clustering_result.zones) if budget_constraint else None
                )
                
                equipment_result = self.clustering_engine.optimize_equipment_selection(
                    zone_area_m2=zone.total_area_m2,
                    water_needs=zone.status,
                    budget_constraint=budget_constraint / len(clustering_result.zones) if budget_constraint else None
                )
                equipment_selections.append(equipment_result)
            
            # Step 3: Design pipe network
            pipe_network = self.design_pipe_network(
                zones=clustering_result.zones,
                source_pressure_bar=water_source_pressure_bar,
                source_flow_lph=water_source_flow_lph
            )
            
            # Step 4: Perform hydraulic calculations
            hydraulic_result = self.hydraulic_engine.calculate_network_hydraulics(
                zones=clustering_result.zones,
                pipes=pipe_network,
                source_pressure_bar=water_source_pressure_bar,
                source_flow_lph=water_source_flow_lph
            )
            
            # Step 5: Calculate costs
            cost_result = self.calculate_system_costs(
                zones=clustering_result.zones,
                equipment_selections=equipment_selections,
                pipe_network=pipe_network
            )
            
            # Step 6: Validate system design
            validation_result = self.hydraulic_engine.validate_system_design(
                zones=clustering_result.zones,
                pipes=pipe_network,
                source_pressure_bar=water_source_pressure_bar,
                source_flow_lph=water_source_flow_lph
            )
            
            return {
                "garden_id": garden_id,
                "zones": clustering_result.zones,
                "equipment_selections": equipment_selections,
                "pipe_network": pipe_network,
                "hydraulic_calculations": hydraulic_result,
                "cost_estimation": cost_result,
                "validation": validation_result,
                "clustering_efficiency": clustering_result.efficiency_score,
                "total_cost": cost_result.total_cost,
                "is_system_viable": hydraulic_result.is_system_viable
            }
            
        except Exception as e:
            self.logger.error(f"Error designing irrigation system: {e}")
            raise
    
    def design_pipe_network(
        self, 
        zones: List[IrrigationZone],
        source_pressure_bar: float,
        source_flow_lph: float
    ) -> List[IrrigationPipe]:
        """
        Design optimal pipe network for irrigation zones.
        
        Args:
            zones: List of irrigation zones
            source_pressure_bar: Source pressure in bar
            source_flow_lph: Source flow rate in liters per hour
            
        Returns:
            List of designed pipes
        """
        pipes = []
        
        # Design main line
        total_flow = sum(zone.required_flow_lph for zone in zones)
        main_pipe = self.hydraulic_engine.optimize_pipe_diameter(
            flow_rate_lph=total_flow,
            length_m=50.0,  # Estimated main line length
            material="pvc",
            max_pressure_loss_bar=0.3
        )
        
        main_pipe_obj = IrrigationPipe(
            id="main_pipe",
            zone_id=None,
            pipe_name="Main Line",
            pipe_type="main",
            material="pvc",
            diameter_mm=main_pipe["optimal_diameter_mm"],
            length_m=50.0,
            flow_rate_lph=total_flow,
            velocity_ms=1.0,
            pressure_loss_bar=main_pipe["pressure_loss_bar"],
            start_x=0.0,
            start_y=0.0,
            end_x=50.0,
            end_y=0.0,
            cost_per_meter=2.5,
            total_cost=main_pipe["total_cost"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        pipes.append(main_pipe_obj)
        
        # Design lateral lines for each zone
        for i, zone in enumerate(zones):
            lateral_pipe = self.hydraulic_engine.optimize_pipe_diameter(
                flow_rate_lph=zone.required_flow_lph,
                length_m=20.0,  # Estimated lateral length
                material="pvc",
                max_pressure_loss_bar=0.2
            )
            
            lateral_pipe_obj = IrrigationPipe(
                id=f"lateral_pipe_{i}",
                zone_id=str(zone.id),
                pipe_name=f"Lateral {i+1}",
                pipe_type="lateral",
                material="pvc",
                diameter_mm=lateral_pipe["optimal_diameter_mm"],
                length_m=20.0,
                flow_rate_lph=zone.required_flow_lph,
                velocity_ms=1.0,
                pressure_loss_bar=lateral_pipe["pressure_loss_bar"],
                start_x=50.0,
                start_y=i * 10.0,
                end_x=70.0,
                end_y=i * 10.0,
                cost_per_meter=2.5,
                total_cost=lateral_pipe["total_cost"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            pipes.append(lateral_pipe_obj)
        
        return pipes
    
    def calculate_system_costs(
        self, 
        zones: List[IrrigationZone],
        equipment_selections: List[EquipmentSelectionResult],
        pipe_network: List[IrrigationPipe]
    ) -> CostEstimationResult:
        """
        Calculate comprehensive system costs.
        
        Args:
            zones: List of irrigation zones
            equipment_selections: Equipment selection results
            pipe_network: Pipe network design
            
        Returns:
            Cost estimation result
        """
        # Calculate equipment costs
        equipment_cost = sum(selection.total_cost for selection in equipment_selections)
        
        # Calculate pipe costs
        pipe_cost = sum(pipe.total_cost for pipe in pipe_network)
        
        # Calculate installation costs (estimated as 30% of material costs)
        material_cost = equipment_cost + pipe_cost
        installation_cost = material_cost * 0.3
        
        # Calculate total cost
        total_cost = material_cost + installation_cost
        
        # Calculate ROI estimate (simplified)
        water_savings_per_year = 1000  # USD (estimated)
        roi_estimate = (water_savings_per_year / total_cost) * 100 if total_cost > 0 else 0
        
        cost_breakdown = {
            "equipment": equipment_cost,
            "pipes": pipe_cost,
            "installation": installation_cost,
            "total": total_cost
        }
        
        return CostEstimationResult(
            equipment_cost=equipment_cost,
            pipe_cost=pipe_cost,
            installation_cost=installation_cost,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            roi_estimate=roi_estimate
        )
    
    async def get_weather_based_scheduling(
        self, 
        garden_id: str,
        days_ahead: int = 7
    ) -> WeatherForecastResult:
        """
        Get weather-based irrigation scheduling recommendations.
        
        Args:
            garden_id: Garden ID
            days_ahead: Number of days to forecast
            
        Returns:
            Weather forecast and irrigation recommendations
        """
        weather_input = WeatherForecastInput(
            garden_id=garden_id,
            days_ahead=days_ahead
        )
        
        return await self.weather_service.get_weather_forecast(weather_input)
    
    def optimize_irrigation_schedule(
        self, 
        zones: List[IrrigationZone],
        weather_forecast: WeatherForecastResult,
        water_availability_hours: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Optimize irrigation schedule based on weather forecast and water availability.
        
        Args:
            zones: List of irrigation zones
            weather_forecast: Weather forecast data
            water_availability_hours: Hours of water availability per day
            
        Returns:
            Optimized irrigation schedules
        """
        schedules = []
        
        # Group recommendations by date
        recommendations_by_date = {}
        for rec in weather_forecast.irrigation_recommendations:
            date_str = rec["date"].strftime("%Y-%m-%d")
            if date_str not in recommendations_by_date:
                recommendations_by_date[date_str] = []
            recommendations_by_date[date_str].append(rec)
        
        # Create schedules for each zone
        for zone in zones:
            zone_schedules = []
            
            for date_str, day_recommendations in recommendations_by_date.items():
                # Find the recommendation for this date
                day_rec = next((r for r in day_recommendations if r["recommendation"] == "irrigate"), None)
                
                if day_rec:
                    # Calculate optimal duration based on zone needs
                    base_duration = day_rec["duration_minutes"]
                    zone_factor = zone.required_flow_lph / 150  # Normalize to standard flow
                    optimal_duration = int(base_duration * zone_factor)
                    
                    # Distribute across available hours
                    start_hour = 6  # Start at 6 AM
                    duration_hours = min(optimal_duration / 60, water_availability_hours)
                    
                    schedule = {
                        "zone_id": str(zone.id),
                        "zone_name": zone.name,
                        "date": date_str,
                        "start_time": f"{start_hour:02d}:00",
                        "duration_minutes": optimal_duration,
                        "duration_hours": duration_hours,
                        "reason": day_rec["reason"],
                        "irrigation_need_mm": day_rec["irrigation_need_mm"]
                    }
                    zone_schedules.append(schedule)
            
            schedules.extend(zone_schedules)
        
        return schedules
    
    def generate_technical_report(
        self, 
        system_design: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive technical report for irrigation system.
        
        Args:
            system_design: Complete irrigation system design
            
        Returns:
            Technical report data
        """
        zones = system_design["zones"]
        hydraulic_calc = system_design["hydraulic_calculations"]
        cost_est = system_design["cost_estimation"]
        validation = system_design["validation"]
        
        report = {
            "system_overview": {
                "total_zones": len(zones),
                "total_area_m2": sum(zone.total_area_m2 for zone in zones),
                "total_flow_lph": hydraulic_calc.total_flow_lph,
                "system_pressure_bar": hydraulic_calc.final_pressure_bar,
                "is_system_viable": hydraulic_calc.is_system_viable
            },
            "zone_details": [
                {
                    "zone_id": str(zone.id),
                    "name": zone.name,
                    "area_m2": zone.total_area_m2,
                    "required_flow_lph": zone.required_flow_lph,
                    "operating_pressure_bar": zone.operating_pressure_bar,
                    "plant_count": len(zone.plant_ids),
                    "estimated_cost": zone.estimated_cost
                }
                for zone in zones
            ],
            "hydraulic_analysis": {
                "total_pressure_loss_bar": hydraulic_calc.total_pressure_loss_bar,
                "average_velocity_ms": hydraulic_calc.velocity_ms,
                "reynolds_number": hydraulic_calc.reynolds_number,
                "friction_factor": hydraulic_calc.friction_factor,
                "warnings": hydraulic_calc.warnings
            },
            "cost_analysis": {
                "equipment_cost": cost_est.equipment_cost,
                "pipe_cost": cost_est.pipe_cost,
                "installation_cost": cost_est.installation_cost,
                "total_cost": cost_est.total_cost,
                "roi_estimate": cost_est.roi_estimate,
                "cost_breakdown": cost_est.cost_breakdown
            },
            "validation_results": {
                "is_valid": validation["is_valid"],
                "warnings": validation["warnings"],
                "errors": validation["errors"],
                "recommendations": validation["recommendations"]
            },
            "efficiency_metrics": {
                "clustering_efficiency": system_design["clustering_efficiency"],
                "hydraulic_efficiency": 1 - (hydraulic_calc.total_pressure_loss_bar / 2.5),
                "cost_efficiency": 1000 / cost_est.total_cost if cost_est.total_cost > 0 else 0
            }
        }
        
        return report
