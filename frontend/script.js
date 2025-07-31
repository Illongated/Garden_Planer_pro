function onMouseUp(event) {
    if (isDragging && selectedObject && selectedObject.userData.type === 'plant') {
        // ... (collision detection)

        if (!collision) {
            // Check for cross-group movement
            const { wateringZones } = getState();
            let newGroupId = null;

            for (const zoneId in wateringZones) {
                const plantsInZone = getState().plants.filter(p => wateringZones[zoneId].includes(p.id));
                const zoneBox = new THREE.Box3();
                plantsInZone.forEach(p => {
                    const plantBox = new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(p.x, p.y, p.z), new THREE.Vector3(2, 2, 2));
                    zoneBox.union(plantBox);
                });

                if (zoneBox.containsPoint(selectedObject.position)) {
                    newGroupId = zoneId;
                    break;
                }
            }

            const oldGroupId = Object.keys(wateringZones).find(zoneId => wateringZones[zoneId].includes(selectedObject.userData.id));

            if (newGroupId && newGroupId !== oldGroupId) {
                if (confirm(`Move this plant to the group with water needs of ${newGroupId} L/h?`)) {
                    getState().movePlantToGroup(selectedObject.userData.id, newGroupId);
                } else {
                    selectedObject.position.copy(originalPosition); // Snap back if cancelled
                }
            } else {
                // Regular move
                getState().movePlant(selectedObject.userData.id, {
                    x: selectedObject.position.x,
                    y: selectedObject.position.y,
                    z: selectedObject.position.z
                });
            }
        }
        // ... (rest of mouse up)
    }
    // ... (rest of mouse up)
}
