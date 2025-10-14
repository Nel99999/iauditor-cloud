import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './NavRail.css';

const NavRail = ({ items }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  return (
    <nav className="ds-nav-rail">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.route || location.pathname.startsWith(item.route + '/');
        
        return (
          <button
            key={item.id}
            onClick={() => navigate(item.route)}
            className={`ds-nav-rail__item ${isActive ? 'ds-nav-rail__item--active' : ''}`}
            aria-label={item.label}
            aria-current={isActive ? 'page' : undefined}
            title={item.label}
          >
            <Icon className="ds-nav-rail__icon" />
            
            {item.badge && (
              <div className="ds-nav-rail__badge" />
            )}
          </button>
        );
      })}
    </nav>
  );
};

export default NavRail;