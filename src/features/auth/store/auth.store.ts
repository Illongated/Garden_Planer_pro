import { create } from 'zustand'

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated'

interface AuthState {
  accessToken: string | null
  status: AuthStatus
  setToken: (token: string | null) => void
  setStatus: (status: AuthStatus) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  status: 'loading', // Start in a loading state
  setToken: (token) => set({ accessToken: token }),
  setStatus: (status) => set({ status }),
  logout: () => set({ accessToken: null, status: 'unauthenticated' }),
}))
