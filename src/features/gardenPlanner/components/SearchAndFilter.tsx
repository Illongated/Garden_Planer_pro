import React from 'react';
import { usePlantTypes, usePlantingSeasons } from '../hooks/usePlantCatalog';
import { PlantCatalogSearchFilters, ViewMode } from '@/types';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { LayoutGrid, List } from 'lucide-react';

interface Props {
  filters: PlantCatalogSearchFilters;
  onFilterChange: (filters: PlantCatalogSearchFilters) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
}

const SearchAndFilter: React.FC<Props> = ({ filters, onFilterChange, viewMode, onViewModeChange }) => {
  const { data: plantTypes } = usePlantTypes();
  const { data: seasons } = usePlantingSeasons();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onFilterChange({ ...filters, [name]: value });
  };

  const handleSelectChange = (name: keyof PlantCatalogSearchFilters) => (value: string) => {
    onFilterChange({ ...filters, [name]: value });
  };

  return (
    <div className="p-4 border-b">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-green-600">Plant Catalog</h2>
        <div className="flex gap-2">
          <Button variant={viewMode === 'grid' ? 'default' : 'outline'} size="icon" onClick={() => onViewModeChange('grid')}>
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button variant={viewMode === 'list' ? 'default' : 'outline'} size="icon" onClick={() => onViewModeChange('list')}>
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <Input
          type="text"
          name="q"
          placeholder="Search plants by name, variety..."
          value={filters.q || ''}
          onChange={handleInputChange}
          className="w-full"
        />
        <div className="grid grid-cols-2 gap-4">
          <Select name="plant_type" value={filters.plant_type || ''} onValueChange={handleSelectChange('plant_type')}>
            <SelectTrigger>
              <SelectValue placeholder="All Plant Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Types</SelectItem>
              {plantTypes?.map(type => <SelectItem key={type} value={type}>{type}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select name="season" value={filters.season || ''} onValueChange={handleSelectChange('season')}>
            <SelectTrigger>
              <SelectValue placeholder="All Planting Seasons" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Seasons</SelectItem>
              {seasons?.map(season => <SelectItem key={season} value={season}>{season}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

export default SearchAndFilter;
