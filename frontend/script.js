document.addEventListener('DOMContentLoaded', () => {
    // ... (setup is the same)
    const socket = io();
    const plantControlsDiv = document.getElementById('plant-controls');
    const gardenAreaInput = document.getElementById('garden-area');
    const sunAngleInput = document.getElementById('sun-angle');
    const rowWidthInput = document.getElementById('row-width');
    const rowWidthValue = document.getElementById('row-width-value');
    const irrigationDashboard = document.getElementById('irrigation-dashboard');
    const layoutScorecardDiv = document.getElementById('layout-scorecard');

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
    const zoneGroup = new THREE.Group();
    scene.add(zoneGroup);
    const textureLoader = new THREE.TextureLoader();
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    socket.on('connect', () => {
        console.log('Connected to server');
        sendGardenData();
    });
    socket.on('plant_data', (plants) => {
        // ... (same as before)
        plantControlsDiv.innerHTML = '';
        for (const plantId in plants) {
            const plant = plants[plantId];
            const controlContainer = document.createElement('div');
            controlContainer.classList.add('plant-control');
            controlContainer.innerHTML = `
                <label>${plant.name}</label>
                <div class="priority-slider"><span>Priority:</span><input type="range" id="${plantId}-priority" min="0" max="10" value="5"></div>
                <div class="quantity-input"><span>Quantity:</span><input type="number" id="${plantId}-quantity" min="0" value="0" disabled></div>
                <button id="${plantId}-lock" class="lock-btn">Lock</button>
            `;
            plantControlsDiv.appendChild(controlContainer);
        }
    });
    socket.on('update_plant_quantities', (quantities) => {
        // ... (same as before)
        for (const plantId in quantities) {
            const quantityInput = document.getElementById(`${plantId}-quantity`);
            if (quantityInput) {
                quantityInput.value = quantities[plantId];
            }
        }
    });

    socket.on('update_layout', (data) => {
        // ... (visualization code is the same)
        while(plantGroup.children.length > 0){ plantGroup.remove(plantGroup.children[0]); }
        while(irrigationGroup.children.length > 0){ irrigationGroup.remove(irrigationGroup.children[0]); }
        while(zoneGroup.children.length > 0){ zoneGroup.remove(zoneGroup.children[0]); }
        const placeholderTexture = textureLoader.load('/assets/placeholder.svg');
        const plantMaterial = new THREE.MeshBasicMaterial({ map: placeholderTexture });
        data.plant_positions.forEach(pos => {
            const geometry = new THREE.PlaneGeometry(2, 2);
            const plane = new THREE.Mesh(geometry, plantMaterial);
            plane.position.set(pos.x, 0.1, pos.y);
            plane.rotation.x = -Math.PI / 2;
            plantGroup.add(plane);
        });
        const zoneColors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0x00ffff, 0xff00ff];
        let colorIndex = 0;
        let dashboardHtml = '<h4>Shopping List</h4>';
        for (const zoneId in data.irrigation_layout.zones) {
            const zone = data.irrigation_layout.zones[zoneId];
            const zoneColor = new THREE.Color(zoneColors[colorIndex % zoneColors.length]);
            colorIndex++;
            zone.emitters.forEach(emitter => {
                const geometry = new THREE.PlaneGeometry(2, 2);
                const material = new THREE.MeshBasicMaterial({ color: zoneColor, transparent: true, opacity: 0.3 });
                const plane = new THREE.Mesh(geometry, material);
                plane.position.set(emitter.x, 0, emitter.y);
                plane.rotation.x = -Math.PI / 2;
                zoneGroup.add(plane);
            });
            const pipe13mmMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 3 });
            const pipe4mmMaterial = new THREE.LineBasicMaterial({ color: 0x333333, linewidth: 1 });
            const points13 = zone.pipe_path_13mm.map(p => new THREE.Vector3(p.x, 0.2, p.y));
            const geometry13 = new THREE.BufferGeometry().setFromPoints(points13);
            const line13 = new THREE.Line(geometry13, pipe13mmMaterial);
            irrigationGroup.add(line13);
            zone.pipe_path_4mm.forEach(path => {
                const points4 = path.map(p => new THREE.Vector3(p.x, 0.2, p.y));
                const geometry4 = new THREE.BufferGeometry().setFromPoints(points4);
                const line4 = new THREE.Line(geometry4, pipe4mmMaterial);
                irrigationGroup.add(line4);
            });
            const emitterTexture = textureLoader.load(`/assets/irrigation__${zone.emitter_type}.svg`);
            const emitterMaterial = new THREE.MeshBasicMaterial({ map: emitterTexture, transparent: true });
            zone.emitters.forEach(emitter => {
                const geometry = new THREE.PlaneGeometry(1, 1);
                const plane = new THREE.Mesh(geometry, emitterMaterial);
                plane.position.set(emitter.x, 0.3, emitter.y);
                plane.rotation.x = -Math.PI / 2;
                irrigationGroup.add(plane);
            });
            const pipe_13mm_length = zone.pipe_path_13mm.reduce((acc, _, i, arr) => i > 0 ? acc + Math.abs(arr[i-1].y - arr[i].y) : 0, 0) / 10;
            const pipe_4mm_length = zone.pipe_path_4mm.reduce((acc, path) => acc + Math.abs(path[1].x - path[0].x), 0) / 10;
            dashboardHtml += `
                <h5>Zone ${zoneId} (Water Needs: ${zoneId} L/h)</h5>
                <ul>
                    <li>Emitter Type: ${zone.emitter_type.replace('_', ' ')}</li>
                    <li>13mm Pipe: ${pipe_13mm_length.toFixed(2)} m</li>
                    <li>4mm Pipe: ${pipe_4mm_length.toFixed(2)} m</li>
                    <li>Emitters: ${zone.emitters.length}</li>
                </ul>
            `;
        }
        const summaryDiv = document.getElementById('dashboard-summary');
        summaryDiv.innerHTML = dashboardHtml;
        const warningsDiv = document.getElementById('dashboard-warnings');
        if (data.irrigation_layout.warnings.length > 0) {
            warningsDiv.innerHTML = `<h4>Warnings</h4><ul>${data.irrigation_layout.warnings.map(w => `<li>${w}</li>`).join('')}</ul>`;
        } else {
            warningsDiv.innerHTML = '';
        }

        // Update scorecard
        const { sun, accessibility, companion } = data.layout_scores;
        layoutScorecardDiv.innerHTML = `
            <ul>
                <li>Sunlight Score: ${(sun * 100).toFixed(0)}%</li>
                <li>Accessibility Score: ${(accessibility * 100).toFixed(0)}%</li>
                <li>Companion Score: ${(companion * 100).toFixed(0)}%</li>
            </ul>
        `;
    });

    function sendGardenData() {
        // ... (same as before)
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
            plant_locks: plantLocks,
            sun_angle: parseFloat(sunAngleInput.value),
            row_width: parseFloat(rowWidthInput.value) / 10
        });
    }

    // --- Event Listeners ---
    gardenAreaInput.addEventListener('input', sendGardenData);
    sunAngleInput.addEventListener('input', sendGardenData);
    rowWidthInput.addEventListener('input', () => {
        rowWidthValue.textContent = `${rowWidthInput.value} cm`;
        sendGardenData();
    });
    plantControlsDiv.addEventListener('input', sendGardenData);
    plantControlsDiv.addEventListener('click', (event) => {
        if (event.target.classList.contains('lock-btn')) {
            event.target.classList.toggle('locked');
            sendGardenData();
        }
    });
});
