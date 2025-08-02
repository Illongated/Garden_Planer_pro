import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { PlantCatalog, ViewMode } from '@/types';
import { useFavoritesStore } from '../store/useFavoritesStore';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Star } from 'lucide-react';
import { Badge } from '@/components/ui/badge';


interface Props {
  plant: PlantCatalog;
  viewMode: ViewMode;
}

const PlantCard: React.FC<Props> = ({ plant, viewMode }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: `draggable-${plant.id}`,
    data: { plant },
  });
  const { isFavorite, toggleFavorite } = useFavoritesStore();

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    zIndex: 100,
    cursor: 'grabbing',
  } : undefined;

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleFavorite(plant.id);
  };

  if (viewMode === 'list') {
    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes} className="w-full">
            <Card className="flex items-center p-2 hover:bg-muted/50 transition-colors cursor-grab">
                <img src={plant.image} alt={plant.name} className="w-16 h-16 object-cover rounded-md" />
                <div className="flex-grow ml-4 text-left">
                    <h3 className="font-semibold">{plant.name} <span className="text-muted-foreground">({plant.variety})</span></h3>
                    <p className="text-sm text-muted-foreground truncate">{plant.description}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={handleFavoriteClick} className="ml-auto">
                    <Star className={`h-5 w-5 ${isFavorite(plant.id) ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground'}`} />
                </Button>
            </Card>
        </div>
    );
  }

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
        <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-grab">
            <CardHeader className="p-0">
                <img src={plant.image} alt={plant.name} className="w-full h-32 object-cover" />
            </CardHeader>
            <CardContent className="p-4 text-left">
                <CardTitle className="text-lg mb-2 truncate">{plant.name}</CardTitle>
                <p className="text-sm text-muted-foreground h-10 overflow-hidden text-ellipsis">
                    {plant.description}
                </p>
                 <div className="mt-2 flex flex-wrap gap-1">
                    <Badge variant="secondary">{plant.plant_type}</Badge>
                    <Badge variant="outline">{plant.sun}</Badge>
                </div>
            </CardContent>
            <CardFooter className="p-4 pt-0">
                 <Button variant="ghost" size="icon" onClick={handleFavoriteClick} className="ml-auto">
                    <Star className={`h-5 w-5 ${isFavorite(plant.id) ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground'}`} />
                </Button>
            </CardFooter>
        </Card>
    </div>
  );
};

export default PlantCard;
