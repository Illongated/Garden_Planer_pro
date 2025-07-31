document.addEventListener('DOMContentLoaded', () => {
    // ... (setup is the same)
    const socket = io();
    // ...

    function onMouseUp(event) {
        if (isDragging && selectedObject) {
            isDragging = false;
            controls.enabled = true;

            const selectedBox = new THREE.Box3().setFromObject(selectedObject);
            let collision = false;
            plantGroup.children.forEach(child => {
                if (child !== selectedObject) {
                    const childBox = new THREE.Box3().setFromObject(child);
                    if (selectedBox.intersectsBox(childBox)) {
                        collision = true;
                    }
                }
            });

            if (collision) {
                selectedObject.position.copy(originalPosition);
            } else {
                // Position is valid, send update to server
                const currentLayout = plantGroup.children.map(child => ({
                    id: child.userData.id,
                    position: child.position
                }));

                socket.emit('update_object_position', {
                    object_id: selectedObject.userData.id,
                    new_position: selectedObject.position,
                    current_layout: currentLayout
                });
            }
        }
    }

    // ... (the rest of the file)
});
