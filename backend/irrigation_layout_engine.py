class IrrigationLayoutEngine:
    def __init__(self, plant_positions, plants_data, irrigation_data, garden_width, garden_depth):
        self.plant_positions = plant_positions
        self.plants_data = plants_data
        self.irrigation_data = irrigation_data
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.max_4mm_pipe_run = 150

    def _create_watering_zones(self):
        # ... (same as before)
        zones = {}
        for plant in self.plant_positions:
            plant_id = plant['plant_id']
            water_needs = self.plants_data[plant_id]['water_L_per_hour']
            zone_id = round(water_needs)
            if zone_id not in zones:
                zones[zone_id] = []
            zones[zone_id].append(plant)
        return zones

    def _select_best_emitter(self, zone_id, plants_in_zone):
        """
        Selects the best emitter type for a given zone based on plant density.
        """
        # Simple logic: if plants are very close together, use a micro-sprayer
        if len(plants_in_zone) > 5: # Arbitrary threshold for density
            avg_dist = self._calculate_avg_distance(plants_in_zone)
            if avg_dist < 20: # 2 meters
                return "micro_sprayer"
        return "drip_emitter"

    def _calculate_avg_distance(self, plants):
        # ... (simplified distance calculation)
        if len(plants) < 2: return 0
        total_dist = 0
        for i in range(len(plants)):
            for j in range(i + 1, len(plants)):
                dist = ((plants[i]['x'] - plants[j]['x'])**2 + (plants[i]['y'] - plants[j]['y'])**2)**0.5
                total_dist += dist
        return total_dist / (len(plants) * (len(plants) - 1) / 2)


    def generate_layout(self):
        warnings = []
        zones = self._create_watering_zones()
        irrigation_layout = {"zones": {}}

        for zone_id, plants_in_zone in zones.items():
            emitter_type = self._select_best_emitter(zone_id, plants_in_zone)

            pipe_path_13mm = []
            pipe_path_4mm = []
            emitters = []

            sorted_plants = sorted(plants_in_zone, key=lambda p: (p['y'], p['x']))

            main_pipe_x = -2
            pipe_path_13mm.append({"x": main_pipe_x, "y": 0})
            pipe_path_13mm.append({"x": main_pipe_x, "y": self.garden_depth})
            total_4mm_pipe_length = 0

            for plant in sorted_plants:
                emitter_pipe_start = {"x": main_pipe_x, "y": plant['y']}
                emitter_pipe_end = {"x": plant['x'], "y": plant['y']}
                pipe_path_4mm.append([emitter_pipe_start, emitter_pipe_end])
                total_4mm_pipe_length += abs(plant['x'] - main_pipe_x)
                emitters.append({
                    "type": emitter_type,
                    "x": plant['x'],
                    "y": plant['y']
                })

            if total_4mm_pipe_length > self.max_4mm_pipe_run:
                warnings.append(f"Zone {zone_id}: Total length of 4mm pipe ({total_4mm_pipe_length / 10}m) exceeds the recommended maximum.")

            irrigation_layout["zones"][zone_id] = {
                "pipe_path_13mm": pipe_path_13mm,
                "pipe_path_4mm": pipe_path_4mm,
                "emitters": emitters,
                "emitter_type": emitter_type
            }

        irrigation_layout["warnings"] = warnings
        return irrigation_layout
