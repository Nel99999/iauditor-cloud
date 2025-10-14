import {
  Home,
  LayoutDashboard,
  Users,
  CheckSquare,
  Settings,
  ClipboardList,
  FileText,
  Building2
} from 'lucide-react';

/**
 * NAVIGATION MODEL - Safe to modify UI
 * Changes here only affect visual presentation
 * Routes remain stable
 */
export const NAV_MODEL = {
  primary: [
    {
      id: 'dashboard',
      label: 'Dashboard',
      route: '/dashboard',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'tasks',
      label: 'Tasks',
      route: '/tasks',
      icon: CheckSquare,
      badge: null,
    },
    {
      id: 'inspections',
      label: 'Inspections',
      route: '/inspections',
      icon: ClipboardList,
      badge: null,
    },
    {
      id: 'users',
      label: 'Users',
      route: '/users',
      icon: Users,
      badge: null,
    },
  ],
  
  secondary: [
    {
      id: 'organization',
      label: 'Organization',
      route: '/organization',
      icon: Building2,
      badge: null,
    },
    {
      id: 'reports',
      label: 'Reports',
      route: '/reports',
      icon: FileText,
      badge: null,
    },
    {
      id: 'settings',
      label: 'Settings',
      route: '/settings',
      icon: Settings,
      badge: null,
    },
  ],
};

// Export combined for mobile bottom nav (primary only)
export const MOBILE_NAV_ITEMS = NAV_MODEL.primary;

// Export combined for tablet nav rail (primary only)
export const TABLET_NAV_ITEMS = NAV_MODEL.primary;

// Desktop uses existing sidebar with all items