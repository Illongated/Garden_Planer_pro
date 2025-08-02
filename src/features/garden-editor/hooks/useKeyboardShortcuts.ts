import { useEffect } from 'react';
import { useEditorStore } from '../store/editorStore';

export const useKeyboardShortcuts = () => {
  const actions = useEditorStore((state) => ({
    undo: state.undo,
    redo: state.redo,
    deleteSelection: state.deleteSelection,
    copySelection: state.copySelection,
    paste: state.paste,
    groupSelection: state.groupSelection,
    ungroupSelection: state.ungroupSelection,
  }));

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modKey = isMac ? e.metaKey : e.ctrlKey;

      if (modKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        e.shiftKey ? actions.redo() : actions.undo();
      } else if (modKey && e.key.toLowerCase() === 'y') {
        e.preventDefault();
        actions.redo();
      } else if (e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault();
        actions.deleteSelection();
      } else if (modKey && e.key.toLowerCase() === 'c') {
        e.preventDefault();
        actions.copySelection();
      } else if (modKey && e.key.toLowerCase() === 'v') {
        e.preventDefault();
        actions.paste();
      } else if (modKey && e.key.toLowerCase() === 'g') {
        e.preventDefault();
        e.shiftKey ? actions.ungroupSelection() : actions.groupSelection();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [actions]);
};
