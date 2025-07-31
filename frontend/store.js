// ... (createVanillaStoreWithUndo is the same)

const gardenStore = createVanillaStoreWithUndo(
    { // Initial State
        // ...
    },
    (set) => ({ // Actions
        // ... (setInitialLayout, movePlant, moveGroup are the same)
        duplicatePlant: (plantId, newPosition) => set((state) => {
            const originalPlant = state.plants.find(p => p.id === plantId);
            if (!originalPlant) return state;

            const newPlant = {
                ...originalPlant,
                id: `plant_${Date.now()}`, // Simple unique ID
                ...newPosition
            };

            return { plants: [...state.plants, newPlant] };
        }),
    })
);

window.gardenStore = gardenStore;
