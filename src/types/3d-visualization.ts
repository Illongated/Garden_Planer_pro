import { Vector3, Euler, Color } from 'three';

// Camera and View Modes
export type CameraMode = 'top-down' | 'isometric' | 'freelook' | 'walkthrough';
export type ViewMode = '2d' | '3d';

// Plant Growth Stages
export type GrowthStage = 'seed' | 'seedling' | 'vegetative' | 'flowering' | 'fruiting' | 'mature';

// 3D Plant Model Interface
export interface Plant3DModel {
  id: string;
  name: string;
  species: string;
  growthStage: GrowthStage;
  position: Vector3;
  rotation: Euler;
  scale: Vector3;
  health: number; // 0-1
  age: number; // days
  maxAge: number; // days
  modelPath: string;
  texturePath: string;
  height: number;
  spread: number;
  rootDepth: number;
  waterNeeds: number;
  sunlightNeeds: number;
  temperatureRange: [number, number];
  seasonalGrowth: {
    spring: number;
    summer: number;
    autumn: number;
    winter: number;
  };
}

// Lighting Configuration
export interface LightingConfig {
  timeOfDay: number; // 0-24 hours
  season: 'spring' | 'summer' | 'autumn' | 'winter';
  weather: 'clear' | 'cloudy' | 'rainy' | 'overcast';
  ambientIntensity: number;
  directionalIntensity: number;
  shadowQuality: 'low' | 'medium' | 'high';
  enableShadows: boolean;
  enableFog: boolean;
  fogDensity: number;
}

// Camera Configuration
export interface CameraConfig {
  mode: CameraMode;
  position: Vector3;
  target: Vector3;
  fov: number;
  near: number;
  far: number;
  enableOrbitControls: boolean;
  enableDamping: boolean;
  dampingFactor: number;
  maxDistance: number;
  minDistance: number;
  maxPolarAngle: number;
  minPolarAngle: number;
}

// Navigation Controls
export interface NavigationControls {
  enablePan: boolean;
  enableRotate: boolean;
  enableZoom: boolean;
  enableDolly: boolean;
  panSpeed: number;
  rotateSpeed: number;
  zoomSpeed: number;
  dollySpeed: number;
}

// 3D Scene Configuration
export interface Scene3DConfig {
  id: string;
  name: string;
  description: string;
  gardenId: string;
  plants: Plant3DModel[];
  lighting: LightingConfig;
  camera: CameraConfig;
  navigation: NavigationControls;
  ground: {
    size: number;
    texturePath: string;
    color: Color;
    roughness: number;
    metalness: number;
  };
  environment: {
    skyboxPath?: string;
    backgroundType: 'color' | 'skybox' | 'gradient';
    backgroundColor: Color;
    enableFog: boolean;
    fogColor: Color;
    fogDensity: number;
  };
  performance: {
    maxFPS: number;
    enableLOD: boolean;
    shadowMapSize: number;
    antialias: boolean;
    enablePostProcessing: boolean;
  };
}

// Export Options
export interface ExportOptions {
  format: 'png' | 'jpg' | 'webp' | 'mp4' | 'webm';
  quality: number; // 0-1
  resolution: {
    width: number;
    height: number;
  };
  includeUI: boolean;
  includeAnnotations: boolean;
  filename: string;
  compression: 'none' | 'lossless' | 'lossy';
}

// Animation Configuration
export interface AnimationConfig {
  enableGrowthAnimation: boolean;
  growthSpeed: number; // days per second
  enableSeasonalChanges: boolean;
  seasonalTransitionSpeed: number;
  enableWeatherEffects: boolean;
  weatherTransitionSpeed: number;
  enableTimeOfDay: boolean;
  timeSpeed: number; // hours per second
}

// Measurement Tools
export interface MeasurementTool {
  id: string;
  type: 'distance' | 'area' | 'volume' | 'angle';
  startPoint: Vector3;
  endPoint?: Vector3;
  points: Vector3[];
  label: string;
  color: Color;
  visible: boolean;
}

// Annotation System
export interface Annotation3D {
  id: string;
  position: Vector3;
  text: string;
  color: Color;
  fontSize: number;
  backgroundColor?: Color;
  borderColor?: Color;
  visible: boolean;
  pinned: boolean;
}

// Performance Metrics
export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  drawCalls: number;
  triangles: number;
  memoryUsage: number;
  gpuMemory: number;
}

// WebXR Configuration
export interface WebXRConfig {
  enabled: boolean;
  mode: 'ar' | 'vr';
  referenceSpace: 'local' | 'local-floor' | 'bounded-floor' | 'unbounded';
  sessionType: 'immersive-ar' | 'immersive-vr';
  enableControllers: boolean;
  enableHandTracking: boolean;
}

// 3D Asset Library
export interface Asset3D {
  id: string;
  name: string;
  category: 'plant' | 'structure' | 'decoration' | 'tool';
  modelPath: string;
  texturePath: string;
  thumbnailPath: string;
  metadata: {
    author: string;
    license: string;
    version: string;
    fileSize: number;
    polygonCount: number;
    textureResolution: number;
  };
  variants: {
    growthStages: string[];
    seasons: string[];
    healthStates: string[];
  };
}

// Scene State Management
export interface Scene3DState {
  currentScene: Scene3DConfig | null;
  cameraMode: CameraMode;
  viewMode: ViewMode;
  isAnimating: boolean;
  isExporting: boolean;
  isMeasuring: boolean;
  selectedPlant: Plant3DModel | null;
  measurements: MeasurementTool[];
  annotations: Annotation3D[];
  performance: PerformanceMetrics;
  webXR: {
    isSupported: boolean;
    isActive: boolean;
    session: any | null;
  };
}

// Event Types
export interface Scene3DEvent {
  type: 'plant-selected' | 'plant-deselected' | 'camera-changed' | 'measurement-added' | 'annotation-added';
  data: any;
  timestamp: number;
}

// Plugin System
export interface Scene3DPlugin {
  id: string;
  name: string;
  version: string;
  enabled: boolean;
  initialize: (scene: any) => void;
  update: (deltaTime: number) => void;
  cleanup: () => void;
} 