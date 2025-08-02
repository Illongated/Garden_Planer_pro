import React, { useCallback } from 'react';
import { Graphics } from '@pixi/react';
import { PlantObject } from '../types';
import { mockPlantData } from './Palette';
import { useEditorStore } from '../store/editorStore';

interface PlantProps {
  plant: PlantObject;
}

const PlantComponent: React.FC<PlantProps> = ({ plant }) => {
  const { setSelection } = useEditorStore.getState();

  const draw = useCallback((g: any) => {
    const plantInfo = mockPlantData[plant.plantId as keyof typeof mockPlantData] || { color: 0xcccccc, radius: 20 };

    g.clear();
    g.beginFill(plantInfo.color);
    g.drawCircle(0, 0, plant.radius);
    g.endFill();

    if (plant.isSelected) {
      g.lineStyle(2, 0x3b82f6, 1);
      g.drawCircle(0, 0, plant.radius + 4);
    }
  }, [plant.radius, plant.plantId, plant.isSelected]);

  const handlePointerDown = (e: any) => {
    e.stopPropagation();
    const { selection, setSelection, setTransformation, objects } = useEditorStore.getState();

    const isAdditive = e.nativeEvent.metaKey || e.nativeEvent.ctrlKey;
    const isSelected = selection.includes(plant.id);

    if (!isAdditive && !isSelected) {
      setSelection([plant.id], { mode: 'replace' });
    } else if (isAdditive) {
      setSelection([plant.id], { mode: isSelected ? 'remove' : 'add' });
    }

    // After selection is handled, initiate a drag transformation for all selected items
    const newSelection = useEditorStore.getState().selection;
    if (newSelection.length > 0) {
      setTransformation({
        type: 'drag',
        ids: newSelection,
        initialObjects: newSelection.reduce((acc, id) => {
          acc[id] = objects[id];
          return acc;
        }, {} as Record<string, GardenObject>),
        startPointer: { x: e.data.global.x, y: e.data.global.y },
      });
    }
  };

  return (
    <Graphics
      x={plant.x}
      y={plant.y}
      rotation={plant.rotation * (Math.PI / 180)}
      draw={draw}
      interactive={true}
      pointerdown={handlePointerDown}
    />
  );
};

export default PlantComponent;
