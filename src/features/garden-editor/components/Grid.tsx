import React, { useCallback } from 'react';
import { Graphics } from '@pixi/react';
import { useEditorStore } from '../store/editorStore';

interface GridProps {
  width: number;
  height: number;
}

const GridComponent: React.FC<GridProps> = ({ width, height }) => {
  const { visible, size } = useEditorStore((state) => state.grid);

  const drawGrid = useCallback((g: any) => {
    g.clear();
    if (!visible || size <= 0) {
      return;
    }

    g.lineStyle(1, 0x000000, 0.1);

    // Draw vertical lines
    for (let i = 0; i < width; i += size) {
      g.moveTo(i, 0);
      g.lineTo(i, height);
    }

    // Draw horizontal lines
    for (let j = 0; j < height; j += size) {
      g.moveTo(0, j);
      g.lineTo(width, j);
    }
  }, [visible, size, width, height]);

  return <Graphics draw={drawGrid} zIndex={-1} />;
};

export default GridComponent;
