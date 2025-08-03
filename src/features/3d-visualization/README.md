# 3D Garden Visualization Module

A comprehensive, production-ready 3D visualization system for the Agrotique Garden Planner, built with Three.js, React Three Fiber, and TypeScript.

## Features

### 🎯 Core 3D Visualization
- **High-performance 3D rendering** with Three.js and React Three Fiber
- **Realistic plant models** with growth stage visualization
- **Dynamic lighting system** with time-of-day and seasonal changes
- **Weather effects** (clear, cloudy, rainy, overcast)
- **Interactive plant selection** and health indicators

### 🎮 Camera & Navigation
- **Multiple camera modes**: Top-down, Isometric, Free-look, Walkthrough
- **Smooth orbit controls** with damping and constraints
- **Seamless 2D/3D transitions**
- **Keyboard shortcuts** for quick navigation
- **Focus on selection** functionality

### 🌟 Advanced Features
- **Real-time performance monitoring** (FPS, draw calls, triangles)
- **Post-processing effects** (bloom, SSAO, chromatic aberration)
- **High-quality export** (images, videos, technical drawings)
- **Measurement tools** for distance, area, and volume
- **Annotation system** for 3D notes and labels

### 📱 WebXR Support
- **Augmented Reality (AR)** for mobile devices
- **Plant placement** in real-world environment
- **Interactive AR controls** and instructions
- **Device compatibility detection**

### 🎨 Visual Quality
- **Realistic materials** with PBR rendering
- **Dynamic shadows** and contact shadows
- **Sky system** with sun position calculation
- **Grid helpers** and visual guides
- **Health-based color variation**

## Technical Architecture

### File Structure
```
src/features/3d-visualization/
├── components/
│   ├── Scene3D.tsx              # Main 3D scene component
│   ├── Scene3DControls.tsx      # Control panel interface
│   └── WebXRViewer.tsx          # AR/VR viewer component
├── pages/
│   └── Scene3DPage.tsx          # Main 3D visualization page
├── store/
│   └── scene3DStore.ts          # Zustand state management
├── utils/
│   └── modelLoader.ts           # 3D model loading utilities
└── README.md                    # This documentation
```

### State Management
The module uses Zustand for state management with the following key features:

- **Scene Configuration**: 3D scene setup, plants, lighting, camera
- **Camera Controls**: Position, target, mode, navigation settings
- **Plant Management**: Selection, growth updates, health monitoring
- **Performance Metrics**: Real-time FPS, draw calls, memory usage
- **Export Controls**: Image/video export settings and progress
- **WebXR Support**: AR/VR session management

### Performance Optimizations

1. **Model Caching**: 3D models are cached to avoid repeated loading
2. **LOD (Level of Detail)**: Automatic detail reduction for distant objects
3. **Frustum Culling**: Only render visible objects
4. **Instanced Rendering**: Efficient rendering of multiple similar objects
5. **Texture Compression**: Optimized texture loading and memory usage
6. **WebWorker Support**: Heavy calculations offloaded to background threads

## Usage

### Basic 3D Scene
```tsx
import Scene3DPage from './features/3d-visualization/pages/Scene3DPage';

// Navigate to 3D view
<Link to="/3d/garden-id">View in 3D</Link>
```

### AR Experience
```tsx
import WebXRViewer from './features/3d-visualization/components/WebXRViewer';

// Navigate to AR view
<Link to="/ar/garden-id">View in AR</Link>
```

### Custom 3D Scene
```tsx
import { useScene3DStore } from './features/3d-visualization/store/scene3DStore';

const { setCurrentScene, updateLighting, setCameraMode } = useScene3DStore();

// Create custom scene
const customScene = {
  id: 'custom-garden',
  name: 'My Garden',
  plants: [...],
  lighting: {...},
  camera: {...},
  // ... other configuration
};

setCurrentScene(customScene);
```

## API Reference

### Scene3DStore Actions

#### Scene Management
- `setCurrentScene(scene: Scene3DConfig)`: Load a 3D scene
- `clearScene()`: Clear current scene
- `resetScene()`: Reset scene to default state

#### Camera Controls
- `setCameraMode(mode: CameraMode)`: Change camera mode
- `setViewMode(mode: ViewMode)`: Switch between 2D/3D
- `updateCameraPosition(position: Vector3)`: Update camera position
- `resetCamera()`: Reset camera to default position
- `focusOnSelection()`: Focus camera on selected plant

#### Plant Management
- `addPlant(plant: Plant3DModel)`: Add plant to scene
- `removePlant(plantId: string)`: Remove plant from scene
- `selectPlant(plant: Plant3DModel | null)`: Select/deselect plant
- `updatePlantGrowth(plantId: string, age: number)`: Update plant growth
- `updatePlantHealth(plantId: string, health: number)`: Update plant health

#### Lighting & Environment
- `updateLighting(lighting: Partial<LightingConfig>)`: Update lighting
- `setTimeOfDay(time: number)`: Set time of day (0-24 hours)
- `setSeason(season: string)`: Set season (spring/summer/autumn/winter)
- `setWeather(weather: string)`: Set weather conditions

#### Export & Tools
- `setExporting(isExporting: boolean)`: Control export state
- `setMeasuring(isMeasuring: boolean)`: Toggle measurement mode
- `addMeasurement(measurement: MeasurementTool)`: Add measurement
- `addAnnotation(annotation: Annotation3D)`: Add 3D annotation

### Types

#### Scene3DConfig
```typescript
interface Scene3DConfig {
  id: string;
  name: string;
  description: string;
  gardenId: string;
  plants: Plant3DModel[];
  lighting: LightingConfig;
  camera: CameraConfig;
  navigation: NavigationControls;
  ground: GroundConfig;
  environment: EnvironmentConfig;
  performance: PerformanceConfig;
}
```

#### Plant3DModel
```typescript
interface Plant3DModel {
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
  seasonalGrowth: SeasonalGrowth;
}
```

## Configuration

### Environment Variables
```env
# 3D Performance Settings
VITE_MAX_FPS=60
VITE_ENABLE_POST_PROCESSING=true
VITE_SHADOW_QUALITY=high
VITE_ANTIALIAS=true

# Model Loading
VITE_MODEL_CACHE_SIZE=50
VITE_TEXTURE_COMPRESSION=true

# WebXR Settings
VITE_WEBXR_ENABLED=true
VITE_AR_SESSION_TYPE=immersive-ar
```

### Performance Settings
```typescript
const performanceConfig = {
  maxFPS: 60,
  enableLOD: true,
  shadowMapSize: 2048,
  antialias: true,
  enablePostProcessing: true,
};
```

## Browser Support

### Required Features
- **WebGL 2.0** support
- **ES2020** JavaScript features
- **WebXR Device API** (for AR features)

### Recommended Hardware
- **GPU**: Dedicated graphics card with 2GB+ VRAM
- **RAM**: 8GB+ system memory
- **CPU**: Multi-core processor (4+ cores)
- **Display**: 1080p or higher resolution

### Mobile Support
- **iOS**: Safari 13+ with ARKit support
- **Android**: Chrome 79+ with ARCore support
- **WebXR**: Compatible AR/VR devices

## Troubleshooting

### Common Issues

#### Low Performance
1. Reduce shadow quality in settings
2. Disable post-processing effects
3. Lower model detail levels
4. Check GPU drivers are up to date

#### Model Loading Failures
1. Verify model file paths are correct
2. Check model format compatibility (GLB/GLTF)
3. Clear model cache and reload
4. Check network connectivity for remote models

#### WebXR Not Working
1. Ensure device supports WebXR
2. Check HTTPS requirement for AR features
3. Grant camera permissions
4. Test with supported browser

#### Export Failures
1. Check available memory
2. Reduce export resolution
3. Close other applications
4. Verify file system permissions

### Debug Mode
Enable debug mode to see performance metrics:
```typescript
// In development
localStorage.setItem('debug-3d', 'true');
```

## Development

### Setup
```bash
# Install dependencies
npm install three @react-three/fiber @react-three/drei

# Start development server
npm run dev

# Access 3D visualization
# Navigate to /3d/garden-id
```

### Testing
```bash
# Run unit tests
npm test

# Run performance tests
npm run test:performance

# Run WebXR tests
npm run test:webxr
```

### Building
```bash
# Build for production
npm run build

# Optimize 3D assets
npm run optimize:models

# Generate model thumbnails
npm run generate:thumbnails
```

## Contributing

### Adding New Plant Types
1. Create 3D model in GLB format
2. Add model to `/public/models/` directory
3. Update `modelLoader.ts` with new model path
4. Add plant type to `Plant3DModel` interface
5. Test with different growth stages

### Custom Shaders
1. Create shader files in `/shaders/` directory
2. Implement in `Scene3D.tsx` component
3. Add shader parameters to store
4. Test performance impact

### Performance Optimization
1. Profile with browser dev tools
2. Implement LOD for complex models
3. Optimize texture sizes
4. Use instanced rendering for repeated objects

## License

This module is part of the Agrotique Garden Planner project and follows the same license terms.

## Support

For technical support or feature requests:
- Create an issue in the project repository
- Check the troubleshooting guide above
- Review browser compatibility requirements
- Test with different hardware configurations 