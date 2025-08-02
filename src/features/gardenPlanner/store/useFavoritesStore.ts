import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface FavoritesState {
  favoriteIds: Set<number>;
  toggleFavorite: (id: number) => void;
  isFavorite: (id: number) => boolean;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      favoriteIds: new Set(),
      toggleFavorite: (id) =>
        set((state) => {
          const newFavorites = new Set(state.favoriteIds);
          if (newFavorites.has(id)) {
            newFavorites.delete(id);
          } else {
            newFavorites.add(id);
          }
          return { favoriteIds: newFavorites };
        }),
      isFavorite: (id) => get().favoriteIds.has(id),
    }),
    {
      name: 'agrotique-planner-favorites-storage', // unique name for localStorage
      // Custom serialization for Set
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          if (!str) return null;
          const { state } = JSON.parse(str);
          return {
            state: {
              ...state,
              favoriteIds: new Set(state.favoriteIds),
            },
          };
        },
        setItem: (name, newValue) => {
          const str = JSON.stringify({
            state: {
              ...newValue.state,
              favoriteIds: Array.from(newValue.state.favoriteIds),
            },
          });
          localStorage.setItem(name, str);
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);
