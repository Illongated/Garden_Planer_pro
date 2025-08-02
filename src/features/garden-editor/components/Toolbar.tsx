import React from 'react';
import { Button } from '@/components/ui/button';
import { Undo, Redo, Group, Ungroup, ZoomIn, ZoomOut, Grid, Magnet } from 'lucide-react';
import { useEditorStore } from '../store/editorStore';

const Toolbar = () => {
  const {
    undo, redo, groupSelection, ungroupSelection,
    viewport, grid, setEditorState
  } = useEditorStore((state) => ({
    undo: state.undo,
    redo: state.redo,
    groupSelection: state.groupSelection,
    ungroupSelection: state.ungroupSelection,
    viewport: state.viewport,
    grid: state.grid,
    setEditorState: state.setEditorState,
  }));

  const zoomIn = () => setEditorState({ viewport: { ...viewport, zoom: Math.min(viewport.zoom * 1.2, 5) } });
  const zoomOut = () => setEditorState({ viewport: { ...viewport, zoom: Math.max(viewport.zoom / 1.2, 0.1) } });
  const toggleGridVisible = () => setEditorState({ grid: { ...grid, visible: !grid.visible } });
  const toggleGridSnap = () => setEditorState({ grid: { ...grid, snap: !grid.snap } });

  return (
    <header className="p-2 border-b bg-white dark:bg-gray-900 shadow-sm z-10 flex items-center justify-between flex-shrink-0">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={undo}><Undo className="h-4 w-4" /><span className="sr-only">Undo</span></Button>
        <Button variant="ghost" size="icon" onClick={redo}><Redo className="h-4 w-4" /><span className="sr-only">Redo</span></Button>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={groupSelection}><Group className="h-4 w-4" /><span className="sr-only">Group</span></Button>
        <Button variant="ghost" size="icon" onClick={ungroupSelection}><Ungroup className="h-4 w-4" /><span className="sr-only">Ungroup</span></Button>
      </div>
      <div className="flex items-center gap-2">
        <Button variant={grid.visible ? "secondary" : "ghost"} size="icon" onClick={toggleGridVisible}><Grid className="h-4 w-4" /><span className="sr-only">Toggle Grid</span></Button>
        <Button variant={grid.snap ? "secondary" : "ghost"} size="icon" onClick={toggleGridSnap}><Magnet className="h-4 w-4" /><span className="sr-only">Toggle Snap</span></Button>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={zoomOut}><ZoomOut className="h-4 w-4" /><span className="sr-only">Zoom Out</span></Button>
        <span className="text-sm w-12 text-center">{Math.round(viewport.zoom * 100)}%</span>
        <Button variant="ghost" size="icon" onClick={zoomIn}><ZoomIn className="h-4 w-4" /><span className="sr-only">Zoom In</span></Button>
      </div>
    </header>
  );
};

export default Toolbar;
