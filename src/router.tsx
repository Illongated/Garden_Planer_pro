import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import LoginPage from './features/auth/pages/LoginPage'
import SignUpPage from './features/auth/pages/SignUpPage'
import RequestPasswordResetPage from './features/auth/pages/RequestPasswordResetPage'
import ResetPasswordPage from './features/auth/pages/ResetPasswordPage'
import VerifyEmailPage from './features/auth/pages/VerifyEmailPage'
import AuthGuard from './features/auth/components/AuthGuard'
import GuestGuard from './features/auth/components/GuestGuard'
import Dashboard from './pages/Dashboard'
import Gardens from './pages/Gardens'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'
import GardenEditorPage from './features/garden-editor/pages/GardenEditorPage'

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
          { path: 'gardens/:gardenId', element: <GardenEditorPage /> },
          { path: 'settings', element: <Settings /> },
        ],
      },
    ],
  },
  {
    path: '/',
    element: <GuestGuard />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignUpPage /> },
      { path: 'request-password-reset', element: <RequestPasswordResetPage /> },
      { path: 'reset-password', element: <ResetPasswordPage /> },
    ]
  },
  {
    path: '/verify-email',
    element: <VerifyEmailPage />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
])
