import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import cdist

from schemas.irrigation import (
    HydraulicCalculationInput, HydraulicCalculationResult,
    PipeMaterial, IrrigationZone, IrrigationPipe
)

logger = logging.getLogger(__name__)


class FlowRegime(str, Enum):
    """Flow regime classification."""
    LAMINAR = "laminar"
    TRANSITIONAL = "transitional"
    TURBULENT = "turbulent"


@dataclass
class PipeProperties:
    """Physical properties of pipes."""
    material: PipeMaterial
    diameter_mm: float
    roughness_mm: float
    cost_per_meter: float
    
    @property
    def diameter_m(self) -> float:
        """Convert diameter from mm to meters."""
        return self.diameter_mm / 1000.0
    
    @property
    def roughness_m(self) -> float:
        """Convert roughness from mm to meters."""
        return self.roughness_mm / 1000.0


class HydraulicEngine:
    """Advanced hydraulic calculation engine for irrigation systems."""
    
    # Physical constants
    GRAVITY = 9.81  # m/s²
    WATER_DENSITY = 998.2  # kg/m³ at 20°C
    WATER_VISCOSITY = 1.002e-3  # Pa·s at 20°C
    
    # Pipe material properties (roughness in mm)
    PIPE_PROPERTIES = {
        PipeMaterial.PVC: {"roughness_mm": 0.0015, "cost_per_meter": 2.5},
        PipeMaterial.PE: {"roughness_mm": 0.007, "cost_per_meter": 3.2},
        PipeMaterial.PEX: {"roughness_mm": 0.007, "cost_per_meter": 4.8},
        PipeMaterial.COPPER: {"roughness_mm": 0.0015, "cost_per_meter": 12.0},
    }
    
    def __init__(self):
        """Initialize the hydraulic engine."""
        self.logger = logging.getLogger(__name__)
    
    def calculate_reynolds_number(self, velocity_ms: float, diameter_m: float) -> float:
        """
        Calculate Reynolds number for flow regime determination.
        
        Args:
            velocity_ms: Flow velocity in m/s
            diameter_m: Pipe diameter in meters
            
        Returns:
            Reynolds number (dimensionless)
        """
        return (self.WATER_DENSITY * velocity_ms * diameter_m) / self.WATER_VISCOSITY
    
    def determine_flow_regime(self, reynolds_number: float) -> FlowRegime:
        """
        Determine flow regime based on Reynolds number.
        
        Args:
            reynolds_number: Reynolds number
            
        Returns:
            Flow regime classification
        """
        if reynolds_number < 2300:
            return FlowRegime.LAMINAR
        elif reynolds_number < 4000:
            return FlowRegime.TRANSITIONAL
        else:
            return FlowRegime.TURBULENT
    
    def calculate_friction_factor(self, reynolds_number: float, relative_roughness: float) -> float:
        """
        Calculate Darcy friction factor using Colebrook-White equation.
        
        Args:
            reynolds_number: Reynolds number
            relative_roughness: Relative roughness (roughness/diameter)
            
        Returns:
            Darcy friction factor
        """
        if reynolds_number < 2300:
            # Laminar flow: f = 64/Re
            return 64.0 / reynolds_number
        
        # Turbulent flow: Colebrook-White equation
        def colebrook(f):
            return 1 / math.sqrt(f) + 2 * math.log10(relative_roughness / 3.7 + 2.51 / (reynolds_number * math.sqrt(f)))
        
        # Initial guess using Swamee-Jain approximation
        f_guess = 0.25 / (math.log10(relative_roughness / 3.7 + 5.74 / (reynolds_number ** 0.9))) ** 2
        
        try:
            result = minimize_scalar(lambda f: abs(colebrook(f)), bounds=(0.001, 0.1), method='bounded')
            return result.x
        except:
            # Fallback to Swamee-Jain approximation
            return f_guess
    
    def calculate_pressure_loss_darcy_weisbach(
        self, 
        flow_rate_lph: float, 
        diameter_m: float, 
        length_m: float, 
        roughness_m: float
    ) -> Tuple[float, float, float, float]:
        """
        Calculate pressure loss using Darcy-Weisbach equation.
        
        Args:
            flow_rate_lph: Flow rate in liters per hour
            diameter_m: Pipe diameter in meters
            length_m: Pipe length in meters
            roughness_m: Pipe roughness in meters
            
        Returns:
            Tuple of (pressure_loss_bar, velocity_ms, reynolds_number, friction_factor)
        """
        # Convert flow rate from LPH to m³/s
        flow_rate_m3s = flow_rate_lph / (1000 * 3600)
        
        # Calculate cross-sectional area
        area_m2 = math.pi * (diameter_m / 2) ** 2
        
        # Calculate velocity
        velocity_ms = flow_rate_m3s / area_m2
        
        # Calculate Reynolds number
        reynolds_number = self.calculate_reynolds_number(velocity_ms, diameter_m)
        
        # Calculate friction factor
        relative_roughness = roughness_m / diameter_m
        friction_factor = self.calculate_friction_factor(reynolds_number, relative_roughness)
        
        # Calculate pressure loss using Darcy-Weisbach equation
        # ΔP = f * (L/D) * (ρv²/2)
        pressure_loss_pa = friction_factor * (length_m / diameter_m) * (self.WATER_DENSITY * velocity_ms ** 2) / 2
        
        # Convert to bar
        pressure_loss_bar = pressure_loss_pa / 100000
        
        return pressure_loss_bar, velocity_ms, reynolds_number, friction_factor
    
    def calculate_minor_losses(self, flow_rate_lph: float, diameter_m: float, k_factors: List[float]) -> float:
        """
        Calculate minor losses from fittings and valves.
        
        Args:
            flow_rate_lph: Flow rate in liters per hour
            diameter_m: Pipe diameter in meters
            k_factors: List of K-factors for fittings
            
        Returns:
            Minor pressure loss in bar
        """
        # Convert flow rate from LPH to m³/s
        flow_rate_m3s = flow_rate_lph / (1000 * 3600)
        
        # Calculate cross-sectional area
        area_m2 = math.pi * (diameter_m / 2) ** 2
        
        # Calculate velocity
        velocity_ms = flow_rate_m3s / area_m2
        
        # Calculate minor losses
        # ΔP = Σ(K * ρv²/2)
        total_k = sum(k_factors)
        pressure_loss_pa = total_k * (self.WATER_DENSITY * velocity_ms ** 2) / 2
        
        # Convert to bar
        pressure_loss_bar = pressure_loss_pa / 100000
        
        return pressure_loss_bar
    
    def optimize_pipe_diameter(
        self, 
        flow_rate_lph: float, 
        length_m: float, 
        material: PipeMaterial,
        max_pressure_loss_bar: float = 0.5
    ) -> Dict[str, Any]:
        """
        Optimize pipe diameter for minimum cost while meeting pressure constraints.
        
        Args:
            flow_rate_lph: Required flow rate in liters per hour
            length_m: Pipe length in meters
            material: Pipe material
            max_pressure_loss_bar: Maximum allowable pressure loss in bar
            
        Returns:
            Dictionary with optimization results
        """
        pipe_props = self.PIPE_PROPERTIES[material]
        roughness_mm = pipe_props["roughness_mm"]
        cost_per_meter = pipe_props["cost_per_meter"]
        
        # Available standard diameters (mm)
        standard_diameters = [13, 16, 20, 25, 32, 40, 50, 63, 75, 90, 110]
        
        best_diameter = None
        best_cost = float('inf')
        best_pressure_loss = float('inf')
        
        for diameter_mm in standard_diameters:
            diameter_m = diameter_mm / 1000.0
            roughness_m = roughness_mm / 1000.0
            
            try:
                pressure_loss_bar, velocity_ms, reynolds_number, friction_factor = self.calculate_pressure_loss_darcy_weisbach(
                    flow_rate_lph, diameter_m, length_m, roughness_m
                )
                
                # Add minor losses (estimated 10% of major losses)
                minor_losses = pressure_loss_bar * 0.1
                total_pressure_loss = pressure_loss_bar + minor_losses
                
                # Calculate cost
                total_cost = length_m * cost_per_meter
                
                # Check if pressure loss is acceptable
                if total_pressure_loss <= max_pressure_loss_bar:
                    if total_cost < best_cost:
                        best_diameter = diameter_mm
                        best_cost = total_cost
                        best_pressure_loss = total_pressure_loss
                        
            except Exception as e:
                self.logger.warning(f"Error calculating for diameter {diameter_mm}mm: {e}")
                continue
        
        if best_diameter is None:
            raise ValueError("No suitable pipe diameter found for given constraints")
        
        return {
            "optimal_diameter_mm": best_diameter,
            "total_cost": best_cost,
            "pressure_loss_bar": best_pressure_loss,
            "material": material.value
        }
    
    def calculate_network_hydraulics(
        self, 
        zones: List[IrrigationZone], 
        pipes: List[IrrigationPipe],
        source_pressure_bar: float,
        source_flow_lph: float
    ) -> HydraulicCalculationResult:
        """
        Calculate complete network hydraulics for an irrigation system.
        
        Args:
            zones: List of irrigation zones
            pipes: List of irrigation pipes
            source_pressure_bar: Source pressure in bar
            source_flow_lph: Source flow rate in liters per hour
            
        Returns:
            Hydraulic calculation results
        """
        total_flow_lph = sum(zone.required_flow_lph for zone in zones)
        
        if total_flow_lph > source_flow_lph:
            warnings = [f"Total required flow ({total_flow_lph:.1f} LPH) exceeds source capacity ({source_flow_lph:.1f} LPH)"]
        else:
            warnings = []
        
        # Calculate pressure losses for each pipe
        total_pressure_loss = 0.0
        pipe_results = []
        
        for pipe in pipes:
            pipe_props = self.PIPE_PROPERTIES[pipe.material]
            roughness_mm = pipe_props["roughness_mm"]
            
            pressure_loss_bar, velocity_ms, reynolds_number, friction_factor = self.calculate_pressure_loss_darcy_weisbach(
                pipe.flow_rate_lph, pipe.diameter_m, pipe.length_m, roughness_mm / 1000.0
            )
            
            # Add minor losses (estimated 10% of major losses)
            minor_losses = pressure_loss_bar * 0.1
            total_pipe_loss = pressure_loss_bar + minor_losses
            
            total_pressure_loss += total_pipe_loss
            
            pipe_results.append({
                "pipe_id": str(pipe.id),
                "pressure_loss_bar": total_pipe_loss,
                "velocity_ms": velocity_ms,
                "reynolds_number": reynolds_number,
                "friction_factor": friction_factor,
                "flow_regime": self.determine_flow_regime(reynolds_number).value
            })
        
        final_pressure = source_pressure_bar - total_pressure_loss
        
        # Check for system viability
        is_system_viable = final_pressure >= 1.0  # Minimum 1 bar required
        
        if final_pressure < 1.0:
            warnings.append(f"Final pressure ({final_pressure:.2f} bar) is below minimum required (1.0 bar)")
        
        if final_pressure < 0.5:
            warnings.append("System pressure is critically low - consider redesign")
        
        # Calculate average velocity and Reynolds number for the system
        avg_velocity = np.mean([pr["velocity_ms"] for pr in pipe_results])
        avg_reynolds = np.mean([pr["reynolds_number"] for pr in pipe_results])
        
        return HydraulicCalculationResult(
            total_flow_lph=total_flow_lph,
            total_pressure_loss_bar=total_pressure_loss,
            final_pressure_bar=final_pressure,
            velocity_ms=avg_velocity,
            reynolds_number=avg_reynolds,
            friction_factor=np.mean([pr["friction_factor"] for pr in pipe_results]),
            warnings=warnings,
            is_system_viable=is_system_viable
        )
    
    def calculate_optimal_flow_distribution(
        self, 
        zones: List[IrrigationZone], 
        source_flow_lph: float
    ) -> Dict[str, float]:
        """
        Calculate optimal flow distribution among zones based on area and water needs.
        
        Args:
            zones: List of irrigation zones
            source_flow_lph: Available source flow rate
            
        Returns:
            Dictionary mapping zone IDs to optimal flow rates
        """
        total_area = sum(zone.total_area_m2 for zone in zones)
        
        if total_area == 0:
            # Equal distribution if no area data
            flow_per_zone = source_flow_lph / len(zones)
            return {str(zone.id): flow_per_zone for zone in zones}
        
        # Distribute flow based on area proportion
        flow_distribution = {}
        for zone in zones:
            area_proportion = zone.total_area_m2 / total_area
            optimal_flow = source_flow_lph * area_proportion
            flow_distribution[str(zone.id)] = optimal_flow
        
        return flow_distribution
    
    def validate_system_design(
        self, 
        zones: List[IrrigationZone], 
        pipes: List[IrrigationPipe],
        source_pressure_bar: float,
        source_flow_lph: float
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of irrigation system design.
        
        Args:
            zones: List of irrigation zones
            pipes: List of irrigation pipes
            source_pressure_bar: Source pressure in bar
            source_flow_lph: Source flow rate in liters per hour
            
        Returns:
            Validation results
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check flow balance
        total_required_flow = sum(zone.required_flow_lph for zone in zones)
        if total_required_flow > source_flow_lph:
            validation_results["errors"].append(
                f"Total required flow ({total_required_flow:.1f} LPH) exceeds source capacity ({source_flow_lph:.1f} LPH)"
            )
            validation_results["is_valid"] = False
        
        # Check pressure requirements
        for zone in zones:
            if zone.operating_pressure_bar < 1.0:
                validation_results["warnings"].append(
                    f"Zone {zone.name} operating pressure ({zone.operating_pressure_bar:.1f} bar) is below recommended minimum (1.0 bar)"
                )
        
        # Check pipe velocities
        for pipe in pipes:
            flow_rate_m3s = pipe.flow_rate_lph / (1000 * 3600)
            area_m2 = math.pi * (pipe.diameter_m / 2) ** 2
            velocity_ms = flow_rate_m3s / area_m2
            
            if velocity_ms > 2.0:
                validation_results["warnings"].append(
                    f"Pipe {pipe.pipe_name} velocity ({velocity_ms:.1f} m/s) exceeds recommended maximum (2.0 m/s)"
                )
            elif velocity_ms < 0.3:
                validation_results["warnings"].append(
                    f"Pipe {pipe.pipe_name} velocity ({velocity_ms:.1f} m/s) is below recommended minimum (0.3 m/s)"
                )
        
        # Check for dead ends
        pipe_connections = {}
        for pipe in pipes:
            start_point = (pipe.start_x, pipe.start_y)
            end_point = (pipe.end_x, pipe.end_y)
            
            if start_point not in pipe_connections:
                pipe_connections[start_point] = []
            if end_point not in pipe_connections:
                pipe_connections[end_point] = []
            
            pipe_connections[start_point].append(end_point)
            pipe_connections[end_point].append(start_point)
        
        # Find dead ends (points with only one connection)
        dead_ends = [point for point, connections in pipe_connections.items() if len(connections) == 1]
        if dead_ends:
            validation_results["warnings"].append(
                f"Found {len(dead_ends)} dead ends in pipe network - consider looped design for better pressure distribution"
            )
        
        # Generate recommendations
        if validation_results["warnings"]:
            validation_results["recommendations"].append(
                "Review system design to address warnings above"
            )
        
        if total_required_flow < source_flow_lph * 0.8:
            validation_results["recommendations"].append(
                "Consider reducing pipe sizes to optimize cost - system is oversized"
            )
        
        return validation_results 