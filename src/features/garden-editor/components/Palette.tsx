import React from 'react';

// In a real app, this would come from a database or API
export const mockPlantData = {
  tomato: { name: 'Tomato', radius: 30, color: 0xe53e3e },
  lettuce: { name: 'Lettuce', radius: 25, color: 0x48bb78 },
  carrot: { name: 'Carrot', radius: 15, color: 0xed8936 },
  basil: { name: 'Basil', radius: 20, color: 0x805ad5 },
  pepper: { name: 'Bell Pepper', radius: 28, color: 0x38a169 },
};

export type PlantId = keyof typeof mockPlantData;

const Palette = () => {
  const onDragStart = (event: React.DragEvent, plantId: PlantId) => {
    event.dataTransfer.setData('application/json', JSON.stringify({
      type: 'new-plant',
      plantId,
    }));
    event.dataTransfer.effectAllowed = 'copy';
  };

  return (
    <aside className="w-64 p-4 border-r bg-white dark:bg-gray-900 overflow-y-auto flex-shrink-0">
      <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">Plants</h2>
      <div className="space-y-3">
        {Object.entries(mockPlantData).map(([id, plant]) => (
          <div
            key={id}
            draggable
            onDragStart={(e) => onDragStart(e, id as PlantId)}
            className="p-3 border rounded-lg cursor-grab bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-3"
          >
            <div
              className="w-5 h-5 rounded-full"
              style={{ backgroundColor: `#${plant.color.toString(16)}` }}
            />
            <span className="font-medium text-gray-700 dark:text-gray-300">{plant.name}</span>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default Palette;
