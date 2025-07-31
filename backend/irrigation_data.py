IRRIGATION_KNOWLEDGE_BASE = {
    "drip_emitter": {
        "name": "Drip Emitter",
        "water_efficiency": 0.9,
        "coverage_m2": 0.01,
        "flow_rate_L_per_hour": 4,
        "best_for": ["individual_plants", "rows", "containers"],
        "description": "Drip emitters deliver water slowly and directly to the base of the plant, minimizing evaporation and runoff. They are highly efficient and ideal for targeted watering."
    },
    "micro_sprayer": {
        "name": "Micro-Sprayer",
        "water_efficiency": 0.75,
        "coverage_m2": 0.5,
        "flow_rate_L_per_hour": 60,
        "best_for": ["dense_planting", "ground_cover"],
        "description": "Micro-sprayers produce a fine mist over a wider area than drip emitters. They are useful for watering groups of plants or areas where individual emitters are not practical."
    },
    "soaker_hose": {
        "name": "Soaker Hose",
        "water_efficiency": 0.95,
        "coverage_m2": 0.2, # Per meter of hose
        "flow_rate_L_per_hour": 20, # Per meter of hose
        "best_for": ["vegetable_gardens", "straight_rows"],
        "description": "Soaker hoses are made from a porous material that weeps water along its entire length. They are extremely efficient and excellent for watering long, straight rows of plants."
    }
}
