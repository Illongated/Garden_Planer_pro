import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { devtools } from 'zustand/middleware';
import {
  GardenEditorState,
  GardenObject,
  GardenStateData,
  PlantObject,
  GroupObject,
  GardenObjectType,
} from '../types';
import { v4 as uuid } from 'uuid';
import { getBoundingBox } from '../utils/geometry';

const getHistoryState = (state: GardenEditorState): GardenStateData => ({
  objects: state.objects,
  rootObjects: state.rootObjects,
});

const initialState: Omit<GardenEditorState, 'setEditorState' | 'addObject' | 'setSelection' | 'updateObjectProperties' | 'setTransformation' | 'setMarquee' | 'setGuides' | 'undo' | 'redo' | 'saveHistory' | 'deleteSelection' | 'copySelection' | 'paste' | 'groupSelection' | 'ungroupSelection'> = {
  objects: {},
  rootObjects: [],
  selection: [],
  viewport: { zoom: 1, position: { x: 0, y: 0 } },
  grid: { visible: true, size: 50, snap: true },
  transformation: null,
  marquee: null,
  past: [],
  future: [],
  clipboard: [],
  guides: [],
};

// --- Mock Data ---
const initialObjects: Record<string, GardenObject> = {
  'plant-1': { id: 'plant-1', type: GardenObjectType.PLANT, plantId: 'tomato', x: 100, y: 150, width: 50, height: 50, rotation: 0, radius: 25, isSelected: false } as PlantObject,
  'plant-2': { id: 'plant-2', type: GardenObjectType.PLANT, plantId: 'basil', x: 250, y: 200, width: 40, height: 40, rotation: 0, radius: 20, isSelected: false } as PlantObject,
};
initialState.objects = initialObjects;
initialState.rootObjects = Object.keys(initialObjects);
// ---

export const useEditorStore = create<GardenEditorState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,

      setEditorState: (updater) => set(updater),

      saveHistory: () => set(state => { state.past.push(getHistoryState(state)); state.future = []; }),

      addObject: (object, parentId) => {
        get().saveHistory();
        set((state) => {
          const newObject = { ...object, id: uuid(), isSelected: false };
          state.objects[newObject.id] = newObject;
          if (parentId) { /* Group logic */ }
          else state.rootObjects.push(newObject.id);
        });
      },

      deleteSelection: () => {
        const { selection } = get();
        if (selection.length === 0) return;
        get().saveHistory();
        set(state => {
          selection.forEach(id => {
            delete state.objects[id];
            const rootIndex = state.rootObjects.indexOf(id);
            if (rootIndex > -1) state.rootObjects.splice(rootIndex, 1);
          });
          state.selection = [];
        });
      },

      copySelection: () => set(state => {
        state.clipboard = state.selection
          .map(id => state.objects[id]).filter(Boolean)
          .map(obj => ({ ...obj, isSelected: false }));
      }),

      paste: () => {
        const { clipboard } = get();
        if (clipboard.length === 0) return;
        get().saveHistory();
        set(state => {
          const newSelection: string[] = [];
          clipboard.forEach(obj => {
            const newId = uuid();
            newSelection.push(newId);
            state.objects[newId] = { ...obj, id: newId, x: obj.x + 20, y: obj.y + 20 };
            state.rootObjects.push(newId);
          });
          state.selection.forEach(id => { if (state.objects[id]) state.objects[id].isSelected = false; });
          newSelection.forEach(id => { state.objects[id].isSelected = true; });
          state.selection = newSelection;
        });
      },

      groupSelection: () => {
        const { selection, objects } = get();
        if (selection.length < 2) return;
        get().saveHistory();
        set(state => {
          const children = selection.map(id => objects[id]);
          const box = getBoundingBox(children);
          const newGroupId = uuid();
          const newGroup: GroupObject = {
            id: newGroupId, type: GardenObjectType.GROUP, children: selection,
            x: box.x, y: box.y, width: box.width, height: box.height, rotation: 0, isSelected: true,
          };
          state.objects[newGroupId] = newGroup;
          state.rootObjects = state.rootObjects.filter(id => !selection.includes(id));
          state.rootObjects.push(newGroupId);
          state.selection.forEach(id => { state.objects[id].isSelected = false; });
          state.selection = [newGroupId];
        });
      },

      ungroupSelection: () => {
        const { selection, objects } = get();
        if (selection.length !== 1) return;
        const group = objects[selection[0]];
        if (!group || group.type !== GardenObjectType.GROUP) return;
        get().saveHistory();
        set(state => {
          const childrenIds = group.children;
          childrenIds.forEach(id => state.rootObjects.push(id));
          delete state.objects[group.id];
          state.rootObjects = state.rootObjects.filter(id => id !== group.id);
          childrenIds.forEach(id => { if(state.objects[id]) state.objects[id].isSelected = true; });
          state.selection = childrenIds;
        });
      },

      setSelection: (ids, options) => {
        const { mode = 'replace' } = options || {};
        set((state) => {
          let newSelectionSet = mode === 'replace' ? new Set(ids) : new Set(state.selection);
          if (mode === 'add') ids.forEach(id => newSelectionSet.add(id));
          if (mode === 'remove') ids.forEach(id => newSelectionSet.delete(id));
          const newSelection = Array.from(newSelectionSet);
          state.selection.forEach(id => { if (!newSelectionSet.has(id) && state.objects[id]) state.objects[id].isSelected = false; });
          newSelection.forEach(id => { if (state.objects[id]) state.objects[id].isSelected = true; });
          state.selection = newSelection;
        });
      },

      updateObjectProperties: (updates) => set(state => {
        for (const id in updates) if (state.objects[id]) Object.assign(state.objects[id], updates[id]);
      }),
      setTransformation: (transformation) => set({ transformation }),
      setMarquee: (marquee) => set({ marquee }),
      setGuides: (guides) => set({ guides }),

      undo: () => set(state => {
        if (state.past.length === 0) return;
        state.future.unshift(getHistoryState(state));
        const lastState = state.past.pop()!;
        state.objects = lastState.objects;
        state.rootObjects = lastState.rootObjects;
        state.selection = [];
      }),

      redo: () => set(state => {
        if (state.future.length === 0) return;
        state.past.push(getHistoryState(state));
        const nextState = state.future.shift()!;
        state.objects = nextState.objects;
        state.rootObjects = nextState.rootObjects;
        state.selection = [];
      }),
    })),
    { name: 'GardenEditorStore' }
  )
);
