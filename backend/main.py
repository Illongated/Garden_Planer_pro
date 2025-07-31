import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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

# Mount the frontend directory to serve static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

@sio.event
async def connect(sid, environ):
    print(f"connect {sid}")
    # Send initial plant data
    await sio.emit('plant_data', PLANTS, to=sid)


@sio.event
async def disconnect(sid):
    print(f"disconnect {sid}")


@sio.on("update_garden_area")
async def update_garden_area(sid, data):
    area = data.get("area", 0)
    if area > 0:
        max_plants = {
            plant_id: {"max": int(area / plant_info["space_m2"])}
            for plant_id, plant_info in PLANTS.items()
        }
        await sio.emit('update_max_plants', max_plants, to=sid)

@sio.on("update_plant_count")
async def update_plant_count(sid, data):
    garden_area = data.get("garden_area", 0)
    plant_counts = data.get("plant_counts", {})
    irrigation_type = data.get("irrigation_type", "drip")

    if garden_area > 0:
        used_area = 0
        total_flow_rate = 0
        pipe_length = 0
        for plant_id, count in plant_counts.items():
            used_area += count * PLANTS[plant_id]["space_m2"]
            total_flow_rate += count * PLANTS[plant_id]["water_L_per_hour"]
            if irrigation_type == "drip":
                pipe_length += count * 1 # 1 meter of pipe per plant
            else:
                pipe_length += count * 0.5 # 0.5 meters of pipe per plant for sprinklers

        remaining_area = garden_area - used_area

        if remaining_area < 0:
            remaining_area = 0

        updated_max_plants = {}
        for plant_id, plant_info in PLANTS.items():
            current_count = plant_counts.get(plant_id, 0)
            additional_plants = int(remaining_area / plant_info["space_m2"])
            updated_max_plants[plant_id] = {"max": current_count + additional_plants}

        await sio.emit('update_max_plants', updated_max_plants, to=sid)
        await sio.emit('pump_flow_results', {"flow_rate": total_flow_rate}, to=sid)
        await sio.emit('pipe_length_results', {"length": pipe_length}, to=sid)


@sio.on("calculate_irrigation")
async def calculate_irrigation(sid, data):
    area = data.get("area", 0)
    irrigation_type = data.get("irrigation_type", "drip")
    zones = 0
    if area > 0:
        if irrigation_type == "drip":
            zones = max(1, int(area / 20)) # 1 zone per 20 m2
        elif irrigation_type == "sprinkler":
            zones = max(1, int(area / 10)) # 1 zone per 10 m2

    await sio.emit("irrigation_results", {"zones": zones})

@sio.on("calculate_shading")
async def calculate_shading(sid, data):
    sun_angle = data.get("sun_angle", 180)

    # Determine sunny and shady sides
    if 90 < sun_angle < 270:
        sunny_side = "South"
        shady_side = "North"
    else:
        sunny_side = "North"
        shady_side = "South"

    # Recommend plants
    full_sun_plants = [p["name"] for p in PLANTS.values() if p["sun_preference"] == "full_sun"]
    partial_shade_plants = [p["name"] for p in PLANTS.values() if p["sun_preference"] == "partial_shade"]

    recommendations = {
        "sunny_side": {"side": sunny_side, "plants": full_sun_plants},
        "shady_side": {"side": shady_side, "plants": partial_shade_plants}
    }

    await sio.emit("shading_results", recommendations)

# Mount the socket.io app
app.mount('/socket.io', socket_app)
