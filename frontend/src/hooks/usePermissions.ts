import { useAuth } from '../contexts/AuthContext';
import { ROLE_LEVELS } from '../utils/permissions';

// Types
interface PageConfig {
  minLevel?: number;
  permissions?: string[];
}

interface UsePermissionsReturn {
  hasPermission: (resource: string, action: string, scope: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  hasRoleLevel: (requiredLevel: number) => boolean;
  canAccessPage: (pageName: string, config?: PageConfig) => boolean;
  canPerformAction: (resource: string, action: string, scope?: string) => boolean;
  getRoleLevel: () => number;
  isAdmin: () => boolean;
  isDeveloper: () => boolean;
  isMaster: () => boolean;
  isDeveloperOrMaster: () => boolean;
  userPermissions: any[];
  userRole: any;
}

/**
 * Hook to check permissions throughout the app
 */
export const usePermissions = (): UsePermissionsReturn => {
  const { user, userPermissions, userRole } = useAuth();

  /**
   * Check if user has a specific permission
   */
  const hasPermission = (resource: string, action: string, scope: string): boolean => {
    // Developer and Master have all permissions (bypass for convenience)
    if (user?.role === 'developer' || user?.role === 'master') {
      return true;
    }
    
    // Check in user's permissions from database
    return userPermissions.some(
      perm =>
        perm.resource_type === resource &&
        perm.action === action &&
        perm.scope === scope
    );
  };

  /**
   * Check if user has ANY of the specified permissions
   */
  const hasAnyPermission = (permissions: string[]): boolean => {
    // Developer and Master have all permissions (bypass for convenience)
    if (user?.role === 'developer' || user?.role === 'master') {
      return true;
    }
    
    return permissions.some(perm => {
      const [resource, action, scope] = perm.split('.');
      return hasPermission(resource, action, scope);
    });
  };

  /**
   * Check if user has ALL of the specified permissions
   */
  const hasAllPermissions = (permissions: string[]): boolean => {
    // Developer and Master have all permissions (bypass for convenience)
    if (user?.role === 'developer' || user?.role === 'master') {
      return true;
    }
    
    return permissions.every(perm => {
      const [resource, action, scope] = perm.split('.');
      return hasPermission(resource, action, scope);
    });
  };

  /**
   * Check if user's role level is sufficient
   */
  const hasRoleLevel = (requiredLevel: number): boolean => {
    const userLevel = (ROLE_LEVELS as any)[user?.role || ''] || 999;
    return userLevel <= requiredLevel;
  };

  /**
   * Check if user can access a page
   */
  const canAccessPage = (_pageName: string, config: PageConfig = {}): boolean => {
    // Developer and Master can access everything
    if (user?.role === 'developer' || user?.role === 'master') {
      return true;
    }

    // Check role level if specified
    if (config.minLevel && !hasRoleLevel(config.minLevel)) {
      return false;
    }

    // Check permissions if specified
    if (config.permissions && config.permissions.length > 0) {
      return hasAnyPermission(config.permissions);
    }

    return true;
  };

  /**
   * Check if user can perform an action (like create, edit, delete)
   */
  const canPerformAction = (resource: string, action: string, scope: string = 'own'): boolean => {
    return hasPermission(resource, action, scope);
  };

  /**
   * Get user's role level
   */
  const getRoleLevel = (): number => {
    return (ROLE_LEVELS as any)[user?.role || ''] || 999;
  };

  /**
   * Check if user is high-level admin (Developer, Master, Admin)
   */
  const isAdmin = (): boolean => {
    return ['developer', 'master', 'admin'].includes(user?.role || '');
  };

  /**
   * Check if user is Developer (highest level)
   */
  const isDeveloper = (): boolean => {
    return user?.role === 'developer';
  };

  /**
   * Check if user is Master (level 2)
   */
  const isMaster = (): boolean => {
    return user?.role === 'master';
  };

  /**
   * Check if user is Developer OR Master (for API settings access)
   */
  const isDeveloperOrMaster = (): boolean => {
    return ['developer', 'master'].includes(user?.role || '');
  };

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRoleLevel,
    canAccessPage,
    canPerformAction,
    getRoleLevel,
    isAdmin,
    isDeveloper,
    isMaster,
    isDeveloperOrMaster,
    userPermissions,
    userRole,
  };
};
