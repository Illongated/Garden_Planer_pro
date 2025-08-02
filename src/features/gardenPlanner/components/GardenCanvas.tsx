import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { DroppedPlant } from '@/types';

interface Props {
  droppedPlants: DroppedPlant[];
}

const GardenCanvas: React.FC<Props> = ({ droppedPlants }) => {
  const { setNodeRef } = useDroppable({
    id: 'garden-canvas',
  });

  return (
    <div
        ref={setNodeRef}
        className="w-full h-full relative bg-gray-100 dark:bg-gray-800 rounded-lg shadow-inner"
        style={{
            backgroundImage:
                'linear-gradient(rgba(0, 0, 0, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.1) 1px, transparent 1px)',
            backgroundSize: '20px 20px',
        }}
    >
      {droppedPlants.map(({ id, plant, position }) => (
        <div
          key={id}
          className="absolute cursor-move"
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
          }}
        >
          <img
            src={plant.image}
            alt={plant.name}
            title={`${plant.name} (${plant.variety})`}
            className="w-16 h-16 object-cover rounded-full border-4 border-green-500 shadow-lg hover:scale-110 transition-transform"
          />
        </div>
      ))}
       {!droppedPlants.length && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <p className="text-muted-foreground text-lg">Drag plants from the catalog and drop them here!</p>
            </div>
        )}
    </div>
  );
};

export default GardenCanvas;
