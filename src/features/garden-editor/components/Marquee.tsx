import React, { useCallback } from 'react';
import { Graphics } from '@pixi/react';
import { useEditorStore } from '../store/editorStore';

const MarqueeComponent: React.FC = () => {
  const marquee = useEditorStore((state) => state.marquee);

  const drawMarquee = useCallback((g: any) => {
    g.clear();
    if (!marquee || !marquee.visible) {
      return;
    }

    g.beginFill(0x3b82f6, 0.2); // Tailwind's blue-500 with 20% opacity
    g.lineStyle(1, 0x3b82f6, 0.8); // Tailwind's blue-500 with 80% opacity
    g.drawRect(marquee.x, marquee.y, marquee.width, marquee.height);
    g.endFill();
  }, [marquee]);

  return <Graphics draw={drawMarquee} />;
};

export default MarqueeComponent;
