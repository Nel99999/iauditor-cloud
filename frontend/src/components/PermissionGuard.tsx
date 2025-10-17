import React, { ReactNode } from 'react';
import { usePermissions } from '@/hooks/usePermissions';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Lock } from 'lucide-react';

interface PermissionGuardProps {
  children: ReactNode;
  /** Permission required in format "resource.action.scope" */
  permission?: string;
  /** Multiple permissions (ANY logic - user needs at least one) */
  anyPermissions?: string[];
  /** Multiple permissions (ALL logic - user needs all) */
  allPermissions?: string[];
  /** Required role level (1-10) */
  minLevel?: number;
  /** Specific roles required */
  roles?: string | string[];
  /** Behavior when permission is denied */
  fallback?: 'hide' | 'disable' | 'show';
  /** Custom tooltip message */
  tooltipMessage?: string;
  /** Custom fallback component */
  customFallback?: ReactNode;
}

/**
 * PermissionGuard Component
 * 
 * Wraps elements and controls their visibility/interactivity based on user permissions
 * 
 * Usage examples:
 * 
 * 1. Hide if no permission:
 *    <PermissionGuard permission="user.delete.organization" fallback="hide">
 *      <Button>Delete User</Button>
 *    </PermissionGuard>
 * 
 * 2. Disable and show tooltip:
 *    <PermissionGuard permission="user.update.organization" fallback="disable">
 *      <Button>Edit User</Button>
 *    </PermissionGuard>
 * 
 * 3. Role-based:
 *    <PermissionGuard roles={['developer', 'master']}>
 *      <Button>Advanced Settings</Button>
 *    </PermissionGuard>
 * 
 * 4. Multiple permissions (ANY):
 *    <PermissionGuard anyPermissions={['user.read.organization', 'user.read.own']}>
 *      <UserList />
 *    </PermissionGuard>
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permission,
  anyPermissions,
  allPermissions,
  minLevel,
  roles,
  fallback = 'disable',
  tooltipMessage = 'Insufficient Permissions',
  customFallback,
}) => {
  const {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRoleLevel,
    user,
  } = usePermissions();

  // Check if user meets permission requirements
  const hasAccess = React.useMemo(() => {
    // Check single permission
    if (permission) {
      const [resource, action, scope] = permission.split('.');
      if (!hasPermission(resource, action, scope)) return false;
    }

    // Check any permissions (OR logic)
    if (anyPermissions && anyPermissions.length > 0) {
      if (!hasAnyPermission(anyPermissions)) return false;
    }

    // Check all permissions (AND logic)
    if (allPermissions && allPermissions.length > 0) {
      if (!hasAllPermissions(allPermissions)) return false;
    }

    // Check role level
    if (minLevel !== undefined) {
      if (!hasRoleLevel(minLevel)) return false;
    }

    // Check specific roles
    if (roles) {
      const roleList = Array.isArray(roles) ? roles : [roles];
      if (!roleList.includes(user?.role || '')) return false;
    }

    return true;
  }, [permission, anyPermissions, allPermissions, minLevel, roles, hasPermission, hasAnyPermission, hasAllPermissions, hasRoleLevel, user]);

  // If user has access, render children normally
  if (hasAccess) {
    return <>{children}</>;
  }

  // Handle denied access based on fallback mode
  switch (fallback) {
    case 'hide':
      return null;

    case 'show':
      // Show children but mark as read-only (useful for display purposes)
      return <div className="opacity-60 pointer-events-none">{children}</div>;

    case 'disable':
    default:
      // Disable and show tooltip
      if (customFallback) {
        return <>{customFallback}</>;
      }

      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="inline-flex relative">
                <div className="opacity-50 pointer-events-none select-none grayscale">
                  {children}
                </div>
                <div className="absolute inset-0 cursor-not-allowed" />
              </div>
            </TooltipTrigger>
            <TooltipContent side="top" className="flex items-center gap-2">
              <Lock className="h-3 w-3" />
              <span>{tooltipMessage}</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
  }
};

// Convenience wrapper components
export const HideIfNoPermission: React.FC<Omit<PermissionGuardProps, 'fallback'>> = (props) => (
  <PermissionGuard {...props} fallback="hide" />
);

export const DisableIfNoPermission: React.FC<Omit<PermissionGuardProps, 'fallback'>> = (props) => (
  <PermissionGuard {...props} fallback="disable" />
);

export const ShowButDisableIfNoPermission: React.FC<Omit<PermissionGuardProps, 'fallback'>> = (props) => (
  <PermissionGuard {...props} fallback="show" />
);
