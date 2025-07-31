// In the render or selection logic
function createSelectionBox(object) {
    const box = new THREE.BoxHelper(object, 0xffff00); // Yellow box

    // Add scale handles (as small spheres)
    const handleGeometry = new THREE.SphereGeometry(0.5, 8, 8);
    const handleMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });

    const corners = [
        new THREE.Vector3(1, 1, 1), new THREE.Vector3(1, 1, -1),
        new THREE.Vector3(1, -1, 1), new THREE.Vector3(1, -1, -1),
        new THREE.Vector3(-1, 1, 1), new THREE.Vector3(-1, 1, -1),
        new THREE.Vector3(-1, -1, 1), new THREE.Vector3(-1, -1, -1),
    ];

    const boxSize = new THREE.Vector3();
    new THREE.Box3().setFromObject(object).getSize(boxSize);

    corners.forEach(corner => {
        const handle = new THREE.Mesh(handleGeometry, handleMaterial);
        handle.position.copy(object.position).add(corner.multiply(boxSize).multiplyScalar(0.5));
        handle.userData.isScaleHandle = true;
        box.add(handle);
    });

    return box;
}

// When an object is selected
if (intersects.length > 0) {
    // ...
    selectedObject = intersects[0].object;

    // Remove old selection box
    if (selectionBox) scene.remove(selectionBox);

    // Create and add new selection box
    selectionBox = createSelectionBox(selectedObject);
    scene.add(selectionBox);
}

// In the animate loop, make the selection box follow the object
if (selectionBox && selectedObject) {
    selectionBox.update();
}
