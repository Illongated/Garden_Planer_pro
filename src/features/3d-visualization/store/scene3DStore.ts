import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { Vector3, Euler, Color } from 'three';
import {
  Scene3DState,
  Scene3DConfig,
  Plant3DModel,
  CameraMode,
  ViewMode,
  MeasurementTool,
  Annotation3D,
  PerformanceMetrics,
  LightingConfig,
  CameraConfig,
  NavigationControls,
  ExportOptions,
  AnimationConfig,
  WebXRConfig,
  Scene3DEvent,
} from '../../../types/3d-visualization';

interface Scene3DActions {
  // Scene Management
  setCurrentScene: (scene: Scene3DConfig) => void;
  clearScene: () => void;
  
  // Camera Controls
  setCameraMode: (mode: CameraMode) => void;
  setViewMode: (mode: ViewMode) => void;
  updateCameraPosition: (position: Vector3) => void;
  updateCameraTarget: (target: Vector3) => void;
  resetCamera: () => void;
  
  // Plant Management
  addPlant: (plant: Plant3DModel) => void;
  removePlant: (plantId: string) => void;
  updatePlant: (plantId: string, updates: Partial<Plant3DModel>) => void;
  selectPlant: (plant: Plant3DModel | null) => void;
  updatePlantGrowth: (plantId: string, age: number) => void;
  updatePlantHealth: (plantId: string, health: number) => void;
  
  // Lighting and Environment
  updateLighting: (lighting: Partial<LightingConfig>) => void;
  setTimeOfDay: (time: number) => void;
  setSeason: (season: 'spring' | 'summer' | 'autumn' | 'winter') => void;
  setWeather: (weather: 'clear' | 'cloudy' | 'rainy' | 'overcast') => void;
  
  // Navigation Controls
  updateNavigationControls: (controls: Partial<NavigationControls>) => void;
  enablePan: (enabled: boolean) => void;
  enableRotate: (enabled: boolean) => void;
  enableZoom: (enabled: boolean) => void;
  
  // Measurements and Annotations
  addMeasurement: (measurement: MeasurementTool) => void;
  removeMeasurement: (measurementId: string) => void;
  updateMeasurement: (measurementId: string, updates: Partial<MeasurementTool>) => void;
  clearMeasurements: () => void;
  
  addAnnotation: (annotation: Annotation3D) => void;
  removeAnnotation: (annotationId: string) => void;
  updateAnnotation: (annotationId: string, updates: Partial<Annotation3D>) => void;
  clearAnnotations: () => void;
  
  // Animation Controls
  setAnimating: (isAnimating: boolean) => void;
  updateAnimationConfig: (config: Partial<AnimationConfig>) => void;
  
  // Export Controls
  setExporting: (isExporting: boolean) => void;
  setExportOptions: (options: ExportOptions) => void;
  
  // Measurement Mode
  setMeasuring: (isMeasuring: boolean) => void;
  
  // Performance Monitoring
  updatePerformanceMetrics: (metrics: Partial<PerformanceMetrics>) => void;
  
  // WebXR Support
  setWebXRSupported: (supported: boolean) => void;
  setWebXRActive: (active: boolean) => void;
  setWebXRSession: (session: any | null) => void;
  updateWebXRConfig: (config: Partial<WebXRConfig>) => void;
  
  // Events
  addEvent: (event: Scene3DEvent) => void;
  clearEvents: () => void;
  
  // Utility Actions
  centerOnPlant: (plantId: string) => void;
  focusOnSelection: () => void;
  toggleFullscreen: () => void;
  resetScene: () => void;
}

const defaultScene3DState: Scene3DState = {
  currentScene: null,
  cameraMode: 'isometric',
  viewMode: '3d',
  isAnimating: false,
  isExporting: false,
  isMeasuring: false,
  selectedPlant: null,
  measurements: [],
  annotations: [],
  performance: {
    fps: 0,
    frameTime: 0,
    drawCalls: 0,
    triangles: 0,
    memoryUsage: 0,
    gpuMemory: 0,
  },
  webXR: {
    isSupported: false,
    isActive: false,
    session: null,
  },
};

export const useScene3DStore = create<Scene3DState & Scene3DActions>()(
  subscribeWithSelector((set, get) => ({
    ...defaultScene3DState,

    // Scene Management
    setCurrentScene: (scene: Scene3DConfig) => {
      set({ currentScene: scene });
    },

    clearScene: () => {
      set({ 
        currentScene: null,
        selectedPlant: null,
        measurements: [],
        annotations: [],
      });
    },

    // Camera Controls
    setCameraMode: (mode: CameraMode) => {
      set({ cameraMode: mode });
    },

    setViewMode: (mode: ViewMode) => {
      set({ viewMode: mode });
    },

    updateCameraPosition: (position: Vector3) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            camera: {
              ...currentScene.camera,
              position: position.clone(),
            },
          },
        });
      }
    },

    updateCameraTarget: (target: Vector3) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            camera: {
              ...currentScene.camera,
              target: target.clone(),
            },
          },
        });
      }
    },

    resetCamera: () => {
      const { currentScene } = get();
      if (currentScene) {
        const defaultPosition = new Vector3(10, 10, 10);
        const defaultTarget = new Vector3(0, 0, 0);
        set({
          currentScene: {
            ...currentScene,
            camera: {
              ...currentScene.camera,
              position: defaultPosition,
              target: defaultTarget,
            },
          },
        });
      }
    },

    // Plant Management
    addPlant: (plant: Plant3DModel) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            plants: [...currentScene.plants, plant],
          },
        });
      }
    },

    removePlant: (plantId: string) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            plants: currentScene.plants.filter(p => p.id !== plantId),
          },
        });
        // Deselect if the removed plant was selected
        const { selectedPlant } = get();
        if (selectedPlant?.id === plantId) {
          set({ selectedPlant: null });
        }
      }
    },

    updatePlant: (plantId: string, updates: Partial<Plant3DModel>) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            plants: currentScene.plants.map(plant =>
              plant.id === plantId ? { ...plant, ...updates } : plant
            ),
          },
        });
        // Update selected plant if it's the one being updated
        const { selectedPlant } = get();
        if (selectedPlant?.id === plantId) {
          set({ selectedPlant: { ...selectedPlant, ...updates } });
        }
      }
    },

    selectPlant: (plant: Plant3DModel | null) => {
      set({ selectedPlant: plant });
    },

    updatePlantGrowth: (plantId: string, age: number) => {
      const { currentScene } = get();
      if (currentScene) {
        const updatedPlants = currentScene.plants.map(plant => {
          if (plant.id === plantId) {
            const growthProgress = Math.min(age / plant.maxAge, 1);
            let growthStage: Plant3DModel['growthStage'] = 'seed';
            
            if (growthProgress > 0.8) growthStage = 'mature';
            else if (growthProgress > 0.6) growthStage = 'fruiting';
            else if (growthProgress > 0.4) growthStage = 'flowering';
            else if (growthProgress > 0.2) growthStage = 'vegetative';
            else if (growthProgress > 0.05) growthStage = 'seedling';
            
            return {
              ...plant,
              age,
              growthStage,
              scale: new Vector3(growthProgress, growthProgress, growthProgress),
            };
          }
          return plant;
        });

        set({
          currentScene: {
            ...currentScene,
            plants: updatedPlants,
          },
        });
      }
    },

    updatePlantHealth: (plantId: string, health: number) => {
      get().updatePlant(plantId, { health: Math.max(0, Math.min(1, health)) });
    },

    // Lighting and Environment
    updateLighting: (lighting: Partial<LightingConfig>) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            lighting: {
              ...currentScene.lighting,
              ...lighting,
            },
          },
        });
      }
    },

    setTimeOfDay: (time: number) => {
      get().updateLighting({ timeOfDay: Math.max(0, Math.min(24, time)) });
    },

    setSeason: (season: 'spring' | 'summer' | 'autumn' | 'winter') => {
      get().updateLighting({ season });
    },

    setWeather: (weather: 'clear' | 'cloudy' | 'rainy' | 'overcast') => {
      get().updateLighting({ weather });
    },

    // Navigation Controls
    updateNavigationControls: (controls: Partial<NavigationControls>) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            navigation: {
              ...currentScene.navigation,
              ...controls,
            },
          },
        });
      }
    },

    enablePan: (enabled: boolean) => {
      get().updateNavigationControls({ enablePan: enabled });
    },

    enableRotate: (enabled: boolean) => {
      get().updateNavigationControls({ enableRotate: enabled });
    },

    enableZoom: (enabled: boolean) => {
      get().updateNavigationControls({ enableZoom: enabled });
    },

    // Measurements and Annotations
    addMeasurement: (measurement: MeasurementTool) => {
      set({ measurements: [...get().measurements, measurement] });
    },

    removeMeasurement: (measurementId: string) => {
      set({
        measurements: get().measurements.filter(m => m.id !== measurementId),
      });
    },

    updateMeasurement: (measurementId: string, updates: Partial<MeasurementTool>) => {
      set({
        measurements: get().measurements.map(m =>
          m.id === measurementId ? { ...m, ...updates } : m
        ),
      });
    },

    clearMeasurements: () => {
      set({ measurements: [] });
    },

    addAnnotation: (annotation: Annotation3D) => {
      set({ annotations: [...get().annotations, annotation] });
    },

    removeAnnotation: (annotationId: string) => {
      set({
        annotations: get().annotations.filter(a => a.id !== annotationId),
      });
    },

    updateAnnotation: (annotationId: string, updates: Partial<Annotation3D>) => {
      set({
        annotations: get().annotations.map(a =>
          a.id === annotationId ? { ...a, ...updates } : a
        ),
      });
    },

    clearAnnotations: () => {
      set({ annotations: [] });
    },

    // Animation Controls
    setAnimating: (isAnimating: boolean) => {
      set({ isAnimating });
    },

    updateAnimationConfig: (config: Partial<AnimationConfig>) => {
      const { currentScene } = get();
      if (currentScene) {
        set({
          currentScene: {
            ...currentScene,
            // Note: AnimationConfig would need to be added to Scene3DConfig
          },
        });
      }
    },

    // Export Controls
    setExporting: (isExporting: boolean) => {
      set({ isExporting });
    },

    setExportOptions: (options: ExportOptions) => {
      // Store export options in a separate state or use a ref
      // This is a placeholder for export options management
    },

    // Measurement Mode
    setMeasuring: (isMeasuring: boolean) => {
      set({ isMeasuring });
    },

    // Performance Monitoring
    updatePerformanceMetrics: (metrics: Partial<PerformanceMetrics>) => {
      set({
        performance: {
          ...get().performance,
          ...metrics,
        },
      });
    },

    // WebXR Support
    setWebXRSupported: (supported: boolean) => {
      set({
        webXR: {
          ...get().webXR,
          isSupported: supported,
        },
      });
    },

    setWebXRActive: (active: boolean) => {
      set({
        webXR: {
          ...get().webXR,
          isActive: active,
        },
      });
    },

    setWebXRSession: (session: any | null) => {
      set({
        webXR: {
          ...get().webXR,
          session,
        },
      });
    },

    updateWebXRConfig: (config: Partial<WebXRConfig>) => {
      // WebXR config would be stored separately or in scene config
    },

    // Events
    addEvent: (event: Scene3DEvent) => {
      // Events could be stored in a separate array or logged
      console.log('Scene3D Event:', event);
    },

    clearEvents: () => {
      // Clear events if they're stored
    },

    // Utility Actions
    centerOnPlant: (plantId: string) => {
      const { currentScene } = get();
      if (currentScene) {
        const plant = currentScene.plants.find(p => p.id === plantId);
        if (plant) {
          const target = plant.position.clone();
          get().updateCameraTarget(target);
          get().selectPlant(plant);
        }
      }
    },

    focusOnSelection: () => {
      const { selectedPlant } = get();
      if (selectedPlant) {
        get().centerOnPlant(selectedPlant.id);
      }
    },

    toggleFullscreen: () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        document.exitFullscreen();
      }
    },

    resetScene: () => {
      set({
        ...defaultScene3DState,
        currentScene: get().currentScene, // Keep the current scene
      });
    },
  }))
);

// Selectors for performance optimization
export const useScene3DSelector = {
  currentScene: () => useScene3DStore(state => state.currentScene),
  cameraMode: () => useScene3DStore(state => state.cameraMode),
  viewMode: () => useScene3DStore(state => state.viewMode),
  selectedPlant: () => useScene3DStore(state => state.selectedPlant),
  isAnimating: () => useScene3DStore(state => state.isAnimating),
  isExporting: () => useScene3DStore(state => state.isExporting),
  isMeasuring: () => useScene3DStore(state => state.isMeasuring),
  measurements: () => useScene3DStore(state => state.measurements),
  annotations: () => useScene3DStore(state => state.annotations),
  performance: () => useScene3DStore(state => state.performance),
  webXR: () => useScene3DStore(state => state.webXR),
}; 