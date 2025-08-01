const createStore = window.zustandVanilla.default;

// A custom implementation of a store with undo/redo capabilities.
const createVanillaStoreWithUndo = (initializer) => {
    return createStore(initializer);
};


const gardenStore = createVanillaStoreWithUndo((set) => ({
    // Initial State
    plants: [],
    wateringZones: {},
    layoutScores: {},
    // Actions
    setInitialLayout: (layout) => set({
        ...layout
    }),
    movePlant: (plantId, newPosition) => set((state) => ({
        ...state,
        plant_positions: {
            ...state.plant_positions,
            [plantId]: newPosition,
        },
    })),
    moveGroup: (groupId, delta) => set((state) => ({
        ...state,
    })),
    duplicatePlant: (plantId, newPosition) => set((state) => ({
        ...state,
    })),
    scaleGarden: (factor) => set((state) => ({
        ...state,
    })),
    movePlantToGroup: (plantId, newGroupId) => set((state) => ({
        ...state,
    })),
    setPlants: (plants) => set({ plants }),
}));

window.gardenStore = gardenStore;
document.dispatchEvent(new Event('store-ready'));
