import { useAuth } from '../contexts/AuthContext';
import { ROLE_LEVELS } from '../utils/permissions';

/**
 * Hook to check permissions throughout the app
 */
export const usePermissions = () => {
  const { user, userPermissions, userRole } = useAuth();

  /**
   * Check if user has a specific permission
   */
  const hasPermission = (resource, action, scope) => {
    // Developer and Master have all permissions
    if (user?.role === 'developer' || user?.role === 'master') {
      return true;
    }

    // Check in user's permissions
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
  const hasAnyPermission = (permissions) => {
    // Developer and Master have all permissions
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
  const hasAllPermissions = (permissions) => {
    // Developer and Master have all permissions
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
  const hasRoleLevel = (requiredLevel) => {
    const userLevel = ROLE_LEVELS[user?.role] || 999;
    return userLevel <= requiredLevel;
  };

  /**
   * Check if user can access a page
   */
  const canAccessPage = (pageName, config = {}) => {
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
  const canPerformAction = (resource, action, scope = 'own') => {
    return hasPermission(resource, action, scope);
  };

  /**
   * Get user's role level
   */
  const getRoleLevel = () => {
    return ROLE_LEVELS[user?.role] || 999;
  };

  /**
   * Check if user is high-level admin (Developer, Master, Admin)
   */
  const isAdmin = () => {
    return ['developer', 'master', 'admin'].includes(user?.role);
  };

  /**
   * Check if user is Developer (highest level)
   */
  const isDeveloper = () => {
    return user?.role === 'developer';
  };

  /**
   * Check if user is Master (level 2)
   */
  const isMaster = () => {
    return user?.role === 'master';
  };

  /**
   * Check if user is Developer OR Master (for API settings access)
   */
  const isDeveloperOrMaster = () => {
    return ['developer', 'master'].includes(user?.role);
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
