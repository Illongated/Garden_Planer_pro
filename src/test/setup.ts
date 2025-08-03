// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock WebGL
const getParameter = vi.fn((param) => {
  switch (param) {
    case 0x1F00: return 'Mock WebGL Vendor'
    case 0x1F01: return 'Mock WebGL Renderer'
    case 0x1F02: return 'Mock WebGL Version'
    default: return null
  }
})

const getExtension = vi.fn(() => null)
const getSupportedExtensions = vi.fn(() => [])

HTMLCanvasElement.prototype.getContext = vi.fn((contextId) => {
  if (contextId === 'webgl' || contextId === 'webgl2') {
    return {
      getParameter,
      getExtension,
      getSupportedExtensions,
      createBuffer: vi.fn(),
      bindBuffer: vi.fn(),
      bufferData: vi.fn(),
      createShader: vi.fn(),
      shaderSource: vi.fn(),
      compileShader: vi.fn(),
      createProgram: vi.fn(),
      attachShader: vi.fn(),
      linkProgram: vi.fn(),
      useProgram: vi.fn(),
      getAttribLocation: vi.fn(),
      enableVertexAttribArray: vi.fn(),
      vertexAttribPointer: vi.fn(),
      drawArrays: vi.fn(),
      clearColor: vi.fn(),
      clear: vi.fn(),
      viewport: vi.fn(),
    }
  }
  return null
})

// Mock Three.js
vi.mock('three', () => ({
  Scene: vi.fn(),
  PerspectiveCamera: vi.fn(),
  WebGLRenderer: vi.fn(() => ({
    setSize: vi.fn(),
    render: vi.fn(),
    dispose: vi.fn(),
  })),
  BoxGeometry: vi.fn(),
  MeshBasicMaterial: vi.fn(),
  Mesh: vi.fn(),
  Vector3: vi.fn(),
  Euler: vi.fn(),
  Color: vi.fn(),
}))

// Mock React Three Fiber
vi.mock('@react-three/fiber', () => ({
  Canvas: vi.fn(({ children }) => children),
  useFrame: vi.fn(),
  useThree: vi.fn(() => ({
    camera: {},
    scene: {},
    gl: {},
  })),
}))

vi.mock('@react-three/drei', () => ({
  OrbitControls: vi.fn(),
  Environment: vi.fn(),
  Sky: vi.fn(),
  Stars: vi.fn(),
  useGLTF: vi.fn(),
  Text: vi.fn(),
  Html: vi.fn(),
  Cloud: vi.fn(),
  Sparkles: vi.fn(),
  ContactShadows: vi.fn(),
  Grid: vi.fn(),
  ARButton: vi.fn(),
  Interactive: vi.fn(),
  useXR: vi.fn(() => ({ isPresenting: false })),
  useHitTest: vi.fn(),
  useController: vi.fn(),
  Float: vi.fn(),
}))

vi.mock('@react-three/postprocessing', () => ({
  EffectComposer: vi.fn(),
  Bloom: vi.fn(),
  ChromaticAberration: vi.fn(),
  SSAO: vi.fn(),
  ToneMapping: vi.fn(),
}))

// Mock Zustand
vi.mock('zustand', () => ({
  create: vi.fn((fn) => fn),
  subscribeWithSelector: vi.fn((fn) => fn),
}))

// Mock Axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}))

// Mock React Router
vi.mock('react-router-dom', () => ({
  createBrowserRouter: vi.fn(),
  RouterProvider: vi.fn(),
  Link: vi.fn(({ children, ...props }) => <a {...props}>{children}</a>),
  useNavigate: vi.fn(() => vi.fn()),
  useParams: vi.fn(() => ({})),
  useLocation: vi.fn(() => ({ pathname: '/' })),
}))

// Mock Sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock Lucide React
vi.mock('lucide-react', () => ({
  Home: vi.fn(() => <div>Home Icon</div>),
  Settings: vi.fn(() => <div>Settings Icon</div>),
  User: vi.fn(() => <div>User Icon</div>),
  LogOut: vi.fn(() => <div>LogOut Icon</div>),
  Plus: vi.fn(() => <div>Plus Icon</div>),
  Search: vi.fn(() => <div>Search Icon</div>),
  Filter: vi.fn(() => <div>Filter Icon</div>),
  Download: vi.fn(() => <div>Download Icon</div>),
  FileText: vi.fn(() => <div>FileText Icon</div>),
  Image: vi.fn(() => <div>Image Icon</div>),
  Printer: vi.fn(() => <div>Printer Icon</div>),
  Camera: vi.fn(() => <div>Camera Icon</div>),
  Sun: vi.fn(() => <div>Sun Icon</div>),
  Settings: vi.fn(() => <div>Settings Icon</div>),
  Ruler: vi.fn(() => <div>Ruler Icon</div>),
  Play: vi.fn(() => <div>Play Icon</div>),
  Pause: vi.fn(() => <div>Pause Icon</div>),
  Maximize: vi.fn(() => <div>Maximize Icon</div>),
  Minimize: vi.fn(() => <div>Minimize Icon</div>),
  Box: vi.fn(() => <div>Box Icon</div>),
  Grid3X3: vi.fn(() => <div>Grid3X3 Icon</div>),
  Walk: vi.fn(() => <div>Walk Icon</div>),
  Cloud: vi.fn(() => <div>Cloud Icon</div>),
  CloudRain: vi.fn(() => <div>CloudRain Icon</div>),
  Image: vi.fn(() => <div>Image Icon</div>),
  Video: vi.fn(() => <div>Video Icon</div>),
  Trash: vi.fn(() => <div>Trash Icon</div>),
  Target: vi.fn(() => <div>Target Icon</div>),
  RotateCcw: vi.fn(() => <div>RotateCcw Icon</div>),
  ArrowLeft: vi.fn(() => <div>ArrowLeft Icon</div>),
  Info: vi.fn(() => <div>Info Icon</div>),
  Share: vi.fn(() => <div>Share Icon</div>),
  Bookmark: vi.fn(() => <div>Bookmark Icon</div>),
  Eye: vi.fn(() => <div>Eye Icon</div>),
  EyeOff: vi.fn(() => <div>EyeOff Icon</div>),
  Loader: vi.fn(() => <div>Loader Icon</div>),
}))

// Mock React Hook Form
vi.mock('react-hook-form', () => ({
  useForm: vi.fn(() => ({
    register: vi.fn(),
    handleSubmit: vi.fn((fn) => fn),
    formState: { errors: {} },
    watch: vi.fn(),
    setValue: vi.fn(),
    reset: vi.fn(),
  })),
}))

// Mock Zod
vi.mock('zod', () => ({
  z: {
    string: vi.fn(() => ({ min: vi.fn(), email: vi.fn() })),
    object: vi.fn(() => ({ refine: vi.fn() })),
    array: vi.fn(() => ({ min: vi.fn() })),
    number: vi.fn(() => ({ min: vi.fn(), max: vi.fn() })),
    boolean: vi.fn(),
    date: vi.fn(),
    enum: vi.fn(),
  },
}))

// Mock class-variance-authority
vi.mock('class-variance-authority', () => ({
  cva: vi.fn(() => vi.fn()),
}))

// Mock clsx and tailwind-merge
vi.mock('clsx', () => vi.fn())
vi.mock('tailwind-merge', () => ({
  twMerge: vi.fn(),
}))

// Mock React
vi.mock('react', () => ({
  ...vi.importActual('react'),
  useRef: vi.fn(() => ({ current: null })),
  useEffect: vi.fn(),
  useState: vi.fn((initial) => [initial, vi.fn()]),
  useCallback: vi.fn((fn) => fn),
  useMemo: vi.fn((fn) => fn()),
  useContext: vi.fn(),
  createContext: vi.fn(() => ({ Provider: vi.fn(), Consumer: vi.fn() })),
}))

// Mock React DOM
vi.mock('react-dom', () => ({
  ...vi.importActual('react-dom'),
  createPortal: vi.fn((children) => children),
}))

// Setup global test utilities
global.testUtils = {
  mockApiResponse: (data: any) => Promise.resolve({ data }),
  mockApiError: (error: any) => Promise.reject(error),
  createMockUser: () => ({
    id: 'test-user-id',
    email: 'test@example.com',
    full_name: 'Test User',
    is_active: true,
    is_superuser: false,
  }),
  createMockGarden: () => ({
    id: 'test-garden-id',
    name: 'Test Garden',
    description: 'A test garden',
    width: 10.0,
    height: 8.0,
    user_id: 'test-user-id',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }),
  createMockPlant: () => ({
    id: 'test-plant-id',
    name: 'Test Plant',
    species: 'Test Species',
    position_x: 1.0,
    position_y: 1.0,
    garden_id: 'test-garden-id',
    plant_catalog_id: 'test-catalog-id',
    planting_date: '2024-03-15',
    growth_stage: 'seedling',
    health_status: 'healthy',
    notes: 'Test plant notes',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }),
  createMockPlantCatalog: () => ({
    id: 'test-catalog-id',
    name: 'Tomato',
    species: 'Solanum lycopersicum',
    family: 'Solanaceae',
    growth_duration_days: 80,
    spacing_cm: 60,
    water_needs: 'medium',
    sunlight_needs: 'full',
    soil_type: 'loamy',
    ph_range: '6.0-6.8',
    max_height_cm: 200,
    max_spread_cm: 60,
    root_depth_cm: 30,
    companion_plants: ['Basil', 'Marigold'],
    antagonist_plants: ['Potato', 'Corn'],
    planting_season: 'spring',
    harvest_season: 'summer',
    yield_per_plant_kg: 2.5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  }),
}
