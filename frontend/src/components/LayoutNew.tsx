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
  CheckCircle2,
  GitBranch,
  UserCheck,
  BarChart3,
  Webhook,
  ListTodo,
  Calendar,
  FolderOpen,
  Lock,
  Package,
  LucideIcon,
} from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import './LayoutNew.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

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
  const { hasPermission, hasAnyPermission, hasRoleLevel } = usePermissions();
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
          // No permission required - accessible to all
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
          anyPermissions: ['organization.read.organization', 'organization.read.all'],
        },
        {
          name: 'User Management',
          icon: Users,
          path: '/users',
          anyPermissions: ['user.read.organization', 'user.read.all'],
        },
        {
          name: 'Roles',
          icon: Shield,
          path: '/roles',
          anyPermissions: ['role.read.organization', 'role.read.all'],
          minLevel: 2, // Master level
        },
        {
          name: 'Groups & Teams',
          icon: Users,
          path: '/groups',
          anyPermissions: ['group.read.organization', 'group.read.all'],
        },
        {
          name: 'Invitations',
          icon: Mail,
          path: '/invitations',
          anyPermissions: ['invitation.create.organization', 'invitation.read.organization'],
          minLevel: 3, // Admin level
        },
        {
          name: 'Bulk Import',
          icon: Upload,
          path: '/bulk-import',
          permission: 'user.create.organization',
          minLevel: 3,
        },
        {
          name: 'Settings',
          icon: Settings,
          path: '/settings',
          // No permission check - users can always access their own settings
        },
        ...(user?.role === 'developer' ? [{
          name: 'Developer Admin',
          icon: Shield,
          path: '/developer-admin',
          roles: ['developer'],
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
          anyPermissions: ['approval.read.own', 'approval.manage.organization'],
        },
        {
          name: 'Workflow Designer',
          icon: GitBranch,
          path: '/workflows',
          anyPermissions: ['workflow.create.organization', 'workflow.read.organization'],
          minLevel: 4,
        },
        {
          name: 'Delegations',
          icon: UserCheck,
          path: '/delegations',
          permission: 'delegation.manage.own',
        },
        {
          name: 'Audit Trail',
          icon: Shield,
          path: '/audit',
          permission: 'audit.read.organization',
          minLevel: 3,
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
          anyPermissions: ['inspection.read.own', 'inspection.read.organization'],
        },
        {
          name: 'Checklists',
          icon: CheckSquare,
          path: '/checklists',
          anyPermissions: ['checklist.read.own', 'checklist.read.organization'],
        },
        {
          name: 'Tasks',
          icon: ListTodo,
          path: '/tasks',
          anyPermissions: ['task.read.own', 'task.read.organization'],
        },
        {
          name: 'Assets',
          icon: Package,
          path: '/assets',
          anyPermissions: ['asset.read.own', 'asset.read.organization'],
        },
        {
          name: 'Work Orders',
          icon: Wrench,
          path: '/work-orders',
          anyPermissions: ['workorder.read.own', 'workorder.read.organization'],
        },
        {
          name: 'Inventory',
          icon: FolderOpen,
          path: '/inventory',
          anyPermissions: ['inventory.read.own', 'inventory.read.organization'],
        },
        {
          name: 'Projects',
          icon: FolderKanban,
          path: '/projects',
          anyPermissions: ['project.read.own', 'project.read.organization'],
        },
        {
          name: 'Schedule',
          icon: Calendar,
          path: '/schedule',
          anyPermissions: ['schedule.read.own', 'schedule.read.organization'],
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
          anyPermissions: ['report.read.own', 'report.read.organization'],
        },
        {
          name: 'Analytics',
          icon: BarChart3,
          path: '/analytics',
          permission: 'analytics.read.organization',
          minLevel: 5,
        },
        {
          name: 'Webhooks',
          icon: Webhook,
          path: '/webhooks',
          permission: 'webhook.manage.organization',
          minLevel: 3,
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
          anyPermissions: ['document.read.own', 'document.read.organization'],
        },
      ],
    },
  ];

  const isActive = (path: string): boolean => location.pathname === path || location.pathname.startsWith(path + '/');

  /**
   * Check if user can access a menu item
   */
  const canAccessMenuItem = (item: MenuItem): boolean => {
    // Check permission
    if (item.permission) {
      const [resource, action, scope] = item.permission.split('.');
      if (!hasPermission(resource, action, scope)) return false;
    }

    // Check any permissions
    if (item.anyPermissions && item.anyPermissions.length > 0) {
      if (!hasAnyPermission(item.anyPermissions)) return false;
    }

    // Check role level
    if (item.minLevel !== undefined) {
      if (!hasRoleLevel(item.minLevel)) return false;
    }

    // Check specific roles
    if (item.roles && item.roles.length > 0) {
      if (!item.roles.includes(user?.role || '')) return false;
    }

    return true;
  };

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
                      const hasAccess = canAccessMenuItem(item);
                      
                      // If no access, show greyed out with tooltip
                      if (!hasAccess) {
                        return (
                          <TooltipProvider key={item.path}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="nav-item nav-item--disabled">
                                  <Icon size={20} />
                                  <span>{item.name}</span>
                                  <Lock size={14} className="ml-auto opacity-50" />
                                </div>
                              </TooltipTrigger>
                              <TooltipContent side="right">
                                <div className="flex items-center gap-2">
                                  <Lock className="h-3 w-3" />
                                  <span>Permission Required</span>
                                </div>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        );
                      }
                      
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
                          {item.badge && (
                            <span className="ml-auto text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">
                              {item.badge}
                            </span>
                          )}
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
                    {user?.picture ? (
                      <img 
                        src={user.picture.startsWith('http') ? user.picture : `${BACKEND_URL}${user.picture}`} 
                        alt={user?.name || 'User'}
                        className="w-full h-full object-cover rounded-full"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          if (e.currentTarget.parentElement) {
                            e.currentTarget.parentElement.textContent = user?.name?.charAt(0).toUpperCase() || 'U';
                          }
                        }}
                      />
                    ) : (
                      user?.name?.charAt(0).toUpperCase() || 'U'
                    )}
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
