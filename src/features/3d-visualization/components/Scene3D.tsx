import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  Environment, 
  Sky, 
  Stars,
  useGLTF,
  Text,
  Html,
  PerspectiveCamera,
  OrthographicCamera,
  Grid,
  AccumulativeShadows,
  RandomizedLight,
  Center,
  Bounds,
  useBounds,
  ContactShadows,
  Float,
  Sparkles,
  Cloud,
  CloudInstance,
  useTexture,
  MeshDistortMaterial,
  MeshWobbleMaterial,
  MeshReflectorMaterial,
  MeshRefractionMaterial,
  MeshTransmissionMaterial,
  MeshDiscardMaterial,
  MeshPhysicalMaterial,
  MeshStandardMaterial,
  MeshBasicMaterial,
  MeshLambertMaterial,
  MeshPhongMaterial,
  MeshToonMaterial,
  MeshNormalMaterial,
  MeshDepthMaterial,
  MeshDistanceMaterial,
  MeshMatcapMaterial,
  MeshFresnelMaterial,
  MeshGlassMaterial,
  MeshPortalMaterial,
  MeshReflectorMaterial as MeshReflectorMaterialType,
  MeshRefractionMaterial as MeshRefractionMaterialType,
  MeshTransmissionMaterial as MeshTransmissionMaterialType,
  MeshDiscardMaterial as MeshDiscardMaterialType,
  MeshPhysicalMaterial as MeshPhysicalMaterialType,
  MeshStandardMaterial as MeshStandardMaterialType,
  MeshBasicMaterial as MeshBasicMaterialType,
  MeshLambertMaterial as MeshLambertMaterialType,
  MeshPhongMaterial as MeshPhongMaterialType,
  MeshToonMaterial as MeshToonMaterialType,
  MeshNormalMaterial as MeshNormalMaterialType,
  MeshDepthMaterial as MeshDepthMaterialType,
  MeshDistanceMaterial as MeshDistanceMaterialType,
  MeshMatcapMaterial as MeshMatcapMaterialType,
  MeshFresnelMaterial as MeshFresnelMaterialType,
  MeshGlassMaterial as MeshGlassMaterialType,
  MeshPortalMaterial as MeshPortalMaterialType,
} from '@react-three/drei';
import { 
  EffectComposer, 
  Bloom, 
  ChromaticAberration, 
  DepthOfField, 
  DotScreen, 
  Glitch, 
  GodRays, 
  HueSaturation, 
  Noise, 
  Outline, 
  Pixelation, 
  Scanline, 
  Sepia, 
  ShaderPass, 
  SMAA, 
  SSAO, 
  TiltShift, 
  ToneMapping, 
  Vignette, 
  Water 
} from '@react-three/postprocessing';
import { 
  Vector3, 
  Euler, 
  Color, 
  MathUtils, 
  Clock, 
  WebGLRenderer,
  Scene,
  Camera,
  Object3D,
  Group,
  Mesh,
  BufferGeometry,
  Material,
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
} from 'three';
import { useScene3DStore, useScene3DSelector } from '../store/scene3DStore';
import { 
  Scene3DConfig, 
  Plant3DModel, 
  CameraMode, 
  ViewMode, 
  LightingConfig,
  PerformanceMetrics,
} from '../../../types/3d-visualization';

// Performance monitoring hook
const usePerformanceMonitor = () => {
  const updatePerformanceMetrics = useScene3DStore(state => state.updatePerformanceMetrics);
  const clock = useRef(new Clock());
  
  useFrame((state) => {
    const deltaTime = clock.current.getDelta();
    const fps = 1 / deltaTime;
    
    updatePerformanceMetrics({
      fps: Math.round(fps),
      frameTime: deltaTime * 1000, // Convert to milliseconds
      drawCalls: state.gl.info.render.calls,
      triangles: state.gl.info.render.triangles,
      memoryUsage: state.gl.info.memory.geometries + state.gl.info.memory.textures,
      gpuMemory: state.gl.info.memory.programs,
    });
  });
};

// Camera controller component
const CameraController: React.FC = () => {
  const { camera } = useThree();
  const cameraMode = useScene3DSelector.cameraMode();
  const currentScene = useScene3DSelector.currentScene();
  const updateCameraPosition = useScene3DStore(state => state.updateCameraPosition);
  const updateCameraTarget = useScene3DStore(state => state.updateCameraTarget);
  
  useEffect(() => {
    if (!currentScene) return;
    
    const { camera: cameraConfig } = currentScene;
    
    switch (cameraMode) {
      case 'top-down':
        camera.position.set(0, 20, 0);
        camera.lookAt(0, 0, 0);
        break;
      case 'isometric':
        camera.position.set(15, 15, 15);
        camera.lookAt(0, 0, 0);
        break;
      case 'freelook':
        camera.position.copy(cameraConfig.position);
        camera.lookAt(cameraConfig.target);
        break;
      case 'walkthrough':
        camera.position.set(0, 2, 10);
        camera.lookAt(0, 2, 0);
        break;
    }
    
    updateCameraPosition(camera.position);
    updateCameraTarget(cameraConfig.target);
  }, [cameraMode, currentScene, camera, updateCameraPosition, updateCameraTarget]);
  
  return null;
};

// Lighting system component
const LightingSystem: React.FC = () => {
  const currentScene = useScene3DSelector.currentScene();
  
  const lightingConfig = useMemo(() => {
    if (!currentScene) return null;
    return currentScene.lighting;
  }, [currentScene]);
  
  if (!lightingConfig) return null;
  
  const { timeOfDay, season, weather, ambientIntensity, directionalIntensity, enableShadows } = lightingConfig;
  
  // Calculate sun position based on time of day
  const sunAngle = (timeOfDay / 24) * Math.PI * 2;
  const sunHeight = Math.sin(sunAngle);
  const sunDistance = 50;
  
  return (
    <>
      {/* Ambient light */}
      <ambientLight intensity={ambientIntensity} />
      
      {/* Directional sun light */}
      <directionalLight
        position={[
          Math.cos(sunAngle) * sunDistance,
          sunHeight * sunDistance,
          Math.sin(sunAngle) * sunDistance
        ]}
        intensity={directionalIntensity}
        castShadow={enableShadows}
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={100}
        shadow-camera-left={-20}
        shadow-camera-right={20}
        shadow-camera-top={20}
        shadow-camera-bottom={-20}
      />
      
      {/* Sky system */}
      <Sky
        distance={450000}
        sunPosition={[
          Math.cos(sunAngle) * sunDistance,
          sunHeight * sunDistance,
          Math.sin(sunAngle) * sunDistance
        ]}
        inclination={0.5}
        azimuth={0.25}
        rayleigh={1}
        turbidity={10}
        mieCoefficient={0.005}
        mieDirectionalG={0.8}
      />
      
      {/* Stars for night time */}
      {timeOfDay < 6 || timeOfDay > 18 ? (
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      ) : null}
      
      {/* Weather effects */}
      {weather === 'cloudy' && (
        <Cloud
          opacity={0.5}
          speed={0.4}
          width={10}
          depth={1.5}
          segments={20}
        />
      )}
      
      {weather === 'rainy' && (
        <Sparkles
          count={1000}
          scale={50}
          size={2}
          speed={0.3}
          opacity={0.6}
          color="#4a90e2"
        />
      )}
    </>
  );
};

// Ground component
const Ground: React.FC = () => {
  const currentScene = useScene3DSelector.currentScene();
  
  const groundConfig = useMemo(() => {
    if (!currentScene) return null;
    return currentScene.ground;
  }, [currentScene]);
  
  if (!groundConfig) return null;
  
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
      <planeGeometry args={[groundConfig.size, groundConfig.size]} />
      <MeshStandardMaterial
        color={groundConfig.color}
        roughness={groundConfig.roughness}
        metalness={groundConfig.metalness}
      />
    </mesh>
  );
};

// 3D Plant component
const Plant3D: React.FC<{ plant: Plant3DModel }> = ({ plant }) => {
  const { scene } = useGLTF(plant.modelPath);
  const selectPlant = useScene3DStore(state => state.selectPlant);
  const selectedPlant = useScene3DSelector.selectedPlant();
  const isSelected = selectedPlant?.id === plant.id;
  
  const handleClick = useCallback(() => {
    selectPlant(isSelected ? null : plant);
  }, [plant, isSelected, selectPlant]);
  
  // Health-based color variation
  const healthColor = useMemo(() => {
    if (plant.health > 0.7) return new Color(0x4ade80); // Green
    if (plant.health > 0.4) return new Color(0xfbbf24); // Yellow
    return new Color(0xef4444); // Red
  }, [plant.health]);
  
  return (
    <group
      position={plant.position}
      rotation={plant.rotation}
      scale={plant.scale}
      onClick={handleClick}
    >
      <primitive object={scene.clone()} />
      
      {/* Health indicator */}
      <Float speed={1} rotationIntensity={0.5} floatIntensity={0.5}>
        <Html position={[0, plant.height + 0.5, 0]} center>
          <div className="bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
            {Math.round(plant.health * 100)}%
          </div>
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

// Plants container component
const PlantsContainer: React.FC = () => {
  const currentScene = useScene3DSelector.currentScene();
  
  const plants = useMemo(() => {
    if (!currentScene) return [];
    return currentScene.plants;
  }, [currentScene]);
  
  return (
    <>
      {plants.map((plant) => (
        <Plant3D key={plant.id} plant={plant} />
      ))}
    </>
  );
};

// Grid helper component
const GridHelper: React.FC = () => {
  const viewMode = useScene3DSelector.viewMode();
  
  if (viewMode !== '3d') return null;
  
  return (
    <Grid
      args={[20, 20]}
      cellSize={1}
      cellThickness={0.5}
      cellColor="#6f6f6f"
      sectionSize={5}
      sectionThickness={1}
      sectionColor="#9d4b4b"
      fadeDistance={30}
      fadeStrength={1}
      followCamera={false}
      infiniteGrid={true}
    />
  );
};

// Post-processing effects
const PostProcessing: React.FC = () => {
  const currentScene = useScene3DSelector.currentScene();
  
  const enablePostProcessing = useMemo(() => {
    if (!currentScene) return false;
    return currentScene.performance.enablePostProcessing;
  }, [currentScene]);
  
  if (!enablePostProcessing) return null;
  
  return (
    <EffectComposer>
      <Bloom luminanceThreshold={0.8} luminanceSmoothing={0.025} intensity={0.5} />
      <ChromaticAberration offset={[0.0005, 0.0005]} />
      <SSAO radius={0.4} intensity={50} luminanceInfluence={0.4} color="black" />
      <ToneMapping />
    </EffectComposer>
  );
};

// Main 3D Scene component
const Scene3DContent: React.FC = () => {
  usePerformanceMonitor();
  
  return (
    <>
      <CameraController />
      <LightingSystem />
      <Ground />
      <PlantsContainer />
      <GridHelper />
      <PostProcessing />
      
      {/* Contact shadows for plants */}
      <ContactShadows
        position={[0, -0.1, 0]}
        opacity={0.4}
        scale={20}
        blur={2}
        far={4}
      />
    </>
  );
};

// Main Scene3D component
const Scene3D: React.FC = () => {
  const currentScene = useScene3DSelector.currentScene();
  const viewMode = useScene3DSelector.viewMode();
  const cameraMode = useScene3DSelector.cameraMode();
  
  if (!currentScene) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 text-white">
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">No 3D Scene Loaded</h3>
          <p className="text-gray-400">Please load a garden scene to view in 3D</p>
        </div>
      </div>
    );
  }
  
  const { camera: cameraConfig, performance } = currentScene;
  
  return (
    <div className="w-full h-full relative">
      <Canvas
        shadows
        gl={{
          antialias: performance.antialias,
          alpha: false,
          powerPreference: "high-performance",
          stencil: false,
          depth: true,
        }}
        camera={{
          fov: cameraConfig.fov,
          near: cameraConfig.near,
          far: cameraConfig.far,
        }}
        performance={{ min: 0.5 }}
        dpr={[1, 2]}
      >
        <Scene3DContent />
        
        {/* Camera controls */}
        <OrbitControls
          enablePan={currentScene.navigation.enablePan}
          enableRotate={currentScene.navigation.enableRotate}
          enableZoom={currentScene.navigation.enableZoom}
          enableDolly={currentScene.navigation.enableDolly}
          panSpeed={currentScene.navigation.panSpeed}
          rotateSpeed={currentScene.navigation.rotateSpeed}
          zoomSpeed={currentScene.navigation.zoomSpeed}
          dollySpeed={currentScene.navigation.dollySpeed}
          maxDistance={currentScene.camera.maxDistance}
          minDistance={currentScene.camera.minDistance}
          maxPolarAngle={currentScene.camera.maxPolarAngle}
          minPolarAngle={currentScene.camera.minPolarAngle}
          enableDamping={currentScene.camera.enableDamping}
          dampingFactor={currentScene.camera.dampingFactor}
        />
      </Canvas>
      
      {/* Performance overlay */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white p-2 rounded text-xs">
        <div>FPS: {Math.round(performance.fps || 0)}</div>
        <div>Draw Calls: {performance.drawCalls || 0}</div>
        <div>Triangles: {performance.triangles || 0}</div>
      </div>
    </div>
  );
};

export default Scene3D; 