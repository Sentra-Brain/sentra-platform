import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

interface PrivateRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, redirectTo = '/login' }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to={redirectTo} replace />;
  }
  return <>{children}</>;
};

export default PrivateRoute;
