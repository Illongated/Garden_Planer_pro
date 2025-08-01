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

    def _calculate_zone_path(self, zone_plants):
        """
        Calculates a simple path connecting all plants in a zone and its length.
        Returns the path (list of points) and the total length in meters.
        """
        if not zone_plants:
            return [], 0

        # Start with a simple heuristic: sort by x then y to create a path
        path_points = sorted(zone_plants, key=lambda p: (p['x'], p['y']))

        # The actual path for drawing is the center of each plant
        path_coords = []
        for p in path_points:
            center_x = p['x'] + p['width'] / 2
            center_y = p['y'] + p['height'] / 2
            path_coords.append({'x': center_x, 'y': center_y})

        total_distance_dm = 0
        for i in range(len(path_coords) - 1):
            p1 = path_coords[i]
            p2 = path_coords[i+1]
            distance = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
            total_distance_dm += distance

        return path_coords, total_distance_dm / 10.0

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
            path_coords, pipe_length_m = self._calculate_zone_path(plants_in_zone)

            detailed_zones[zone_name] = {
                "num_plants": len(plants_in_zone),
                "water_needs_lph": round(zone_water_lph, 2),
                "estimated_pipe_m": round(pipe_length_m, 2),
                "plant_ids": list(set(p['plant_id'] for p in plants_in_zone)),
                "path": path_coords # Add the path for frontend rendering
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
