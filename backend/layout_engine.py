class LayoutEngine:
    def __init__(self, garden_width, garden_depth, plants_data):
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.plants_data = plants_data
        self.grid = [[None for _ in range(garden_width)] for _ in range(garden_depth)]

    def generate_layout(self, plant_quantities):
        """
        A simple grid-based layout generator.
        """
        plant_list = []
        for plant_id, quantity in plant_quantities.items():
            for _ in range(quantity):
                plant_list.append(plant_id)

        x, y = 0, 0
        for plant_id in plant_list:
            plant_size_m = self.plants_data[plant_id]['space_m2'] ** 0.5
            plant_size_units = int(plant_size_m * 10) # Assuming 1 unit = 10cm

            if x + plant_size_units > self.garden_width:
                x = 0
                y += plant_size_units

            if y + plant_size_units > self.garden_depth:
                # Not enough space
                break

            # Place the plant
            for i in range(y, y + plant_size_units):
                for j in range(x, x + plant_size_units):
                    if i < self.garden_depth and j < self.garden_width:
                        self.grid[i][j] = plant_id

            x += plant_size_units

        return self.grid

    def get_plant_positions(self):
        """
        Returns a list of plant positions.
        """
        positions = []
        placed_plants = set()
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell and (cell, x, y) not in placed_plants:
                    # This is a simplified way to get a single point for each plant
                    # A more robust solution would find the center of each plant area
                    positions.append({"plant_id": cell, "x": x, "y": y})
                    # Mark all cells of this plant as placed
                    plant_size_m = self.plants_data[cell]['space_m2'] ** 0.5
                    plant_size_units = int(plant_size_m * 10)
                    for i in range(y, y + plant_size_units):
                        for j in range(x, x + plant_size_units):
                            if i < self.garden_depth and j < self.garden_width:
                                placed_plants.add((self.grid[i][j], j, i))

        return positions
