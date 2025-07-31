// ... (createVanillaStoreWithUndo is the same)

const gardenStore = createVanillaStoreWithUndo(
    { // Initial State
        // ...
    },
    (set) => ({ // Actions
        // ... (other actions)
        movePlantToGroup: (plantId, newGroupId) => set((state) => {
            const newWateringZones = { ...state.wateringZones };
            // Remove plant from old zone
            for (const zoneId in newWateringZones) {
                newWateringZones[zoneId] = newWateringZones[zoneId].filter(id => id !== plantId);
            }
            // Add plant to new zone
            if (!newWateringZones[newGroupId]) {
                newWateringZones[newGroupId] = [];
            }
            newWateringZones[newGroupId].push(plantId);

            return { wateringZones: newWateringZones };
        }),
    })
);

window.gardenStore = gardenStore;
