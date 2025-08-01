class GardenPlanner {
    constructor() {
        // DOM Elements
        this.gardenAreaInput = document.getElementById('garden-area-input');
        this.sunAngleSlider = document.getElementById('sun-angle-slider');
        this.sunAngleValue = document.getElementById('sun-angle-value');
        this.plantSlidersContainer = document.getElementById('plant-sliders-container');
        this.paletteContainer = document.getElementById('palette-container');
        this.irrigationTypeSelect = document.getElementById('irrigation-type-select');
        this.wateringTimeInput = document.getElementById('watering-time-input');
        this.canvasContainer = document.getElementById('canvas-container');
        this.resultsContent = document.getElementById('results-content');

        // State
        this.plants = {};
        this.plantColors = {};
        this.irrigationKnowledgeBase = {};
        this.gardenArea = parseFloat(this.gardenAreaInput.value);
        this.plantQuantities = {}; // Total desired quantity from sliders
        this.placedPlants = new Map(); // Plants actually on the canvas map<instanceId, {plantId, x, y, mesh}>
        this.nextInstanceId = 0;

        // Drag & Drop State
        this.draggedPlantInfo = null; // { plantId, isNew: true } or { instanceId, isNew: false }
        this.draggedElement = null; // The visual element being dragged

        // Throttling for socket events
        this.updateTimeout = null;

        // Raycasting for object interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        // Initialize
        this.initSocket();
        this.bindEventListeners();
        this.initThreeJS();
    }

    initSocket() {
        this.socket = io({ transports: ["websocket"] });

        this.socket.on('connect', () => console.log("Connecté au serveur via Socket.IO"));

        this.socket.on('plant_data', (data) => {
            this.plants = data;
            this.assignPlantColors();
            this.initializePlantQuantities();
            this.renderPlantSliders();
        });

        this.socket.on('irrigation_knowledge_base', (data) => {
            this.irrigationKnowledgeBase = data;
            this.renderIrrigationOptions();
        });

        this.socket.on('update_layout', (data) => {
            this.renderResults(data);
            this.renderScene(data);
        });
    }

    bindEventListeners() {
        this.gardenAreaInput.addEventListener('input', () => {
            this.gardenArea = parseFloat(this.gardenAreaInput.value);
            this.updateAllSlidersMax();
            this.requestLayoutUpdate();
        });

        this.sunAngleSlider.addEventListener('input', () => {
            this.sunAngleValue.textContent = `${this.sunAngleSlider.value}°`;
            this.requestLayoutUpdate();
        });

        this.irrigationTypeSelect.addEventListener('change', () => this.requestLayoutUpdate());
        this.wateringTimeInput.addEventListener('input', () => this.requestLayoutUpdate());

        window.addEventListener('resize', () => this.onWindowResize());

        // --- Drag and Drop Listeners ---
        this.onDragMove = this.onDragMove.bind(this);
        this.onDragEnd = this.onDragEnd.bind(this);
        this.paletteContainer.addEventListener('mousedown', (e) => this.onPaletteDragStart(e));
        this.canvasContainer.addEventListener('mousedown', (e) => this.onCanvasDragStart(e));
    }

    // --- Drag and Drop Handlers ---

    onPaletteDragStart(event) {
        if (event.target.classList.contains('palette-plant')) {
            event.preventDefault();
            const plantId = event.target.dataset.plantId;
            this.draggedPlantInfo = { plantId, isNew: true };

            this.draggedElement = event.target.cloneNode(true);
            this.draggedElement.classList.add('dragging');
            document.body.appendChild(this.draggedElement);
            this.draggedElement.style.left = `${event.clientX - 25}px`;
            this.draggedElement.style.top = `${event.clientY - 25}px`;

            window.addEventListener('mousemove', this.onDragMove);
            window.addEventListener('mouseup', this.onDragEnd);
        }
    }

    onCanvasDragStart(event) {
        event.preventDefault();
        const groundPlane = this.scene.getObjectByName("ground");
        if (!groundPlane) return;

        const pos = this.getCanvasIntersection(event);
        if (!pos) return;

        // Check if we clicked on an existing plant
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.plantMeshes.children);

        if (intersects.length > 0) {
            const clickedMesh = intersects[0].object;
            const instanceId = clickedMesh.userData.instanceId;
            if (instanceId !== undefined) {
                this.draggedPlantInfo = { instanceId, isNew: false };
                this.draggedPlantInfo.mesh = clickedMesh; // Keep a direct reference
                this.controls.enabled = false; // Disable camera pan/zoom while dragging plant

                window.addEventListener('mousemove', this.onDragMove);
                window.addEventListener('mouseup', this.onDragEnd);
            }
        }
    }


    onDragMove(event) {
        if (!this.draggedPlantInfo) return;
        event.preventDefault();

        // If dragging from palette, move the icon
        if (this.draggedElement) {
            this.draggedElement.style.left = `${event.clientX - 25}px`;
            this.draggedElement.style.top = `${event.clientY - 25}px`;
        }

        // Get intersection with ground plane
        const intersection = this.getCanvasIntersection(event);
        if (intersection) {
            // If dragging an existing mesh, move it in real-time
            if (this.draggedPlantInfo.mesh) {
                const gardenDim = Math.sqrt(this.gardenArea);
                this.draggedPlantInfo.mesh.position.x = intersection.x;
                this.draggedPlantInfo.mesh.position.z = intersection.z;

                // Throttled update to re-calculate pipes while dragging
                this.requestLayoutUpdate();
            }
        }
    }

    onDragEnd(event) {
        if (!this.draggedPlantInfo) return;
        event.preventDefault();

        this.controls.enabled = true;

        const intersection = this.getCanvasIntersection(event);

        if (intersection) { // We dropped on the canvas
            const gardenDim = Math.sqrt(this.gardenArea);
            const x = intersection.x + gardenDim / 2;
            const z = intersection.z + gardenDim / 2;

            if (this.draggedPlantInfo.isNew) {
                // Convert from world coords back to grid coords for backend
                this.addPlantToScene(this.draggedPlantInfo.plantId, { x: x * 10, y: z * 10 });
            } else {
                this.movePlantOnScene(this.draggedPlantInfo.instanceId, { x: x * 10, y: z * 10 });
            }
        } else {
            // If we didn't drop on a valid location, and it was an existing plant, snap it back
            if (!this.draggedPlantInfo.isNew) {
                const plant = this.placedPlants.get(this.draggedPlantInfo.instanceId);
                if (plant) this.updateMeshPosition(plant.mesh, plant.x, plant.y);
            }
        }

        // Cleanup
        if (this.draggedElement) {
            document.body.removeChild(this.draggedElement);
        }
        this.draggedPlantInfo = null;
        this.draggedElement = null;
        window.removeEventListener('mousemove', this.onDragMove);
        window.removeEventListener('mouseup', this.onDragEnd);

        this.renderPalette();
        this.requestLayoutUpdate(); // Notify backend of the change
    }

    // --- D&D Helper Methods ---

    getCanvasIntersection(event) {
        const rect = this.canvasContainer.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const groundPlane = this.scene.getObjectByName("ground");
        if (!groundPlane) return null;

        const intersects = this.raycaster.intersectObject(groundPlane);
        return intersects.length > 0 ? intersects[0].point : null;
    }

    addPlantToScene(plantId, pos) {
        const instanceId = this.nextInstanceId++;
        const plantData = this.plants[plantId];
        const size = Math.sqrt(plantData.space_m2);
        const geometry = new THREE.BoxGeometry(size, size * 1.5, size);
        const material = new THREE.MeshStandardMaterial({ color: this.plantColors[plantId] });
        const mesh = new THREE.Mesh(geometry, material);

        mesh.userData.instanceId = instanceId;
        mesh.userData.isProcedural = false; // Manually placed

        this.plantMeshes.add(mesh);
        this.placedPlants.set(instanceId, { plantId, x: pos.x, y: pos.y, mesh });
        this.updateMeshPosition(mesh, pos.x, pos.y);
    }

    movePlantOnScene(instanceId, pos) {
        const plant = this.placedPlants.get(instanceId);
        if (plant) {
            plant.x = pos.x;
            plant.y = pos.y;
            this.updateMeshPosition(plant.mesh, pos.x, pos.y);
        }
    }

    updateMeshPosition(mesh, gridX, gridY) {
        const gardenDim = Math.sqrt(this.gardenArea);
        const plantData = this.plants[mesh.userData.plantId || this.placedPlants.get(mesh.userData.instanceId).plantId];
        const size = Math.sqrt(plantData.space_m2);

        mesh.position.set(
            (gridX / 10) - gardenDim / 2 + size / 2,
            (size * 1.5) / 2,
            (gridY / 10) - gardenDim / 2 + size / 2
        );
    }

    assignPlantColors() {
        const colors = [0x8BC34A, 0xFFC107, 0x03A9F4, 0xE91E63, 0x9C27B0, 0x4CAF50];
        let i = 0;
        for(const plantId in this.plants) {
            this.plantColors[plantId] = colors[i % colors.length];
            i++;
        }
    }

    initializePlantQuantities() {
        for (const plantId in this.plants) {
            this.plantQuantities[plantId] = 0;
        }
        this.renderPalette();
    }

    renderPalette() {
        this.paletteContainer.innerHTML = '';
        let availablePlants = 0;

        for (const plantId in this.plantQuantities) {
            const total = this.plantQuantities[plantId];
            const placedCount = Array.from(this.placedPlants.values()).filter(p => p.plantId === plantId).length;
            const available = total - placedCount;

            if (available > 0) {
                 availablePlants += available;
                for (let i = 0; i < available; i++) {
                    const plant = this.plants[plantId];
                    const el = document.createElement('div');
                    el.className = 'palette-plant';
                    el.dataset.plantId = plantId;
                    el.style.backgroundColor = `#${this.plantColors[plantId].toString(16)}`;
                    el.textContent = plant.name.substring(0, 1);
                    el.title = `Placer ${plant.name}`;
                    this.paletteContainer.appendChild(el);
                }
            }
        }
        if (availablePlants === 0) {
             this.paletteContainer.innerHTML = `<p class="palette-placeholder">Ajustez les curseurs ci-dessus pour ajouter des plantes ici.</p>`;
        }
    }

    renderPlantSliders() {
        this.plantSlidersContainer.innerHTML = '';
        for (const plantId in this.plants) {
            const plant = this.plants[plantId];
            const sliderHTML = `
                <div class="plant-slider" id="slider-group-${plantId}">
                    <div class="plant-slider-header">
                        <label for="plant-slider-${plantId}">${plant.name}</label>
                        <span class="plant-count" id="plant-count-${plantId}">0</span>
                    </div>
                    <div class="slider-group">
                        <input type="range" id="plant-slider-${plantId}" min="0" value="0">
                    </div>
                    <div class="max-plant-info" id="max-plant-info-${plantId}"></div>
                </div>
            `;
            this.plantSlidersContainer.innerHTML += sliderHTML;
        }

        this.updateAllSlidersMax();

        for (const plantId in this.plants) {
            document.getElementById(`plant-slider-${plantId}`).addEventListener('input', () => this.handleSliderChange(plantId));
        }
    }

    handleSliderChange(changedPlantId) {
        const slider = document.getElementById(`plant-slider-${changedPlantId}`);
        this.plantQuantities[changedPlantId] = parseInt(slider.value);
        document.getElementById(`plant-count-${changedPlantId}`).textContent = slider.value;

        // Ensure we don't have more plants placed than the slider allows
        const placedCount = Array.from(this.placedPlants.values()).filter(p => p.plantId === changedPlantId).length;
        if (placedCount > this.plantQuantities[changedPlantId]) {
            // This is a simplification. A real implementation might need to
            // intelligently remove plants from the canvas. For now, we just log it.
            console.warn(`Plus de ${this.plants[changedPlantId].name} placés que permis. Ajustement nécessaire.`);
        }

        this.renderPalette();
        this.updateAllSlidersMax();
        this.requestLayoutUpdate();
    }

    updateAllSlidersMax() {
        // Used area is now calculated based on plants actually placed on the canvas
        let usedArea = Array.from(this.placedPlants.values()).reduce((acc, p) => acc + this.plants[p.plantId].space_m2, 0);
        const remainingArea = this.gardenArea - usedArea;
        this.gardenAreaInput.style.backgroundColor = remainingArea < 0 ? '#FFCDD2' : 'white';

        for (const plantId in this.plants) {
            const plant = this.plants[plantId];
            const currentQuantity = this.plantQuantities[plantId];
            const maxForThisPlant = currentQuantity + (plant.space_m2 > 0 ? Math.floor(remainingArea / plant.space_m2) : 0);

            const slider = document.getElementById(`plant-slider-${plantId}`);
            if (slider) slider.max = Math.max(currentQuantity, maxForThisPlant);

            const maxInfo = document.getElementById(`max-plant-info-${plantId}`);
            if(maxInfo) maxInfo.textContent = `Max Total: ${plant.space_m2 > 0 ? Math.floor(this.gardenArea / plant.space_m2) : 'N/A'}`;
        }
    }

    renderIrrigationOptions() {
        for (const typeId in this.irrigationKnowledgeBase) {
            this.irrigationTypeSelect.add(new Option(this.irrigationKnowledgeBase[typeId].name, typeId));
        }
    }

    requestLayoutUpdate() {
        clearTimeout(this.updateTimeout);
        this.updateTimeout = setTimeout(() => {
            // Serialize placedPlants map for backend
            const placed_plants = Array.from(this.placedPlants.entries()).map(([id, p]) => ({
                instance_id: id,
                plant_id: p.plantId,
                x: p.x,
                y: p.y
            }));

            this.socket.emit('update_garden_layout', {
                garden_area: this.gardenArea,
                plant_quantities: this.plantQuantities,
                placed_plants: placed_plants, // Send manually placed plants
                sun_angle: parseInt(this.sunAngleSlider.value),
                irrigation_type: this.irrigationTypeSelect.value,
                watering_time: parseInt(this.wateringTimeInput.value)
            });
        }, 250);
    }

    renderResults(data) {
        const { irrigation_layout, layout_scores } = data;
        this.resultsContent.innerHTML = ''; // Clear previous results

        // Irrigation Summary Card
        const summary = irrigation_layout.summary;
        this.resultsContent.innerHTML += `
            <div class="result-card">
                <h3>Résumé de l'Irrigation</h3>
                <p>Pompe recommandée: <span class="value">${summary.recommended_pump}</span></p>
                <p>Débit requis: <span class="value">${summary.required_flow_rate_lph} L/h</span> (pour ${summary.watering_time_min} min)</p>
                <p>Longeur totale de tuyau: <span class="value">${summary.total_pipe_length_m} m</span></p>
            </div>`;

        // Layout Scores Card
        this.resultsContent.innerHTML += `
            <div class="result-card">
                <h3>Qualité de l'agencement</h3>
                <p>Score d'ensoleillement: <span class="value">${(layout_scores.sun * 100).toFixed(0)}%</span></p>
                <p>Score de compagnonnage: <span class="value">${(layout_scores.companion * 100).toFixed(0)}%</span></p>
            </div>`;

        // Irrigation Zones Cards
        for(const zone_name in irrigation_layout.zones) {
            const zone = irrigation_layout.zones[zone_name];
            const plant_names = zone.plant_ids.map(id => this.plants[id].name).join(', ');
            this.resultsContent.innerHTML += `
            <div class="result-card">
                <h3>Zone d'irrigation: ${zone_name.charAt(0).toUpperCase() + zone_name.slice(1)}</h3>
                <p>Cultures: ${plant_names}</p>
                <p>Besoin en eau: <span class="value">${zone.water_needs_lph} L/h</span></p>
                <p>Tuyau estimé: <span class="value">${zone.estimated_pipe_m} m</span></p>
            </div>`;
        }
    }

    // --- Three.js Methods ---
    initThreeJS() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xF4F7F5);

        // Use OrthographicCamera for an isometric view
        const aspect = this.canvasContainer.clientWidth / this.canvasContainer.clientHeight;
        const frustumSize = 20;
        this.camera = new THREE.OrthographicCamera(frustumSize * aspect / -2, frustumSize * aspect / 2, frustumSize / 2, frustumSize / -2, 1, 1000);
        this.camera.position.set(10, 20, 10); // Positioned for a top-down isometric angle
        this.camera.lookAt(0, 0, 0);


        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.canvasContainer.clientWidth, this.canvasContainer.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.canvasContainer.appendChild(this.renderer.domElement);

        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        // Lock to a top-down view
        this.controls.enableRotate = false;
        this.controls.mouseButtons = {
            LEFT: THREE.MOUSE.PAN,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.PAN // Using right for pan as well, common in CAD
        };


        this.scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
        dirLight.position.set(10, 15, 5);
        this.scene.add(dirLight);

        this.plantMeshes = new THREE.Group();
        this.scene.add(this.plantMeshes);

        this.pipeMeshes = new THREE.Group();
        this.scene.add(this.pipeMeshes);

        this.animate();
    }

    renderScene({ plant_positions, sun_map, diagnostics, irrigation_layout }) {
        this.renderPipes(irrigation_layout);

        const gardenDim = Math.sqrt(this.gardenArea);
        const gardenWidthDm = diagnostics.garden_dimensions_dm.split('x')[0];
        const gardenDepthDm = diagnostics.garden_dimensions_dm.split('x')[1];

        // --- Ground Plane with Sun Map ---
        if (this.ground) this.scene.remove(this.ground);
        const groundGeometry = new THREE.PlaneGeometry(gardenDim, gardenDim, gardenWidthDm -1, gardenDepthDm - 1);

        const sunData = new Uint8Array(sun_map.flat().length * 3);
        const sunColors = sun_map.flat().map(intensity => new THREE.Color().setHSL(0.17, 1.0, intensity * 0.4 + 0.1)); // yellow-green to dark green
        sunColors.forEach((c, i) => c.toArray(sunData, i * 3));

        const sunTexture = new THREE.DataTexture(sunData, gardenWidthDm, gardenDepthDm, THREE.RGBFormat);
        sunTexture.needsUpdate = true;

        const groundMaterial = new THREE.MeshStandardMaterial({ map: sunTexture, side: THREE.DoubleSide });
        this.ground = new THREE.Mesh(groundGeometry, groundMaterial);
        this.ground.rotation.x = -Math.PI / 2;
        this.ground.name = "ground"; // Name the ground for raycasting
        this.scene.add(this.ground);

        // --- Plant Meshes ---
        // Clear only procedurally-placed plants before re-drawing them
        // Iterate backwards to safely remove items from the collection
        for (let i = this.plantMeshes.children.length - 1; i >= 0; i--) {
            const child = this.plantMeshes.children[i];
            if (child.userData.isProcedural) {
                this.plantMeshes.remove(child);
            }
        }

        plant_positions.forEach(pos => {
            // Only draw the plants that are NOT manually placed by the user
            if (!pos.is_manual) {
                const plantData = this.plants[pos.plant_id];
                const size = Math.sqrt(plantData.space_m2);
                const geometry = new THREE.BoxGeometry(size, size * 1.5, size);
                const material = new THREE.MeshStandardMaterial({ color: this.plantColors[pos.plant_id] });

                const cube = new THREE.Mesh(geometry, material);
                cube.userData.isProcedural = true; // Flag for future clearing

                this.updateMeshPosition(cube, pos.x, pos.y);
                this.plantMeshes.add(cube);
            }
        });

        // Adjust camera zoom to fit the garden, instead of moving the camera
        const gardenSize = Math.max(gardenDim, 1); // Avoid division by zero
        this.camera.zoom = 18 / gardenSize;
        this.camera.updateProjectionMatrix();
        this.controls.target.set(0, 0, 0);
    }

    renderPipes(irrigation_layout) {
        // Clear existing pipes
        while(this.pipeMeshes.children.length > 0){
            this.pipeMeshes.remove(this.pipeMeshes.children[0]);
        }

        const gardenDim = Math.sqrt(this.gardenArea);
        const pipeMaterial = new THREE.LineBasicMaterial({ color: 0x0077FF, linewidth: 2 });

        for (const zoneName in irrigation_layout.zones) {
            const zone = irrigation_layout.zones[zoneName];
            if (zone.path && zone.path.length > 1) {
                const points = zone.path.map(p => {
                    const x = (p.x / 10) - gardenDim / 2;
                    const y = 0.1; // Slightly above the ground
                    const z = (p.y / 10) - gardenDim / 2;
                    return new THREE.Vector3(x, y, z);
                });

                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const pipeLine = new THREE.Line(geometry, pipeMaterial);
                this.pipeMeshes.add(pipeLine);
            }
        }
    }

    onWindowResize() {
        const aspect = this.canvasContainer.clientWidth / this.canvasContainer.clientHeight;
        const frustumSize = 20;
        this.camera.left = frustumSize * aspect / -2;
        this.camera.right = frustumSize * aspect / 2;
        this.camera.top = frustumSize / 2;
        this.camera.bottom = frustumSize / -2;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.canvasContainer.clientWidth, this.canvasContainer.clientHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new GardenPlanner();
});
