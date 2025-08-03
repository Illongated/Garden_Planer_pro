import { useAuthStore } from '@/features/auth/store/auth.store'

// This is a mock API hook. In a real application, you would use
// a library like axios or the native fetch API to make requests
// to your backend. The useQuery and useMutation hooks from
// @tanstack/react-query would wrap these calls.

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1' // Configurable API base URL

export const useApi = () => {
  const { token } = useAuthStore()

  const getHeaders = () => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    return headers
  }

  const get = async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: getHeaders(),
    })
    if (!response.ok) {
      throw new Error('Network response was not ok')
    }
    return response.json() as Promise<T>
  }

  const post = async <T>(endpoint: string, body: unknown): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    })
    if (!response.ok) {
      throw new Error('Network response was not ok')
    }
    return response.json() as Promise<T>
  }

  // You can add other methods like put, patch, delete as needed.

  return {
    get,
    post,
  }
}

// Example of how you might use this with React Query in a feature hook
/*
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useGardens = () => {
  const api = useApi();
  const queryClient = useQueryClient();

  const { data: gardens, isLoading, error } = useQuery({
    queryKey: ['gardens'],
    queryFn: () => api.get('/gardens'),
  });

  const createGarden = useMutation({
    mutationFn: (newGarden) => api.post('/gardens', newGarden),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gardens'] });
    },
  });

  return { gardens, isLoading, error, createGarden };
}
*/
