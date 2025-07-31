import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .irrigation_data import IRRIGATION_KNOWLEDGE_BASE
from .layout_engine import LayoutEngine
from .irrigation_layout_engine import IrrigationLayoutEngine
from .companion_data import COMPANION_DATA

# --- Plant Data ---
PLANTS = {
    "tomatoes": {"name": "Tomatoes", "space_m2": 0.5, "water_L_per_hour": 5, "sun_preference": "full_sun"},
    "lettuce": {"name": "Lettuce", "space_m2": 0.1, "water_L_per_hour": 2, "sun_preference": "partial_shade"},
    "carrots": {"name": "Carrots", "space_m2": 0.05, "water_L_per_hour": 1.5, "sun_preference": "full_sun"},
    "cucumbers": {"name": "Cucumbers", "space_m2": 0.75, "water_L_per_hour": 6, "sun_preference": "full_sun"},
}

# Create a FastAPI instance
app = FastAPI()

# Create a Socket.IO ASGI app
sio = socketio.AsyncServer(async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

# Mount static file directories
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")


@sio.event
async def connect(sid, environ):
    print(f"connect {sid}")
    await sio.emit('plant_data', PLANTS, to=sid)
    await sio.emit('irrigation_knowledge_base', IRRIGATION_KNOWLEDGE_BASE, to=sid)


@sio.event
async def disconnect(sid):
    print(f"disconnect {sid}")


@sio.on("update_garden_layout")
async def update_garden_layout(sid, data):
    garden_area = data.get("garden_area", 10)
    plant_priorities = data.get("plant_priorities", {})
    plant_locks = data.get("plant_locks", {})
    sun_angle = data.get("sun_angle", 180)
    row_width = data.get("row_width", 5)

    plant_quantities = {plant_id: 0 for plant_id in PLANTS}
    remaining_area = garden_area

    for plant_id, is_locked in plant_locks.items():
        if is_locked:
            quantity = 5
            area_needed = quantity * PLANTS[plant_id]["space_m2"]
            if remaining_area >= area_needed:
                plant_quantities[plant_id] = quantity
                remaining_area -= area_needed

    total_priority = sum(plant_priorities.values())
    if total_priority > 0:
        for plant_id, priority in plant_priorities.items():
            if not plant_locks.get(plant_id, False):
                proportion = priority / total_priority
                available_area_for_plant = remaining_area * proportion
                quantity = int(available_area_for_plant / PLANTS[plant_id]["space_m2"])
                plant_quantities[plant_id] += quantity

    await sio.emit('update_plant_quantities', plant_quantities, to=sid)

    garden_width = int(garden_area ** 0.5 * 10)
    garden_depth = int(garden_area ** 0.5 * 10)
    layout_engine = LayoutEngine(garden_width, garden_depth, PLANTS, COMPANION_DATA, sun_angle, row_width)
    layout_engine.generate_layout(plant_quantities)
    plant_positions = layout_engine.get_plant_positions()
    layout_scores = layout_engine.get_layout_scores()

    irrigation_engine = IrrigationLayoutEngine(plant_positions, PLANTS, IRRIGATION_KNOWLEDGE_BASE, garden_width, garden_depth)
    irrigation_layout = irrigation_engine.generate_layout()

    await sio.emit('update_layout', {
        "plant_positions": plant_positions,
        "irrigation_layout": irrigation_layout,
        "layout_scores": layout_scores
    })

# Mount the socket.io app
app.mount('/socket.io', socket_app)
