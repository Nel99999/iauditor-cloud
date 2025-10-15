import React, { ReactNode } from 'react';
import LayoutNew from './LayoutNew';

// Legacy Layout component - re-exports LayoutNew for backwards compatibility
interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return <LayoutNew>{children}</LayoutNew>;
};

export default Layout;
