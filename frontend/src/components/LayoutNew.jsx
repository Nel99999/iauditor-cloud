import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { Button, GlassCard, AdaptiveNav, MOBILE_NAV_ITEMS } from '@/design-system/components';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import NotificationCenter from '@/components/NotificationCenter';
import GlobalSearch from '@/components/GlobalSearch';
import {
  LayoutDashboard,
  CheckSquare,
  ClipboardList,
  Users,
  Building2,
  Settings,
  FileText,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  Bell,
  Search,
  User,
  Mail,
  Shield,
  Upload,
  CheckCircle2,
  GitBranch,
  UserCheck,
  Activity,
  BarChart3,
  Webhook,
  ListTodo,
  Calendar,
  FolderOpen,
} from 'lucide-react';
import './LayoutNew.css';

const LayoutNew = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { canAccessPage } = usePermissions();
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);

  const menuItems = [
    // Core
    {
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
    },
    // Organization
    {
      name: 'Users',
      icon: Users,
      path: '/users',
    },
    {
      name: 'Roles',
      icon: Settings,
      path: '/roles',
    },
    {
      name: 'Organization',
      icon: Building2,
      path: '/organization',
    },
    {
      name: 'Groups',
      icon: Users,
      path: '/groups',
    },
    {
      name: 'Invitations',
      icon: Mail,
      path: '/invitations',
    },
    // Workflows
    {
      name: 'Workflows',
      icon: FileText,
      path: '/workflows',
    },
    {
      name: 'My Approvals',
      icon: CheckSquare,
      path: '/approvals',
    },
    {
      name: 'Delegations',
      icon: Users,
      path: '/delegations',
    },
    {
      name: 'Audit Trail',
      icon: Settings,
      path: '/audit',
    },
    // Operations
    {
      name: 'Inspections',
      icon: ClipboardList,
      path: '/inspections',
    },
    {
      name: 'Checklists',
      icon: CheckSquare,
      path: '/checklists',
    },
    {
      name: 'Tasks',
      icon: CheckSquare,
      path: '/tasks',
    },
    // Insights
    {
      name: 'Reports',
      icon: FileText,
      path: '/reports',
    },
    {
      name: 'Analytics',
      icon: FileText,
      path: '/analytics',
    },
    // Integrations
    {
      name: 'Webhooks',
      icon: Settings,
      path: '/webhooks',
    },
    {
      name: 'Bulk Import',
      icon: FileText,
      path: '/bulk-import',
    },
    // Settings
    {
      name: 'Settings',
      icon: Settings,
      path: '/settings',
    },
  ];

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout-new">
      {/* Animated Background */}
      <div className="layout-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      {/* Desktop Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            className="layout-sidebar"
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <GlassCard className="sidebar-card" padding="none">
              {/* Logo/Brand */}
              <div className="sidebar-header">
                <div className="brand">
                  <Building2 size={32} className="brand-icon" />
                  <div>
                    <h1 className="brand-title">Operations</h1>
                    <p className="brand-subtitle">Management v2.0</p>
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <nav className="sidebar-nav">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);
                  
                  return (
                    <motion.button
                      key={item.path}
                      onClick={() => navigate(item.path)}
                      className={`nav-item ${active ? 'nav-item--active' : ''}`}
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon size={20} />
                      <span>{item.name}</span>
                      {active && (
                        <motion.div
                          className="active-indicator"
                          layoutId="activeIndicator"
                          transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
                        />
                      )}
                    </motion.button>
                  );
                })}
              </nav>

              {/* User Profile */}
              <div className="sidebar-footer">
                <div className="user-profile">
                  <div className="user-avatar">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="user-info">
                    <p className="user-name">{user?.name || 'User'}</p>
                    <p className="user-role">{user?.role || 'Member'}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  icon={<LogOut size={16} />}
                  className="logout-button"
                >
                  Logout
                </Button>
              </div>
            </GlassCard>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className={`layout-main ${sidebarOpen ? 'with-sidebar' : 'full-width'}`}>
        {/* Top Header */}
        <header className="layout-header">
          <GlassCard className="header-card" padding="none">
            <div className="header-content">
              {/* Left: Menu Toggle */}
              <Button
                variant="ghost"
                size="md"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                icon={sidebarOpen ? <X size={20} /> : <Menu size={20} />}
                className="menu-toggle"
              />

              {/* Right: Actions */}
              <div className="header-actions">
                <Button
                  variant="ghost"
                  size="md"
                  onClick={() => setSearchOpen(true)}
                  icon={<Search size={20} />}
                  className="action-button"
                />
                <Button
                  variant="ghost"
                  size="md"
                  onClick={toggleTheme}
                  icon={theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                  className="action-button"
                />
                <NotificationCenter />
              </div>
            </div>
          </GlassCard>
        </header>

        {/* Page Content */}
        <main className="layout-content">
          {children}
        </main>
      </div>

      {/* Mobile/Tablet Adaptive Navigation */}
      <AdaptiveNav items={MOBILE_NAV_ITEMS} />

      {/* Global Search Modal */}
      <GlobalSearch isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
};

export default LayoutNew;
