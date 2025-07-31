const { createStore } = window.zustand;

const createVanillaStoreWithUndo = (initialState, actions) => {
    const store = createStore((set) => ({
        ...initialState,
        ...actions(set),
        history: {
            past: [],
            future: [],
        },
    }));

    const originalSet = store.setState;

    store.setState = (update, replace, ...args) => {
        const { history, ...currentState } = store.getState();
        history.past.push(currentState);
        history.future = []; // Clear future on new action

        return originalSet(update, replace, ...args);
    };

    store.undo = () => {
        const { history, ...currentState } = store.getState();
        if (history.past.length > 0) {
            const previousState = history.past.pop();
            history.future.unshift(currentState);
            store.setState(previousState, true);
        }
    };

    store.redo = () => {
        const { history } = store.getState();
        if (history.future.length > 0) {
            const nextState = history.future.shift();
            history.past.push(store.getState());
            store.setState(nextState, true);
        }
    };

    return store;
};


const gardenStore = createVanillaStoreWithUndo(
    { // Initial State
        plants: [],
        irrigationLayout: {},
        layoutScores: {},
    },
    (set) => ({ // Actions
        setInitialLayout: (layout) => set({
            plants: layout.plant_positions.map((p, i) => ({ ...p, id: `plant_${i}`, x: p.x, y: 0, z: p.y })),
            irrigationLayout: layout.irrigation_layout,
            layoutScores: layout.layout_scores
        }),
        movePlant: (plantId, newPosition) => set((state) => ({
            plants: state.plants.map(p =>
                p.id === plantId ? { ...p, ...newPosition } : p
            ),
        })),
    })
);


window.gardenStore = gardenStore;
