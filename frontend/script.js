class GardenPlanner {
    constructor() {
        // DOM Elements
        this.gardenAreaInput = document.getElementById('garden-area-input');
        this.sunAngleSlider = document.getElementById('sun-angle-slider');
        this.sunAngleValue = document.getElementById('sun-angle-value');
        this.plantSlidersContainer = document.getElementById('plant-sliders-container');
        this.irrigationTypeSelect = document.getElementById('irrigation-type-select');
        this.wateringTimeInput = document.getElementById('watering-time-input');
        this.canvasContainer = document.getElementById('canvas-container');
        this.resultsContent = document.getElementById('results-content');

        // State
        this.plants = {};
        this.plantColors = {};
        this.irrigationKnowledgeBase = {};
        this.gardenArea = parseFloat(this.gardenAreaInput.value);
        this.plantQuantities = {};

        // Throttling for socket events
        this.updateTimeout = null;

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
        this.updateAllSlidersMax();
        this.requestLayoutUpdate();
    }

    updateAllSlidersMax() {
        let usedArea = Object.entries(this.plantQuantities).reduce((acc, [id, qty]) => acc + qty * this.plants[id].space_m2, 0);
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
            this.socket.emit('update_garden_layout', {
                garden_area: this.gardenArea,
                plant_quantities: this.plantQuantities,
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

        this.camera = new THREE.PerspectiveCamera(50, this.canvasContainer.clientWidth / this.canvasContainer.clientHeight, 0.1, 1000);
        this.camera.position.set(10, 20, 20);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.canvasContainer.clientWidth, this.canvasContainer.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.canvasContainer.appendChild(this.renderer.domElement);

        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        this.scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
        dirLight.position.set(10, 15, 5);
        this.scene.add(dirLight);

        this.plantMeshes = new THREE.Group();
        this.scene.add(this.plantMeshes);

        this.animate();
    }

    renderScene({ plant_positions, sun_map, diagnostics }) {
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
        this.scene.add(this.ground);

        // --- Plant Meshes ---
        this.plantMeshes.clear();
        plant_positions.forEach(pos => {
            const plantData = this.plants[pos.plant_id];
            const size = Math.sqrt(plantData.space_m2);
            const geometry = new THREE.BoxGeometry(size, size * 1.5, size);
            const material = new THREE.MeshStandardMaterial({ color: this.plantColors[pos.plant_id] });

            const cube = new THREE.Mesh(geometry, material);
            cube.position.set(
                (pos.x / 10) + size / 2 - gardenDim / 2,
                (size * 1.5) / 2,
                (pos.y / 10) + size / 2 - gardenDim / 2
            );
            this.plantMeshes.add(cube);
        });

        this.controls.target.set(0, 0, 0);
        this.camera.position.set(gardenDim, gardenDim * 1.5, gardenDim);
    }

    onWindowResize() {
        this.camera.aspect = this.canvasContainer.clientWidth / this.canvasContainer.clientHeight;
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
