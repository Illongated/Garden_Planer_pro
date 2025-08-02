import React, { useCallback } from 'react';
import { Container, Graphics } from '@pixi/react';
import { useEditorStore } from '../store/editorStore';
import { GardenObject, Handle, Transformation } from '../types';

const HANDLE_SIZE = 10;
const ROTATE_HANDLE_OFFSET = 25;

const Transformer: React.FC = () => {
  const { selection, objects, setTransformation } = useEditorStore((state) => ({
    selection: state.selection,
    objects: state.objects,
    setTransformation: state.setTransformation,
  }));

  if (selection.length !== 1) {
    return null;
  }

  const objectId = selection[0];
  const selectedObject = objects[objectId];

  if (!selectedObject) {
    return null;
  }

  const { x, y, width, height, rotation } = selectedObject;

  const onPointerDown = (e: any, handle: Handle) => {
    e.stopPropagation();
    setTransformation({
      type: handle === 'rotate' ? 'rotate' : 'resize',
      ids: [objectId],
      handle: handle,
      initialObjects: { [objectId]: { ...selectedObject } },
      startPointer: { x: e.data.global.x, y: e.data.global.y },
    });
  };

  const drawBoundingBox = useCallback((g: any) => {
    g.clear();
    g.lineStyle(1.5, 0x3b82f6, 0.8);
    g.drawRect(-width / 2, -height / 2, width, height);
  }, [width, height]);

  const drawHandle = useCallback((g: any) => {
    g.clear();
    g.beginFill(0xffffff);
    g.lineStyle(1.5, 0x3b82f6, 1);
    g.drawRect(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE);
    g.endFill();
  }, []);

  const drawRotationLine = useCallback((g: any) => {
    g.clear();
    g.lineStyle(1.5, 0x3b82f6, 0.8);
    g.moveTo(0, -height / 2);
    g.lineTo(0, -height / 2 - ROTATE_HANDLE_OFFSET + HANDLE_SIZE / 2);
  }, [height]);

  return (
    <Container x={x} y={y} rotation={rotation * (Math.PI / 180)}>
      <Graphics draw={drawBoundingBox} />
      <Graphics draw={drawRotationLine} />

      {/* Resize Handles */}
      <Graphics draw={drawHandle} x={-width / 2} y={-height / 2} interactive cursor="nwse-resize" onpointerdown={(e) => onPointerDown(e, 'topLeft')} />
      <Graphics draw={drawHandle} x={width / 2} y={-height / 2} interactive cursor="nesw-resize" onpointerdown={(e) => onPointerDown(e, 'topRight')} />
      <Graphics draw={drawHandle} x={-width / 2} y={height / 2} interactive cursor="nesw-resize" onpointerdown={(e) => onPointerDown(e, 'bottomLeft')} />
      <Graphics draw={drawHandle} x={width / 2} y={height / 2} interactive cursor="nwse-resize" onpointerdown={(e) => onPointerDown(e, 'bottomRight')} />

      {/* Rotation Handle */}
      <Graphics draw={drawHandle} x={0} y={-height / 2 - ROTATE_HANDLE_OFFSET} interactive cursor="crosshair" onpointerdown={(e) => onPointerDown(e, 'rotate')} />
    </Container>
  );
};

export default Transformer;
