import type Victor from 'victor';

/**
 * =================================================================
 * ENUMS & CONSTANTS
 * =================================================================
 */
export enum GardenObjectType {
  PLANT = 'PLANT',
  GROUP = 'GROUP',
}

/**
 * =================================================================
 * CORE OBJECT INTERFACES
 * =================================================================
 */

// Base interface for all selectable objects on the canvas
export interface BaseGardenObject {
  id: string;
  type: GardenObjectType;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number; // in degrees
  isSelected: boolean;
}

// Represents a single plant in the garden
export interface PlantObject extends BaseGardenObject {
  type: GardenObjectType.PLANT;
  plantId: string; // e.g., 'tomato', 'basil', from a plant database
  radius: number; // Adult radius of the plant in canvas units
}

// Represents a group of objects that behave as a single unit
export interface GroupObject extends BaseGardenObject {
  type: GardenObjectType.GROUP;
  // IDs of the children objects
  children: string[];
}

// A union of all possible object types in the garden
export type GardenObject = PlantObject | GroupObject;

/**
 * =================================================================
 * EDITOR & STATE MANAGEMENT TYPES
 * =================================================================
 */

// Represents the state of the editor's viewport
export interface ViewportState {
  zoom: number;
  position: { x: number; y: number };
}

// Represents the settings for the grid and snapping
export interface GridState {
  visible: boolean;
  size: number;
  snap: boolean;
}

// The core data of the editor that is subject to undo/redo
export interface GardenStateData {
  objects: Record<string, GardenObject>;
  // The top-level objects on the canvas (not inside a group)
  rootObjects: string[];
}

// Represents the history for the undo/redo stack
export interface HistoryState {
  past: GardenStateData[];
  future: GardenStateData[];
  undo: () => void;
  redo: () => void;
}

// The complete state for the garden editor, managed by Zustand
export interface GardenEditorState extends GardenStateData {
  selection: string[];
  viewport: ViewportState;
  grid: GridState;
  transformation: Transformation | null;
  marquee: Marquee | null;
  past: GardenStateData[];
  future: GardenStateData[];
  clipboard: GardenObject[];

  // --- Actions ---
  setEditorState: (state: Partial<GardenEditorState>) => void;
  addObject: (object: GardenObject, parentId?: string) => void;
  deleteSelection: () => void;
  setSelection: (selectionIds: string[], options?: { mode: 'replace' | 'add' | 'remove' }) => void;
  updateObjectProperties: (updates: Record<string, Partial<GardenObject>>) => void;
  setTransformation: (transformation: Transformation | null) => void;
  setMarquee: (marquee: Marquee | null) => void;
  undo: () => void;
  redo: () => void;
  saveHistory: () => void;
  copySelection: () => void;
  paste: () => void;
  groupSelection: () => void;
  ungroupSelection: () => void;
}

/**
 * =================================================================
 * UTILITY & INTERACTION TYPES
 * =================================================================
 */

// Bounding box used for selections and transformations
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
}

// Type for the marquee selection rectangle
export interface Marquee {
  x: number;
  y: number;
  width: number;
  height: number;
  visible: boolean;
}

/**
 * =================================================================
 * TRANSFORMATION TYPES
 * =================================================================
 */

// Defines which handle on the transformer is being dragged
export type Handle = 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight' | 'rotate';

// Represents an in-progress transformation operation
export interface Transformation {
  type: 'resize' | 'rotate' | 'drag';
  ids: string[];
  handle?: Handle;
  // The state of the objects when the transformation started
  initialObjects: Record<string, GardenObject>;
  // The screen coordinates where the pointer started the transformation
  startPointer: { x: number; y: number };
}
