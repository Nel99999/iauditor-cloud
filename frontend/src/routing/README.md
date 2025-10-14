# Routing System Documentation

## Overview

Our routing system ensures **link stability** and **backwards compatibility** through:

1. **Route Contracts** (`routes.config.js`)
2. **Legacy Redirects** (`redirects.json`)
3. **Route Middleware** (automatic redirect handling)

## Route Contracts

### Purpose
- Single source of truth for all routes
- Type-safe route building
- Prevents hardcoded URLs

### Usage

```javascript
import ROUTES from '@/routing/routes.config';
import { useNavigate } from 'react-router-dom';

function MyComponent() {
  const navigate = useNavigate();
  
  // ✅ Good: Use route constants
  return <Link to={ROUTES.DASHBOARD}>Dashboard</Link>;
  
  // ✅ Good: Dynamic routes
  navigate(ROUTES.INSPECTION_EXECUTION('123'));
  
  // ❌ Bad: Hardcoded routes
  navigate('/dashboard'); // DON'T DO THIS
}
```

## Legacy Redirects

### When to Add
- Route path changes
- Feature renamed
- URL structure refactored

### Example

```javascript
// redirects.js
{
  from: '/old-path',
  to: '/new-path',
  type: 301, // Permanent redirect
  comment: 'Renamed feature'
}
```

### Pattern Redirects

```javascript
{
  from: '/items/:id',
  to: '/tasks/:id',
  type: 302,
  comment: 'Items renamed to tasks'
}
```

## Route Middleware

### Setup

Wrap your app with `RouteMiddleware`:

```javascript
// App.js
import RouteMiddleware from '@/routing/RouteMiddleware';

function App() {
  return (
    <BrowserRouter>
      <RouteMiddleware>
        <Routes>
          {/* Your routes */}
        </Routes>
      </RouteMiddleware>
    </BrowserRouter>
  );
}
```

### How It Works
1. Middleware checks current path
2. If legacy route found, redirects automatically
3. Uses `replace: true` to avoid history pollution

## Benefits

✅ **Links Never Break** - Old URLs redirect to new ones
✅ **Bookmarks Work** - Users' saved links continue working
✅ **SEO Friendly** - Proper 301/302 redirects
✅ **Type Safe** - Route constants catch typos at compile time
✅ **Easy Refactoring** - Change route structure confidently
✅ **Backwards Compatible** - External links keep working

## Best Practices

### DO
- ✅ Always use `ROUTES` constants
- ✅ Add redirects when changing routes
- ✅ Document redirect reasons
- ✅ Test redirects after adding

### DON'T
- ❌ Hardcode route paths
- ❌ Delete old routes without redirects
- ❌ Remove redirects (they're permanent)
- ❌ Skip testing redirects

## Testing Redirects

```javascript
import { handleLegacyRoutes } from '@/routing/redirects';

// Test redirect
const newPath = handleLegacyRoutes('/old-path');
console.log(newPath); // '/new-path'
```

## Migration Guide

### Step 1: Import Route Constants
```javascript
import ROUTES from '@/routing/routes.config';
```

### Step 2: Replace Hardcoded Paths
```javascript
// Before
<Link to="/dashboard">Dashboard</Link>

// After
<Link to={ROUTES.DASHBOARD}>Dashboard</Link>
```

### Step 3: Add Redirects for Changed Routes
```javascript
// If you change /dashboard to /home
// Add to redirects.js:
{
  from: '/dashboard',
  to: '/home',
  type: 301
}
```

## Summary

This routing system ensures your application's URLs remain stable forever, even as your codebase evolves. Users' bookmarks, external links, and search engine results will always work.
