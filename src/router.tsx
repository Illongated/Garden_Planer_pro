import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import LoginPage from './features/auth/pages/LoginPage'
import SignUpPage from './features/auth/pages/SignUpPage'
import AuthGuard from './features/auth/components/AuthGuard'
import Dashboard from './pages/Dashboard'
import Gardens from './pages/Gardens'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AuthGuard />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/', element: <Navigate to="/dashboard" replace /> },
          { path: 'dashboard', element: <Dashboard /> },
          { path: 'gardens', element: <Gardens /> },
          { path: 'settings', element: <Settings /> },
        ],
      },
    ],
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/signup',
    element: <SignUpPage />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
