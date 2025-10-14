import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import './BottomNav.css';

interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
  route: string;
  badge?: boolean;
}

interface BottomNavProps {
  items: NavItem[];
}

const BottomNav: React.FC<BottomNavProps> = ({ items }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  return (
    <nav className="ds-bottom-nav">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.route || location.pathname.startsWith(item.route + '/');
        
        return (
          <motion.button
            key={item.id}
            onClick={() => navigate(item.route)}
            className={`ds-bottom-nav__item ${isActive ? 'ds-bottom-nav__item--active' : ''}`}
            whileTap={{ scale: 0.95 }}
            aria-label={item.label}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon className="ds-bottom-nav__icon" />
            <span className="ds-bottom-nav__label">{item.label}</span>
            
            {item.badge && (
              <motion.div
                className="ds-bottom-nav__badge"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
              />
            )}
          </motion.button>
        );
      })}
    </nav>
  );
};

export default BottomNav;
