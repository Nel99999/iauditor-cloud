// Permission checking utilities

// Types
interface PageConfig {
  required: boolean;
  permissions?: string[];
  minLevel?: number;
}

type RoleName = 'developer' | 'master' | 'admin' | 'operations_manager' | 'team_lead' | 'manager' | 'supervisor' | 'inspector' | 'operator' | 'viewer';

interface Permission {
  resource_type: string;
  action: string;
  scope: string;
  [key: string]: any;
}

// Define permission requirements for each page/section
export const PAGE_PERMISSIONS: Record<string, PageConfig> = {
  dashboard: { required: false }, // Always accessible
  'organization-structure': {
    required: true,
    permissions: ['user.read.organization']
  },
  users: {
    required: true,
    permissions: ['user.read.organization'],
    minLevel: 3 // Admin level
  },
  roles: {
    required: true,
    permissions: ['user.read.organization'],
    minLevel: 2 // Master level
  },
  invitations: {
    required: true,
    permissions: ['user.create.organization'],
    minLevel: 3 // Admin level
  },
  settings: { required: false }, // Own settings always accessible
  inspections: {
    required: true,
    permissions: ['inspection.read.own']
  },
  checklists: { required: false },
  tasks: {
    required: true,
    permissions: ['task.read.own']
  },
  reports: {
    required: true,
    permissions: ['report.read.own']
  }
};

// Role hierarchy levels
export const ROLE_LEVELS: Record<RoleName, number> = {
  developer: 1,
  master: 2,
  admin: 3,
  operations_manager: 4,
  team_lead: 5,
  manager: 6,
  supervisor: 7,
  inspector: 8,
  operator: 9,
  viewer: 10
};

/**
 * Check if user has required role level
 */
export const hasRequiredLevel = (userRole: string, requiredLevel: number): boolean => {
  const userLevel = (ROLE_LEVELS as any)[userRole] || 999;
  return userLevel <= requiredLevel;
};

/**
 * Check if user can access a page
 */
export const canAccessPage = (pageName: string, userRole: string, userPermissions: Permission[] = []): boolean => {
  const pageConfig = PAGE_PERMISSIONS[pageName];
  
  if (!pageConfig) return true; // Unknown page, allow by default
  if (!pageConfig.required) return true; // No restrictions
  
  // Check role level if required
  if (pageConfig.minLevel) {
    if (!hasRequiredLevel(userRole, pageConfig.minLevel)) {
      return false;
    }
  }
  
  // Check permissions if required
  if (pageConfig.permissions && pageConfig.permissions.length > 0) {
    // User needs at least one of the required permissions
    return pageConfig.permissions.some(perm => 
      userPermissions.some(up => 
        up.resource_type === perm.split('.')[0] &&
        up.action === perm.split('.')[1] &&
        up.scope === perm.split('.')[2]
      )
    );
  }
  
  return true;
};

/**
 * Check if user can invite others based on role hierarchy
 */
export const canInviteRole = (inviterRole: string, inviteeRole: string): boolean => {
  const inviterLevel = (ROLE_LEVELS as any)[inviterRole] || 999;
  const inviteeLevel = (ROLE_LEVELS as any)[inviteeRole] || 999;
  
  // Can only invite lower or equal level roles
  return inviterLevel <= inviteeLevel;
};

/**
 * Get roles that a user can invite
 */
export const getInvitableRoles = (inviterRole: string): string[] => {
  const inviterLevel = (ROLE_LEVELS as any)[inviterRole] || 999;
  return Object.keys(ROLE_LEVELS).filter(role => (ROLE_LEVELS as any)[role] >= inviterLevel);
};

/**
 * Check if user can delete an invitation
 */
export const canDeleteInvitation = (userRole: string, inviterRole: string, invitedBy: string): boolean => {
  const userLevel = (ROLE_LEVELS as any)[userRole] || 999;
  const inviterLevel = (ROLE_LEVELS as any)[inviterRole] || 999;
  
  // Can delete if: 1) You are the inviter, OR 2) You have higher role level
  return invitedBy === 'self' || userLevel < inviterLevel;
};

/**
 * Format permission for display
 */
export const formatPermission = (permission: Permission): string => {
  return `${permission.resource_type}.${permission.action}.${permission.scope}`;
};
