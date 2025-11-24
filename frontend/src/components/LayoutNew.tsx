import React, { useState, ReactNode, useEffect } from 'react';
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
  Wrench,
  FolderKanban,
  AlertTriangle,
  GraduationCap,
  DollarSign,
  Megaphone,
  AlertOctagon,
  MessageCircle,
  LucideIcon,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
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

  // Sidebar state management
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [sidebarMode, setSidebarMode] = useState<'expanded' | 'collapsed' | 'mini'>(() => {
    // Load from localStorage or default to 'expanded'
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('sidebar-mode');
      return (savedMode as 'expanded' | 'collapsed' | 'mini') || 'expanded';
    }
    return 'expanded';
  });

  // User preferences from backend
  const [sidebarPreferences, setSidebarPreferences] = useState({
    default_mode: 'collapsed',
    hover_expand_enabled: false,
    auto_collapse_enabled: false,
    inactivity_timeout: 10,
    context_aware_enabled: false,
    collapse_after_navigation: false,
    click_outside_to_hide: true  // ON by default for first-time users
  });

  // Organization-level defaults
  const [orgSidebarDefaults, setOrgSidebarDefaults] = useState({
    default_mode: 'collapsed',
    hover_expand_enabled: false,
    auto_collapse_enabled: false,
    inactivity_timeout: 10,
    context_aware_enabled: false,
    collapse_after_navigation: false,
    click_outside_to_hide: true  // ON by default for first-time users
  });

  // Hover state
  const [isHovering, setIsHovering] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const [tempExpandedMode, setTempExpandedMode] = useState<'expanded' | 'collapsed' | 'mini' | null>(null);

  // Inactivity timer
  const inactivityTimerRef = React.useRef<NodeJS.Timeout | null>(null);
  const [lastInteractionTime, setLastInteractionTime] = useState(Date.now());

  // Accordion sections state - tracks which sections are expanded
  const [expandedSections, setExpandedSections] = useState<Set<string>>(() => {
    // Load from localStorage or default to Main, Organization, Operations open
    if (typeof window !== 'undefined') {
      const savedSections = localStorage.getItem('expanded-sections');
      if (savedSections) {
        return new Set(JSON.parse(savedSections));
      }
    }
    return new Set(['Main', 'Organization', 'Operations']);
  });

  const [searchOpen, setSearchOpen] = useState<boolean>(false);
  const [swipeProgress, setSwipeProgress] = useState<number>(0);

  // Load organization sidebar defaults (works before login)
  useEffect(() => {
    const loadOrgDefaults = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/organization/sidebar-settings`);

        if (response.ok) {
          const orgDefaults = await response.json();
          setOrgSidebarDefaults(orgDefaults);

          // Apply org defaults immediately if no user prefs loaded yet
          if (!user) {
            setSidebarPreferences(orgDefaults);
            if (orgDefaults.context_aware_enabled) {
              applyContextAwareMode(orgDefaults.default_mode);
            } else {
              // Check localStorage first for manual toggle state
              const manualMode = localStorage.getItem('sidebar-mode');
              if (manualMode) {
                setSidebarMode(manualMode as 'expanded' | 'collapsed' | 'mini');
              } else {
                setSidebarMode(orgDefaults.default_mode as 'expanded' | 'collapsed' | 'mini');
              }
            }
          }
        } else {
          // Use system defaults
          console.log('Using system sidebar defaults');
        }
      } catch (error) {
        console.log('Using system sidebar defaults');
      }
    };

    loadOrgDefaults();
  }, []);

  // Load user sidebar preferences from backend (after login)
  useEffect(() => {
    const loadPreferences = async () => {
      if (!user) return;

      try {
        const response = await fetch(`${BACKEND_URL}/api/users/sidebar-preferences`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (response.ok) {
          const userPrefs = await response.json();
          setSidebarPreferences(userPrefs);

          // Priority: localStorage manual toggle > user prefs > org defaults
          const manualMode = localStorage.getItem('sidebar-mode');

          if (manualMode) {
            // User manually toggled, respect that
            setSidebarMode(manualMode as 'expanded' | 'collapsed' | 'mini');
          } else {
            // Use user prefs (which fall back to org defaults if not set)
            if (userPrefs.context_aware_enabled) {
              applyContextAwareMode(userPrefs.default_mode);
            } else {
              setSidebarMode(userPrefs.default_mode as 'expanded' | 'collapsed' | 'mini');
            }
          }
        } else if (response.status === 401) {
          // Auth not ready yet, use org defaults silently
          console.log('Sidebar preferences will load after authentication completes');
        } else {
          // Use org defaults
          console.log('Using organization sidebar defaults');
        }
      } catch (error) {
        // Use org defaults silently
        console.log('Using organization sidebar defaults');
      }
    };

    // Add delay to ensure auth is ready
    const timer = setTimeout(() => {
      loadPreferences();
    }, 500);

    return () => clearTimeout(timer);
  }, [user]);

  // Detect touch device
  useEffect(() => {
    const checkTouchDevice = () => {
      setIsTouchDevice('ontouchstart' in window || navigator.maxTouchPoints > 0);
    };
    checkTouchDevice();
  }, []);

  // Click outside to hide (desktop only, if enabled)
  useEffect(() => {
    if (!sidebarPreferences.click_outside_to_hide || isTouchDevice) return;

    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.querySelector('.layout-sidebar');
      const target = event.target as Node;

      // Only hide if:
      // 1. Click is outside sidebar
      // 2. Sidebar is not in mini mode already
      // 3. Not clicking on toggle button
      if (sidebar && !sidebar.contains(target) && sidebarMode !== 'mini') {
        const isToggleButton = (event.target as Element)?.closest('.sidebar-toggle-btn');
        if (!isToggleButton) {
          setSidebarMode('mini');
          handleUserInteraction();
        }
      }
    };

    // Add listener with delay to avoid immediate trigger
    const timer = setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside);
    }, 500);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sidebarPreferences.click_outside_to_hide, isTouchDevice, sidebarMode]);

  // Apply context-aware mode based on screen size and route
  const applyContextAwareMode = (defaultMode: string) => {
    if (!sidebarPreferences.context_aware_enabled) return;

    const screenWidth = window.innerWidth;
    const currentPath = location.pathname;

    // Data-heavy pages that benefit from mini mode
    const dataHeavyRoutes = ['/dashboards', '/reports', '/analytics'];
    const isDataHeavy = dataHeavyRoutes.some(route => currentPath.startsWith(route));

    // Screen size rules
    if (screenWidth < 1440) {
      setSidebarMode('mini');
    } else if (isDataHeavy) {
      setSidebarMode('mini');
    } else {
      setSidebarMode(defaultMode as 'expanded' | 'collapsed' | 'mini');
    }
  };

  // Context-aware mode on route change
  useEffect(() => {
    if (sidebarPreferences.context_aware_enabled) {
      applyContextAwareMode(sidebarPreferences.default_mode);
    }
  }, [location.pathname, sidebarPreferences.context_aware_enabled]);

  // Inactivity auto-collapse
  useEffect(() => {
    if (!sidebarPreferences.auto_collapse_enabled) return;

    const checkInactivity = () => {
      const now = Date.now();
      const timeSinceLastInteraction = (now - lastInteractionTime) / 1000;

      if (timeSinceLastInteraction >= sidebarPreferences.inactivity_timeout) {
        if (sidebarMode !== 'mini' && !isHovering) {
          setSidebarMode('mini');
        }
      }
    };

    inactivityTimerRef.current = setInterval(checkInactivity, 1000);

    return () => {
      if (inactivityTimerRef.current) {
        clearInterval(inactivityTimerRef.current);
      }
    };
  }, [sidebarPreferences.auto_collapse_enabled, sidebarPreferences.inactivity_timeout, lastInteractionTime, sidebarMode, isHovering]);

  // Reset inactivity timer on user interaction
  const handleUserInteraction = () => {
    setLastInteractionTime(Date.now());
  };

  // Hover to expand (desktop only, not on touch devices)
  const handleMouseEnter = () => {
    if (isTouchDevice || !sidebarPreferences.hover_expand_enabled) return;

    setIsHovering(true);

    // If in mini mode, temporarily expand
    if (sidebarMode === 'mini') {
      setTempExpandedMode(sidebarMode);
      setSidebarMode('expanded');
    }
  };

  const handleMouseLeave = () => {
    if (isTouchDevice || !sidebarPreferences.hover_expand_enabled) return;

    setIsHovering(false);

    // Return to previous mode if it was temporarily expanded
    if (tempExpandedMode) {
      setSidebarMode(tempExpandedMode);
      setTempExpandedMode(null);
    }
  };

  // Persist sidebar mode to localStorage
  useEffect(() => {
    localStorage.setItem('sidebar-mode', sidebarMode);
  }, [sidebarMode]);

  // Persist expanded sections to localStorage
  useEffect(() => {
    localStorage.setItem('expanded-sections', JSON.stringify(Array.from(expandedSections)));
  }, [expandedSections]);

  // Toggle section expand/collapse
  const toggleSection = (sectionName: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionName)) {
        newSet.delete(sectionName);
      } else {
        newSet.add(sectionName);
      }
      return newSet;
    });
    handleUserInteraction();
  };

  // Cycle sidebar modes: expanded -> collapsed -> mini -> expanded
  const cycleSidebarMode = () => {
    // Clear any temporary expanded state from hover
    setTempExpandedMode(null);
    setIsHovering(false);

    setSidebarMode(current => {
      if (current === 'expanded') return 'collapsed';
      if (current === 'collapsed') return 'mini';
      return 'expanded';
    });
    handleUserInteraction();
  };

  // Handle navigation click
  const handleNavigationClick = (path: string) => {
    navigate(path);

    // Auto-collapse after navigation if enabled
    if (sidebarPreferences.collapse_after_navigation) {
      setSidebarMode('mini');
    }

    handleUserInteraction();
  };

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
          name: 'Incidents',
          icon: AlertTriangle,
          path: '/incidents',
          anyPermissions: ['incident.read.own', 'incident.read.organization'],
        },
        {
          name: 'Training',
          icon: GraduationCap,
          path: '/training',
          anyPermissions: ['training.read.own', 'training.read.organization'],
        },
        {
          name: 'Emergencies',
          icon: AlertTriangle,
          path: '/emergencies',
          anyPermissions: ['emergency.read.organization'],
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
      section: 'Financial',
      items: [
        {
          name: 'Financial',
          icon: DollarSign,
          path: '/financial',
          anyPermissions: ['financial.read.organization'],
        },
      ],
    },
    {
      section: 'Communication',
      items: [
        {
          name: 'Team Chat',
          icon: MessageCircle,
          path: '/chat',
          anyPermissions: ['chat.read.organization'],
        },
        {
          name: 'Announcements',
          icon: Megaphone,
          path: '/announcements',
          anyPermissions: ['announcement.read.organization'],
        },
      ],
    },
    {
      section: 'Supply Chain',
      items: [
        {
          name: 'Contractors',
          icon: Building2,
          path: '/contractors',
          anyPermissions: ['contractor.read.organization'],
        },
      ],
    },
    {
      section: 'Analytics',
      items: [
        {
          name: 'Dashboards',
          icon: BarChart3,
          path: '/dashboards',
          anyPermissions: ['dashboard.read.organization'],
        },
        {
          name: 'Reports',
          icon: FileText,
          path: '/reports',
          anyPermissions: ['report.read.own', 'report.read.organization'],
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
    // FIELD WORKER MODE:
    // If user is NOT admin/developer/manager, strictly limit menu items
    const isFieldWorker = user && !['admin', 'developer', 'manager'].includes(user.role);

    if (isFieldWorker) {
      // Allowed paths for field workers
      const allowedPaths = [
        '/dashboard',
        '/inspections',
        '/tasks',
        '/chat',
        '/settings',
        '/logout'
      ];

      // Check if path starts with any allowed path
      const isAllowed = allowedPaths.some(path => item.path === path || item.path.startsWith(path + '/'));

      if (!isAllowed) return false;
    }

    // Standard permission checks (keep existing logic for admins/managers)
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
            className={`layout-sidebar layout-sidebar--${sidebarMode}`}
            initial={{ x: -280 }}
            animate={{
              x: 0,
              width: sidebarMode === 'expanded' ? 280 : sidebarMode === 'collapsed' ? 200 : 80
            }}
            exit={{ x: -280 }}
            transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onClick={handleUserInteraction}
          >
            <GlassCard className="sidebar-card" padding="none">
              {/* Logo/Brand */}
              <div className="sidebar-header">
                <div className="brand">
                  <Building2 size={32} className="brand-icon" />
                  {sidebarMode !== 'mini' && (
                    <div>
                      <h1 className="brand-title">Operations</h1>
                      <p className="brand-subtitle">Management v2.0</p>
                    </div>
                  )}
                </div>
                {/* Sidebar toggle button */}
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={cycleSidebarMode}
                        className="sidebar-toggle-btn"
                        aria-label="Toggle sidebar"
                      >
                        {sidebarMode === 'expanded' ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <span>{sidebarMode === 'expanded' ? 'Collapse' : sidebarMode === 'collapsed' ? 'Mini mode' : 'Expand'}</span>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>

              {/* Navigation */}
              <nav className="sidebar-nav">
                {menuItems.map((section: any, sectionIndex: number) => {
                  const isExpanded = expandedSections.has(section.section);
                  const accessibleItems = section.items.filter(canAccessMenuItem);

                  return (
                    <div key={sectionIndex} className="nav-section">
                      {/* Section Header - Clickable to expand/collapse */}
                      <button
                        onClick={() => toggleSection(section.section)}
                        className="nav-section-title nav-section-title--clickable"
                      >
                        {sidebarMode === 'mini' ? (
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex items-center justify-center w-full">
                                  {section.items[0]?.icon && React.createElement(section.items[0].icon, { size: 20 })}
                                </div>
                              </TooltipTrigger>
                              <TooltipContent side="right">
                                <span>{section.section}</span>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        ) : (
                          <>
                            <span>{section.section}</span>
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </>
                        )}
                      </button>

                      {/* Section Items - Collapsible */}
                      <AnimatePresence>
                        {(isExpanded || sidebarMode === 'mini') && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            style={{ overflow: 'hidden' }}
                          >
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
                                          {sidebarMode !== 'mini' && <span>{item.name}</span>}
                                          {sidebarMode !== 'mini' && <Lock size={14} className="ml-auto opacity-50" />}
                                        </div>
                                      </TooltipTrigger>
                                      <TooltipContent side="right">
                                        <div className="flex items-center gap-2">
                                          <Lock className="h-3 w-3" />
                                          <span>{sidebarMode === 'mini' ? item.name : 'Permission Required'}</span>
                                        </div>
                                      </TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                );
                              }

                              // Mini mode: Show icon only with tooltip
                              if (sidebarMode === 'mini') {
                                return (
                                  <TooltipProvider key={item.path}>
                                    <Tooltip>
                                      <TooltipTrigger asChild>
                                        <motion.button
                                          onClick={() => handleNavigationClick(item.path)}
                                          className={`nav-item nav-item--icon-only ${active ? 'nav-item--active' : ''}`}
                                          whileHover={{ scale: 1.05 }}
                                          whileTap={{ scale: 0.95 }}
                                        >
                                          <Icon size={20} />
                                          {active && (
                                            <motion.div
                                              className="active-indicator"
                                              layoutId="activeIndicator"
                                              transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
                                            />
                                          )}
                                        </motion.button>
                                      </TooltipTrigger>
                                      <TooltipContent side="right">
                                        <span>{item.name}</span>
                                      </TooltipContent>
                                    </Tooltip>
                                  </TooltipProvider>
                                );
                              }

                              return (
                                <motion.button
                                  key={item.path}
                                  onClick={() => handleNavigationClick(item.path)}
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
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </nav>

              {/* User Profile */}
              <div className="sidebar-footer">
                {sidebarMode === 'mini' ? (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="user-avatar-mini">
                          {user?.picture ? (
                            <img
                              src={user.picture.startsWith('http') ? user.picture : `${BACKEND_URL}${user.picture}`}
                              alt={user?.name || 'User'}
                              className="w-full h-full object-cover rounded-full"
                            />
                          ) : (
                            user?.name?.charAt(0).toUpperCase() || 'U'
                          )}
                        </div>
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        <div>
                          <p className="font-medium">{user?.name || 'User'}</p>
                          <p className="text-xs text-muted-foreground">{user?.role || 'Member'}</p>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                ) : (
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
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  icon={<LogOut size={16} />}
                  className="logout-button"
                >
                  {sidebarMode !== 'mini' && 'Logout'}
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
