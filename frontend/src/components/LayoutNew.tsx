import React, { useState, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSwipeable } from 'react-swipeable';
import { useAuth } from '../contexts/AuthContext';
import { Button, GlassCard, AdaptiveNav, MOBILE_NAV_ITEMS } from '@/design-system/components';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';
import { usePermissions } from '@/hooks/usePermissions';
import NotificationCenter from '@/components/NotificationCenter';
import GlobalSearch from '@/components/GlobalSearch';
import {
  LayoutDashboard,
  CheckSquare,
  ClipboardCheck,
  Users,
  Building2,
  Settings,
  FileText,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
  Search,
  Mail,
  Shield,
  Upload,
  CheckCircle,
  CheckCircle2,
  GitBranch,
  UserCheck,
  BarChart3,
  Webhook,
  ListTodo,
  Calendar,
  FolderOpen,
  Lock,
  LucideIcon,
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import './LayoutNew.css';

// Types
interface MenuItem {
  name: string;
  icon: LucideIcon;
  path: string;
  badge?: string;
  permission?: string;  // Required permission
  anyPermissions?: string[];  // Any of these permissions
  roles?: string[];  // Required roles
  minLevel?: number;  // Required role level
}

interface MenuSection {
  section: string;
  items: MenuItem[];
}

interface LayoutNewProps {
  children: ReactNode;
}

const LayoutNew: React.FC<LayoutNewProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [searchOpen, setSearchOpen] = useState<boolean>(false);
  const [swipeProgress, setSwipeProgress] = useState<number>(0);

  // Gesture support for mobile - swipe right to go back
  const swipeHandlers = useSwipeable({
    onSwiping: (eventData) => {
      // Show visual feedback during swipe
      if (window.innerWidth < 768 && eventData.dir === 'Right' && eventData.initial[0] < 50) {
        const progress = Math.min(eventData.deltaX / 100, 1);
        setSwipeProgress(progress);
      }
    },
    onSwipedRight: (eventData) => {
      // Only enable on mobile (screen width < 768px)
      if (window.innerWidth < 768) {
        // Only go back if not on home/dashboard and swipe started from left edge
        if (location.pathname !== '/' && location.pathname !== '/dashboard' && eventData.initial[0] < 50) {
          navigate(-1);
        }
      }
      setSwipeProgress(0);
    },
    onSwiped: () => {
      setSwipeProgress(0);
    },
    trackMouse: false, // Disable mouse tracking (desktop)
    trackTouch: true,  // Enable touch tracking (mobile)
    delta: 50,         // Minimum swipe distance
    preventScrollOnSwipe: false, // Allow vertical scrolling
    swipeDuration: 500, // Maximum swipe duration
  });

  const menuItems: MenuSection[] = [
    {
      section: 'Main',
      items: [
        {
          name: 'Dashboard',
          icon: LayoutDashboard,
          path: '/dashboard',
        },
      ],
    },
    {
      section: 'Organization',
      items: [
        {
          name: 'Organization Structure',
          icon: Building2,
          path: '/organization',
        },
        {
          name: 'User Management',
          icon: Users,
          path: '/users',
        },
        ...(['master', 'admin', 'developer'].includes(user?.role || '') ? [{
          name: 'Pending Approvals',
          icon: CheckCircle,
          path: '/users/approvals',
          badge: 'NEW'
        }] : []),
        {
          name: 'Roles',
          icon: Shield,
          path: '/roles',
        },
        {
          name: 'Groups & Teams',
          icon: Users,
          path: '/groups',
        },
        {
          name: 'Invitations',
          icon: Mail,
          path: '/invitations',
        },
        {
          name: 'Bulk Import',
          icon: Upload,
          path: '/bulk-import',
        },
        {
          name: 'Settings',
          icon: Settings,
          path: '/settings',
        },
        ...(user?.role === 'developer' ? [{
          name: 'Developer Admin',
          icon: Shield,
          path: '/developer-admin',
        }] : []),
      ],
    },
    {
      section: 'Workflows',
      items: [
        {
          name: 'My Approvals',
          icon: CheckCircle2,
          path: '/approvals',
        },
        {
          name: 'Workflow Designer',
          icon: GitBranch,
          path: '/workflows',
        },
        {
          name: 'Delegations',
          icon: UserCheck,
          path: '/delegations',
        },
        {
          name: 'Audit Trail',
          icon: Shield,
          path: '/audit',
        },
      ],
    },
    {
      section: 'Operations',
      items: [
        {
          name: 'Inspections',
          icon: ClipboardCheck,
          path: '/inspections',
        },
        {
          name: 'Checklists',
          icon: CheckSquare,
          path: '/checklists',
        },
        {
          name: 'Tasks',
          icon: ListTodo,
          path: '/tasks',
        },
        {
          name: 'Schedule',
          icon: Calendar,
          path: '/schedule',
        },
      ],
    },
    {
      section: 'Insights',
      items: [
        {
          name: 'Reports',
          icon: FileText,
          path: '/reports',
        },
        {
          name: 'Analytics',
          icon: BarChart3,
          path: '/analytics',
        },
        {
          name: 'Webhooks',
          icon: Webhook,
          path: '/webhooks',
        },
      ],
    },
    {
      section: 'Resources',
      items: [
        {
          name: 'Documents',
          icon: FolderOpen,
          path: '/documents',
        },
      ],
    },
  ];

  const isActive = (path: string): boolean => location.pathname === path || location.pathname.startsWith(path + '/');

  const handleLogout = async (): Promise<void> => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout-new" {...swipeHandlers}>
      {/* Swipe Back Indicator (Mobile Only) */}
      {swipeProgress > 0 && (
        <motion.div
          style={{
            position: 'fixed',
            left: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            width: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(99, 102, 241, 0.2)',
            backdropFilter: 'blur(8px)',
            borderRadius: '0 50% 50% 0',
            opacity: swipeProgress,
            zIndex: 9999,
            pointerEvents: 'none',
          }}
          initial={{ opacity: 0, x: -60 }}
          animate={{ opacity: swipeProgress, x: 0 }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: '#6366f1' }}>
            <path d="M19 12H5M5 12l7 7M5 12l7-7" />
          </svg>
        </motion.div>
      )}

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
                {menuItems.map((section: any, sectionIndex: number) => (
                  <div key={sectionIndex} className="nav-section">
                    <div className="nav-section-title">{section.section}</div>
                    {section.items.map((item: any) => {
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
                  </div>
                ))}
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
      <AdaptiveNav items={MOBILE_NAV_ITEMS as any} />

      {/* Global Search Modal */}
      <GlobalSearch isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
};

export default LayoutNew;
