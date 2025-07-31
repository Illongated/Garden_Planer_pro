document.addEventListener('DOMContentLoaded', () => {
    const { getState, setState, subscribe, undo, redo } = window.gardenStore;

    // ... (the rest of the script is the same)

    // --- Keyboard Listeners for Undo/Redo ---
    window.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.key === 'z') {
            event.preventDefault();
            undo();
        }
        if (event.ctrlKey && event.key === 'y') {
            event.preventDefault();
            redo();
        }
    });

    // ... (the rest of the file)
});
