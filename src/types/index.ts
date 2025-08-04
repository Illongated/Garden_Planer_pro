// User types - synchronized with backend schemas
export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string | null;
}

export interface UserUpdate {
  email?: string | null;
  full_name?: string | null;
  password?: string | null;
}

// Authentication credentials
export interface LoginCredentials {
  email: string;
  password?: string;
}

export interface SignUpCredentials extends LoginCredentials {
  full_name: string;
}

// Garden types - synchronized with backend schemas
export interface Garden {
  id: string;
  name: string;
  description?: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface GardenCreate {
  name: string;
  description?: string | null;
}

export interface GardenUpdate {
  name?: string;
  description?: string | null;
}

// Plant types - synchronized with backend schemas
export interface Plant {
  id: string;
  name: string;
  species: string;
  variety?: string | null;
  planting_date?: string | null;
  harvest_date?: string | null;
  notes?: string | null;
  garden_id: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface PlantCreate {
  name: string;
  species: string;
  variety?: string | null;
  planting_date?: string | null;
  harvest_date?: string | null;
  notes?: string | null;
  garden_id: string;
}

export interface PlantUpdate {
  name?: string;
  species?: string;
  variety?: string | null;
  planting_date?: string | null;
  harvest_date?: string | null;
  notes?: string | null;
}

// Plant Catalog Types
export interface PlantCatalog {
  id: number;
  name: string;
  variety: string;
  plant_type: string;
  image: string;
  description: string;
  sun: string;
  water: string;
  spacing: string;
  planting_season: string[];
  harvest_season: string[];
  compatibility: string[];
  tips: string;
}

export interface PaginatedPlantCatalogResponse {
  total: number;
  page: number;
  page_size: number;
  items: PlantCatalog[];
}

export interface PlantCatalogSearchFilters {
  q?: string;
  plant_type?: string;
  season?: string;
  sun?: string;
}

export type ViewMode = 'grid' | 'list';

export interface DroppedPlant {
    id: string;
    plant: PlantCatalog;
    position: { x: number; y: number };
}

// Authentication tokens - synchronized with backend schemas
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenData {
  sub?: string | null;
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

// Error response
export interface ApiError {
  detail: string;
  errors?: Array<{
    loc: string;
    msg: string;
  }>;
}
