import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Download, FileText, Image as ImageIcon, Printer } from 'lucide-react';

interface Plant {
  id: number;
  name: string;
  x: number;
  y: number;
  water_needs: 'low' | 'moderate' | 'high';
  area_m2: number;
}

interface IrrigationZone {
  id: string;
  name: string;
  plants: Plant[];
  center_x: number;
  center_y: number;
  area_m2: number;
  required_flow_lph: number;
  operating_pressure_bar: number;
  estimated_cost: number;
}

interface IrrigationPipe {
  id: string;
  name: string;
  start_x: number;
  start_y: number;
  end_x: number;
  end_y: number;
  diameter_mm: number;
  material: string;
  flow_rate_lph: number;
  pressure_loss_bar: number;
  cost_per_meter: number;
  total_cost: number;
}

interface Equipment {
  id: string;
  name: string;
  type: 'drip' | 'sprinkler' | 'microjet' | 'rotor' | 'spray';
  flow_rate_lph: number;
  coverage_radius_m: number;
  cost_per_unit: number;
  manufacturer: string;
  model: string;
  spacing_m: number;
  coverage_area: number;
}

interface HydraulicResult {
  total_flow_lph: number;
  total_pressure_loss_bar: number;
  final_pressure_bar: number;
  velocity_ms: number;
  reynolds_number: number;
  friction_factor: number;
  warnings: string[];
  is_system_viable: boolean;
}

interface CostEstimation {
  equipment_cost: number;
  pipe_cost: number;
  installation_cost: number;
  total_cost: number;
  roi_estimate: number;
}

interface WeatherData {
  date: string;
  temperature_c: number;
  humidity_percent: number;
  rainfall_mm: number;
  wind_speed_kmh: number;
  solar_radiation_mj_m2: number;
  evapotranspiration_mm: number;
  irrigation_need_mm: number;
}

export const IrrigationDesigner: React.FC = () => {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [zones, setZones] = useState<IrrigationZone[]>([]);
  const [pipes, setPipes] = useState<IrrigationPipe[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [hydraulicResult, setHydraulicResult] = useState<HydraulicResult | null>(null);
  const [costEstimation, setCostEstimation] = useState<CostEstimation | null>(null);
      const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
    const [isCalculating, setIsCalculating] = useState(false);
    const [activeTab, setActiveTab] = useState('design');
    const [isExporting, setIsExporting] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    // Mock plants
    const mockPlants: Plant[] = [
      { id: 1, name: 'Tomato', x: 10, y: 15, water_needs: 'high', area_m2: 2.0 },
      { id: 2, name: 'Lettuce', x: 25, y: 10, water_needs: 'moderate', area_m2: 1.5 },
      { id: 3, name: 'Carrot', x: 40, y: 20, water_needs: 'moderate', area_m2: 1.0 },
      { id: 4, name: 'Herbs', x: 15, y: 35, water_needs: 'low', area_m2: 0.5 },
      { id: 5, name: 'Pepper', x: 35, y: 30, water_needs: 'high', area_m2: 1.8 },
    ];
    setPlants(mockPlants);

    // Mock equipment
    const mockEquipment: Equipment[] = [
      {
        id: '1',
        name: 'Drip Emitter 4LPH',
        type: 'drip',
        flow_rate_lph: 4.0,
        coverage_radius_m: 0.4,
        cost_per_unit: 0.6,
        manufacturer: 'Rain Bird',
        model: 'XFS-4',
        spacing_m: 0.8,
        coverage_area: 0.5
      },
      {
        id: '2',
        name: 'Spray Head 360°',
        type: 'sprinkler',
        flow_rate_lph: 50.0,
        coverage_radius_m: 3.0,
        cost_per_unit: 2.5,
        manufacturer: 'Hunter',
        model: 'MP Rotator',
        spacing_m: 6.0,
        coverage_area: 28.3
      },
      {
        id: '3',
        name: 'Microjet 25LPH',
        type: 'microjet',
        flow_rate_lph: 25.0,
        coverage_radius_m: 2.0,
        cost_per_unit: 1.5,
        manufacturer: 'Netafim',
        model: 'MJ-25',
        spacing_m: 4.0,
        coverage_area: 12.6
      }
    ];
    setEquipment(mockEquipment);

    // Mock weather data
    const mockWeather: WeatherData[] = [
      {
        date: '2024-01-15',
        temperature_c: 22.5,
        humidity_percent: 65,
        rainfall_mm: 0,
        wind_speed_kmh: 8,
        solar_radiation_mj_m2: 18.5,
        evapotranspiration_mm: 3.2,
        irrigation_need_mm: 2.8
      },
      {
        date: '2024-01-16',
        temperature_c: 24.0,
        humidity_percent: 60,
        rainfall_mm: 0,
        wind_speed_kmh: 12,
        solar_radiation_mj_m2: 20.1,
        evapotranspiration_mm: 3.8,
        irrigation_need_mm: 3.4
      }
    ];
    setWeatherData(mockWeather);
  }, []);

  const performClustering = useCallback(async () => {
    setIsCalculating(true);
    try {
      // Mock clustering result
      const mockZones: IrrigationZone[] = [
        {
          id: 'zone1',
          name: 'Zone 1 - High Water Needs',
          plants: plants.filter(p => p.water_needs === 'high'),
          center_x: 22.5,
          center_y: 22.5,
          area_m2: 3.8,
          required_flow_lph: 76,
          operating_pressure_bar: 1.5,
          estimated_cost: 45.0
        },
        {
          id: 'zone2',
          name: 'Zone 2 - Moderate Water Needs',
          plants: plants.filter(p => p.water_needs === 'moderate'),
          center_x: 32.5,
          center_y: 15.0,
          area_m2: 2.5,
          required_flow_lph: 50,
          operating_pressure_bar: 1.3,
          estimated_cost: 32.0
        },
        {
          id: 'zone3',
          name: 'Zone 3 - Low Water Needs',
          plants: plants.filter(p => p.water_needs === 'low'),
          center_x: 15.0,
          center_y: 35.0,
          area_m2: 0.5,
          required_flow_lph: 10,
          operating_pressure_bar: 1.0,
          estimated_cost: 8.0
        }
      ];
      setZones(mockZones);
      toast.success('Plant clustering completed successfully!');
    } catch (error) {
      toast.error('Error performing clustering');
    } finally {
      setIsCalculating(false);
    }
  }, [plants]);

  const calculateHydraulics = useCallback(async () => {
    if (zones.length === 0) {
      toast.error('Please perform clustering first');
      return;
    }

    setIsCalculating(true);
    try {
      // Mock hydraulic calculation
      const mockResult: HydraulicResult = {
        total_flow_lph: 136,
        total_pressure_loss_bar: 0.8,
        final_pressure_bar: 1.7,
        velocity_ms: 1.2,
        reynolds_number: 8500,
        friction_factor: 0.025,
        warnings: [],
        is_system_viable: true
      };
      setHydraulicResult(mockResult);
      toast.success('Hydraulic calculations completed!');
    } catch (error) {
      toast.error('Error calculating hydraulics');
    } finally {
      setIsCalculating(false);
    }
  }, [zones]);

  const estimateCosts = useCallback(async () => {
    if (zones.length === 0) {
      toast.error('Please perform clustering first');
      return;
    }

    setIsCalculating(true);
    try {
      // Mock cost estimation
      const mockCosts: CostEstimation = {
        equipment_cost: 85.0,
        pipe_cost: 120.0,
        installation_cost: 61.5,
        total_cost: 266.5,
        roi_estimate: 375.2
      };
      setCostEstimation(mockCosts);
      toast.success('Cost estimation completed!');
    } catch (error) {
      toast.error('Error estimating costs');
    } finally {
      setIsCalculating(false);
    }
  }, [zones]);

  const handleExportPDF = useCallback(async () => {
    setIsExporting(true);
    try {
      // Simulate API call to export PDF
      const systemDesign = {
        zones,
        hydraulic_calculations: hydraulicResult,
        cost_estimation: costEstimation,
        pipe_network: pipes,
        equipment_selections: equipment.map(eq => ({
          recommended_equipment: eq,
          quantity_needed: Math.ceil(eq.coverage_area / eq.spacing_m),
          total_cost: eq.cost_per_unit * Math.ceil(eq.coverage_area / eq.spacing_m),
          coverage_efficiency: 0.85
        }))
      };
      
      // In a real implementation, this would call the backend API
      console.log('Exporting PDF with system design:', systemDesign);
      
      // Simulate download
      const blob = new Blob(['PDF content would be here'], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `irrigation_technical_report_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('PDF technical report exported successfully');
    } catch (error) {
      toast.error('Failed to export PDF');
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
    }
  }, [zones, hydraulicResult, costEstimation, pipes, equipment]);

  const handleExportSVG = useCallback(async (type: 'layout' | 'pipe-network') => {
    setIsExporting(true);
    try {
      // Simulate API call to export SVG
      const systemDesign = {
        zones,
        hydraulic_calculations: hydraulicResult,
        cost_estimation: costEstimation,
        pipe_network: pipes,
        equipment_selections: equipment.map(eq => ({
          recommended_equipment: eq,
          quantity_needed: Math.ceil(eq.coverage_area / eq.spacing_m),
          total_cost: eq.cost_per_unit * Math.ceil(eq.coverage_area / eq.spacing_m),
          coverage_efficiency: 0.85
        }))
      };
      
      // In a real implementation, this would call the backend API
      console.log(`Exporting SVG ${type} with system design:`, systemDesign);
      
      // Simulate download
      const svgContent = `<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
        <rect width="800" height="600" fill="#ffffff"/>
        <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="16">
          ${type === 'layout' ? 'System Layout' : 'Pipe Network'} SVG Export
        </text>
      </svg>`;
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `irrigation_${type}_${Date.now()}.svg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success(`${type === 'layout' ? 'System Layout' : 'Pipe Network'} SVG exported successfully`);
    } catch (error) {
      toast.error(`Failed to export ${type} SVG`);
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
    }
  }, [zones, hydraulicResult, costEstimation, pipes, equipment]);

  const handleExportAll = useCallback(async () => {
    setIsExporting(true);
    try {
      // Simulate API call to export all formats
      const systemDesign = {
        zones,
        hydraulic_calculations: hydraulicResult,
        cost_estimation: costEstimation,
        pipe_network: pipes,
        equipment_selections: equipment.map(eq => ({
          recommended_equipment: eq,
          quantity_needed: Math.ceil(eq.coverage_area / eq.spacing_m),
          total_cost: eq.cost_per_unit * Math.ceil(eq.coverage_area / eq.spacing_m),
          coverage_efficiency: 0.85
        }))
      };
      
      // In a real implementation, this would call the backend API
      console.log('Exporting all formats with system design:', systemDesign);
      
      // Simulate multiple downloads
      const formats = [
        { type: 'pdf', content: 'PDF content', filename: 'technical_report.pdf' },
        { type: 'svg', content: '<svg>Layout SVG</svg>', filename: 'system_layout.svg' },
        { type: 'svg', content: '<svg>Pipe Network SVG</svg>', filename: 'pipe_network.svg' }
      ];
      
      formats.forEach(format => {
        const blob = new Blob([format.content], { 
          type: format.type === 'pdf' ? 'application/pdf' : 'image/svg+xml' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = format.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
      
      toast.success('All technical plans exported successfully');
    } catch (error) {
      toast.error('Failed to export technical plans');
      console.error('Export error:', error);
    } finally {
      setIsExporting(false);
    }
  }, [zones, hydraulicResult, costEstimation, pipes, equipment]);

  const generatePipeNetwork = useCallback(() => {
    if (zones.length === 0) {
      toast.error('Please perform clustering first');
      return;
    }

    // Mock pipe network generation
    const mockPipes: IrrigationPipe[] = [
      {
        id: 'main1',
        name: 'Main Line',
        start_x: 0,
        start_y: 0,
        end_x: 50,
        end_y: 0,
        diameter_mm: 32,
        material: 'PVC',
        flow_rate_lph: 136,
        pressure_loss_bar: 0.3,
        cost_per_meter: 2.5,
        total_cost: 125.0
      },
      {
        id: 'lateral1',
        name: 'Lateral 1',
        start_x: 50,
        start_y: 0,
        end_x: 70,
        end_y: 22.5,
        diameter_mm: 20,
        material: 'PVC',
        flow_rate_lph: 76,
        pressure_loss_bar: 0.2,
        cost_per_meter: 1.8,
        total_cost: 36.0
      },
      {
        id: 'lateral2',
        name: 'Lateral 2',
        start_x: 50,
        start_y: 0,
        end_x: 70,
        end_y: 15.0,
        diameter_mm: 16,
        material: 'PVC',
        flow_rate_lph: 50,
        pressure_loss_bar: 0.15,
        cost_per_meter: 1.5,
        total_cost: 30.0
      }
    ];
    setPipes(mockPipes);
    toast.success('Pipe network generated!');
  }, [zones]);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Irrigation System Designer</h1>
        <div className="flex gap-2">
          <Button onClick={performClustering} disabled={isCalculating}>
            {isCalculating ? 'Clustering...' : 'Perform Clustering'}
          </Button>
          <Button onClick={calculateHydraulics} disabled={zones.length === 0 || isCalculating}>
            {isCalculating ? 'Calculating...' : 'Calculate Hydraulics'}
          </Button>
          <Button onClick={estimateCosts} disabled={zones.length === 0 || isCalculating}>
            {isCalculating ? 'Estimating...' : 'Estimate Costs'}
          </Button>
        </div>
      </div>

      {/* Export Controls */}
      {(zones.length > 0 || hydraulicResult || costEstimation) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Export Technical Plans
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button 
                onClick={handleExportPDF} 
                disabled={isExporting}
                variant="outline"
                className="flex items-center gap-2"
              >
                <FileText className="h-4 w-4" />
                {isExporting ? 'Exporting PDF...' : 'Export PDF Report'}
              </Button>
              <Button 
                onClick={() => handleExportSVG('layout')} 
                disabled={isExporting}
                variant="outline"
                className="flex items-center gap-2"
              >
                <ImageIcon className="h-4 w-4" />
                {isExporting ? 'Exporting...' : 'Export Layout SVG'}
              </Button>
              <Button 
                onClick={() => handleExportSVG('pipe-network')} 
                disabled={isExporting}
                variant="outline"
                className="flex items-center gap-2"
              >
                <ImageIcon className="h-4 w-4" />
                {isExporting ? 'Exporting...' : 'Export Pipe Network SVG'}
              </Button>
              <Button 
                onClick={handleExportAll} 
                disabled={isExporting}
                className="flex items-center gap-2"
              >
                <Printer className="h-4 w-4" />
                {isExporting ? 'Exporting All...' : 'Export All Plans'}
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Generate professional technical reports and drawings for your irrigation system design.
            </p>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="design">Design</TabsTrigger>
          <TabsTrigger value="zones">Zones</TabsTrigger>
          <TabsTrigger value="pipes">Pipes</TabsTrigger>
          <TabsTrigger value="equipment">Equipment</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="design" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Garden Layout</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative w-full h-80 bg-gray-100 border rounded-lg">
                  {/* Mock garden layout visualization */}
                  <div className="absolute inset-0 p-4">
                    {plants.map((plant) => (
                      <div
                        key={plant.id}
                        className={`absolute w-4 h-4 rounded-full ${
                          plant.water_needs === 'high' ? 'bg-red-500' :
                          plant.water_needs === 'moderate' ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{
                          left: `${(plant.x / 50) * 100}%`,
                          top: `${(plant.y / 40) * 100}%`
                        }}
                        title={`${plant.name} (${plant.water_needs} water needs)`}
                      />
                    ))}
                    {zones.map((zone) => (
                      <div
                        key={zone.id}
                        className="absolute border-2 border-blue-500 rounded-lg bg-blue-100 bg-opacity-30"
                        style={{
                          left: `${(zone.center_x - 5) / 50 * 100}%`,
                          top: `${(zone.center_y - 5) / 40 * 100}%`,
                          width: '10%',
                          height: '10%'
                        }}
                        title={zone.name}
                      />
                    ))}
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span className="text-sm">High water needs</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm">Moderate water needs</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm">Low water needs</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="source-pressure">Source Pressure (bar)</Label>
                    <Input id="source-pressure" type="number" defaultValue="2.5" step="0.1" />
                  </div>
                  <div>
                    <Label htmlFor="source-flow">Source Flow (LPH)</Label>
                    <Input id="source-flow" type="number" defaultValue="1000" />
                  </div>
                </div>
                <div>
                  <Label htmlFor="pipe-material">Pipe Material</Label>
                  <Select defaultValue="pvc">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pvc">PVC</SelectItem>
                      <SelectItem value="pe">PE</SelectItem>
                      <SelectItem value="pex">PEX</SelectItem>
                      <SelectItem value="copper">Copper</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="max-zones">Max Zones</Label>
                  <Input id="max-zones" type="number" defaultValue="5" min="1" max="10" />
                </div>
                <Button onClick={generatePipeNetwork} className="w-full">
                  Generate Pipe Network
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="zones" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Irrigation Zones</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {zones.map((zone) => (
                  <div key={zone.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{zone.name}</h3>
                        <p className="text-sm text-gray-600">
                          {zone.plants.length} plants, {zone.area_m2.toFixed(1)} m²
                        </p>
                      </div>
                      <Badge variant={zone.required_flow_lph > 50 ? "destructive" : "default"}>
                        {zone.required_flow_lph} LPH
                      </Badge>
                    </div>
                    <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Flow Rate:</span> {zone.required_flow_lph} LPH
                      </div>
                      <div>
                        <span className="font-medium">Pressure:</span> {zone.operating_pressure_bar} bar
                      </div>
                      <div>
                        <span className="font-medium">Cost:</span> ${zone.estimated_cost.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pipes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pipe Network</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pipes.map((pipe) => (
                  <div key={pipe.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{pipe.name}</h3>
                        <p className="text-sm text-gray-600">
                          {pipe.material} {pipe.diameter_mm}mm
                        </p>
                      </div>
                      <Badge variant="outline">
                        {pipe.flow_rate_lph} LPH
                      </Badge>
                    </div>
                    <div className="mt-2 grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Length:</span> {pipe.length_m}m
                      </div>
                      <div>
                        <span className="font-medium">Pressure Loss:</span> {pipe.pressure_loss_bar} bar
                      </div>
                      <div>
                        <span className="font-medium">Cost/m:</span> ${pipe.cost_per_meter}
                      </div>
                      <div>
                        <span className="font-medium">Total Cost:</span> ${pipe.total_cost.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="equipment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Available Equipment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {equipment.map((item) => (
                  <div key={item.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{item.name}</h3>
                        <p className="text-sm text-gray-600">
                          {item.manufacturer} - {item.model}
                        </p>
                      </div>
                      <Badge variant="secondary">{item.type}</Badge>
                    </div>
                    <div className="mt-2 grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Flow Rate:</span> {item.flow_rate_lph} LPH
                      </div>
                      <div>
                        <span className="font-medium">Coverage:</span> {item.coverage_radius_m}m
                      </div>
                      <div>
                        <span className="font-medium">Cost:</span> ${item.cost_per_unit}
                      </div>
                      <div>
                        <span className="font-medium">Type:</span> {item.type}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {hydraulicResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Hydraulic Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>System Viability</span>
                      <Badge variant={hydraulicResult.is_system_viable ? "default" : "destructive"}>
                        {hydraulicResult.is_system_viable ? "Viable" : "Not Viable"}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total Flow:</span>
                        <span>{hydraulicResult.total_flow_lph} LPH</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Pressure Loss:</span>
                        <span>{hydraulicResult.total_pressure_loss_bar} bar</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Final Pressure:</span>
                        <span>{hydraulicResult.final_pressure_bar} bar</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Velocity:</span>
                        <span>{hydraulicResult.velocity_ms} m/s</span>
                      </div>
                    </div>
                    {hydraulicResult.warnings.length > 0 && (
                      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                        <h4 className="font-medium text-yellow-800">Warnings:</h4>
                        <ul className="mt-2 text-sm text-yellow-700">
                          {hydraulicResult.warnings.map((warning, index) => (
                            <li key={index}>• {warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {costEstimation && (
              <Card>
                <CardHeader>
                  <CardTitle>Cost Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Equipment Cost:</span>
                        <span>${costEstimation.equipment_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Pipe Cost:</span>
                        <span>${costEstimation.pipe_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Installation Cost:</span>
                        <span>${costEstimation.installation_cost.toFixed(2)}</span>
                      </div>
                      <Separator />
                      <div className="flex justify-between font-semibold">
                        <span>Total Cost:</span>
                        <span>${costEstimation.total_cost.toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="mt-4">
                      <div className="flex justify-between mb-2">
                        <span>ROI Estimate:</span>
                        <span>{costEstimation.roi_estimate.toFixed(1)}%</span>
                      </div>
                      <Progress value={Math.min(costEstimation.roi_estimate, 100)} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Weather Data & Scheduling</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {weatherData.map((weather, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{weather.date}</h4>
                        <Badge variant="outline">
                          {weather.irrigation_need_mm > 2 ? "High Need" : "Low Need"}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Temperature:</span> {weather.temperature_c}°C
                        </div>
                        <div>
                          <span className="font-medium">Humidity:</span> {weather.humidity_percent}%
                        </div>
                        <div>
                          <span className="font-medium">Rainfall:</span> {weather.rainfall_mm}mm
                        </div>
                        <div>
                          <span className="font-medium">Irrigation Need:</span> {weather.irrigation_need_mm}mm
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 