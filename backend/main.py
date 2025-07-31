// ...

@sio.on("scale_garden")
async def scale_garden(sid, data):
    factor = data.get("factor", 1.0)
    print(f"Received scale factor: {factor}")
    # Here, we would take the current layout, apply the scale factor,
    # and then re-run all the irrigation and scoring calculations.
    # This is a complex operation that requires a persistent state on the backend.
    await sio.emit('layout_updated_by_server', {"status": "success"}, to=sid)


@sio.on("move_plant_to_group")
async def move_plant_to_group(sid, data):
    plant_id = data.get("plant_id")
    new_group_id = data.get("new_group_id")
    print(f"Received request to move {plant_id} to group {new_group_id}")
    # Similar to scaling, this requires updating the layout state
    # and re-running all the calculations.
    await sio.emit('layout_updated_by_server', {"status": "success"}, to=sid)

// ...
