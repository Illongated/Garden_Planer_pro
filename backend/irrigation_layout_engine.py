class IrrigationLayoutEngine:
    def __init__(self, plant_positions, garden_width, garden_depth):
        self.plant_positions = plant_positions
        self.garden_width = garden_width
        self.garden_depth = garden_depth
        self.max_4mm_pipe_run = 150 # in 10cm units (15 meters)

    def generate_layout(self):
        pipe_path_13mm = []
        pipe_path_4mm = []
        emitters = []
        warnings = []

        if not self.plant_positions:
            return {"pipe_path_13mm": [], "pipe_path_4mm": [], "emitters": [], "warnings": []}

        sorted_plants = sorted(self.plant_positions, key=lambda p: (p['y'], p['x']))

        # Main 13mm pipe will run along the y-axis
        main_pipe_x = -2 # Place it just outside the garden area
        pipe_path_13mm.append({"x": main_pipe_x, "y": 0})
        pipe_path_13mm.append({"x": main_pipe_x, "y": self.garden_depth})

        total_4mm_pipe_length = 0

        for plant in sorted_plants:
            # 4mm pipe from the main line to the plant
            emitter_pipe_start = {"x": main_pipe_x, "y": plant['y']}
            emitter_pipe_end = {"x": plant['x'], "y": plant['y']}
            pipe_path_4mm.append([emitter_pipe_start, emitter_pipe_end])

            total_4mm_pipe_length += abs(plant['x'] - main_pipe_x)

            emitters.append({
                "type": "drip_emitter",
                "x": plant['x'],
                "y": plant['y']
            })

        if total_4mm_pipe_length > self.max_4mm_pipe_run:
            warnings.append(f"Total length of 4mm pipe ({total_4mm_pipe_length / 10}m) exceeds the recommended maximum of {self.max_4mm_pipe_run / 10}m. This may cause pressure loss.")

        return {
            "pipe_path_13mm": pipe_path_13mm,
            "pipe_path_4mm": pipe_path_4mm,
            "emitters": emitters,
            "warnings": warnings
        }
