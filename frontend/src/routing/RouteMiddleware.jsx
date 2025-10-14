/**
 * Route Middleware Component
 * Handles legacy route redirects automatically
 */
import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { handleLegacyRoutes } from './redirects';

const RouteMiddleware = ({ children }) => {
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
  
  return children;
};

export default RouteMiddleware;