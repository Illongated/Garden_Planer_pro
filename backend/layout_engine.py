class LayoutEngine:
    def __init__(self, garden_width, garden_depth, plants_data, companion_data, sun_angle=180, row_width=5, weights=None):
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.plants_data = plants_data
        self.companion_data = companion_data
        self.sun_angle = sun_angle
        self.row_width = row_width
        self.weights = weights if weights is not None else {"sun": 1.0, "companion": 1.0}
        self.grid = [[None for _ in range(garden_width)] for _ in range(garden_depth)]
        self.scores = {"sun": [], "accessibility": [], "companion": []}
        self.sun_map = self._calculate_sun_map()

    def _calculate_sun_map(self):
        """
        Calculates a sun map for the garden, with values from ~0.2 (shade) to 1.0 (sun).
        This creates a north-south gradient based on the sun's angle.
        """
        sun_map = [[0.0 for _ in range(self.garden_width)] for _ in range(self.garden_depth)]
        angle = self.sun_angle % 360
        is_from_south = 90 < angle < 270

        for y in range(self.garden_depth):
            if self.garden_depth > 1:
                if is_from_south:
                    sun_intensity = 1.0 - 0.8 * (y / (self.garden_depth - 1))
                else:
                    sun_intensity = 0.2 + 0.8 * (y / (self.garden_depth - 1))
            else:
                sun_intensity = 1.0

            for x in range(self.garden_width):
                sun_map[y][x] = sun_intensity
        return sun_map

    def _get_sun_score(self, x, y, plant_id):
        """
        Calculates the sun score for a given plant at a given position based on the sun map.
        """
        plant_size_m = self.plants_data[plant_id]['space_m2'] ** 0.5
        plant_size_units = int(plant_size_m * 10)
        total_intensity = 0
        num_cells = 0
        for i in range(y, y + plant_size_units):
            for j in range(x, x + plant_size_units):
                if 0 <= i < self.garden_depth and 0 <= j < self.garden_width:
                    total_intensity += self.sun_map[i][j]
                    num_cells += 1

        if num_cells == 0:
            return 0.0
        avg_intensity = total_intensity / num_cells
        plant_sun_pref = self.plants_data[plant_id].get("sun_preference", "full_sun")

        if plant_sun_pref == "full_sun":
            score = avg_intensity
        elif plant_sun_pref == "partial_shade":
            score = 1.0 - abs(avg_intensity - 0.5) * 1.5
        else:
            score = avg_intensity
        return max(0.0, min(1.0, score))

    def _get_accessibility_score(self, x, y, plant_size_units, plant_id):
        """
        Ensures a minimum distance (path width) between groups of different plants.
        A plant group is implicitly defined by plants of the same ID.
        """
        path_width_units = self.row_width

        # Check the perimeter around the plant's bounding box for other plant types.
        for i in range(y - path_width_units, y + plant_size_units + path_width_units):
            for j in range(x - path_width_units, x + plant_size_units + path_width_units):
                # Skip checking the area where the plant itself will be placed.
                if (y <= i < y + plant_size_units) and (x <= j < x + plant_size_units):
                    continue

                if 0 <= i < self.garden_depth and 0 <= j < self.garden_width:
                    neighbor_id = self.grid[i][j]
                    if neighbor_id is not None and neighbor_id != plant_id:
                        # This position is too close to a plant of another type.
                        return 0.0
        return 1.0

    def _get_companion_score(self, x, y, plant_id):
        score = 1.0
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if 0 <= i < self.garden_depth and 0 <= j < self.garden_width and self.grid[i][j]:
                    neighbor_id = self.grid[i][j]
                    if neighbor_id in self.companion_data.get(plant_id, {}).get("friends", []):
                        score += 0.2
                    if neighbor_id in self.companion_data.get(plant_id, {}).get("enemies", []):
                        score -= 0.5
        return max(0, score)

    def _find_best_position(self, plant_id):
        best_pos = None
        best_score = -1
        plant_size_m = self.plants_data[plant_id]['space_m2'] ** 0.5
        plant_size_units = int(plant_size_m * 10)
        for y in range(self.garden_depth - plant_size_units + 1):
            for x in range(self.garden_width - plant_size_units + 1):
                is_available = all(self.grid[i][j] is None for i in range(y, y + plant_size_units) for j in range(x, x + plant_size_units))
                if is_available:
                    sun_score = self._get_sun_score(x, y, plant_id)
                    accessibility_score = self._get_accessibility_score(x, y, plant_size_units, plant_id)
                    companion_score = self._get_companion_score(x, y, plant_id)
                    if accessibility_score == 0:
                        continue

                    # Calculate a weighted score
                    total_score = (sun_score * self.weights.get("sun", 1.0)) + \
                                  (companion_score * self.weights.get("companion", 1.0))

                    if total_score > best_score:
                        best_score = total_score
                        best_pos = (x, y, sun_score, accessibility_score, companion_score)
        return best_pos

    def generate_layout(self, plant_quantities):
        plant_list = []
        for plant_id, quantity in plant_quantities.items():
            for _ in range(quantity):
                plant_list.append(plant_id)
        plant_list.sort(key=lambda pid: self.plants_data[pid]['space_m2'], reverse=True)
        for plant_id in plant_list:
            best_pos = self._find_best_position(plant_id)
            if best_pos:
                x, y, sun, acc, comp = best_pos
                self.scores["sun"].append(sun)
                self.scores["accessibility"].append(acc)
                self.scores["companion"].append(comp)
                plant_size_m = self.plants_data[plant_id]['space_m2'] ** 0.5
                plant_size_units = int(plant_size_m * 10)
                for i in range(y, y + plant_size_units):
                    for j in range(x, x + plant_size_units):
                        self.grid[i][j] = plant_id
        return self.grid

    def get_layout_scores(self):
        avg_scores = {}
        for score_type, score_list in self.scores.items():
            if score_list:
                avg_scores[score_type] = sum(score_list) / len(score_list)
            else:
                avg_scores[score_type] = 0
        return avg_scores

    def get_plant_positions(self):
        positions = []
        processed_coords = set()
        for y in range(self.garden_depth):
            for x in range(self.garden_width):
                plant_id = self.grid[y][x]
                if plant_id and (x, y) not in processed_coords:
                    is_top_left = True
                    if x > 0 and self.grid[y][x-1] == plant_id:
                        is_top_left = False
                    if y > 0 and self.grid[y-1][x] == plant_id:
                        is_top_left = False
                    if is_top_left:
                        positions.append({"plant_id": plant_id, "x": x, "y": y})
                    processed_coords.add((x, y))
        return positions
