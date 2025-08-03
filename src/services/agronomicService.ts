import { toast } from 'sonner';

// Types for agronomic calculations
export interface PlantSpecs {
  name: string;
  type: 'vegetable' | 'herb' | 'fruit' | 'flower' | 'root' | 'legume';
  spacing_min: number;
  spacing_optimal: number;
  water_need: 'low' | 'medium' | 'high';
  sun_exposure: 'full_sun' | 'partial_sun' | 'shade';
  growth_days: number;
  height_max: number;
  width_max: number;
  root_depth: number;
  yield_per_plant: number;
  companion_plants: string[];
  incompatible_plants: string[];
  water_consumption_daily: number;
  nutrient_requirements: Record<string, number>;
  frost_tolerance: boolean;
  heat_tolerance: boolean;
}

export interface GardenZone {
  id: string;
  name: string;
  area: number;
  soil_type: string;
  ph_level: number;
  sun_exposure: 'full_sun' | 'partial_sun' | 'shade';
  water_availability: number;
  elevation: number;
  slope: number;
  coordinates: [number, number];
}

export interface PlantPlacement {
  plant_id: string;
  plant_specs: PlantSpecs;
  x: number;
  y: number;
  planted_date: string;
  current_stage: 'seed' | 'seedling' | 'vegetative' | 'flowering' | 'fruiting' | 'harvest';
  health_score: number;
  water_stress: number;
  nutrient_stress: number;
}

export interface EnvironmentalData {
  weather: Record<string, any>;
  sun_data: Record<string, any>;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  precipitation: number;
}

export interface OptimizationConstraints {
  max_plants?: number;
  min_spacing: number;
  max_water_usage?: number;
  preferred_zones: string[];
  excluded_zones: string[];
  companion_plant_preferences: Record<string, string[]>;
  incompatible_plant_restrictions: Record<string, string[]>;
}

export interface AnalysisResult {
  water_analysis: Record<string, any>;
  solar_analysis: Record<string, number>;
  growth_predictions: Record<string, Record<string, any>>;
  conflicts: Record<string, any[]>;
  total_predicted_yield: number;
  efficiency_metrics: Record<string, any>;
  timestamp: string;
}

export interface OptimizationResult {
  optimized_placements: Record<string, any>[];
  fitness_score: number;
  conflicts_resolved: number;
  water_efficiency: number;
  space_utilization: number;
  computation_time: number;
}

export interface WorkerMessage {
  type: string;
  id: string;
  data: any;
}

export interface AgronomicCache {
  [key: string]: {
    result: any;
    timestamp: string;
    ttl: number;
  };
}

class AgronomicService {
  private worker: Worker | null = null;
  private messageCallbacks: Map<string, (data: any) => void> = new Map();
  private progressCallbacks: Map<string, (progress: any) => void> = new Map();
  private cache: AgronomicCache = {};
  private cacheTTL = 5 * 60 * 1000; // 5 minutes
  private isWorkerReady = false;

  constructor() {
    this.initializeWorker();
  }

  private initializeWorker(): void {
    try {
      this.worker = new Worker(new URL('../workers/agronomic-worker.ts', import.meta.url), {
        type: 'module'
      });

      this.worker.onmessage = (event: MessageEvent<WorkerMessage>) => {
        const { type, id, data } = event.data;

        switch (type) {
          case 'worker_ready':
            this.isWorkerReady = true;
            console.log('Agronomic worker ready');
            break;

          case 'analysis_result':
          case 'optimization_result':
          case 'conflicts_result':
          case 'incremental_result':
            const callback = this.messageCallbacks.get(id);
            if (callback) {
              callback(data);
              this.messageCallbacks.delete(id);
            }
            break;

          case 'optimization_progress':
            const progressCallback = this.progressCallbacks.get(id);
            if (progressCallback) {
              progressCallback(data);
            }
            break;

          case 'error':
            console.error('Worker error:', data.message);
            toast.error(`Calculation error: ${data.message}`);
            const errorCallback = this.messageCallbacks.get(id);
            if (errorCallback) {
              errorCallback({ error: data.message });
              this.messageCallbacks.delete(id);
            }
            break;

          default:
            console.warn('Unknown worker message type:', type);
        }
      };

      this.worker.onerror = (error) => {
        console.error('Worker error:', error);
        toast.error('Agronomic calculation worker failed');
      };

    } catch (error) {
      console.error('Failed to initialize agronomic worker:', error);
      toast.error('Failed to initialize calculation engine');
    }
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sendMessage(type: string, data: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.worker || !this.isWorkerReady) {
        reject(new Error('Worker not ready'));
        return;
      }

      const id = this.generateMessageId();
      
      this.messageCallbacks.set(id, (result) => {
        if (result.error) {
          reject(new Error(result.error));
        } else {
          resolve(result);
        }
      });

      this.worker.postMessage({ type, id, data });
    });
  }

  private getCacheKey(operation: string, data: any): string {
    return `${operation}_${JSON.stringify(data)}`;
  }

  private isCacheValid(key: string): boolean {
    const cached = this.cache[key];
    if (!cached) return false;
    
    const now = Date.now();
    return (now - new Date(cached.timestamp).getTime()) < cached.ttl;
  }

  private setCache(key: string, result: any): void {
    this.cache[key] = {
      result,
      timestamp: new Date().toISOString(),
      ttl: this.cacheTTL
    };
  }

  private getCache(key: string): any | null {
    if (this.isCacheValid(key)) {
      return this.cache[key].result;
    }
    return null;
  }

  public async analyzeGarden(
    placements: PlantPlacement[],
    gardenZones: GardenZone[],
    environmentalData: EnvironmentalData,
    useCache: boolean = true
  ): Promise<AnalysisResult> {
    const cacheKey = this.getCacheKey('analyze', { placements, gardenZones, environmentalData });
    
    if (useCache) {
      const cached = this.getCache(cacheKey);
      if (cached) {
        return cached;
      }
    }

    try {
      const result = await this.sendMessage('analyze_garden', {
        placements,
        garden_zones: gardenZones,
        environmental_data: environmentalData
      });

      if (useCache) {
        this.setCache(cacheKey, result);
      }

      return result;
    } catch (error) {
      console.error('Garden analysis failed:', error);
      throw error;
    }
  }

  public async optimizePlacement(
    plants: PlantSpecs[],
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints,
    onProgress?: (progress: any) => void
  ): Promise<OptimizationResult> {
    const cacheKey = this.getCacheKey('optimize', { plants, gardenZones, constraints });
    
    // Don't cache optimization results as they can be expensive and vary
    const id = this.generateMessageId();
    
    if (onProgress) {
      this.progressCallbacks.set(id, onProgress);
    }

    try {
      const result = await this.sendMessage('optimize_placement', {
        plants,
        garden_zones: gardenZones,
        constraints
      });

      if (onProgress) {
        this.progressCallbacks.delete(id);
      }

      return result;
    } catch (error) {
      console.error('Placement optimization failed:', error);
      throw error;
    }
  }

  public async detectConflicts(
    placements: PlantPlacement[],
    gardenZones: GardenZone[]
  ): Promise<Record<string, any[]>> {
    const cacheKey = this.getCacheKey('conflicts', { placements, gardenZones });
    
    const cached = this.getCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const result = await this.sendMessage('detect_conflicts', {
        placements,
        garden_zones: gardenZones
      });

      this.setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('Conflict detection failed:', error);
      throw error;
    }
  }

  public async calculateIncrementalUpdate(
    currentPlacements: PlantPlacement[],
    newPlacement: PlantPlacement,
    gardenZones: GardenZone[],
    environmentalData: EnvironmentalData
  ): Promise<Record<string, any>> {
    try {
      const result = await this.sendMessage('calculate_incremental', {
        current_placements: currentPlacements,
        new_placement: newPlacement,
        garden_zones: gardenZones,
        environmental_data: environmentalData
      });

      return result;
    } catch (error) {
      console.error('Incremental calculation failed:', error);
      throw error;
    }
  }

  public clearCache(): void {
    this.cache = {};
    console.log('Agronomic cache cleared');
  }

  public getCacheStats(): Record<string, any> {
    const now = Date.now();
    const validEntries = Object.entries(this.cache).filter(([_, entry]) => {
      return (now - new Date(entry.timestamp).getTime()) < entry.ttl;
    });

    return {
      total_entries: Object.keys(this.cache).length,
      valid_entries: validEntries.length,
      cache_size_mb: JSON.stringify(this.cache).length / (1024 * 1024),
      worker_ready: this.isWorkerReady
    };
  }

  public destroy(): void {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    this.messageCallbacks.clear();
    this.progressCallbacks.clear();
    this.cache = {};
  }
}

// Create singleton instance
export const agronomicService = new AgronomicService();

// Export types for use in other modules
export type {
  PlantSpecs,
  GardenZone,
  PlantPlacement,
  EnvironmentalData,
  OptimizationConstraints,
  AnalysisResult,
  OptimizationResult
}; 