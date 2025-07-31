document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const plantSliders = document.getElementById('plant-sliders');
    const gardenAreaInput = document.getElementById('garden-area');
    const irrigationTypeInput = document.getElementById('irrigation-type');
    const sunAngleInput = document.getElementById('sun-angle');
    const resultsDiv = document.getElementById('results');

    let irrigationZones = 0;
    let pumpFlowRate = 0;
    let pipeLength = 0;
    let shadingRecs = {};

    function updateResults() {
        let shadingHtml = '';
        if (shadingRecs.sunny_side) {
            shadingHtml = `
                <h3>Sunlight Recommendations</h3>
                <p><strong>${shadingRecs.sunny_side.side}-facing (Sunny):</strong> ${shadingRecs.sunny_side.plants.join(', ')}</p>
                <p><strong>${shadingRecs.shady_side.side}-facing (Shady):</strong> ${shadingRecs.shady_side.plants.join(', ')}</p>
            `;
        }

        resultsDiv.innerHTML = `
            <h3>Irrigation</h3>
            <p>Recommended Zones: ${irrigationZones}</p>
            <h3>Pump</h3>
            <p>Recommended Flow Rate: ${pumpFlowRate.toFixed(2)} L/h</p>
            <h3>Piping</h3>
            <p>Estimated Pipe Length: ${pipeLength.toFixed(2)} m</p>
            ${shadingHtml}
        `;
    }

    socket.on('connect', () => {
        console.log('Connected to server');
        sendGardenArea();
        sendIrrigationData();
        sendSunAngleData();
        updateResults();
    });

    socket.on('plant_data', (plants) => {
        plantSliders.innerHTML = ''; // Clear existing sliders
        for (const plantId in plants) {
            const plant = plants[plantId];
            const sliderContainer = document.createElement('div');
            sliderContainer.classList.add('plant-slider');
            sliderContainer.innerHTML = `
                <label for="${plantId}-slider">${plant.name}</label>
                <input type="range" id="${plantId}-slider" min="0" value="0">
                <span id="${plantId}-value">0</span>
            `;
            plantSliders.appendChild(sliderContainer);
        }
    });

    socket.on('update_max_plants', (maxPlants) => {
        for (const plantId in maxPlants) {
            const slider = document.getElementById(`${plantId}-slider`);
            if (slider) {
                if (slider.max != maxPlants[plantId].max) {
                    slider.max = maxPlants[plantId].max;
                }
            }
        }
    });

    socket.on('irrigation_results', (data) => {
        irrigationZones = data.zones;
        updateResults();
    });

    socket.on('pump_flow_results', (data) => {
        pumpFlowRate = data.flow_rate;
        updateResults();
    });

    socket.on('pipe_length_results', (data) => {
        pipeLength = data.length;
        updateResults();
    });

    socket.on('shading_results', (data) => {
        shadingRecs = data;
        updateResults();
    });

    function sendGardenArea() {
        const area = gardenAreaInput.value;
        socket.emit('update_garden_area', { area: parseFloat(area) });
    }

    function sendPlantCounts() {
        const plantCounts = {};
        const sliders = plantSliders.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            const plantId = slider.id.replace('-slider', '');
            plantCounts[plantId] = parseInt(slider.value, 10);
        });
        socket.emit('update_plant_count', {
            garden_area: parseFloat(gardenAreaInput.value),
            plant_counts: plantCounts,
            irrigation_type: irrigationTypeInput.value
        });
    }

    function sendIrrigationData() {
        socket.emit('calculate_irrigation', {
            area: parseFloat(gardenAreaInput.value),
            irrigation_type: irrigationTypeInput.value
        });
    }

    function sendSunAngleData() {
        socket.emit('calculate_shading', {
            sun_angle: parseFloat(sunAngleInput.value)
        });
    }

    gardenAreaInput.addEventListener('input', () => {
        sendGardenArea();
        sendPlantCounts();
        sendIrrigationData();
        sendSunAngleData();
    });

    irrigationTypeInput.addEventListener('change', () => {
        sendIrrigationData();
        sendPlantCounts();
    });

    sunAngleInput.addEventListener('input', sendSunAngleData);

    plantSliders.addEventListener('input', (event) => {
        if (event.target.type === 'range') {
            const plantId = event.target.id.replace('-slider', '');
            const valueSpan = document.getElementById(`${plantId}-value`);
            valueSpan.textContent = event.target.value;
            sendPlantCounts();
        }
    });
});
