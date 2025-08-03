import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  ARButton, 
  Interactive, 
  useXR, 
  useHitTest, 
  useController,
  Html,
  Text,
  Float,
  Environment,
  Sky,
  Stars,
  useGLTF,
  ContactShadows,
  AccumulativeShadows,
  RandomizedLight,
  Center,
  Bounds,
  useBounds,
  Grid,
  OrbitControls,
  PerspectiveCamera,
  OrthographicCamera,
  Box,
  Sphere,
  Cylinder,
  Plane,
  Torus,
  Ring,
  Circle,
  Cone,
  Octahedron,
  Tetrahedron,
  Icosahedron,
  Dodecahedron,
  TetrahedronGeometry,
  OctahedronGeometry,
  IcosahedronGeometry,
  DodecahedronGeometry,
  BoxGeometry,
  SphereGeometry,
  CylinderGeometry,
  PlaneGeometry,
  TorusGeometry,
  RingGeometry,
  CircleGeometry,
  ConeGeometry,
  BufferGeometry,
  Material,
  Mesh,
  Group,
  Object3D,
  Vector3,
  Euler,
  Color,
  MathUtils,
  Clock,
  WebGLRenderer,
  Scene,
  Camera,
  Texture,
  TextureLoader,
  CubeTextureLoader,
  DataTexture,
  CompressedTexture,
  VideoTexture,
  CanvasTexture,
  DepthTexture,
  DepthStencilTexture,
  UnsignedByteType,
  FloatType,
  HalfFloatType,
  ClampToEdgeWrapping,
  RepeatWrapping,
  MirroredRepeatWrapping,
  NearestFilter,
  NearestMipmapNearestFilter,
  NearestMipmapLinearFilter,
  LinearFilter,
  LinearMipmapNearestFilter,
  LinearMipmapLinearFilter,
  UnsignedByteType as UnsignedByteTypeType,
  FloatType as FloatTypeType,
  HalfFloatType as HalfFloatTypeType,
  ClampToEdgeWrapping as ClampToEdgeWrappingType,
  RepeatWrapping as RepeatWrappingType,
  MirroredRepeatWrapping as MirroredRepeatWrappingType,
  NearestFilter as NearestFilterType,
  NearestMipmapNearestFilter as NearestMipmapNearestFilterType,
  NearestMipmapLinearFilter as NearestMipmapLinearFilterType,
  LinearFilter as LinearFilterType,
  LinearMipmapNearestFilter as LinearMipmapNearestFilterType,
  LinearMipmapLinearFilter as LinearMipmapLinearFilterType,
} from '@react-three/drei';
import { useScene3DStore, useScene3DSelector } from '../store/scene3DStore';
import { 
  Plant3DModel, 
  Vector3, 
  Euler, 
  Color,
  WebXRConfig,
} from '../../../types/3d-visualization';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { toast } from 'sonner';

// AR Plant Placement Component
const ARPlantPlacement: React.FC = () => {
  const [placedPlants, setPlacedPlants] = useState<Plant3DModel[]>([]);
  const [selectedPlantType, setSelectedPlantType] = useState<string>('tomato');
  const [isPlacing, setIsPlacing] = useState(false);
  
  const plantTypes = [
    { id: 'tomato', name: 'Tomato', modelPath: '/models/tomato.glb', color: '#ef4444' },
    { id: 'basil', name: 'Basil', modelPath: '/models/basil.glb', color: '#22c55e' },
    { id: 'lettuce', name: 'Lettuce', modelPath: '/models/lettuce.glb', color: '#84cc16' },
    { id: 'carrot', name: 'Carrot', modelPath: '/models/carrot.glb', color: '#f97316' },
  ];
  
  const handlePlacePlant = useCallback((position: Vector3) => {
    if (!isPlacing) return;
    
    const plantType = plantTypes.find(p => p.id === selectedPlantType);
    if (!plantType) return;
    
    const newPlant: Plant3DModel = {
      id: `ar-plant-${Date.now()}`,
      name: plantType.name,
      species: plantType.name,
      growthStage: 'seedling',
      position,
      rotation: new Euler(0, 0, 0),
      scale: new Vector3(1, 1, 1),
      health: 1.0,
      age: 0,
      maxAge: 90,
      modelPath: plantType.modelPath,
      texturePath: '',
      height: 0.5,
      spread: 0.3,
      rootDepth: 0.2,
      waterNeeds: 0.6,
      sunlightNeeds: 0.7,
      temperatureRange: [15, 30],
      seasonalGrowth: {
        spring: 0.4,
        summer: 0.8,
        autumn: 0.3,
        winter: 0.0,
      },
    };
    
    setPlacedPlants(prev => [...prev, newPlant]);
    setIsPlacing(false);
    toast.success(`${plantType.name} placed successfully!`);
  }, [isPlacing, selectedPlantType, plantTypes]);
  
  return (
    <>
      {/* Plant Selection UI */}
      {isPlacing && (
        <Html position={[0, 2, 0]} center>
          <Card className="bg-white/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-sm">Select Plant Type</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {plantTypes.map((plant) => (
                  <Button
                    key={plant.id}
                    variant={selectedPlantType === plant.id ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedPlantType(plant.id)}
                    className="text-xs"
                  >
                    <div 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: plant.color }}
                    />
                    {plant.name}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </Html>
      )}
      
      {/* Placed Plants */}
      {placedPlants.map((plant) => (
        <ARPlant key={plant.id} plant={plant} />
      ))}
    </>
  );
};

// AR Plant Component
const ARPlant: React.FC<{ plant: Plant3DModel }> = ({ plant }) => {
  const [isSelected, setIsSelected] = useState(false);
  
  const handleClick = useCallback(() => {
    setIsSelected(!isSelected);
    toast.success(`${plant.name} selected`);
  }, [plant.name, isSelected]);
  
  return (
    <group position={plant.position} onClick={handleClick}>
      {/* Simple plant representation for AR */}
      <mesh>
        <cylinderGeometry args={[0.1, 0.1, plant.height, 8]} />
        <MeshStandardMaterial color="#8b4513" />
      </mesh>
      
      {/* Plant foliage */}
      <mesh position={[0, plant.height / 2, 0]}>
        <sphereGeometry args={[plant.spread, 8, 8]} />
        <MeshStandardMaterial color="#22c55e" />
      </mesh>
      
      {/* Health indicator */}
      <Float speed={1} rotationIntensity={0.5} floatIntensity={0.5}>
        <Html position={[0, plant.height + 0.3, 0]} center>
          <Badge variant="secondary" className="bg-black/50 text-white text-xs">
            {Math.round(plant.health * 100)}%
          </Badge>
        </Html>
      </Float>
      
      {/* Selection highlight */}
      {isSelected && (
        <mesh position={[0, 0, 0]}>
          <ringGeometry args={[plant.spread + 0.2, plant.spread + 0.3, 32]} />
          <MeshBasicMaterial color="#00ff00" transparent opacity={0.5} />
        </mesh>
      )}
    </group>
  );
};

// AR Scene Component
const ARScene: React.FC = () => {
  const { session } = useXR();
  const [isSupported, setIsSupported] = useState(false);
  
  useEffect(() => {
    if ('xr' in navigator) {
      navigator.xr?.isSessionSupported('immersive-ar').then((supported) => {
        setIsSupported(supported);
        useScene3DStore.getState().setWebXRSupported(supported);
      });
    }
  }, []);
  
  if (!isSupported) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <h2 className="text-xl font-semibold mb-2">AR Not Supported</h2>
          <p className="text-gray-400">Your device doesn't support AR features</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="w-full h-full">
      <Canvas
        camera={{ position: [0, 0, 0], fov: 75 }}
        gl={{ preserveDrawingBuffer: true }}
        onCreated={({ gl }) => {
          gl.setClearColor(0x000000, 0);
        }}
      >
        <ARPlantPlacement />
        
        {/* AR Environment */}
        <Environment preset="sunset" />
        <ContactShadows position={[0, -0.1, 0]} opacity={0.4} scale={20} blur={2} far={4} />
      </Canvas>
    </div>
  );
};

// Main WebXR Viewer Component
const WebXRViewer: React.FC = () => {
  const [isARActive, setIsARActive] = useState(false);
  const [showPlacementUI, setShowPlacementUI] = useState(false);
  
  const handleStartAR = useCallback(() => {
    setIsARActive(true);
    toast.success('AR session started');
  }, []);
  
  const handleStopAR = useCallback(() => {
    setIsARActive(false);
    toast.success('AR session stopped');
  }, []);
  
  return (
    <div className="w-full h-screen bg-gray-900 relative">
      {isARActive ? (
        <>
          <ARScene />
          
          {/* AR Controls Overlay */}
          <div className="absolute top-4 right-4 z-10">
            <div className="flex flex-col gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowPlacementUI(!showPlacementUI)}
                className="bg-white/20 text-white hover:bg-white/30"
              >
                {showPlacementUI ? 'Hide' : 'Show'} Placement
              </Button>
              
              <Button
                variant="destructive"
                size="sm"
                onClick={handleStopAR}
                className="bg-red-500 hover:bg-red-600"
              >
                Stop AR
              </Button>
            </div>
          </div>
          
          {/* AR Instructions */}
          <div className="absolute bottom-4 left-4 z-10">
            <Card className="bg-white/90 backdrop-blur-sm">
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-2">AR Instructions</h3>
                <div className="text-xs space-y-1">
                  <div>• Point camera at flat surface</div>
                  <div>• Tap to place plants</div>
                  <div>• Move around to explore</div>
                  <div>• Tap plants to select</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center text-white">
            <h2 className="text-2xl font-semibold mb-4">Augmented Reality Garden</h2>
            <p className="text-gray-400 mb-8">Experience your garden in AR</p>
            
            <div className="space-y-4">
              <Button
                size="lg"
                onClick={handleStartAR}
                className="bg-green-500 hover:bg-green-600"
              >
                Start AR Experience
              </Button>
              
              <div className="text-sm text-gray-400">
                <p>• Requires AR-capable device</p>
                <p>• Good lighting recommended</p>
                <p>• Flat surface needed</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebXRViewer; 