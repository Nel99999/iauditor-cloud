// Permission checking utilities

// Define permission requirements for each page/section
export const PAGE_PERMISSIONS = {
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
export const ROLE_LEVELS = {
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
export const hasRequiredLevel = (userRole, requiredLevel) => {
  const userLevel = ROLE_LEVELS[userRole] || 999;
  return userLevel <= requiredLevel;
};

/**
 * Check if user can access a page
 */
export const canAccessPage = (pageName, userRole, userPermissions = []) => {
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
export const canInviteRole = (inviterRole, inviteeRole) => {
  const inviterLevel = ROLE_LEVELS[inviterRole] || 999;
  const inviteeLevel = ROLE_LEVELS[inviteeRole] || 999;
  
  // Can only invite lower or equal level roles
  return inviterLevel <= inviteeLevel;
};

/**
 * Get roles that a user can invite
 */
export const getInvitableRoles = (inviterRole) => {
  const inviterLevel = ROLE_LEVELS[inviterRole] || 999;
  return Object.keys(ROLE_LEVELS).filter(role => ROLE_LEVELS[role] >= inviterLevel);
};

/**
 * Check if user can delete an invitation
 */
export const canDeleteInvitation = (userRole, inviterRole, invitedBy) => {
  const userLevel = ROLE_LEVELS[userRole] || 999;
  const inviterLevel = ROLE_LEVELS[inviterRole] || 999;
  
  // Can delete if: 1) You are the inviter, OR 2) You have higher role level
  return invitedBy === 'self' || userLevel < inviterLevel;
};

/**
 * Format permission for display
 */
export const formatPermission = (permission) => {
  return `${permission.resource_type}.${permission.action}.${permission.scope}`;
};
