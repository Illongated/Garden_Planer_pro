document.addEventListener('DOMContentLoaded', () => {
    // --- Socket.IO Setup ---
    const socket = io();
    const plantControlsDiv = document.getElementById('plant-controls');
    // ... (getting other elements)

    // --- Three.js Setup ---
    const container = document.getElementById('canvas-container');
    // ... (scene, camera, renderer setup)

    // --- Interaction Variables ---
    const raycaster = new THREE.Raycaster();
    // ... (other interaction variables)

    // --- RENDER/UPDATE LOOP ---
    function animate() {
        // ...
    }
    animate();

    // --- Event Listeners for Interaction ---
    container.addEventListener('mousedown', onMouseDown, false);
    // ... (other event listeners)

    // --- Socket Handlers ---
    socket.on('update_layout', (data) => {
        // ...
    });

    // ... (the rest of the file)
});
