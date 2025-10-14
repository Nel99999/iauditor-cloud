import React, { useEffect, useState } from 'react';
import BottomNav from './BottomNav';
import NavRail from './NavRail';
import './AdaptiveNav.css';

const BREAKPOINTS = {
  MOBILE: 600,
  TABLET: 1024,
};

const AdaptiveNav = ({ items }) => {
  const [navType, setNavType] = useState('desktop');
  
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      
      if (width < BREAKPOINTS.MOBILE) {
        setNavType('bottom');
      } else if (width < BREAKPOINTS.TABLET) {
        setNavType('rail');
      } else {
        setNavType('desktop');
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Same navigation data, different UI
  switch (navType) {
    case 'bottom':
      return <BottomNav items={items} />;
    case 'rail':
      return <NavRail items={items} />;
    case 'desktop':
      // Desktop uses existing sidebar from Layout.jsx
      return null;
    default:
      return null;
  }
};

export default AdaptiveNav;