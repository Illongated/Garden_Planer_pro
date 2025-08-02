import { GardenObject } from "../types";

/**
 * Calculates the smallest axis-aligned bounding box that contains all the given objects.
 * This does not account for object rotation.
 * @param objects An array of GardenObjects.
 * @returns A bounding box { x, y, width, height }.
 */
export const getBoundingBox = (objects: GardenObject[]): { x: number, y: number, width: number, height: number } => {
    if (objects.length === 0) {
        return { x: 0, y: 0, width: 100, height: 100 }; // Default size for an empty group
    }

    // Initialize with the bounds of the first object
    const first = objects[0];
    let minX = first.x - first.width / 2;
    let minY = first.y - first.height / 2;
    let maxX = first.x + first.width / 2;
    let maxY = first.y + first.height / 2;

    // Expand the bounds to include all other objects
    for (let i = 1; i < objects.length; i++) {
        const obj = objects[i];
        const objMinX = obj.x - obj.width / 2;
        const objMinY = obj.y - obj.height / 2;
        const objMaxX = obj.x + obj.width / 2;
        const objMaxY = obj.y + obj.height / 2;

        minX = Math.min(minX, objMinX);
        minY = Math.min(minY, objMinY);
        maxX = Math.max(maxX, objMaxX);
        maxY = Math.max(maxY, objMaxY);
    }

    return {
        x: (minX + maxX) / 2, // Center X
        y: (minY + maxY) / 2, // Center Y
        width: maxX - minX,
        height: maxY - minY,
    };
};
