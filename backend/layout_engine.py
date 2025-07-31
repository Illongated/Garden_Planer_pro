class LayoutEngine:
    def __init__(self, garden_width, garden_depth, plants_data, companion_data, sun_angle=180, row_width=5):
        # ... (same as before)
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.plants_data = plants_data
        self.companion_data = companion_data
        self.sun_angle = sun_angle
        self.row_width = row_width
        self.grid = [[None for _ in range(garden_width)] for _ in range(garden_depth)]
        self.scores = {"sun": [], "accessibility": [], "companion": []}

    def _get_sun_score(self, x, y, plant_id):
        # ... (same as before)
        plant_sun_pref = self.plants_data[plant_id].get("sun_preference", "full_sun")
        if 90 < self.sun_angle < 270: sunny_side_is_south = True
        else: sunny_side_is_south = False
        is_on_sunny_side = (y < self.garden_depth / 2) if sunny_side_is_south else (y >= self.garden_depth / 2)
        if (plant_sun_pref == "full_sun" and is_on_sunny_side) or (plant_sun_pref == "partial_shade" and not is_on_sunny_side): return 1.0
        elif plant_sun_pref == "full_sun" and not is_on_sunny_side: return 0.2
        elif plant_sun_pref == "partial_shade" and is_on_sunny_side: return 0.5
        return 0.0

    def _get_accessibility_score(self, x, y, plant_size_units):
        # ... (same as before)
        if (x % (plant_size_units + self.row_width)) < self.row_width and x != 0: return 0.0
        return 1.0

    def _get_companion_score(self, x, y, plant_id):
        # ... (same as before)
        score = 1.0
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if 0 <= i < self.garden_depth and 0 <= j < self.garden_width and self.grid[i][j]:
                    neighbor_id = self.grid[i][j]
                    if neighbor_id in self.companion_data.get(plant_id, {}).get("friends", []): score += 0.2
                    if neighbor_id in self.companion_data.get(plant_id, {}).get("enemies", []): score -= 0.5
        return max(0, score)

    def _find_best_position(self, plant_id):
        # ... (same as before)
        best_pos = None
        best_score = -1
        plant_size_m = self.plants_data[plant_id]['space_m2'] ** 0.5
        plant_size_units = int(plant_size_m * 10)
        for y in range(self.garden_depth - plant_size_units + 1):
            for x in range(self.garden_width - plant_size_units + 1):
                is_available = all(self.grid[i][j] is None for i in range(y, y + plant_size_units) for j in range(x, x + plant_size_units))
                if is_available:
                    sun_score = self._get_sun_score(x, y, plant_id)
                    accessibility_score = self._get_accessibility_score(x, y, plant_size_units)
                    companion_score = self._get_companion_score(x, y, plant_id)
                    if accessibility_score == 0: continue
                    total_score = sun_score * companion_score
                    if total_score > best_score:
                        best_score = total_score
                        best_pos = (x, y, sun_score, accessibility_score, companion_score)
        return best_pos

    def generate_layout(self, plant_quantities):
        # ... (same as before)
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
        """
        Returns the average scores for the layout.
        """
        avg_scores = {}
        for score_type, score_list in self.scores.items():
            if score_list:
                avg_scores[score_type] = sum(score_list) / len(score_list)
            else:
                avg_scores[score_type] = 0
        return avg_scores

    def get_plant_positions(self):
        # ... (same as before)
        positions = []
        processed_coords = set()
        for y in range(self.garden_depth):
            for x in range(self.garden_width):
                plant_id = self.grid[y][x]
                if plant_id and (x, y) not in processed_coords:
                    is_top_left = True
                    if x > 0 and self.grid[y][x-1] == plant_id: is_top_left = False
                    if y > 0 and self.grid[y-1][x] == plant_id: is_top_left = False
                    if is_top_left:
                        positions.append({"plant_id": plant_id, "x": x, "y": y})
                    processed_coords.add((x, y))
        return positions
