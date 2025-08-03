import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  agronomicService, 
  type PlantSpecs, 
  type GardenZone, 
  type PlantPlacement, 
  type EnvironmentalData,
  type AnalysisResult,
  type OptimizationResult
} from '../services/agronomicService';
import { websocketService, type WebSocketEvent } from '../services/websocketService';
import { toast } from 'sonner';

interface AgronomicAnalysisProps {
  gardenId: string;
  userId: string;
}

export const AgronomicAnalysis: React.FC<AgronomicAnalysisProps> = ({ 
  gardenId, 
  userId 
}) => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [optimization, setOptimization] = useState<OptimizationResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationProgress, setOptimizationProgress] = useState(0);
  const [websocketStatus, setWebsocketStatus] = useState('disconnected');

  // Sample data for demonstration
  const samplePlants: PlantSpecs[] = [
    {
      name: "Tomato",
      type: "vegetable",
      spacing_min: 30,
      spacing_optimal: 45,
      water_need: "medium",
      sun_exposure: "full_sun",
      growth_days: 80,
      height_max: 120,
      width_max: 60,
      root_depth: 45,
      yield_per_plant: 2.5,
      companion_plants: ["Basil", "Marigold"],
      incompatible_plants: ["Potato", "Corn"],
      water_consumption_daily: 2.0,
      nutrient_requirements: { N: 0.15, P: 0.10, K: 0.20 },
      frost_tolerance: false,
      heat_tolerance: true
    },
    {
      name: "Basil",
      type: "herb",
      spacing_min: 15,
      spacing_optimal: 25,
      water_need: "medium",
      sun_exposure: "full_sun",
      growth_days: 60,
      height_max: 40,
      width_max: 25,
      root_depth: 20,
      yield_per_plant: 0.5,
      companion_plants: ["Tomato"],
      incompatible_plants: [],
      water_consumption_daily: 1.5,
      nutrient_requirements: { N: 0.10, P: 0.05, K: 0.15 },
      frost_tolerance: false,
      heat_tolerance: true
    }
  ];

  const sampleZones: GardenZone[] = [
    {
      id: "zone_1",
      name: "Main Garden",
      area: 100,
      soil_type: "loamy",
      ph_level: 6.5,
      sun_exposure: "full_sun",
      water_availability: 50,
      elevation: 100,
      slope: 5,
      coordinates: [0, 0]
    }
  ];

  const samplePlacements: PlantPlacement[] = [
    {
      plant_id: "tomato_1",
      plant_specs: samplePlants[0],
      x: 10,
      y: 10,
      planted_date: new Date().toISOString(),
      current_stage: "seedling",
      health_score: 1.0,
      water_stress: 0.0,
      nutrient_stress: 0.0
    },
    {
      plant_id: "basil_1",
      plant_specs: samplePlants[1],
      x: 15,
      y: 15,
      planted_date: new Date().toISOString(),
      current_stage: "seedling",
      health_score: 0.9,
      water_stress: 0.1,
      nutrient_stress: 0.0
    }
  ];

  const environmentalData: EnvironmentalData = {
    weather: { et0: 5.0, temperature: 25, humidity: 60 },
    sun_data: { seasonal_factor: 1.0, sun_angle: 45 },
    soil_moisture: 0.6,
    temperature: 25,
    humidity: 60,
    wind_speed: 5,
    precipitation: 0
  };

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        await websocketService.connect(userId);
        setWebsocketStatus('connected');
        
        // Subscribe to garden updates
        websocketService.subscribeToGarden(gardenId);
        
        // Listen for agronomic updates
        websocketService.on('agronomic_update', handleAgronomicUpdate);
        websocketService.on('optimization_progress', handleOptimizationProgress);
        websocketService.on('conflict_alert', handleConflictAlert);
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setWebsocketStatus('error');
      }
    };

    connectWebSocket();

    return () => {
      websocketService.disconnect();
    };
  }, [userId, gardenId]);

  const handleAgronomicUpdate = useCallback((event: WebSocketEvent) => {
    if (event.type === 'agronomic_update' && event.garden_id === gardenId) {
      setAnalysis(event.data);
      toast.success('Real-time agronomic analysis updated');
    }
  }, [gardenId]);

  const handleOptimizationProgress = useCallback((event: WebSocketEvent) => {
    if (event.type === 'optimization_progress') {
      setOptimizationProgress(event.progress.progress);
    }
  }, []);

  const handleConflictAlert = useCallback((event: WebSocketEvent) => {
    if (event.type === 'conflict_alert' && event.garden_id === gardenId) {
      toast.warning('Plant conflicts detected in your garden');
    }
  }, [gardenId]);

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const result = await agronomicService.analyzeGarden(
        samplePlacements,
        sampleZones,
        environmentalData
      );
      setAnalysis(result);
      toast.success('Garden analysis completed');
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const runOptimization = async () => {
    setIsOptimizing(true);
    setOptimizationProgress(0);
    
    try {
      const result = await agronomicService.optimizePlacement(
        samplePlants,
        sampleZones,
        {
          min_spacing: 0.3,
          preferred_zones: [],
          excluded_zones: [],
          companion_plant_preferences: {},
          incompatible_plant_restrictions: {}
        },
        (progress) => {
          setOptimizationProgress(progress.progress);
        }
      );
      setOptimization(result);
      toast.success('Placement optimization completed');
    } catch (error) {
      console.error('Optimization failed:', error);
      toast.error('Optimization failed');
    } finally {
      setIsOptimizing(false);
      setOptimizationProgress(0);
    }
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConflictSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Agronomic Analysis</h2>
        <div className="flex items-center space-x-4">
          <Badge variant={websocketStatus === 'connected' ? 'default' : 'secondary'}>
            {websocketStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
          </Badge>
          <Button onClick={runAnalysis} disabled={isAnalyzing}>
            {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
          </Button>
          <Button onClick={runOptimization} disabled={isOptimizing}>
            {isOptimizing ? 'Optimizing...' : 'Optimize Placement'}
          </Button>
        </div>
      </div>

      {isOptimizing && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Optimization Progress</span>
                <span>{Math.round(optimizationProgress)}%</span>
              </div>
              <Progress value={optimizationProgress} />
            </div>
          </CardContent>
        </Card>
      )}

      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Efficiency Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Efficiency Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Overall Score</span>
                <span className={`font-bold ${getEfficiencyColor(analysis.efficiency_metrics.overall_score)}`}>
                  {Math.round(analysis.efficiency_metrics.overall_score)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span>Space Utilization</span>
                <span>{(analysis.efficiency_metrics.space_utilization * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Water Efficiency</span>
                <span>{(analysis.efficiency_metrics.water_efficiency * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Solar Efficiency</span>
                <span>{(analysis.efficiency_metrics.solar_efficiency * 100).toFixed(1)}%</span>
              </div>
              <Separator />
              <div className="text-sm text-gray-600">
                <div>Total Plants: {analysis.efficiency_metrics.details.total_plants}</div>
                <div>Total Conflicts: {analysis.efficiency_metrics.details.total_conflicts}</div>
                <div>Predicted Yield: {analysis.total_predicted_yield.toFixed(1)} kg</div>
              </div>
            </CardContent>
          </Card>

          {/* Conflicts */}
          <Card>
            <CardHeader>
              <CardTitle>Conflicts & Issues</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(analysis.conflicts).map(([type, conflicts]) => (
                <div key={type}>
                  <h4 className="font-semibold capitalize mb-2">
                    {type.replace('_', ' ')} ({conflicts.length})
                  </h4>
                  {conflicts.length > 0 ? (
                    <div className="space-y-2">
                      {conflicts.slice(0, 3).map((conflict, index) => (
                        <div key={index} className="text-sm p-2 bg-gray-50 rounded">
                          <Badge className={getConflictSeverityColor(conflict.severity)}>
                            {conflict.severity}
                          </Badge>
                          <div className="mt-1">
                            {conflict.plant1 && conflict.plant2 && (
                              <span>{conflict.plant1} ↔ {conflict.plant2}</span>
                            )}
                            {conflict.current_distance && (
                              <span> - {conflict.current_distance.toFixed(2)}m</span>
                            )}
                          </div>
                        </div>
                      ))}
                      {conflicts.length > 3 && (
                        <div className="text-sm text-gray-500">
                          +{conflicts.length - 3} more conflicts
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-green-600">No conflicts detected</div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Water Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Water Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(analysis.water_analysis.total_water_needs || {}).map(([level, amount]) => (
                  <div key={level} className="flex justify-between items-center">
                    <span className="capitalize">{level} Water Plants</span>
                    <span className="font-mono">{amount.toFixed(1)} L/day</span>
                  </div>
                ))}
                <Separator />
                <div className="text-sm text-gray-600">
                  Efficiency: {(analysis.water_analysis.efficiency_score * 100).toFixed(1)}%
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Solar Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Solar Exposure</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(analysis.solar_analysis).map(([plantId, exposure]) => (
                  <div key={plantId} className="flex justify-between items-center">
                    <span className="text-sm">{plantId}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full" 
                          style={{ width: `${exposure * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-mono">{(exposure * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {optimization && (
        <Card>
          <CardHeader>
            <CardTitle>Optimization Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{optimization.fitness_score}</div>
                <div className="text-sm text-gray-600">Fitness Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{optimization.conflicts_resolved}</div>
                <div className="text-sm text-gray-600">Conflicts Resolved</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{(optimization.water_efficiency * 100).toFixed(0)}%</div>
                <div className="text-sm text-gray-600">Water Efficiency</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{(optimization.space_utilization * 100).toFixed(0)}%</div>
                <div className="text-sm text-gray-600">Space Utilization</div>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              Computation time: {optimization.computation_time.toFixed(2)}s
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cache Stats */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-semibold">Cache Entries</div>
              <div className="text-gray-600">{agronomicService.getCacheStats().valid_entries}</div>
            </div>
            <div>
              <div className="font-semibold">Cache Size</div>
              <div className="text-gray-600">{agronomicService.getCacheStats().cache_size_mb.toFixed(2)} MB</div>
            </div>
            <div>
              <div className="font-semibold">Worker Status</div>
              <div className="text-gray-600">
                {agronomicService.getCacheStats().worker_ready ? '🟢 Ready' : '🔴 Not Ready'}
              </div>
            </div>
            <div>
              <div className="font-semibold">WebSocket</div>
              <div className="text-gray-600">
                {websocketService.isConnectionActive() ? '🟢 Active' : '🔴 Inactive'}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 