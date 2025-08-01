document.addEventListener('store-ready', () => {
    // --- Socket.IO Setup ---
    const socket = io();
    const plantSlidersDiv = document.getElementById('plant-sliders');
    const plantLocksDiv = document.getElementById('plant-locks');

    function renderPlantControls(plants) {
        plantSlidersDiv.innerHTML = '';
        plantLocksDiv.innerHTML = '';

        for (const plantId in plants) {
            const plant = plants[plantId];

            // Slider
            const sliderLabel = document.createElement('label');
            sliderLabel.for = `${plantId}-slider`;
            sliderLabel.textContent = `${plant.name}:`;
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.id = `${plantId}-slider`;
            slider.min = 0;
            slider.max = 1;
            slider.step = 0.1;
            slider.value = 0.5; // Default value
            plantSlidersDiv.appendChild(sliderLabel);
            plantSlidersDiv.appendChild(slider);

            // Lock
            const lockLabel = document.createElement('label');
            lockLabel.for = `${plantId}-lock`;
            lockLabel.textContent = `Lock ${plant.name}:`;
            const lock = document.createElement('input');
            lock.type = 'checkbox';
            lock.id = `${plantId}-lock`;
            plantLocksDiv.appendChild(lockLabel);
            plantLocksDiv.appendChild(lock);
        }
    }

    // --- Three.js Setup ---
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);

    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

    const plantMeshes = {};

    function renderScene(plant_positions) {
        // Remove old plants
        for (const plantId in plantMeshes) {
            scene.remove(plantMeshes[plantId]);
            delete plantMeshes[plantId];
        }

        // Add new plants
        for (const plantId in plant_positions) {
            const pos = plant_positions[plantId];
            const cube = new THREE.Mesh(geometry, material);
            cube.position.set(pos.x / 10, 0, pos.y / 10); // Scale down for better viewing
            scene.add(cube);
            plantMeshes[plantId] = cube;
        }
    }

    camera.position.z = 5;

    // --- Interaction Variables ---
    const raycaster = new THREE.Raycaster();
    // ... (other interaction variables)

    // --- Event Handler for Mouse Down ---
    function onMouseDown(event) {
        // Placeholder for future implementation
    }

    // --- RENDER/UPDATE LOOP ---
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // --- Event Listeners for Interaction ---
    container.addEventListener('mousedown', onMouseDown, false);
    // ... (other event listeners)

    // --- Socket Handlers ---
    socket.on('connect', () => {
        console.log('Socket connected, requesting initial layout.');
        const gardenArea = document.getElementById('garden-area').value;
        const sunAngle = document.getElementById('sun-angle').value;
        const rowWidth = document.getElementById('row-width').value;
        const sunWeight = document.getElementById('sun-weight').value;
        const companionWeight = document.getElementById('companion-weight').value;

        socket.emit('update_garden_layout', {
            garden_area: parseFloat(gardenArea),
            plant_priorities: {}, // Sending empty for now
            plant_locks: {}, // Sending empty for now
            sun_angle: parseInt(sunAngle),
            row_width: parseFloat(rowWidth),
            layout_weights: {
                sun: parseFloat(sunWeight),
                companion: parseFloat(companionWeight),
            },
        });
    });

    socket.on('plant_data', (data) => {
        window.gardenStore.getState().setPlants(data);
    });

    socket.on('update_layout', (data) => {
        window.gardenStore.getState().setInitialLayout(data);
    });

    // --- Store Subscriptions ---
    window.gardenStore.subscribe((state) => {
        if (state.plants) {
            renderPlantControls(state.plants);
        }
        if (state.plant_positions) {
            renderScene(state.plant_positions);
        }
    });
});
