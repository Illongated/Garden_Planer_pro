import { api } from '@/lib/api';
import { PaginatedPlantCatalogResponse, PlantCatalogSearchFilters } from '@/types';

export const getPlantCatalog = async (
  filters: PlantCatalogSearchFilters,
  page: number,
  pageSize: number
): Promise<PaginatedPlantCatalogResponse> => {
  const params = { ...filters, page, page_size: pageSize };
  const response = await api.get('/plant-catalog/', { params });
  return response.data;
};

export const getPlantTypes = async (): Promise<string[]> => {
  const response = await api.get('/plant-catalog/types');
  return response.data;
};

export const getPlantingSeasons = async (): Promise<string[]> => {
    const response = await api.get('/plant-catalog/seasons');
    return response.data;
};
