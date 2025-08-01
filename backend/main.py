import os
import math
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .irrigation_data import IRRIGATION_KNOWLEDGE_BASE
from .layout_engine import LayoutEngine
from .irrigation_layout_engine import IrrigationLayoutEngine
from .companion_data import COMPANION_DATA

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# --- Plant Data ---
PLANTS = {
    "tomatoes": {"name": "Tomates", "space_m2": 0.5, "water_L_per_hour": 5, "sun_preference": "full_sun"},
    "lettuce": {"name": "Laitue", "space_m2": 0.1, "water_L_per_hour": 2, "sun_preference": "partial_shade"},
    "carrots": {"name": "Carottes", "space_m2": 0.05, "water_L_per_hour": 1.5, "sun_preference": "full_sun"},
    "cucumbers": {"name": "Concombres", "space_m2": 0.75, "water_L_per_hour": 6, "sun_preference": "full_sun"},
    "peppers": {"name": "Poivrons", "space_m2": 0.4, "water_L_per_hour": 4, "sun_preference": "full_sun"},
    "beans": {"name": "Haricots", "space_m2": 0.15, "water_L_per_hour": 3, "sun_preference": "full_sun"},
}

# --- FastAPI & Socket.IO Setup ---
app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)
app.mount('/socket.io', socket_app)

# --- Static Files Mount ---
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

# --- Socket.IO Event Handlers ---
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('plant_data', PLANTS, to=sid)
    await sio.emit('irrigation_knowledge_base', IRRIGATION_KNOWLEDGE_BASE, to=sid)
    # Send an initial layout on connect
    await update_garden_layout(sid, {
        'garden_area': 20,
        'plant_quantities': {plant: 0 for plant in PLANTS},
        'sun_angle': 180,
        'irrigation_type': 'drip_emitter',
        'watering_time': 30
    })

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.on("update_garden_layout")
async def update_garden_layout(sid, data):
    """
    Main event handler that triggers all procedural engines based on frontend input.
    """
    # 1. Get data from frontend
    garden_area = data.get("garden_area", 10)
    plant_quantities = data.get("plant_quantities", {})
    sun_angle = data.get("sun_angle", 180)
    irrigation_type = data.get("irrigation_type", "drip_emitter")
    watering_time_min = data.get("watering_time", 30)

    # 2. Generate the intelligent plant layout
    garden_dim = math.sqrt(garden_area)
    garden_width_dm = int(garden_dim * 10)
    garden_depth_dm = int(garden_dim * 10)

    layout_engine = LayoutEngine(
        garden_width_dm,
        garden_depth_dm,
        PLANTS,
        COMPANION_DATA,
        sun_angle
    )
    layout_engine.generate_layout(plant_quantities)
    plant_positions = layout_engine.get_plant_positions()
    layout_scores = layout_engine.get_layout_scores()

    # 3. Generate the intelligent irrigation layout
    irrigation_engine = IrrigationLayoutEngine(
        plant_positions,
        PLANTS,
        IRRIGATION_KNOWLEDGE_BASE,
        irrigation_type,
        watering_time_min
    )
    irrigation_layout = irrigation_engine.generate_layout()

    # 4. Send the complete, updated layout to the frontend
    response_data = {
        "plant_positions": plant_positions,
        "irrigation_layout": irrigation_layout,
        "layout_scores": layout_scores,
        "sun_map": layout_engine.sun_map, # Add sun_map for frontend visualization
        "diagnostics": {
            "received_area": garden_area,
            "received_quantities": plant_quantities,
            "garden_dimensions_dm": f"{garden_width_dm}x{garden_depth_dm}"
        }
    }
    await sio.emit('update_layout', response_data, to=sid)
