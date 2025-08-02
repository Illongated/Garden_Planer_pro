import React from 'react';
import Toolbar from '../components/Toolbar';
import Palette from '../components/Palette';
import EditorCanvas from '../components/EditorCanvas';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

const GardenEditorPage = () => {
  useKeyboardShortcuts();

  return (
    <div className="w-full h-screen flex flex-col bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 overflow-hidden">
      <Toolbar />
      <div className="flex flex-1 overflow-hidden">
        <Palette />
        <main className="flex-1 flex items-start justify-start overflow-auto">
          <EditorCanvas />
        </main>
        {/* An inspector panel could be added here on the right side */}
      </div>
    </div>
  );
};

export default GardenEditorPage;
