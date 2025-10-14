/**
 * Legacy route support
 * Add entries here when routes change
 * Never remove old routes - redirect them
 */
export const REDIRECTS = [
  {
    from: '/dashboard-home',
    to: '/dashboard',
    type: 301,
    comment: 'Legacy dashboard route'
  },
  {
    from: '/team',
    to: '/users',
    type: 301,
    comment: 'Renamed team → users'
  },
  // Add more redirects as routes evolve
];

/**
 * Handle legacy route redirects
 * Returns new path if redirect exists, null otherwise
 */
export function handleLegacyRoutes(path) {
  for (const redirect of REDIRECTS) {
    // Simple match
    if (redirect.from === path) {
      return redirect.to;
    }
    
    // Pattern match (e.g., /item/:id)
    if (redirect.from.includes(':')) {
      const pattern = redirect.from.replace(/:[^/]+/g, '([^/]+)');
      const regex = new RegExp(`^${pattern}$`);
      const match = path.match(regex);
      
      if (match) {
        let newPath = redirect.to;
        match.slice(1).forEach((value) => {
          newPath = newPath.replace(/:[^/]+/, value);
        });
        return newPath;
      }
    }
  }
  
  return null;
}

export default REDIRECTS;