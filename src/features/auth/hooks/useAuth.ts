import { useAuthStore } from '../store/auth.store'
import { useApi } from '@/hooks/use-api'
import { LoginCredentials, SignUpCredentials, User } from '@/types'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

export const useAuth = () => {
  const { user, token, isAuthenticated, setUser, setToken, logout: clearAuth } = useAuthStore()
  const navigate = useNavigate()
  const api = useApi()

  // Mock login
  const login = async (credentials: LoginCredentials) => {
    try {
      // In a real app, you'd call your API here.
      // const { user, token } = await api.post('/auth/login', credentials);
      console.log('Logging in with:', credentials)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      if (credentials.email === 'test@example.com' && credentials.password === 'password') {
        const mockUser: User = {
          id: '1',
          name: 'Test User',
          email: 'test@example.com',
        }
        const mockToken = 'fake-jwt-token'

        setUser(mockUser)
        setToken(mockToken)
        toast.success('Login successful!')
        navigate('/dashboard')
        return { user: mockUser, token: mockToken }
      } else {
        throw new Error('Invalid credentials')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred'
      toast.error(`Login failed: ${errorMessage}`)
      throw error
    }
  }

  // Mock signup
  const signup = async (credentials: SignUpCredentials) => {
    try {
      // In a real app, you'd call your API here.
      // const { user, token } = await api.post('/auth/signup', credentials);
      console.log('Signing up with:', credentials)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const mockUser: User = {
        id: '2',
        name: credentials.name,
        email: credentials.email,
      }
      const mockToken = 'fake-jwt-token-new-user'

      setUser(mockUser)
      setToken(mockToken)
      toast.success('Sign up successful!')
      navigate('/dashboard')
      return { user: mockUser, token: mockToken }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred'
      toast.error(`Sign up failed: ${errorMessage}`)
      throw error
    }
  }

  // Logout
  const logout = () => {
    clearAuth()
    toast.info('You have been logged out.')
    navigate('/login')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    signup,
    logout,
  }
}
