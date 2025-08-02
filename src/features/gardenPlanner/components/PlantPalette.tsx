import React, { useState } from 'react';
import { useDebounce } from '@/hooks/use-debounce'; // Assuming a debounce hook exists
import { usePlantCatalog } from '../hooks/usePlantCatalog';
import { PlantCatalogSearchFilters, ViewMode } from '@/types';
import PlantCard from './PlantCard';
import SearchAndFilter from './SearchAndFilter';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LoadingSpinner } from '@/components/loading-spinner';

const PlantPalette: React.FC = () => {
  const [filters, setFilters] = useState<PlantCatalogSearchFilters>({});
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const debouncedFilters = useDebounce(filters, 300);

  const { data, isLoading, isError, isFetching } = usePlantCatalog(debouncedFilters, page, 20);

  const handleFilterChange = (newFilters: PlantCatalogSearchFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  // Note: A proper infinite scroll would be better here,
  // but for simplicity, we'll just show a loading spinner.

  return (
    <div className="flex flex-col h-full border-r bg-card text-card-foreground shadow">
      <SearchAndFilter
        filters={filters}
        onFilterChange={handleFilterChange}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />
      <ScrollArea className="flex-grow">
        <div className={`p-4 grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2' : 'grid-cols-1'}`}>
            {isLoading && <LoadingSpinner />}
            {isError && <p className="text-destructive">Error fetching plants.</p>}
            {data?.items.map(plant => (
                <PlantCard key={plant.id} plant={plant} viewMode={viewMode} />
            ))}
        </div>
        {isFetching && !isLoading && (
            <div className="flex justify-center p-4">
                <LoadingSpinner />
            </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default PlantPalette;
