import { useAuth } from '../hooks/useAuth';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import LoadingSpinner from '@/components/loading-spinner';
import { Suspense } from 'react';

const AuthGuard = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <Suspense fallback={<div className="flex h-full w-full items-center justify-center"><LoadingSpinner /></div>}>
      <Outlet />
    </Suspense>
  );
};

export default AuthGuard;
