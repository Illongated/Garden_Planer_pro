import { Vector3, Euler, Color } from 'three';
import { Plant3DModel, GrowthStage } from '../../../types/3d-visualization';

// Fallback plant geometries for when 3D models aren't available
export const createFallbackPlantGeometry = (plant: Plant3DModel) => {
  const { height, spread, growthStage } = plant;
  
  // Base stem geometry
  const stemGeometry = {
    type: 'cylinder' as const,
    args: [0.05, 0.05, height * 0.8, 8] as [number, number, number, number],
    material: {
      color: new Color(0x8b4513), // Brown
      roughness: 0.8,
      metalness: 0.1,
    },
  };
  
  // Foliage geometry based on growth stage
  let foliageGeometry;
  switch (growthStage) {
    case 'seed':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.2, 8, 8] as [number, number, number],
        material: {
          color: new Color(0x22c55e), // Green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    case 'seedling':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.4, 8, 8] as [number, number, number],
        material: {
          color: new Color(0x22c55e), // Green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    case 'vegetative':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.7, 12, 12] as [number, number, number],
        material: {
          color: new Color(0x16a34a), // Dark green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    case 'flowering':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.8, 16, 16] as [number, number, number],
        material: {
          color: new Color(0x16a34a), // Dark green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    case 'fruiting':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.9, 16, 16] as [number, number, number],
        material: {
          color: new Color(0x16a34a), // Dark green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    case 'mature':
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread, 20, 20] as [number, number, number],
        material: {
          color: new Color(0x15803d), // Very dark green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
      break;
    default:
      foliageGeometry = {
        type: 'sphere' as const,
        args: [spread * 0.5, 8, 8] as [number, number, number],
        material: {
          color: new Color(0x22c55e), // Green
          roughness: 0.6,
          metalness: 0.0,
        },
      };
  }
  
  return {
    stem: stemGeometry,
    foliage: foliageGeometry,
  };
};

// Health-based color variation
export const getHealthColor = (health: number): Color => {
  if (health > 0.8) return new Color(0x22c55e); // Green
  if (health > 0.6) return new Color(0x84cc16); // Light green
  if (health > 0.4) return new Color(0xfbbf24); // Yellow
  if (health > 0.2) return new Color(0xf97316); // Orange
  return new Color(0xef4444); // Red
};

// Growth stage-based scale
export const getGrowthScale = (plant: Plant3DModel): Vector3 => {
  const { age, maxAge, growthStage } = plant;
  const growthProgress = Math.min(age / maxAge, 1);
  
  let scaleMultiplier = 0.3; // Start small
  
  switch (growthStage) {
    case 'seed':
      scaleMultiplier = 0.1;
      break;
    case 'seedling':
      scaleMultiplier = 0.3;
      break;
    case 'vegetative':
      scaleMultiplier = 0.6;
      break;
    case 'flowering':
      scaleMultiplier = 0.8;
      break;
    case 'fruiting':
      scaleMultiplier = 0.9;
      break;
    case 'mature':
      scaleMultiplier = 1.0;
      break;
  }
  
  return new Vector3(scaleMultiplier, scaleMultiplier, scaleMultiplier);
};

// Seasonal color variation
export const getSeasonalColor = (plant: Plant3DModel, season: string): Color => {
  const baseColor = getHealthColor(plant.health);
  
  switch (season) {
    case 'spring':
      return baseColor.clone().multiplyScalar(1.2); // Brighter
    case 'summer':
      return baseColor; // Normal
    case 'autumn':
      return baseColor.clone().multiplyScalar(0.8); // Duller
    case 'winter':
      return baseColor.clone().multiplyScalar(0.6); // Very dull
    default:
      return baseColor;
  }
};

// Weather effects on plant appearance
export const getWeatherEffects = (weather: string) => {
  switch (weather) {
    case 'rainy':
      return {
        opacity: 0.8,
        roughness: 0.9,
        metalness: 0.0,
      };
    case 'cloudy':
      return {
        opacity: 0.9,
        roughness: 0.7,
        metalness: 0.0,
      };
    case 'overcast':
      return {
        opacity: 0.7,
        roughness: 0.8,
        metalness: 0.0,
      };
    default:
      return {
        opacity: 1.0,
        roughness: 0.6,
        metalness: 0.0,
      };
  }
};

// Model loading status
export interface ModelLoadStatus {
  loaded: boolean;
  error: string | null;
  progress: number;
}

// Model cache
const modelCache = new Map<string, any>();

export const loadModel = async (modelPath: string): Promise<any> => {
  // Check cache first
  if (modelCache.has(modelPath)) {
    return modelCache.get(modelPath);
  }
  
  try {
    // In a real implementation, this would load the actual GLB file
    // For now, we'll simulate loading with a delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return fallback geometry for demonstration
    const fallbackModel = {
      scene: {
        type: 'group',
        children: [
          {
            type: 'mesh',
            geometry: { type: 'cylinder', args: [0.05, 0.05, 1, 8] },
            material: { color: 0x22c55e },
          },
        ],
      },
    };
    
    modelCache.set(modelPath, fallbackModel);
    return fallbackModel;
  } catch (error) {
    console.error(`Failed to load model: ${modelPath}`, error);
    throw error;
  }
};

// Texture loading
export const loadTexture = async (texturePath: string): Promise<any> => {
  try {
    // In a real implementation, this would load the actual texture
    // For now, we'll return a default texture
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      type: 'texture',
      path: texturePath,
      loaded: true,
    };
  } catch (error) {
    console.error(`Failed to load texture: ${texturePath}`, error);
    throw error;
  }
};

// Preload common models
export const preloadCommonModels = async () => {
  const commonModels = [
    '/models/tomato.glb',
    '/models/basil.glb',
    '/models/lettuce.glb',
    '/models/carrot.glb',
  ];
  
  const loadPromises = commonModels.map(modelPath => 
    loadModel(modelPath).catch(error => {
      console.warn(`Failed to preload model: ${modelPath}`, error);
      return null;
    })
  );
  
  await Promise.all(loadPromises);
  console.log('Common models preloaded');
};

// Clear model cache
export const clearModelCache = () => {
  modelCache.clear();
  console.log('Model cache cleared');
};

// Get model cache info
export const getModelCacheInfo = () => {
  return {
    size: modelCache.size,
    keys: Array.from(modelCache.keys()),
  };
}; 