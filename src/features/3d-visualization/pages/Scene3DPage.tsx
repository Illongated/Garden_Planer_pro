import React, { useEffect, useState, useCallback } from 'react';
import { 
  ArrowLeft, 
  Home, 
  Settings, 
  HelpCircle, 
  Info, 
  Download, 
  Share, 
  Bookmark,
  Eye,
  EyeOff,
  Layers,
  Grid3X3,
  Box,
  Globe,
  Camera,
  Sun,
  Moon,
  Cloud,
  CloudRain,
  Thermometer,
  Droplets,
  Wind,
  Calendar,
  Clock,
  MapPin,
  Target,
  Ruler,
  Type,
  Image,
  Video,
  FileText,
  Share2,
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
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  AlertCircle,
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
import { Badge } from '../../../components/ui/badge';
import { Separator } from '../../../components/ui/separator';
import { useScene3DStore, useScene3DSelector } from '../store/scene3DStore';
import Scene3D from '../components/Scene3D';
import Scene3DControls from '../components/Scene3DControls';
import { 
  Scene3DConfig, 
  Plant3DModel, 
  Vector3, 
  Euler, 
  Color,
  CameraMode,
  ViewMode,
} from '../../../types/3d-visualization';
import { toast } from 'sonner';

// Mock 3D scene data for demonstration
const createMockScene3D = (): Scene3DConfig => ({
  id: 'mock-garden-3d',
  name: 'Demo Garden 3D',
  description: 'A beautiful 3D garden with various plants and realistic lighting',
  gardenId: 'demo-garden',
  plants: [
    {
      id: 'plant-1',
      name: 'Tomato Plant',
      species: 'Solanum lycopersicum',
      growthStage: 'fruiting',
      position: new Vector3(2, 0, 2),
      rotation: new Euler(0, 0, 0),
      scale: new Vector3(1, 1, 1),
      health: 0.9,
      age: 45,
      maxAge: 90,
      modelPath: '/models/tomato.glb',
      texturePath: '/textures/tomato.jpg',
      height: 1.2,
      spread: 0.8,
      rootDepth: 0.3,
      waterNeeds: 0.7,
      sunlightNeeds: 0.8,
      temperatureRange: [15, 30],
      seasonalGrowth: {
        spring: 0.3,
        summer: 0.8,
        autumn: 0.2,
        winter: 0.0,
      },
    },
    {
      id: 'plant-2',
      name: 'Basil Plant',
      species: 'Ocimum basilicum',
      growthStage: 'vegetative',
      position: new Vector3(-1, 0, 1),
      rotation: new Euler(0, 0, 0),
      scale: new Vector3(0.8, 0.8, 0.8),
      health: 0.95,
      age: 30,
      maxAge: 60,
      modelPath: '/models/basil.glb',
      texturePath: '/textures/basil.jpg',
      height: 0.6,
      spread: 0.4,
      rootDepth: 0.2,
      waterNeeds: 0.6,
      sunlightNeeds: 0.7,
      temperatureRange: [18, 28],
      seasonalGrowth: {
        spring: 0.4,
        summer: 0.9,
        autumn: 0.3,
        winter: 0.0,
      },
    },
    {
      id: 'plant-3',
      name: 'Lettuce Plant',
      species: 'Lactuca sativa',
      growthStage: 'mature',
      position: new Vector3(0, 0, -2),
      rotation: new Euler(0, 0, 0),
      scale: new Vector3(1.2, 1.2, 1.2),
      health: 0.85,
      age: 25,
      maxAge: 40,
      modelPath: '/models/lettuce.glb',
      texturePath: '/textures/lettuce.jpg',
      height: 0.3,
      spread: 0.5,
      rootDepth: 0.15,
      waterNeeds: 0.8,
      sunlightNeeds: 0.6,
      temperatureRange: [10, 25],
      seasonalGrowth: {
        spring: 0.7,
        summer: 0.4,
        autumn: 0.6,
        winter: 0.2,
      },
    },
    {
      id: 'plant-4',
      name: 'Carrot Plant',
      species: 'Daucus carota',
      growthStage: 'vegetative',
      position: new Vector3(-2, 0, -1),
      rotation: new Euler(0, 0, 0),
      scale: new Vector3(0.9, 0.9, 0.9),
      health: 0.75,
      age: 35,
      maxAge: 75,
      modelPath: '/models/carrot.glb',
      texturePath: '/textures/carrot.jpg',
      height: 0.4,
      spread: 0.3,
      rootDepth: 0.25,
      waterNeeds: 0.5,
      sunlightNeeds: 0.7,
      temperatureRange: [12, 28],
      seasonalGrowth: {
        spring: 0.6,
        summer: 0.7,
        autumn: 0.5,
        winter: 0.1,
      },
    },
  ],
  lighting: {
    timeOfDay: 14, // 2 PM
    season: 'summer',
    weather: 'clear',
    ambientIntensity: 0.3,
    directionalIntensity: 1.0,
    shadowQuality: 'high',
    enableShadows: true,
    enableFog: false,
    fogDensity: 0.01,
  },
  camera: {
    mode: 'isometric',
    position: new Vector3(15, 15, 15),
    target: new Vector3(0, 0, 0),
    fov: 60,
    near: 0.1,
    far: 1000,
    enableOrbitControls: true,
    enableDamping: true,
    dampingFactor: 0.05,
    maxDistance: 50,
    minDistance: 1,
    maxPolarAngle: Math.PI,
    minPolarAngle: 0,
  },
  navigation: {
    enablePan: true,
    enableRotate: true,
    enableZoom: true,
    enableDolly: true,
    panSpeed: 1.0,
    rotateSpeed: 1.0,
    zoomSpeed: 1.0,
    dollySpeed: 1.0,
  },
  ground: {
    size: 20,
    texturePath: '/textures/grass.jpg',
    color: new Color(0x4ade80),
    roughness: 0.8,
    metalness: 0.1,
  },
  environment: {
    skyboxPath: '/textures/skybox.jpg',
    backgroundType: 'skybox',
    backgroundColor: new Color(0x87ceeb),
    enableFog: false,
    fogColor: new Color(0xcccccc),
    fogDensity: 0.01,
  },
  performance: {
    maxFPS: 60,
    enableLOD: true,
    shadowMapSize: 2048,
    antialias: true,
    enablePostProcessing: true,
  },
});

const Scene3DPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  
  // Store actions
  const setCurrentScene = useScene3DStore(state => state.setCurrentScene);
  const currentScene = useScene3DSelector.currentScene();
  const cameraMode = useScene3DSelector.cameraMode();
  const viewMode = useScene3DSelector.viewMode();
  const selectedPlant = useScene3DSelector.selectedPlant();
  const performance = useScene3DSelector.performance();
  const isAnimating = useScene3DSelector.isAnimating();
  const isExporting = useScene3DSelector.isExporting();
  
  // Initialize scene
  useEffect(() => {
    const initializeScene = async () => {
      setIsLoading(true);
      try {
        // Simulate loading time for 3D assets
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const mockScene = createMockScene3D();
        setCurrentScene(mockScene);
        
        toast.success('3D Garden Scene loaded successfully');
      } catch (error) {
        toast.error('Failed to load 3D scene');
        console.error('Error loading 3D scene:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    if (!currentScene) {
      initializeScene();
    } else {
      setIsLoading(false);
    }
  }, [currentScene, setCurrentScene]);
  
  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'h':
        case 'H':
          setShowControls(!showControls);
          break;
        case 'i':
        case 'I':
          setShowInfo(!showInfo);
          break;
        case 'Escape':
          setShowControls(false);
          setShowInfo(false);
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [showControls, showInfo]);
  
  // Handle WebXR support detection
  useEffect(() => {
    const checkWebXRSupport = () => {
      if ('xr' in navigator) {
        navigator.xr?.isSessionSupported('immersive-vr').then((supported) => {
          useScene3DStore.getState().setWebXRSupported(supported);
        });
      }
    };
    
    checkWebXRSupport();
  }, []);
  
  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <Loader className="h-12 w-12 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Loading 3D Garden Scene</h2>
          <p className="text-gray-400">Initializing 3D environment and assets...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full h-screen bg-gray-900 relative overflow-hidden">
      {/* Main 3D Scene */}
      <div className="w-full h-full">
        <Scene3D />
      </div>
      
      {/* Top Navigation Bar */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-black/50 backdrop-blur-sm border-b border-white/20">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="text-white hover:bg-white/20">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="text-white">
              <h1 className="text-lg font-semibold">3D Garden Visualization</h1>
              <p className="text-sm text-gray-300">Immersive 3D garden experience</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Camera Mode Indicator */}
            <Badge variant="secondary" className="bg-white/20 text-white">
              <Camera className="h-3 w-3 mr-1" />
              {cameraMode}
            </Badge>
            
            {/* View Mode Indicator */}
            <Badge variant="secondary" className="bg-white/20 text-white">
              <Box className="h-3 w-3 mr-1" />
              {viewMode}
            </Badge>
            
            {/* Animation Status */}
            {isAnimating && (
              <Badge variant="default" className="bg-green-500">
                <Loader className="h-3 w-3 mr-1 animate-spin" />
                Animating
              </Badge>
            )}
            
            {/* Export Status */}
            {isExporting && (
              <Badge variant="default" className="bg-blue-500">
                <Loader className="h-3 w-3 mr-1 animate-spin" />
                Exporting
              </Badge>
            )}
            
            {/* Performance Indicator */}
            <Badge variant="secondary" className="bg-white/20 text-white">
              {Math.round(performance.fps)} FPS
            </Badge>
            
            {/* Control Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowControls(!showControls)}
              className="text-white hover:bg-white/20"
            >
              {showControls ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
            
            {/* Info Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowInfo(!showInfo)}
              className="text-white hover:bg-white/20"
            >
              <Info className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Controls Panel */}
      {showControls && (
        <div className="absolute top-20 right-4 z-20">
          <Scene3DControls />
        </div>
      )}
      
      {/* Info Panel */}
      {showInfo && (
        <div className="absolute top-20 left-4 z-20 w-80">
          <Card className="bg-white/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                Scene Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Scene Details */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Scene Details</h3>
                <div className="text-xs space-y-1">
                  <div><strong>Name:</strong> {currentScene?.name}</div>
                  <div><strong>Plants:</strong> {currentScene?.plants.length || 0}</div>
                  <div><strong>Time:</strong> {currentScene?.lighting.timeOfDay.toFixed(1)}h</div>
                  <div><strong>Season:</strong> {currentScene?.lighting.season}</div>
                  <div><strong>Weather:</strong> {currentScene?.lighting.weather}</div>
                </div>
              </div>
              
              <Separator />
              
              {/* Performance Metrics */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Performance</h3>
                <div className="text-xs space-y-1">
                  <div><strong>FPS:</strong> {Math.round(performance.fps)}</div>
                  <div><strong>Draw Calls:</strong> {performance.drawCalls}</div>
                  <div><strong>Triangles:</strong> {performance.triangles}</div>
                  <div><strong>Memory:</strong> {Math.round(performance.memoryUsage / 1024)}KB</div>
                </div>
              </div>
              
              <Separator />
              
              {/* Selected Plant Info */}
              {selectedPlant && (
                <>
                  <div>
                    <h3 className="text-sm font-semibold mb-2">Selected Plant</h3>
                    <div className="text-xs space-y-1">
                      <div><strong>Name:</strong> {selectedPlant.name}</div>
                      <div><strong>Species:</strong> {selectedPlant.species}</div>
                      <div><strong>Health:</strong> {Math.round(selectedPlant.health * 100)}%</div>
                      <div><strong>Age:</strong> {selectedPlant.age}/{selectedPlant.maxAge} days</div>
                      <div><strong>Growth Stage:</strong> {selectedPlant.growthStage}</div>
                      <div><strong>Height:</strong> {selectedPlant.height}m</div>
                      <div><strong>Spread:</strong> {selectedPlant.spread}m</div>
                    </div>
                  </div>
                  <Separator />
                </>
              )}
              
              {/* Controls Help */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Controls</h3>
                <div className="text-xs space-y-1">
                  <div><strong>H:</strong> Toggle controls</div>
                  <div><strong>I:</strong> Toggle info</div>
                  <div><strong>ESC:</strong> Close panels</div>
                  <div><strong>Mouse:</strong> Orbit camera</div>
                  <div><strong>Scroll:</strong> Zoom</div>
                  <div><strong>Click:</strong> Select plants</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Bottom Status Bar */}
      <div className="absolute bottom-0 left-0 right-0 z-10 bg-black/50 backdrop-blur-sm border-t border-white/20">
        <div className="flex items-center justify-between p-2 text-white text-xs">
          <div className="flex items-center space-x-4">
            <span>Scene: {currentScene?.name}</span>
            <span>Plants: {currentScene?.plants.length || 0}</span>
            {selectedPlant && (
              <span>Selected: {selectedPlant.name}</span>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <span>FPS: {Math.round(performance.fps)}</span>
            <span>Draw Calls: {performance.drawCalls}</span>
            <span>Triangles: {performance.triangles}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scene3DPage; 