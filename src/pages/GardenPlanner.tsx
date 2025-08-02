import { useState } from 'react';
import { DndContext, DragEndEvent } from '@dnd-kit/core';
import { DroppedPlant, PlantCatalog } from '@/types';
import PlantPalette from '@/features/gardenPlanner/components/PlantPalette';
import GardenCanvas from '@/features/gardenPlanner/components/GardenCanvas';

const GardenPlanner = () => {
  const [droppedPlants, setDroppedPlants] = useState<DroppedPlant[]>([]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { over, active } = event;

    if (over && over.id === 'garden-canvas') {
      const plant = active.data.current?.plant as PlantCatalog;
      if (plant) {
        // In a real app, you might want to adjust the drop position
        // relative to the canvas.
        const newPlant: DroppedPlant = {
          id: `${plant.id}-${new Date().getTime()}`,
          plant,
          position: {
            x: event.delta.x,
            y: event.delta.y,
          },
        };
        setDroppedPlants((prev) => [...prev, newPlant]);
      }
    }
  };

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-[350px_1fr] h-[calc(100vh-4rem)]">
        <aside className="h-full">
          <PlantPalette />
        </aside>
        <main className="h-full p-4">
          <GardenCanvas droppedPlants={droppedPlants} />
        </main>
      </div>
    </DndContext>
  );
};

export default GardenPlanner;
