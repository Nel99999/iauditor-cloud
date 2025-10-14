/**
 * ROUTE CONTRACTS - DO NOT MODIFY EXISTING ROUTES
 * Add new routes only. Use redirects.json for legacy support.
 */

export const ROUTES = {
  // Primary routes
  HOME: '/',
  DASHBOARD: '/dashboard',
  
  // Organization
  ORGANIZATION: '/organization',
  USERS: '/users',
  ROLES: '/roles',
  INVITATIONS: '/invitations',
  GROUPS: '/groups',
  
  // Workflows
  WORKFLOWS: '/workflows',
  APPROVALS: '/approvals',
  DELEGATIONS: '/delegations',
  AUDIT: '/audit',
  
  // Operations
  INSPECTIONS: '/inspections',
  INSPECTION_TEMPLATES_NEW: '/inspections/templates/new',
  INSPECTION_EXECUTION: (id) => `/inspections/${id}/execute`,
  
  CHECKLISTS: '/checklists',
  CHECKLIST_TEMPLATES_NEW: '/checklists/templates/new',
  CHECKLIST_EXECUTION: (id) => `/checklists/${id}/execute`,
  
  TASKS: '/tasks',
  REPORTS: '/reports',
  
  // Analytics & Insights
  ANALYTICS: '/analytics',
  WEBHOOKS: '/webhooks',
  BULK_IMPORT: '/bulk-import',
  
  // Settings
  SETTINGS: '/settings',
  MFA_SETUP: '/settings/mfa',
  DEVELOPER_ADMIN: '/developer',
  
  // Auth
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  
  // Design System
  DESIGN_SYSTEM: '/design-system',
  
} as const;

/**
 * Type-safe route builder
 * Usage: buildRoute(ROUTES.INSPECTION_EXECUTION, { id: '123' })
 */
export function buildRoute(route, params) {
  if (typeof route === 'function') {
    return route(...Object.values(params || {}));
  }
  return route;
}

/**
 * Check if route exists
 */
export function isValidRoute(path) {
  const routeValues = Object.values(ROUTES);
  return routeValues.some(route => {
    if (typeof route === 'function') {
      // For dynamic routes, check pattern
      return false; // Would need pattern matching
    }
    return route === path;
  });
}

export default ROUTES;