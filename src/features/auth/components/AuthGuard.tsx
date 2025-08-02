import { useAuth } from '../hooks/useAuth';
import { Navigate, Outlet } from 'react-router-dom';

const AuthGuard = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // The AuthProvider will handle the loading state.
    // If we get here and we are not authenticated, redirect to login.
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default AuthGuard;
