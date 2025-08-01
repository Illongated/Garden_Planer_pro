import math
from collections import defaultdict

class IrrigationLayoutEngine:
    def __init__(self, plant_positions, plants_data, irrigation_data, irrigation_type, watering_time_min):
        self.plant_positions = plant_positions
        self.plants_data = plants_data
        self.irrigation_data = irrigation_data
        self.irrigation_type = irrigation_type
        self.watering_time_h = watering_time_min / 60.0

    def _group_plants_into_zones(self):
        """Groups plants based on similar water requirements."""
        zones = defaultdict(list)
        # Define water need thresholds for zoning (e.g., low, medium, high)
        thresholds = {
            'low': (0, 2.5),
            'medium': (2.5, 5.5),
            'high': (5.5, float('inf'))
        }
        for i, pos in enumerate(self.plant_positions):
            plant_id = pos['plant_id']
            water_needs = self.plants_data[plant_id]['water_L_per_hour']

            zone_name = 'medium' # Default
            for name, (low, high) in thresholds.items():
                if low <= water_needs < high:
                    zone_name = name
                    break

            # Add the full position object to the zone for later calculations
            zones[zone_name].append({**pos, 'instance_id': i})

        return dict(zones)

    def _estimate_pipe_length(self, zone_plants):
        """
        Estimates pipe length for a zone by calculating a simple path connecting all plants.
        This is a rough estimation (traveling salesman problem is NP-hard).
        """
        if not zone_plants:
            return 0

        # Start with a simple heuristic: sort by x then y and sum distances
        path = sorted(zone_plants, key=lambda p: (p['x'], p['y']))
        total_distance = 0
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i+1]
            # Euclidean distance in decimeters
            distance = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
            total_distance += distance

        # Convert from decimeters to meters
        return total_distance / 10.0

    def _recommend_pump(self, required_flow_lph):
        """Recommends a standard pump size."""
        if required_flow_lph == 0:
            return "Aucune"
        pump_sizes = [500, 1000, 1500, 2000, 3000, 5000] # L/h
        for size in pump_sizes:
            if size >= required_flow_lph:
                return f"{size} L/h"
        return f"> {pump_sizes[-1]} L/h"

    def generate_layout(self):
        plant_zones = self._group_plants_into_zones()

        detailed_zones = {}
        total_system_water_lph = 0
        total_pipe_length_m = 0

        for zone_name, plants_in_zone in plant_zones.items():
            if not plants_in_zone: continue

            zone_water_lph = sum(self.plants_data[p['plant_id']]['water_L_per_hour'] for p in plants_in_zone)
            pipe_length_m = self._estimate_pipe_length(plants_in_zone)

            detailed_zones[zone_name] = {
                "num_plants": len(plants_in_zone),
                "water_needs_lph": round(zone_water_lph, 2),
                "estimated_pipe_m": round(pipe_length_m, 2),
                "plant_ids": list(set(p['plant_id'] for p in plants_in_zone))
            }
            total_system_water_lph += zone_water_lph
            total_pipe_length_m += pipe_length_m

        # Calculate flow rate needed based on desired watering time
        if self.watering_time_h > 0:
            required_flow_rate_lph = total_system_water_lph / self.watering_time_h
        else:
            required_flow_rate_lph = 0

        recommended_pump = self._recommend_pump(required_flow_rate_lph)

        return {
            "zones": detailed_zones,
            "summary": {
                "total_pipe_length_m": round(total_pipe_length_m, 2),
                "total_water_per_hour_lph": round(total_system_water_lph, 2),
                "required_flow_rate_lph": round(required_flow_rate_lph, 2),
                "recommended_pump": recommended_pump,
                "watering_time_min": self.watering_time_h * 60
            }
        }
