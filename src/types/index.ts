// User type
export interface User {
  id: string;
  name: string;
  email: string;
}

// Authentication credentials
export interface LoginCredentials {
  email: string;
  password?: string;
}

export interface SignUpCredentials extends LoginCredentials {
  name: string;
}

// Garden types
export interface Garden {
  id: string;
  name: string;
  description: string;
  plantIds: string[];
}

// Plant types
export interface Plant {
  id: string;
  name: string;
  species: string;
  plantingDate: string;
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
