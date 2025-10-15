/**
 * Route Middleware Component
 * Handles legacy route redirects automatically
 */
import React, { useEffect, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { handleLegacyRoutes } from './redirects';

interface RouteMiddlewareProps {
  children: ReactNode;
}

const RouteMiddleware: React.FC<RouteMiddlewareProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const currentPath = location.pathname;
    const redirectPath = handleLegacyRoutes(currentPath);
    
    if (redirectPath) {
      console.log(`Redirecting: ${currentPath} → ${redirectPath}`);
      navigate(redirectPath, { replace: true });
    }
  }, [location.pathname, navigate]);
  
  return <>{children}</>;
};

export default RouteMiddleware;
