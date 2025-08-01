import math
import random

class LayoutEngine:
    def __init__(self, garden_width, garden_depth, plants_data, companion_data, sun_angle=180, placed_plants=[]):
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.plants_data = plants_data
        self.companion_data = companion_data
        self.sun_angle = sun_angle
        self.placed_plants = placed_plants

        self.grid = [[None for _ in range(garden_width)] for _ in range(garden_depth)]
        self.scores = {"sun": [], "companion": []}
        self.sun_map = self._calculate_sun_map()
        self.placed_plant_ids = {p['instance_id'] for p in self.placed_plants}

    def _pin_placed_plants(self):
        """Marks the grid with the positions of manually placed plants."""
        for plant in self.placed_plants:
            plant_id = plant['plant_id']
            plant_data = self.plants_data[plant_id]
            plant_size_m = math.sqrt(plant_data['space_m2'])
            plant_size_units = int(plant_size_m * 10)

            x, y = int(plant['x']), int(plant['y'])

            for i in range(y, y + plant_size_units):
                for j in range(x, x + plant_size_units):
                    if 0 <= i < self.garden_depth and 0 <= j < self.garden_width:
                        # Use a special identifier for manually placed plants
                        self.grid[i][j] = f"manual_{plant['instance_id']}"

    def _calculate_sun_map(self):
        sun_map = [[0.0 for _ in range(self.garden_width)] for _ in range(self.garden_depth)]
        angle_rad = math.radians(self.sun_angle - 90)
        sun_vector = (math.cos(angle_rad), math.sin(angle_rad))

        for y in range(self.garden_depth):
            for x in range(self.garden_width):
                # Normalize coordinates to -0.5 to 0.5 range
                norm_x = x / self.garden_width - 0.5
                norm_y = y / self.garden_depth - 0.5

                # Project onto sun vector
                dot_product = norm_x * sun_vector[0] + norm_y * sun_vector[1]

                # Map the dot product to a 0.2 (shade) to 1.0 (sun) range
                sun_intensity = 0.6 + 0.4 * dot_product
                sun_map[y][x] = max(0.2, min(1.0, sun_intensity))
        return sun_map

    def _get_sun_score(self, x, y, plant):
        plant_size_m = math.sqrt(plant['space_m2'])
        plant_size_units = int(plant_size_m * 10)

        total_intensity = 0
        num_cells = 0
        for i in range(y, y + plant_size_units):
            for j in range(x, x + plant_size_units):
                if 0 <= i < self.garden_depth and 0 <= j < self.garden_width:
                    total_intensity += self.sun_map[i][j]
                    num_cells += 1

        if num_cells == 0: return 0.0
        avg_intensity = total_intensity / num_cells

        if plant.get("sun_preference") == "full_sun":
            # Score is higher for intensities closer to 1.0
            return avg_intensity
        elif plant.get("sun_preference") == "partial_shade":
            # Score is highest at an intensity of 0.5-0.6
            return 1.0 - abs(avg_intensity - 0.55) * 1.8
        else: # "any"
            return 1.0

    def _get_companion_score(self, x, y, plant_id):
        score_multiplier = 1.0
        plant_size_m = math.sqrt(self.plants_data[plant_id]['space_m2'])
        plant_size_units = int(plant_size_m * 10)

        # Check a wider radius for companions/enemies
        check_radius = plant_size_units + 2

        for i in range(max(0, y - check_radius), min(self.garden_depth, y + plant_size_units + check_radius)):
            for j in range(max(0, x - check_radius), min(self.garden_width, x + plant_size_units + check_radius)):
                if self.grid[i][j] is not None:
                    neighbor_id = self.grid[i][j]
                    if neighbor_id == plant_id: continue

                    if neighbor_id in self.companion_data.get(plant_id, {}).get("friends", []):
                        score_multiplier *= 1.1 # 10% boost for each friend nearby
                    if neighbor_id in self.companion_data.get(plant_id, {}).get("enemies", []):
                        score_multiplier *= 0.7 # 30% penalty for each enemy

        return min(2.0, score_multiplier) # Cap the score to avoid extreme values

    def _find_best_position(self, plant_id):
        best_pos_info = None
        best_score = -1

        plant = self.plants_data[plant_id]
        plant_size_m = math.sqrt(plant['space_m2'])
        plant_size_units = int(plant_size_m * 10)

        for y in range(self.garden_depth - plant_size_units + 1):
            for x in range(self.garden_width - plant_size_units + 1):
                if all(self.grid[i][j] is None for i in range(y, y + plant_size_units) for j in range(x, x + plant_size_units)):
                    sun_score = self._get_sun_score(x, y, plant)
                    companion_score = self._get_companion_score(x, y, plant_id)

                    # We multiply the scores - this makes each one more critical
                    # A zero in one score will veto the position
                    total_score = sun_score * companion_score

                    if total_score > best_score:
                        best_score = total_score
                        best_pos_info = {
                            "x": x, "y": y,
                            "sun_score": sun_score,
                            "companion_score": companion_score
                        }
        return best_pos_info

    def generate_layout(self, plant_quantities):
        self._pin_placed_plants()

        # Calculate quantities of plants to be placed procedurally
        procedural_quantities = plant_quantities.copy()
        for p in self.placed_plants:
            if p['plant_id'] in procedural_quantities:
                procedural_quantities[p['plant_id']] -= 1

        plant_list = []
        for plant_id, quantity in procedural_quantities.items():
            if quantity > 0:
                plant_list.extend([plant_id] * quantity)

        # Sort plants: sun-lovers and larger plants first
        plant_list.sort(key=lambda pid: (
            self.plants_data[pid].get("sun_preference") != "full_sun", # Place full_sun first
            -self.plants_data[pid]['space_m2'] # Then by size descending
        ))

        for plant_id in plant_list:
            best_pos = self._find_best_position(plant_id)
            if best_pos:
                x, y = best_pos['x'], best_pos['y']
                self.scores["sun"].append(best_pos['sun_score'])
                self.scores["companion"].append(best_pos['companion_score'])

                plant_size_m = math.sqrt(self.plants_data[plant_id]['space_m2'])
                plant_size_units = int(plant_size_m * 10)

                for i in range(y, y + plant_size_units):
                    for j in range(x, x + plant_size_units):
                        if 0 <= i < self.garden_depth and 0 <= j < self.garden_width:
                            self.grid[i][j] = plant_id
        return self.grid

    def get_layout_scores(self):
        avg_scores = {}
        for score_type, score_list in self.scores.items():
            avg_scores[score_type] = sum(score_list) / len(score_list) if score_list else 0
        return avg_scores

    def get_plant_positions(self):
        positions = []
        # Keep track of the top-left corner of plants already added
        procedurally_placed = set()

        # 1. Get procedurally placed plants from the grid
        for y in range(self.garden_depth):
            for x in range(self.garden_width):
                cell_content = self.grid[y][x]
                if cell_content and not str(cell_content).startswith("manual_"):
                    plant_id = cell_content
                    # Find the top-left corner of this plant block to avoid duplicates
                    origin_x, origin_y = x, y
                    while origin_x > 0 and self.grid[y][origin_x - 1] == plant_id:
                        origin_x -= 1
                    while origin_y > 0 and all(self.grid[origin_y - 1][k] == plant_id for k in range(origin_x, x + 1)):
                        origin_y -= 1

                    if (origin_x, origin_y) not in procedurally_placed:
                        plant = self.plants_data[plant_id]
                        plant_size_m = math.sqrt(plant['space_m2'])
                        plant_size_units = int(plant_size_m * 10)

                        positions.append({
                            "plant_id": plant_id,
                            "x": origin_x, "y": origin_y,
                            "width": plant_size_units,
                            "height": plant_size_units,
                            "is_manual": False
                        })
                        procedurally_placed.add((origin_x, origin_y))

        # 2. Add the manually placed plants
        for plant in self.placed_plants:
            plant_data = self.plants_data[plant['plant_id']]
            plant_size_m = math.sqrt(plant_data['space_m2'])
            plant_size_units = int(plant_size_m * 10)
            positions.append({
                "plant_id": plant['plant_id'],
                "x": int(plant['x']),
                "y": int(plant['y']),
                "width": plant_size_units,
                "height": plant_size_units,
                "is_manual": True,
                "instance_id": plant['instance_id']
            })

        return positions
