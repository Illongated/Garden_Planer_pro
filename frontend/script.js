document.addEventListener('DOMContentLoaded', () => {
    // --- Socket.IO Setup ---
    const socket = io();
    const plantControlsDiv = document.getElementById('plant-controls');
    const gardenAreaInput = document.getElementById('garden-area');
    const irrigationTypeInput = document.getElementById('irrigation-type');
    const sunAngleInput = document.getElementById('sun-angle');
    const irrigationDashboard = document.getElementById('irrigation-dashboard');

    // --- Three.js Setup ---
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf4f4f4);
    const aspect = container.clientWidth / container.clientHeight;
    const d = 20;
    const camera = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 1, 1000);

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);

    camera.position.set(20, 20, 20);
    camera.lookAt(scene.position);
    controls.update();

    const plantGroup = new THREE.Group();
    scene.add(plantGroup);
    const irrigationGroup = new THREE.Group();
    scene.add(irrigationGroup);

    const textureLoader = new THREE.TextureLoader();

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // --- Event Listeners and Socket Handlers ---
    socket.on('connect', () => {
        console.log('Connected to server');
        sendGardenData();
    });

    socket.on('plant_data', (plants) => {
        plantControlsDiv.innerHTML = ''; // Clear existing controls
        for (const plantId in plants) {
            const plant = plants[plantId];
            const controlContainer = document.createElement('div');
            controlContainer.classList.add('plant-control');
            controlContainer.innerHTML = `
                <label>${plant.name}</label>
                <div class="priority-slider">
                    <span>Priority:</span>
                    <input type="range" id="${plantId}-priority" min="0" max="10" value="5">
                </div>
                <div class="quantity-input">
                    <span>Quantity:</span>
                    <input type="number" id="${plantId}-quantity" min="0" value="0" disabled>
                </div>
                <button id="${plantId}-lock" class="lock-btn">Lock</button>
            `;
            plantControlsDiv.appendChild(controlContainer);
        }
    });

    socket.on('update_plant_quantities', (quantities) => {
        for (const plantId in quantities) {
            const quantityInput = document.getElementById(`${plantId}-quantity`);
            if (quantityInput) {
                quantityInput.value = quantities[plantId];
            }
        }
    });

    socket.on('update_layout', (data) => {
        // ... (visualization code remains the same)

        // Update dashboard
        const { pipe_path_13mm, pipe_path_4mm, emitters, warnings } = data.irrigation_layout;
        const pipe_13mm_length = pipe_path_13mm.reduce((acc, _, i, arr) => i > 0 ? acc + arr[i-1].y - arr[i].y : 0, 0) / 10;
        const pipe_4mm_length = pipe_path_4mm.reduce((acc, path) => acc + Math.abs(path[1].x - path[0].x), 0) / 10;

        const summaryDiv = document.getElementById('dashboard-summary');
        summaryDiv.innerHTML = `
            <h4>Shopping List</h4>
            <ul>
                <li>13mm Pipe: ${pipe_13mm_length.toFixed(2)} m</li>
                <li>4mm Pipe: ${pipe_4mm_length.toFixed(2)} m</li>
                <li>Emitters: ${emitters.length}</li>
            </ul>
        `;

        const warningsDiv = document.getElementById('dashboard-warnings');
        if (warnings.length > 0) {
            warningsDiv.innerHTML = `
                <h4>Warnings</h4>
                <ul>
                    ${warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            `;
        } else {
            warningsDiv.innerHTML = '';
        }
    });

    function sendGardenData() {
        const plantPriorities = {};
        const plantLocks = {};
        const plantControls = plantControlsDiv.querySelectorAll('.plant-control');
        plantControls.forEach(control => {
            const plantId = control.querySelector('input[type="range"]').id.replace('-priority', '');
            plantPriorities[plantId] = parseInt(control.querySelector('input[type="range"]').value, 10);
            plantLocks[plantId] = control.querySelector('.lock-btn').classList.contains('locked');
        });

        socket.emit('update_garden_layout', {
            garden_area: parseFloat(gardenAreaInput.value),
            plant_priorities: plantPriorities,
            plant_locks: plantLocks
        });
    }

    // --- Event Listeners ---
    gardenAreaInput.addEventListener('input', sendGardenData);
    plantControlsDiv.addEventListener('input', sendGardenData);
    plantControlsDiv.addEventListener('click', (event) => {
        if (event.target.classList.contains('lock-btn')) {
            event.target.classList.toggle('locked');
            sendGardenData();
        }
    });
});
