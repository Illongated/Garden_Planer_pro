document.addEventListener('DOMContentLoaded', () => {
    // --- Socket.IO Setup ---
    const socket = io();
    const plantControlsDiv = document.getElementById('plant-controls');
    const gardenAreaInput = document.getElementById('garden-area');
    const irrigationTypeInput = document.getElementById('irrigation-type');
    const sunAngleInput = document.getElementById('sun-angle');
    const irrigationInfoDiv = document.getElementById('irrigation-info');

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

    const textureLoader = new THREE.TextureLoader();

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // --- Data Store ---
    let irrigationKnowledgeBase = {};

    // --- Event Listeners and Socket Handlers ---
    socket.on('connect', () => {
        console.log('Connected to server');
        sendGardenData();
    });

    socket.on('irrigation_knowledge_base', (data) => {
        irrigationKnowledgeBase = data;
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
        while(plantGroup.children.length > 0){
            plantGroup.remove(plantGroup.children[0]);
        }

        const placeholderTexture = textureLoader.load('/assets/placeholder.svg');
        const material = new THREE.MeshBasicMaterial({ map: placeholderTexture });

        data.positions.forEach(pos => {
            const geometry = new THREE.PlaneGeometry(2, 2);
            const plane = new THREE.Mesh(geometry, material);
            plane.position.set(pos.x, 0, pos.y);
            plane.rotation.x = -Math.PI / 2; // Orient the plane to be horizontal
            plantGroup.add(plane);
        });
    });

    socket.on('irrigation_results', (data) => {
        const { recommended_system, explanation } = data;
        irrigationInfoDiv.innerHTML = `
            <h3>Recommended System: ${explanation.name}</h3>
            <p>${explanation.description}</p>
            <p><strong>Water Efficiency:</strong> ${explanation.water_efficiency * 100}%</p>
        `;
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
