import { useQuery } from '@tanstack/react-query';
import { getPlantCatalog, getPlantTypes, getPlantingSeasons } from '../api/plantCatalogApi';
import { PlantCatalogSearchFilters } from '@/types';

export const usePlantCatalog = (filters: PlantCatalogSearchFilters, page: number, pageSize: number) => {
  return useQuery({
    queryKey: ['plantCatalog', filters, page, pageSize],
    queryFn: () => getPlantCatalog(filters, page, pageSize),
    keepPreviousData: true,
  });
};

export const usePlantTypes = () => {
    return useQuery({
        queryKey: ['plantCatalogTypes'],
        queryFn: getPlantTypes,
        staleTime: Infinity, // Static data
    });
};

export const usePlantingSeasons = () => {
    return useQuery({
        queryKey: ['plantCatalogSeasons'],
        queryFn: getPlantingSeasons,
        staleTime: Infinity, // Static data
    });
};
