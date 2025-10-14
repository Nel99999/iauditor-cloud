import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LucideIcon } from 'lucide-react';
import './NavRail.css';

interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
  route: string;
  badge?: boolean;
}

interface NavRailProps {
  items: NavItem[];
}

const NavRail: React.FC<NavRailProps> = ({ items }) => {
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
