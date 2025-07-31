import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .irrigation_data import IRRIGATION_KNOWLEDGE_BASE
from .layout_engine import LayoutEngine

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

    plant_quantities = {plant_id: 0 for plant_id in PLANTS}
    remaining_area = garden_area

    # 1. Allocate locked plants first
    for plant_id, is_locked in plant_locks.items():
        if is_locked:
            quantity = 5
            area_needed = quantity * PLANTS[plant_id]["space_m2"]
            if remaining_area >= area_needed:
                plant_quantities[plant_id] = quantity
                remaining_area -= area_needed

    # 2. Distribute remaining area based on priority
    total_priority = sum(plant_priorities.values())
    if total_priority > 0:
        for plant_id, priority in plant_priorities.items():
            if not plant_locks.get(plant_id, False):
                proportion = priority / total_priority
                available_area_for_plant = remaining_area * proportion
                quantity = int(available_area_for_plant / PLANTS[plant_id]["space_m2"])
                plant_quantities[plant_id] += quantity

    await sio.emit('update_plant_quantities', plant_quantities, to=sid)

    # 3. Generate layout
    garden_width = int(garden_area ** 0.5 * 10) # in 10cm units
    garden_depth = int(garden_area ** 0.5 * 10)
    layout_engine = LayoutEngine(garden_width, garden_depth, PLANTS)
    layout_engine.generate_layout(plant_quantities)
    plant_positions = layout_engine.get_plant_positions()

    await sio.emit('update_layout', {"positions": plant_positions})


# ... (other event handlers remain the same for now)
@sio.on("calculate_irrigation")
async def calculate_irrigation(sid, data):
    recommended_system = "drip_emitter"
    explanation = IRRIGATION_KNOWLEDGE_BASE[recommended_system]

    await sio.emit("irrigation_results", {
        "recommended_system": recommended_system,
        "explanation": explanation
    })

@sio.on("calculate_shading")
async def calculate_shading(sid, data):
    sun_angle = data.get("sun_angle", 180)

    if 90 < sun_angle < 270:
        sunny_side = "South"
        shady_side = "North"
    else:
        sunny_side = "North"
        shady_side = "South"

    full_sun_plants = [p["name"] for p in PLANTS.values() if p["sun_preference"] == "full_sun"]
    partial_shade_plants = [p["name"] for p in PLANTS.values() if p["sun_preference"] == "partial_shade"]

    recommendations = {
        "sunny_side": {"side": sunny_side, "plants": full_sun_plants},
        "shady_side": {"side": shady_side, "plants": partial_shade_plants}
    }

    await sio.emit("shading_results", recommendations)


# Mount the socket.io app
app.mount('/socket.io', socket_app)
