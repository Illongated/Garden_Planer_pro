// Agronomic Computation WebWorker
// Handles heavy calculations on the client side to prevent UI blocking

interface PlantSpecs {
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

interface GardenZone {
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

interface PlantPlacement {
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

interface EnvironmentalData {
  weather: Record<string, any>;
  sun_data: Record<string, any>;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  precipitation: number;
}

interface OptimizationConstraints {
  max_plants?: number;
  min_spacing: number;
  max_water_usage?: number;
  preferred_zones: string[];
  excluded_zones: string[];
  companion_plant_preferences: Record<string, string[]>;
  incompatible_plant_restrictions: Record<string, string[]>;
}

interface AnalysisResult {
  water_analysis: Record<string, any>;
  solar_analysis: Record<string, number>;
  growth_predictions: Record<string, Record<string, any>>;
  conflicts: Record<string, any[]>;
  total_predicted_yield: number;
  efficiency_metrics: Record<string, any>;
  timestamp: string;
}

interface OptimizationResult {
  optimized_placements: Record<string, any>[];
  fitness_score: number;
  conflicts_resolved: number;
  water_efficiency: number;
  space_utilization: number;
  computation_time: number;
}

interface WorkerMessage {
  type: string;
  id: string;
  data: any;
}

class AgronomicCalculator {
  private cache = new Map<string, any>();

  calculateOptimalSpacing(plantSpecs: PlantSpecs, soilQuality: number): number {
    const cacheKey = `spacing_${plantSpecs.name}_${soilQuality}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const baseSpacing = plantSpecs.spacing_optimal;
    
    // Adjust for soil quality (better soil = closer spacing)
    const soilFactor = 0.8 + (soilQuality * 0.4); // 0.8 to 1.2 range
    
    // Adjust for water availability
    const waterFactor = {
      low: 1.0,
      medium: 1.1,
      high: 1.2
    }[plantSpecs.water_need] || 1.0;
    
    // Adjust for sun exposure
    const sunFactor = {
      full_sun: 1.1,
      partial_sun: 1.0,
      shade: 0.9
    }[plantSpecs.sun_exposure] || 1.0;
    
    const optimalSpacing = baseSpacing * soilFactor * waterFactor * sunFactor;
    const result = Math.max(optimalSpacing, plantSpecs.spacing_min);
    
    this.cache.set(cacheKey, result);
    return result;
  }

  calculateWaterNeeds(
    plantSpecs: PlantSpecs, 
    weatherData: Record<string, any>, 
    soilMoisture: number, 
    growthStage: string
  ): number {
    const cacheKey = `water_${plantSpecs.name}_${growthStage}_${soilMoisture}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Base evapotranspiration (ET0) from weather data
    const et0 = weatherData.et0 || 5.0; // mm/day
    
    // Crop coefficient based on growth stage
    const kcValues: Record<string, number> = {
      seed: 0.3,
      seedling: 0.5,
      vegetative: 0.8,
      flowering: 1.0,
      fruiting: 1.1,
      harvest: 0.7
    };
    const kc = kcValues[growthStage] || 0.8;
    
    // Water need multiplier based on plant type
    const waterMultiplier = {
      low: 0.7,
      medium: 1.0,
      high: 1.3
    }[plantSpecs.water_need] || 1.0;
    
    // Soil moisture stress factor
    const stressFactor = Math.max(0.5, Math.min(1.5, soilMoisture / 0.3));
    
    // Calculate daily water need in liters
    const dailyWater = (et0 * kc * waterMultiplier * stressFactor * 
                       plantSpecs.width_max * plantSpecs.width_max / 10000);
    
    const result = Math.max(0.1, dailyWater);
    this.cache.set(cacheKey, result);
    return result;
  }

  calculateSolarExposure(
    plantPlacement: PlantPlacement,
    gardenZones: GardenZone[],
    sunData: Record<string, any>
  ): number {
    const zone = gardenZones.find(z => this.isInZone(plantPlacement, z));
    if (!zone) {
      return 0.5;
    }
    
    // Base exposure from zone
    const baseExposure = {
      full_sun: 1.0,
      partial_sun: 0.6,
      shade: 0.3
    }[zone.sun_exposure] || 0.5;
    
    // Adjust for seasonal sun angle
    const seasonalFactor = sunData.seasonal_factor || 1.0;
    
    // Adjust for slope and orientation
    const slopeFactor = 1.0 + (zone.slope / 90.0) * 0.2;
    
    // Calculate final exposure score
    const exposureScore = baseExposure * seasonalFactor * slopeFactor;
    
    return Math.min(1.0, Math.max(0.0, exposureScore));
  }

  private isInZone(placement: PlantPlacement, zone: GardenZone): boolean {
    const dx = placement.x - zone.coordinates[0];
    const dy = placement.y - zone.coordinates[1];
    const distance = Math.sqrt(dx * dx + dy * dy);
    return distance <= Math.sqrt(zone.area / Math.PI);
  }

  calculateGrowthPrediction(
    plantSpecs: PlantSpecs,
    placement: PlantPlacement,
    environmentalFactors: Record<string, any>
  ): Record<string, any> {
    const waterStress = placement.water_stress;
    const nutrientStress = placement.nutrient_stress;
    const healthScore = placement.health_score;
    
    // Environmental stress factors
    const tempStress = environmentalFactors.temperature_stress || 0.0;
    const humidityStress = environmentalFactors.humidity_stress || 0.0;
    
    // Combined stress factor
    const totalStress = (waterStress + nutrientStress + tempStress + humidityStress) / 4;
    
    // Growth rate modifier (0.5 to 1.5)
    const growthModifier = 1.0 - (totalStress * 0.5);
    const adjustedGrowthModifier = Math.max(0.5, Math.min(1.5, growthModifier));
    
    // Calculate adjusted growth timeline
    const adjustedGrowthDays = Math.floor(plantSpecs.growth_days / adjustedGrowthModifier);
    
    // Calculate yield prediction
    const baseYield = plantSpecs.yield_per_plant;
    const yieldModifier = healthScore * (1.0 - totalStress * 0.3);
    const predictedYield = baseYield * yieldModifier;
    
    // Calculate stage progression
    const stageDurations: Record<string, number> = {
      seed: 0.1,
      seedling: 0.2,
      vegetative: 0.4,
      flowering: 0.2,
      fruiting: 0.1
    };
    
    const stages = ['seed', 'seedling', 'vegetative', 'flowering', 'fruiting', 'harvest'];
    const currentStageIndex = stages.indexOf(placement.current_stage);
    let currentProgress = 0;
    
    for (let i = 0; i <= currentStageIndex; i++) {
      currentProgress += stageDurations[stages[i]] || 0;
    }
    
    const plantedDate = new Date(placement.planted_date);
    const daysElapsed = (Date.now() - plantedDate.getTime()) / (1000 * 60 * 60 * 24);
    const totalProgress = daysElapsed / adjustedGrowthDays;
    
    return {
      growth_modifier: adjustedGrowthModifier,
      adjusted_growth_days: adjustedGrowthDays,
      predicted_yield: predictedYield,
      current_progress: Math.min(1.0, totalProgress),
      days_to_harvest: Math.max(0, adjustedGrowthDays - daysElapsed),
      health_score: healthScore,
      stress_factors: {
        water: waterStress,
        nutrient: nutrientStress,
        temperature: tempStress,
        humidity: humidityStress
      }
    };
  }
}

class PlacementOptimizer {
  private calculator: AgronomicCalculator;
  private populationSize = 50;
  private generations = 100;
  private mutationRate = 0.1;
  private crossoverRate = 0.8;

  constructor(calculator: AgronomicCalculator) {
    this.calculator = calculator;
  }

  async optimizePlacement(
    plants: PlantSpecs[],
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints
  ): Promise<PlantPlacement[]> {
    // Initialize population
    const population = await this.initializePopulation(plants, gardenZones, constraints);
    
    let bestFitness = -Infinity;
    let bestSolution: PlantPlacement[] | null = null;
    
    for (let generation = 0; generation < this.generations; generation++) {
      // Evaluate fitness
      const fitnessScores: number[] = [];
      for (const individual of population) {
        const fitness = await this.calculateFitness(individual, gardenZones, constraints);
        fitnessScores.push(fitness);
        
        if (fitness > bestFitness) {
          bestFitness = fitness;
          bestSolution = [...individual];
        }
      }
      
      // Selection
      const newPopulation: PlantPlacement[][] = [];
      for (let i = 0; i < this.populationSize / 2; i++) {
        const parent1 = this.tournamentSelection(population, fitnessScores);
        const parent2 = this.tournamentSelection(population, fitnessScores);
        
        // Crossover
        let child1: PlantPlacement[], child2: PlantPlacement[];
        if (Math.random() < this.crossoverRate) {
          [child1, child2] = this.crossover(parent1, parent2);
        } else {
          child1 = [...parent1];
          child2 = [...parent2];
        }
        
        // Mutation
        if (Math.random() < this.mutationRate) {
          child1 = this.mutate(child1, gardenZones, constraints);
        }
        if (Math.random() < this.mutationRate) {
          child2 = this.mutate(child2, gardenZones, constraints);
        }
        
        newPopulation.push(child1, child2);
      }
      
      population.splice(0, population.length, ...newPopulation.slice(0, this.populationSize));
      
      // Report progress every 10 generations
      if (generation % 10 === 0) {
        self.postMessage({
          type: 'optimization_progress',
          data: {
            generation,
            best_fitness: bestFitness,
            progress: (generation / this.generations) * 100
          }
        });
      }
    }
    
    return bestSolution || [];
  }

  private async initializePopulation(
    plants: PlantSpecs[],
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints
  ): Promise<PlantPlacement[][]> {
    const population: PlantPlacement[][] = [];
    
    for (let i = 0; i < this.populationSize; i++) {
      const individual: PlantPlacement[] = [];
      for (const plantSpecs of plants) {
        const placement = await this.createRandomPlacement(plantSpecs, gardenZones, constraints);
        individual.push(placement);
      }
      population.push(individual);
    }
    
    return population;
  }

  private async createRandomPlacement(
    plantSpecs: PlantSpecs,
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints
  ): Promise<PlantPlacement> {
    // Select random zone
    const zone = gardenZones[Math.floor(Math.random() * gardenZones.length)];
    
    // Generate random coordinates within zone bounds
    const radius = Math.sqrt(zone.area / Math.PI);
    const angle = Math.random() * 2 * Math.PI;
    const distance = Math.random() * radius;
    
    const x = zone.coordinates[0] + distance * Math.cos(angle);
    const y = zone.coordinates[1] + distance * Math.sin(angle);
    
    return {
      plant_id: `${plantSpecs.name}_${Math.floor(Math.random() * 9000) + 1000}`,
      plant_specs: plantSpecs,
      x,
      y,
      planted_date: new Date().toISOString(),
      current_stage: 'seed',
      health_score: 1.0,
      water_stress: 0.0,
      nutrient_stress: 0.0
    };
  }

  private async calculateFitness(
    individual: PlantPlacement[],
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints
  ): Promise<number> {
    if (individual.length === 0) {
      return -Infinity;
    }
    
    // Spacing violations penalty
    let spacingPenalty = 0;
    for (let i = 0; i < individual.length; i++) {
      for (let j = i + 1; j < individual.length; j++) {
        const placement1 = individual[i];
        const placement2 = individual[j];
        
        const distance = Math.sqrt(
          Math.pow(placement1.x - placement2.x, 2) + 
          Math.pow(placement1.y - placement2.y, 2)
        );
        
        const minSpacing = this.calculator.calculateOptimalSpacing(placement1.plant_specs, 0.7) / 100;
        
        if (distance < minSpacing) {
          spacingPenalty += (minSpacing - distance) * 10;
        }
      }
    }
    
    // Compatibility violations penalty
    let compatibilityPenalty = 0;
    for (let i = 0; i < individual.length; i++) {
      for (let j = i + 1; j < individual.length; j++) {
        const placement1 = individual[i];
        const placement2 = individual[j];
        
        if (placement1.plant_specs.incompatible_plants.includes(placement2.plant_specs.name) ||
            placement2.plant_specs.incompatible_plants.includes(placement1.plant_specs.name)) {
          
          const distance = Math.sqrt(
            Math.pow(placement1.x - placement2.x, 2) + 
            Math.pow(placement1.y - placement2.y, 2)
          );
          
          if (distance < 1.0) { // Within 1 meter
            compatibilityPenalty += 50;
          }
        }
      }
    }
    
    // Zone constraint violations
    let zonePenalty = 0;
    for (const placement of individual) {
      const inValidZone = gardenZones.some(zone => this.calculator['isInZone'](placement, zone));
      if (!inValidZone) {
        zonePenalty += 100;
      }
    }
    
    // Calculate total fitness (higher is better)
    const totalPenalty = spacingPenalty + compatibilityPenalty + zonePenalty;
    const baseFitness = individual.length * 10;
    
    return baseFitness - totalPenalty;
  }

  private tournamentSelection(
    population: PlantPlacement[][],
    fitnessScores: number[]
  ): PlantPlacement[] {
    const tournamentSize = 3;
    const tournamentIndices: number[] = [];
    
    for (let i = 0; i < tournamentSize; i++) {
      tournamentIndices.push(Math.floor(Math.random() * population.length));
    }
    
    const tournamentFitness = tournamentIndices.map(i => fitnessScores[i]);
    const winnerIndex = tournamentIndices[tournamentFitness.indexOf(Math.max(...tournamentFitness))];
    
    return population[winnerIndex];
  }

  private crossover(
    parent1: PlantPlacement[],
    parent2: PlantPlacement[]
  ): [PlantPlacement[], PlantPlacement[]] {
    if (parent1.length !== parent2.length) {
      return [[...parent1], [...parent2]];
    }
    
    const crossoverPoint = Math.floor(Math.random() * (parent1.length - 1)) + 1;
    
    const child1 = [...parent1.slice(0, crossoverPoint), ...parent2.slice(crossoverPoint)];
    const child2 = [...parent2.slice(0, crossoverPoint), ...parent1.slice(crossoverPoint)];
    
    return [child1, child2];
  }

  private mutate(
    individual: PlantPlacement[],
    gardenZones: GardenZone[],
    constraints: OptimizationConstraints
  ): PlantPlacement[] {
    const mutated = [...individual];
    
    // Randomly mutate some placements
    for (let i = 0; i < mutated.length; i++) {
      if (Math.random() < 0.1) { // 10% mutation rate per placement
        // Small random adjustment to coordinates
        mutated[i].x += (Math.random() - 0.5);
        mutated[i].y += (Math.random() - 0.5);
      }
    }
    
    return mutated;
  }
}

class ConflictDetector {
  private calculator: AgronomicCalculator;

  constructor(calculator: AgronomicCalculator) {
    this.calculator = calculator;
  }

  async detectConflicts(
    placements: PlantPlacement[],
    gardenZones: GardenZone[]
  ): Promise<Record<string, any[]>> {
    const conflicts = {
      spacing_violations: [],
      compatibility_violations: [],
      zone_violations: [],
      resource_conflicts: []
    };
    
    // Check spacing violations
    for (let i = 0; i < placements.length; i++) {
      for (let j = i + 1; j < placements.length; j++) {
        const placement1 = placements[i];
        const placement2 = placements[j];
        
        const distance = Math.sqrt(
          Math.pow(placement1.x - placement2.x, 2) + 
          Math.pow(placement1.y - placement2.y, 2)
        );
        
        const minSpacing = this.calculator.calculateOptimalSpacing(placement1.plant_specs, 0.7) / 100;
        
        if (distance < minSpacing) {
          conflicts.spacing_violations.push({
            plant1: placement1.plant_id,
            plant2: placement2.plant_id,
            current_distance: distance,
            required_distance: minSpacing,
            severity: distance < minSpacing * 0.5 ? 'high' : 'medium'
          });
        }
      }
    }
    
    // Check compatibility violations
    for (let i = 0; i < placements.length; i++) {
      for (let j = i + 1; j < placements.length; j++) {
        const placement1 = placements[i];
        const placement2 = placements[j];
        
        if (placement1.plant_specs.incompatible_plants.includes(placement2.plant_specs.name) ||
            placement2.plant_specs.incompatible_plants.includes(placement1.plant_specs.name)) {
          
          const distance = Math.sqrt(
            Math.pow(placement1.x - placement2.x, 2) + 
            Math.pow(placement1.y - placement2.y, 2)
          );
          
          if (distance < 2.0) { // Within 2 meters
            conflicts.compatibility_violations.push({
              plant1: placement1.plant_id,
              plant2: placement2.plant_id,
              distance,
              severity: 'high'
            });
          }
        }
      }
    }
    
    // Check zone violations
    for (const placement of placements) {
      const inValidZone = gardenZones.some(zone => this.calculator['isInZone'](placement, zone));
      if (!inValidZone) {
        conflicts.zone_violations.push({
          plant_id: placement.plant_id,
          position: [placement.x, placement.y],
          severity: 'high'
        });
      }
    }
    
    return conflicts;
  }
}

// Initialize calculators
const calculator = new AgronomicCalculator();
const optimizer = new PlacementOptimizer(calculator);
const conflictDetector = new ConflictDetector(calculator);

// Handle messages from main thread
self.addEventListener('message', async (event: MessageEvent<WorkerMessage>) => {
  const { type, id, data } = event.data;
  
  try {
    switch (type) {
      case 'analyze_garden':
        const analysisResult = await performAnalysis(data);
        self.postMessage({
          type: 'analysis_result',
          id,
          data: analysisResult
        });
        break;
        
      case 'optimize_placement':
        const optimizationResult = await performOptimization(data);
        self.postMessage({
          type: 'optimization_result',
          id,
          data: optimizationResult
        });
        break;
        
      case 'detect_conflicts':
        const conflicts = await conflictDetector.detectConflicts(data.placements, data.garden_zones);
        self.postMessage({
          type: 'conflicts_result',
          id,
          data: conflicts
        });
        break;
        
      case 'calculate_incremental':
        const incrementalResult = await calculateIncrementalUpdate(data);
        self.postMessage({
          type: 'incremental_result',
          id,
          data: incrementalResult
        });
        break;
        
      default:
        self.postMessage({
          type: 'error',
          id,
          data: { message: `Unknown message type: ${type}` }
        });
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      id,
      data: { message: error instanceof Error ? error.message : 'Unknown error' }
    });
  }
});

async function performAnalysis(data: {
  placements: PlantPlacement[];
  garden_zones: GardenZone[];
  environmental_data: EnvironmentalData;
}): Promise<AnalysisResult> {
  const { placements, garden_zones, environmental_data } = data;
  
  // Calculate water needs per zone
  const waterAnalysis = await calculateIrrigationZones(placements, garden_zones, environmental_data);
  
  // Calculate solar exposure for each plant
  const solarAnalysis: Record<string, number> = {};
  for (const placement of placements) {
    solarAnalysis[placement.plant_id] = calculator.calculateSolarExposure(
      placement, garden_zones, environmental_data.sun_data || {}
    );
  }
  
  // Calculate growth predictions
  const growthPredictions: Record<string, Record<string, any>> = {};
  for (const placement of placements) {
    growthPredictions[placement.plant_id] = calculator.calculateGrowthPrediction(
      placement.plant_specs, placement, environmental_data
    );
  }
  
  // Detect conflicts
  const conflicts = await conflictDetector.detectConflicts(placements, garden_zones);
  
  // Calculate yield estimates
  const totalYield = Object.values(growthPredictions).reduce(
    (sum, prediction) => sum + prediction.predicted_yield, 0
  );
  
  // Calculate efficiency metrics
  const efficiencyMetrics = calculateEfficiencyMetrics(placements, waterAnalysis, solarAnalysis, conflicts);
  
  return {
    water_analysis: waterAnalysis,
    solar_analysis: solarAnalysis,
    growth_predictions: growthPredictions,
    conflicts,
    total_predicted_yield: totalYield,
    efficiency_metrics: efficiencyMetrics,
    timestamp: new Date().toISOString()
  };
}

async function performOptimization(data: {
  plants: PlantSpecs[];
  garden_zones: GardenZone[];
  constraints: OptimizationConstraints;
}): Promise<OptimizationResult> {
  const startTime = performance.now();
  
  const optimizedPlacements = await optimizer.optimizePlacement(
    data.plants, data.garden_zones, data.constraints
  );
  
  const computationTime = (performance.now() - startTime) / 1000;
  
  // Calculate metrics for response
  const conflicts = await conflictDetector.detectConflicts(optimizedPlacements, data.garden_zones);
  const totalConflicts = Object.values(conflicts).reduce((sum, conflicts) => sum + conflicts.length, 0);
  
  // Calculate water efficiency
  const waterAnalysis = await calculateIrrigationZones(optimizedPlacements, data.garden_zones, {});
  const waterEfficiency = waterAnalysis.efficiency_score || 0.0;
  
  // Calculate space utilization
  const totalArea = data.garden_zones.reduce((sum, zone) => sum + zone.area, 0);
  const spaceUtilization = optimizedPlacements.length / Math.max(totalArea, 1.0);
  
  // Calculate fitness score
  const fitnessScore = optimizedPlacements.length * 10 - totalConflicts * 5;
  
  // Convert placements to dict format for response
  const placementDicts = optimizedPlacements.map(placement => ({
    plant_id: placement.plant_id,
    plant_name: placement.plant_specs.name,
    x: placement.x,
    y: placement.y,
    planted_date: placement.planted_date,
    current_stage: placement.current_stage,
    health_score: placement.health_score,
    water_stress: placement.water_stress,
    nutrient_stress: placement.nutrient_stress
  }));
  
  return {
    optimized_placements: placementDicts,
    fitness_score: fitnessScore,
    conflicts_resolved: totalConflicts,
    water_efficiency: waterEfficiency,
    space_utilization: spaceUtilization,
    computation_time: computationTime
  };
}

async function calculateIncrementalUpdate(data: {
  current_placements: PlantPlacement[];
  new_placement: PlantPlacement;
  garden_zones: GardenZone[];
  environmental_data: EnvironmentalData;
}): Promise<Record<string, any>> {
  const { current_placements, new_placement, garden_zones, environmental_data } = data;
  
  // Add new placement to existing ones
  const updatedPlacements = [...current_placements, new_placement];
  
  // Calculate only the affected metrics
  const affectedMetrics = {
    new_plant_analysis: {
      water_need: calculator.calculateWaterNeeds(
        new_placement.plant_specs,
        environmental_data.weather || {},
        0.5,
        new_placement.current_stage
      ),
      solar_exposure: calculator.calculateSolarExposure(
        new_placement, garden_zones, environmental_data.sun_data || {}
      ),
      growth_prediction: calculator.calculateGrowthPrediction(
        new_placement.plant_specs, new_placement, environmental_data
      )
    },
    conflicts_with_new_plant: await conflictDetector.detectConflicts(updatedPlacements, garden_zones),
    updated_irrigation_zones: await calculateIrrigationZones(updatedPlacements, garden_zones, environmental_data)
  };
  
  return affectedMetrics;
}

async function calculateIrrigationZones(
  placements: PlantPlacement[],
  gardenZones: GardenZone[],
  waterConstraints: Record<string, any>
): Promise<Record<string, any>> {
  // Group plants by water needs
  const waterGroups: Record<string, PlantPlacement[]> = {
    low: [],
    medium: [],
    high: []
  };
  
  for (const placement of placements) {
    waterGroups[placement.plant_specs.water_need].push(placement);
  }
  
  // Calculate zones for each water need level
  const zones: Record<string, any> = {};
  for (const [waterNeed, plants] of Object.entries(waterGroups)) {
    if (plants.length > 0) {
      zones[waterNeed] = createIrrigationZone(plants, gardenZones, waterNeed);
    }
  }
  
  // Calculate total water requirements
  const totalWaterNeeds: Record<string, number> = {};
  for (const [waterNeed, zoneData] of Object.entries(zones)) {
    const dailyWater = zoneData.plants.reduce((sum: number, placement: PlantPlacement) => {
      return sum + calculator.calculateWaterNeeds(
        placement.plant_specs,
        waterConstraints.weather || {},
        0.5,
        placement.current_stage
      );
    }, 0);
    totalWaterNeeds[waterNeed] = dailyWater;
  }
  
  return {
    zones,
    total_water_needs: totalWaterNeeds,
    efficiency_score: calculateIrrigationEfficiency(zones, totalWaterNeeds)
  };
}

function createIrrigationZone(
  plants: PlantPlacement[],
  gardenZones: GardenZone[],
  waterNeed: string
): Record<string, any> {
  if (plants.length === 0) {
    return { plants: [], center: [0, 0], radius: 0 };
  }
  
  // Calculate center of the zone
  const centerX = plants.reduce((sum, p) => sum + p.x, 0) / plants.length;
  const centerY = plants.reduce((sum, p) => sum + p.y, 0) / plants.length;
  
  // Calculate radius to cover all plants
  const maxDistance = Math.max(
    ...plants.map(p => Math.sqrt(Math.pow(p.x - centerX, 2) + Math.pow(p.y - centerY, 2)))
  );
  
  return {
    plants,
    center: [centerX, centerY],
    radius: maxDistance + 1.0, // Add 1m buffer
    water_need: waterNeed
  };
}

function calculateIrrigationEfficiency(
  zones: Record<string, any>,
  waterNeeds: Record<string, number>
): number {
  if (Object.keys(zones).length === 0) {
    return 0.0;
  }
  
  // Calculate overlap between zones
  let totalOverlap = 0;
  const zoneList = Object.values(zones);
  
  for (let i = 0; i < zoneList.length; i++) {
    for (let j = i + 1; j < zoneList.length; j++) {
      const zone1 = zoneList[i];
      const zone2 = zoneList[j];
      
      const distance = Math.sqrt(
        Math.pow(zone1.center[0] - zone2.center[0], 2) +
        Math.pow(zone1.center[1] - zone2.center[1], 2)
      );
      const combinedRadius = zone1.radius + zone2.radius;
      
      if (distance < combinedRadius) {
        const overlap = combinedRadius - distance;
        totalOverlap += overlap;
      }
    }
  }
  
  // Efficiency based on minimal overlap and balanced water distribution
  const overlapPenalty = totalOverlap * 0.1;
  const waterValues = Object.values(waterNeeds);
  const waterBalance = 1.0 - (Math.max(...waterValues) - Math.min(...waterValues)) / 10;
  
  return Math.max(0.0, Math.min(1.0, waterBalance - overlapPenalty));
}

function calculateEfficiencyMetrics(
  placements: PlantPlacement[],
  waterAnalysis: Record<string, any>,
  solarAnalysis: Record<string, number>,
  conflicts: Record<string, any[]>
): Record<string, any> {
  if (placements.length === 0) {
    return { overall_score: 0.0, details: {} };
  }
  
  // Space utilization
  const totalArea = Object.values(waterAnalysis.zones || {}).reduce((sum: number, zone: any) => sum + zone.area, 0);
  const spaceUtilization = placements.length / Math.max(totalArea, 1.0);
  
  // Water efficiency
  const waterEfficiency = waterAnalysis.efficiency_score || 0.0;
  
  // Solar efficiency
  const solarValues = Object.values(solarAnalysis);
  const avgSolarScore = solarValues.length > 0 ? solarValues.reduce((sum, score) => sum + score, 0) / solarValues.length : 0.0;
  
  // Conflict penalty
  const conflictPenalty = (
    (conflicts.spacing_violations?.length || 0) * 0.1 +
    (conflicts.compatibility_violations?.length || 0) * 0.2 +
    (conflicts.zone_violations?.length || 0) * 0.3
  );
  
  // Overall score (0-100)
  const overallScore = (
    spaceUtilization * 25 +
    waterEfficiency * 25 +
    avgSolarScore * 25 +
    (1.0 - Math.min(conflictPenalty, 1.0)) * 25
  );
  
  return {
    overall_score: Math.min(100.0, Math.max(0.0, overallScore)),
    space_utilization: spaceUtilization,
    water_efficiency: waterEfficiency,
    solar_efficiency: avgSolarScore,
    conflict_penalty: conflictPenalty,
    details: {
      total_plants: placements.length,
      total_conflicts: Object.values(conflicts).reduce((sum, conflicts) => sum + conflicts.length, 0),
      avg_water_need: placements.reduce((sum, p) => sum + (p.plant_specs.water_need === 'high' ? 1 : 0), 0) / placements.length
    }
  };
}

// Notify main thread that worker is ready
self.postMessage({
  type: 'worker_ready',
  data: { message: 'Agronomic worker initialized and ready' }
}); 