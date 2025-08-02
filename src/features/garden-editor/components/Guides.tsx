import React, { useCallback } from 'react';
import { Graphics } from '@pixi/react';
import { useEditorStore } from '../store/editorStore';

interface GuidesProps {
  width: number;
  height: number;
}

const GuidesComponent: React.FC<GuidesProps> = ({ width, height }) => {
  const guides = useEditorStore((state) => state.guides);

  const drawGuides = useCallback((g: any) => {
    g.clear();
    if (!guides || guides.length === 0) {
      return;
    }

    g.lineStyle(1, 0xff0000, 0.8); // Red, slightly transparent

    guides.forEach(guide => {
      if (guide.axis === 'x') {
        g.moveTo(guide.position, 0);
        g.lineTo(guide.position, height);
      } else {
        g.moveTo(0, guide.position);
        g.lineTo(width, guide.position);
      }
    });
  }, [guides, width, height]);

  return <Graphics draw={drawGuides} />;
};

export default GuidesComponent;
