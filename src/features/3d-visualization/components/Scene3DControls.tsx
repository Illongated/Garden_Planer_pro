import React, { useState, useCallback } from 'react';
import { 
  Camera, 
  Sun, 
  Moon, 
  Cloud, 
  CloudRain, 
  Eye, 
  EyeOff, 
  Grid3X3, 
  Ruler, 
  Type, 
  Download, 
  Settings, 
  RotateCcw, 
  Maximize, 
  Minimize,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Calendar,
  Clock,
  Thermometer,
  Droplets,
  Wind,
  Sparkles,
  Layers,
  Box,
  Globe,
  MapPin,
  Target,
  Move,
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw as RotateCcwIcon,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Home,
  Search,
  Filter,
  Sliders,
  Palette,
  Lightbulb,
  Monitor,
  Smartphone,
  Tablet,
  Headphones,
  Video,
  Image,
  FileText,
  Share,
  Save,
  Loader,
  Check,
  X,
  Plus,
  Minus,
  Edit,
  Trash,
  Copy,
  Paste,
  Undo,
  Redo,
  Lock,
  Unlock,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  AlertCircle,
  Info,
  HelpCircle,
  ExternalLink,
  Link,
  Unlink,
  Shield,
  ShieldOff,
  Wifi,
  WifiOff,
  Battery,
  BatteryCharging,
  Volume,
  VolumeX,
  Volume1,
  Volume2,
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  Mail,
  MessageSquare,
  MessageCircle,
  Send,
  Paperclip,
  Smile,
  Frown,
  Meh,
  Laugh,
  Cry,
  Angry,
  Surprised,
  Wink,
  Tongue,
  Kiss,
  Heart as HeartIcon,
  Star as StarIcon,
  Zap,
  ZapOff,
  Flash,
  FlashOff,
  Fire,
  Snowflake,
  Umbrella,
  Anchor,
  Ship,
  Plane,
  Car,
  Bike,
  Walk,
  Run,
  Swim,
  Ski,
  Surf,
  Skateboard,
  Snowboard,
  Golf,
  Tennis,
  Basketball,
  Football,
  Baseball,
  Soccer,
  Volleyball,
  Hockey,
  Cricket,
  Rugby,
  Boxing,
  Wrestling,
  Judo,
  Karate,
  Taekwondo,
  Kungfu,
  Yoga,
  Pilates,
  Gym,
  Weight,
  Dumbbell,
  Treadmill,
  Bike as BikeIcon,
  Pool,
  Sauna,
  Massage,
  Spa,
  Hotel,
  Restaurant,
  Cafe,
  Bar,
  Store,
  ShoppingCart,
  ShoppingBag,
  CreditCard,
  DollarSign,
  Euro,
  Pound,
  Yen,
  Bitcoin,
  Ethereum,
  Wallet,
  PiggyBank,
  Safe,
  Vault,
  Lock as LockIcon,
  Unlock as UnlockIcon,
  Key,
  Fingerprint,
  Scan,
  QrCode,
  Barcode,
  Tag,
  PriceTag,
  Discount,
  Percent,
  Calculator,
  Chart,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart,
  BarChart3,
  PieChart,
  LineChart,
  ScatterChart,
  AreaChart,
  DonutChart,
  RadarChart,
  HeatMap,
  Map,
  Navigation,
  Compass,
  Globe as GlobeIcon,
  MapPin as MapPinIcon,
  Navigation as NavigationIcon,
  Route,
  Road,
  Highway,
  Street,
  Avenue,
  Boulevard,
  Lane,
  Drive,
  Court,
  Place,
  Plaza,
  Square,
  Circle,
  Triangle,
  Diamond,
  Hexagon,
  Octagon,
  Star as StarIcon2,
  Heart as HeartIcon2,
  Circle as CircleIcon,
  Square as SquareIcon,
  Triangle as TriangleIcon,
  Diamond as DiamondIcon,
  Hexagon as HexagonIcon,
  Octagon as OctagonIcon,
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Slider } from '../../../components/ui/slider';
import { Switch } from '../../../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Badge } from '../../../components/ui/badge';
import { Separator } from '../../../components/ui/separator';
import { useScene3DStore, useScene3DSelector } from '../store/scene3DStore';
import { 
  CameraMode, 
  ViewMode, 
  ExportOptions,
  MeasurementTool,
  Annotation3D,
} from '../../../types/3d-visualization';
import { toast } from 'sonner';

interface Scene3DControlsProps {
  className?: string;
}

const Scene3DControls: React.FC<Scene3DControlsProps> = ({ className }) => {
  const [activeTab, setActiveTab] = useState<'camera' | 'lighting' | 'export' | 'tools' | 'settings'>('camera');
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Store selectors
  const cameraMode = useScene3DSelector.cameraMode();
  const viewMode = useScene3DSelector.viewMode();
  const isAnimating = useScene3DSelector.isAnimating();
  const isExporting = useScene3DSelector.isExporting();
  const isMeasuring = useScene3DSelector.isMeasuring();
  const selectedPlant = useScene3DSelector.selectedPlant();
  const performance = useScene3DSelector.performance();
  const webXR = useScene3DSelector.webXR();
  const currentScene = useScene3DSelector.currentScene();
  
  // Store actions
  const setCameraMode = useScene3DStore(state => state.setCameraMode);
  const setViewMode = useScene3DStore(state => state.setViewMode);
  const setAnimating = useScene3DStore(state => state.setAnimating);
  const setExporting = useScene3DStore(state => state.setExporting);
  const setMeasuring = useScene3DStore(state => state.setMeasuring);
  const resetCamera = useScene3DStore(state => state.resetCamera);
  const toggleFullscreen = useScene3DStore(state => state.toggleFullscreen);
  const updateLighting = useScene3DStore(state => state.updateLighting);
  const setTimeOfDay = useScene3DStore(state => state.setTimeOfDay);
  const setSeason = useScene3DStore(state => state.setSeason);
  const setWeather = useScene3DStore(state => state.setWeather);
  const focusOnSelection = useScene3DStore(state => state.focusOnSelection);
  const clearMeasurements = useScene3DStore(state => state.clearMeasurements);
  const clearAnnotations = useScene3DStore(state => state.clearAnnotations);
  
  // Camera mode handlers
  const handleCameraModeChange = useCallback((mode: CameraMode) => {
    setCameraMode(mode);
    toast.success(`Camera mode changed to ${mode}`);
  }, [setCameraMode]);
  
  // View mode handlers
  const handleViewModeChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
    toast.success(`View mode changed to ${mode}`);
  }, [setViewMode]);
  
  // Animation controls
  const handleAnimationToggle = useCallback(() => {
    setAnimating(!isAnimating);
    toast.success(isAnimating ? 'Animation paused' : 'Animation started');
  }, [isAnimating, setAnimating]);
  
  // Export handlers
  const handleExportImage = useCallback(async () => {
    setExporting(true);
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Image exported successfully');
    } catch (error) {
      toast.error('Failed to export image');
    } finally {
      setExporting(false);
    }
  }, [setExporting]);
  
  const handleExportVideo = useCallback(async () => {
    setExporting(true);
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 5000));
      toast.success('Video exported successfully');
    } catch (error) {
      toast.error('Failed to export video');
    } finally {
      setExporting(false);
    }
  }, [setExporting]);
  
  // Measurement tools
  const handleMeasurementToggle = useCallback(() => {
    setMeasuring(!isMeasuring);
    toast.success(isMeasuring ? 'Measurement mode disabled' : 'Measurement mode enabled');
  }, [isMeasuring, setMeasuring]);
  
  const handleClearMeasurements = useCallback(() => {
    clearMeasurements();
    toast.success('All measurements cleared');
  }, [clearMeasurements]);
  
  // Lighting controls
  const handleTimeOfDayChange = useCallback((value: number[]) => {
    const time = value[0];
    setTimeOfDay(time);
  }, [setTimeOfDay]);
  
  const handleSeasonChange = useCallback((season: 'spring' | 'summer' | 'autumn' | 'winter') => {
    setSeason(season);
    toast.success(`Season changed to ${season}`);
  }, [setSeason]);
  
  const handleWeatherChange = useCallback((weather: 'clear' | 'cloudy' | 'rainy' | 'overcast') => {
    setWeather(weather);
    toast.success(`Weather changed to ${weather}`);
  }, [setWeather]);
  
  // Fullscreen handler
  const handleFullscreenToggle = useCallback(() => {
    toggleFullscreen();
    setIsFullscreen(!isFullscreen);
  }, [toggleFullscreen, isFullscreen]);
  
  const tabs = [
    { id: 'camera', label: 'Camera', icon: Camera },
    { id: 'lighting', label: 'Lighting', icon: Sun },
    { id: 'export', label: 'Export', icon: Download },
    { id: 'tools', label: 'Tools', icon: Settings },
    { id: 'settings', label: 'Settings', icon: Settings },
  ] as const;
  
  return (
    <div className={`bg-white/90 backdrop-blur-sm border rounded-lg shadow-lg p-4 ${className}`}>
      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-4">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2"
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </Button>
          );
        })}
      </div>
      
      {/* Camera Controls */}
      {activeTab === 'camera' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Camera Mode</h3>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={cameraMode === 'top-down' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCameraModeChange('top-down')}
              >
                <ArrowDown className="h-4 w-4 mr-2" />
                Top Down
              </Button>
              <Button
                variant={cameraMode === 'isometric' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCameraModeChange('isometric')}
              >
                <Box className="h-4 w-4 mr-2" />
                Isometric
              </Button>
              <Button
                variant={cameraMode === 'freelook' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCameraModeChange('freelook')}
              >
                <Eye className="h-4 w-4 mr-2" />
                Free Look
              </Button>
              <Button
                variant={cameraMode === 'walkthrough' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCameraModeChange('walkthrough')}
              >
                <Walk className="h-4 w-4 mr-2" />
                Walkthrough
              </Button>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">View Mode</h3>
            <div className="flex gap-2">
              <Button
                variant={viewMode === '2d' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleViewModeChange('2d')}
              >
                <Grid3X3 className="h-4 w-4 mr-2" />
                2D
              </Button>
              <Button
                variant={viewMode === '3d' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleViewModeChange('3d')}
              >
                <Box className="h-4 w-4 mr-2" />
                3D
              </Button>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={resetCamera}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset Camera
            </Button>
            <Button variant="outline" size="sm" onClick={focusOnSelection}>
              <Target className="h-4 w-4 mr-2" />
              Focus Selection
            </Button>
            <Button variant="outline" size="sm" onClick={handleFullscreenToggle}>
              {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      )}
      
      {/* Lighting Controls */}
      {activeTab === 'lighting' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Time of Day</h3>
            <Slider
              value={[currentScene?.lighting.timeOfDay || 12]}
              onValueChange={handleTimeOfDayChange}
              max={24}
              min={0}
              step={0.5}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Dawn</span>
              <span>Noon</span>
              <span>Dusk</span>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Season</h3>
            <Select value={currentScene?.lighting.season} onValueChange={handleSeasonChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="spring">Spring</SelectItem>
                <SelectItem value="summer">Summer</SelectItem>
                <SelectItem value="autumn">Autumn</SelectItem>
                <SelectItem value="winter">Winter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Weather</h3>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={currentScene?.lighting.weather === 'clear' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleWeatherChange('clear')}
              >
                <Sun className="h-4 w-4 mr-2" />
                Clear
              </Button>
              <Button
                variant={currentScene?.lighting.weather === 'cloudy' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleWeatherChange('cloudy')}
              >
                <Cloud className="h-4 w-4 mr-2" />
                Cloudy
              </Button>
              <Button
                variant={currentScene?.lighting.weather === 'rainy' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleWeatherChange('rainy')}
              >
                <CloudRain className="h-4 w-4 mr-2" />
                Rainy
              </Button>
              <Button
                variant={currentScene?.lighting.weather === 'overcast' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleWeatherChange('overcast')}
              >
                <Cloud className="h-4 w-4 mr-2" />
                Overcast
              </Button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Shadows</span>
            <Switch
              checked={currentScene?.lighting.enableShadows}
              onCheckedChange={(checked) => updateLighting({ enableShadows: checked })}
            />
          </div>
        </div>
      )}
      
      {/* Export Controls */}
      {activeTab === 'export' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Export Options</h3>
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportImage}
                disabled={isExporting}
                className="w-full"
              >
                <Image className="h-4 w-4 mr-2" />
                {isExporting ? 'Exporting...' : 'Export Image'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportVideo}
                disabled={isExporting}
                className="w-full"
              >
                <Video className="h-4 w-4 mr-2" />
                {isExporting ? 'Exporting...' : 'Export Video'}
              </Button>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Quality Settings</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Resolution</span>
                <Select defaultValue="hd">
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sd">SD</SelectItem>
                    <SelectItem value="hd">HD</SelectItem>
                    <SelectItem value="4k">4K</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Format</span>
                <Select defaultValue="png">
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="png">PNG</SelectItem>
                    <SelectItem value="jpg">JPG</SelectItem>
                    <SelectItem value="webp">WebP</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Tools */}
      {activeTab === 'tools' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Animation</h3>
            <Button
              variant={isAnimating ? 'default' : 'outline'}
              size="sm"
              onClick={handleAnimationToggle}
              className="w-full"
            >
              {isAnimating ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {isAnimating ? 'Pause Animation' : 'Start Animation'}
            </Button>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Measurement Tools</h3>
            <div className="space-y-2">
              <Button
                variant={isMeasuring ? 'default' : 'outline'}
                size="sm"
                onClick={handleMeasurementToggle}
                className="w-full"
              >
                <Ruler className="h-4 w-4 mr-2" />
                {isMeasuring ? 'Disable' : 'Enable'} Measurement
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearMeasurements}
                className="w-full"
              >
                <Trash className="h-4 w-4 mr-2" />
                Clear Measurements
              </Button>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Annotations</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={clearAnnotations}
              className="w-full"
            >
              <Trash className="h-4 w-4 mr-2" />
              Clear Annotations
            </Button>
          </div>
        </div>
      )}
      
      {/* Settings */}
      {activeTab === 'settings' && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2">Performance</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span>FPS:</span>
                <span>{Math.round(performance.fps)}</span>
              </div>
              <div className="flex justify-between">
                <span>Draw Calls:</span>
                <span>{performance.drawCalls}</span>
              </div>
              <div className="flex justify-between">
                <span>Triangles:</span>
                <span>{performance.triangles}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">WebXR</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Supported</span>
                <Badge variant={webXR.isSupported ? 'default' : 'secondary'}>
                  {webXR.isSupported ? 'Yes' : 'No'}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Active</span>
                <Badge variant={webXR.isActive ? 'default' : 'secondary'}>
                  {webXR.isActive ? 'Yes' : 'No'}
                </Badge>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold mb-2">Selected Plant</h3>
            {selectedPlant ? (
              <div className="text-xs space-y-1">
                <div><strong>Name:</strong> {selectedPlant.name}</div>
                <div><strong>Species:</strong> {selectedPlant.species}</div>
                <div><strong>Health:</strong> {Math.round(selectedPlant.health * 100)}%</div>
                <div><strong>Age:</strong> {selectedPlant.age} days</div>
              </div>
            ) : (
              <span className="text-xs text-gray-500">No plant selected</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Scene3DControls; 