import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import NotificationCenter from '@/components/NotificationCenter';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard,
  Building2,
  ClipboardCheck,
  CheckSquare,
  ListTodo,
  FileText,
  BarChart3,
  Settings,
  Users,
  Shield,
  Mail,
  LogOut,
  Menu,
  X,
  GitBranch,
  CheckCircle2,
  UserCheck,
  Calendar,
  FolderOpen,
  Bell,
  Lock,
  Activity,
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout, userRole } = useAuth();
  const { canAccessPage, hasAnyPermission } = usePermissions();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  const menuItems = [
    {
      section: 'Main',
      items: [
        {
          name: 'Dashboard',
          icon: LayoutDashboard,
          path: '/dashboard',
          badge: null,
          active: true,
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
          badge: null,
          active: true,
          description: 'Manage hierarchy',
        },
        {
          name: 'User Management',
          icon: Users,
          path: '/users',
          badge: 'New',
          active: true,
          description: 'Manage team members',
        },
        {
          name: 'Roles',
          icon: Shield,
          path: '/roles',
          badge: null,
          active: true,
          description: '10 system roles',
        },
        {
          name: 'Invitations',
          icon: Mail,
          path: '/invitations',
          badge: null,
          active: true,
          description: 'Track invites',
        },
        {
          name: 'Settings',
          icon: Settings,
          path: '/settings',
          badge: 'New',
          active: true,
          description: 'Account & preferences',
        },
        ...(user?.role === 'developer' ? [{
          name: 'Developer Admin',
          icon: Shield,
          path: '/developer-admin',
          badge: 'DEV',
          active: true,
          description: 'System admin panel',
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
          badge: 'NEW',
          active: true,
          description: 'Pending approvals',
        },
        {
          name: 'Workflow Designer',
          icon: GitBranch,
          path: '/workflows',
          badge: 'NEW',
          active: true,
          description: 'Manage workflows',
        },
        {
          name: 'Delegations',
          icon: UserCheck,
          path: '/delegations',
          badge: 'NEW',
          active: true,
          description: 'Authority delegation',
        },
        {
          name: 'Audit Trail',
          icon: Shield,
          path: '/audit',
          badge: 'NEW',
          active: true,
          description: 'Compliance & logs',
        },
        {
          name: 'Analytics',
          icon: Activity,
          path: '/analytics',
          badge: 'NEW',
          active: true,
          description: 'Charts & insights',
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
          badge: 'New',
          active: true,
          description: 'Templates & execution',
        },
        {
          name: 'Checklists',
          icon: CheckSquare,
          path: '/checklists',
          badge: 'New',
          active: true,
          description: 'Daily operations',
        },
        {
          name: 'Tasks',
          icon: ListTodo,
          path: '/tasks',
          badge: '✓',
          active: true,
          description: 'Task management',
        },
        {
          name: 'Schedule',
          icon: Calendar,
          path: '/schedule',
          badge: 'Soon',
          active: false,
          description: 'Team scheduling',
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
          badge: '✓',
          active: true,
          description: 'Analytics & reports',
        },
        {
          name: 'Analytics',
          icon: BarChart3,
          path: '/analytics',
          badge: 'Soon',
          active: false,
          description: 'Performance metrics',
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
          badge: 'Soon',
          active: false,
          description: 'Document library',
        },
      ],
    },
  ];

  const isActive = (path) => location.pathname === path;

  // Define permission requirements for each menu item
  const getPagePermissions = (pageName) => {
    const permissionMap = {
      'organization-structure': { permissions: ['user.read.organization'], minLevel: 3 },
      'users': { permissions: ['user.read.organization'], minLevel: 3 },
      'roles': { permissions: ['user.read.organization'], minLevel: 2 },
      'invitations': { permissions: ['user.create.organization'], minLevel: 3 },
      'inspections': { permissions: ['inspection.read.own'] },
      'tasks': { permissions: ['task.read.own'] },
      'reports': { permissions: ['report.read.own'] },
      'dashboard': {},
      'settings': {},
      'checklists': {},
    };
    return permissionMap[pageName] || {};
  };

  const handleMenuClick = (item) => {
    // Check if item requires permissions
    const pageName = item.path.replace('/', '');
    const pageConfig = getPagePermissions(pageName);
    const hasAccess = canAccessPage(pageName, pageConfig);
    
    if (!hasAccess) {
      alert(`Access Denied: You need higher permissions to access ${item.name}`);
      return;
    }
    
    if (item.active) {
      navigate(item.path);
    } else {
      alert(`${item.name} - Coming in ${item.badge || 'future milestone'}!`);
    }
  };

  const checkItemAccess = (item) => {
    const pageName = item.path.replace('/', '');
    const pageConfig = getPagePermissions(pageName);
    return canAccessPage(pageName, pageConfig);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center justify-between h-16 px-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <div className="flex items-center gap-3">
              <Building2 className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                  OpsPlatform
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Operational Excellence</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar data-testid="user-avatar">
                    <AvatarImage src={user?.picture} alt={user?.name} />
                    <AvatarFallback>{getInitials(user?.name || 'U')}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user?.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                    <Badge variant="outline" className="mt-1 w-fit capitalize">
                      {user?.role}
                    </Badge>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/profile')}>
                  <Users className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} data-testid="logout-button">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`
          fixed top-16 left-0 bottom-0 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 
          transition-transform duration-300 ease-in-out z-40 overflow-y-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
        data-testid="sidebar"
      >
        <nav className="p-4 space-y-6">
          {menuItems.map((section, idx) => (
            <div key={idx}>
              <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                {section.section}
              </h3>
              <div className="space-y-1">
                {section.items.map((item, itemIdx) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);
                  const hasAccess = checkItemAccess(item);
                  const isRestricted = item.active && !hasAccess;
                  
                  return (
                    <button
                      key={itemIdx}
                      onClick={() => handleMenuClick(item)}
                      disabled={!item.active || isRestricted}
                      className={`
                        w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors
                        ${active
                          ? 'bg-primary text-primary-foreground'
                          : item.active && hasAccess
                          ? 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                          : 'text-slate-400 dark:text-slate-500 cursor-not-allowed opacity-50'
                        }
                        ${isRestricted ? 'relative' : ''}
                      `}
                      data-testid={`menu-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="h-5 w-5" />
                        <div className="text-left">
                          <div className="flex items-center gap-2">
                            {item.name}
                            {isRestricted && <Lock className="h-3 w-3" />}
                          </div>
                          {item.description && (
                            <div className="text-xs opacity-70">{item.description}</div>
                          )}
                        </div>
                      </div>
                      {item.badge && (
                        <Badge
                          variant={item.active && hasAccess ? 'secondary' : 'outline'}
                          className="text-xs"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
          <div className="text-xs text-center text-slate-500 dark:text-slate-400">
            <p className="font-semibold">Phase 1 MVP</p>
            <p className="mt-1">All Milestones Complete</p>
            <div className="mt-2 flex gap-1 justify-center">
              <Badge variant="outline" className="text-xs">M1 ✓</Badge>
              <Badge variant="outline" className="text-xs">M2 ✓</Badge>
              <Badge variant="outline" className="text-xs">M3 ✓</Badge>
              <Badge variant="outline" className="text-xs">M4 ✓</Badge>
              <Badge variant="outline" className="text-xs">M5 ✓</Badge>
              <Badge variant="outline" className="text-xs">M6 ✓</Badge>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={`
          pt-16 transition-all duration-300
          ${sidebarOpen ? 'lg:pl-64' : ''}
        `}
      >
        <div className="p-6">
          {children}
        </div>
      </main>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;