# TypeScript Migration Guide

Guide for incrementally migrating the v2.0 Operational Management Platform from JavaScript to TypeScript.

## Overview

**Current Status:** Foundation Complete (20%)
- ✅ TypeScript installed and configured
- ✅ `tsconfig.json` created with strict settings
- ✅ Comprehensive type definitions in `/src/types/index.ts`
- 🔄 Component migration in progress

**Migration Strategy:** Incremental, bottom-up approach
- Start with type definitions
- Migrate design system components
- Migrate contexts and hooks
- Migrate pages
- Convert utilities

## Table of Contents

1. [Setup Complete](#setup-complete)
2. [Type Definitions](#type-definitions)
3. [Migration Order](#migration-order)
4. [Component Migration](#component-migration)
5. [Best Practices](#best-practices)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Setup Complete

### Installed Dependencies

```json
{
  "typescript": "^5.3.3",
  "@types/react": "^18.2.45",
  "@types/react-dom": "^18.2.18",
  "@types/node": "^20.10.5"
}
```

### TypeScript Configuration

`tsconfig.json` is configured with:
- Strict mode enabled
- Path aliases (`@/*`)
- Incremental compilation
- ES2020 target
- JSX: react-jsx

---

## Type Definitions

All type definitions are in `/src/types/index.ts`:

### Available Types

- **User Types**: `User`, `UserRole`, `UserStatus`, `UserProfile`
- **Task Types**: `Task`, `TaskStatus`, `TaskPriority`, `TaskStats`
- **Inspection Types**: `Inspection`, `InspectionTemplate`, `InspectionStats`
- **Checklist Types**: `ChecklistExecution`, `ChecklistTemplate`, `ChecklistStats`
- **Organization Types**: `OrganizationUnit`, `Organization`
- **Workflow Types**: `WorkflowTemplate`, `WorkflowInstance`
- **Component Props**: `ButtonProps`, `CardProps`, `FABProps`, `BottomSheetProps`
- **API Types**: `ApiResponse`, `PaginatedResponse`, `ApiError`
- **Context Types**: `AuthContextType`, `ThemeContextType`

### Usage

```typescript
import type { User, Task, ButtonProps } from '@/types';

const user: User = {
  id: '1',
  email: 'user@example.com',
  name: 'John Doe',
  role: 'admin',
  status: 'active',
  created_at: new Date().toISOString(),
};
```

---

## Migration Order

### Phase 1: Foundation ✅ (COMPLETE)
- Install TypeScript
- Create `tsconfig.json`
- Define all types

### Phase 2: Design System Components (2-3 hours)
Priority order:
1. `Button.jsx` → `Button.tsx`
2. `Card.jsx` → `Card.tsx`
3. `GlassCard.jsx` → `GlassCard.tsx`
4. `Input.jsx` → `Input.tsx`
5. `BottomSheet.jsx` → `BottomSheet.tsx`
6. `FAB.jsx` → `FAB.tsx`
7. `ModernTable.jsx` → `ModernTable.tsx`
8. `Spinner.jsx` → `Spinner.tsx`
9. `Toast.jsx` → `Toast.tsx`
10. `Skeleton.jsx` → `Skeleton.tsx`
11. `EmptyState.jsx` → `EmptyState.tsx`
12. `ModernPageWrapper.jsx` → `ModernPageWrapper.tsx`

### Phase 3: Navigation Components (1 hour)
- `BottomNav.jsx` → `BottomNav.tsx`
- `NavRail.jsx` → `NavRail.tsx`
- `AdaptiveNav.jsx` → `AdaptiveNav.tsx`

### Phase 4: Contexts (1 hour)
- `AuthContext.jsx` → `AuthContext.tsx`
- `ThemeContext.jsx` → `ThemeContext.tsx`

### Phase 5: Hooks (30 min)
- `usePermissions.js` → `usePermissions.ts`
- `useBottomSheet.js` → `useBottomSheet.ts`

### Phase 6: Utilities (30 min)
- `permissions.js` → `permissions.ts`

### Phase 7: Key Pages (3-4 hours)
- `LoginPageNew.jsx` → `LoginPageNew.tsx`
- `DashboardHomeNew.jsx` → `DashboardHomeNew.tsx`
- `TasksPageNew.jsx` → `TasksPageNew.tsx`
- `UserManagementPageNew.jsx` → `UserManagementPageNew.tsx`
- `InspectionsPageNew.jsx` → `InspectionsPageNew.tsx`

### Phase 8: Core App Files (30 min)
- `App.js` → `App.tsx`
- `index.js` → `index.tsx`

### Phase 9: Storybook Stories (1 hour)
- Update all `.stories.jsx` → `.stories.tsx`

---

## Component Migration

### Step-by-Step Process

#### 1. Rename File
```bash
mv Button.jsx Button.tsx
```

#### 2. Add Type Imports
```typescript
import React from 'react';
import type { ButtonProps } from '@/types';
```

#### 3. Type Component Props
```typescript
// Before (JSX)
const Button = ({ variant = 'primary', size = 'md', children, ...props }) => {
  // ...
};

// After (TSX)
const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  size = 'md', 
  children,
  ...props 
}) => {
  // ...
};
```

#### 4. Type State and Refs
```typescript
// State
const [isOpen, setIsOpen] = React.useState<boolean>(false);
const [data, setData] = React.useState<User[]>([]);

// Refs
const inputRef = React.useRef<HTMLInputElement>(null);
```

#### 5. Type Event Handlers
```typescript
const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  // ...
};

const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  // ...
};

const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  // ...
};
```

#### 6. Export with Types
```typescript
export default Button;
export type { ButtonProps };
```

---

## Best Practices

### 1. Use Explicit Types
```typescript
// ❌ Bad - implicit any
const data = await response.json();

// ✅ Good - explicit type
const data: User[] = await response.json();
```

### 2. Avoid `any`
```typescript
// ❌ Bad
const processData = (data: any) => { /* ... */ };

// ✅ Good
const processData = (data: User[]) => { /* ... */ };

// ✅ Also Good - use unknown if type is truly unknown
const processData = (data: unknown) => { /* ... */ };
```

### 3. Use Type Guards
```typescript
const isUser = (obj: any): obj is User => {
  return obj && typeof obj.id === 'string' && typeof obj.email === 'string';
};

if (isUser(data)) {
  // TypeScript knows data is User here
  console.log(data.email);
}
```

### 4. Use Optional Chaining
```typescript
// ❌ Bad
const email = user && user.profile && user.profile.email;

// ✅ Good
const email = user?.profile?.email;
```

### 5. Use Nullish Coalescing
```typescript
// ❌ Bad
const name = user.name || 'Anonymous';

// ✅ Good
const name = user.name ?? 'Anonymous';
```

---

## Common Patterns

### API Calls
```typescript
const fetchUsers = async (): Promise<User[]> => {
  try {
    const response = await fetch(`${API}/users`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    const data: User[] = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};
```

### Form Handling
```typescript
import type { TaskFormData } from '@/types';

const TaskForm: React.FC<{ onSubmit: (data: TaskFormData) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = React.useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
  });

  const handleChange = (field: keyof TaskFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... */}
    </form>
  );
};
```

### Context with TypeScript
```typescript
import React from 'react';
import type { AuthContextType } from '@/types';

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // ...
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

### Custom Hooks
```typescript
import { useState, useEffect } from 'react';
import type { User } from '@/types';

export const useUser = (userId: string): { user: User | null; loading: boolean; error: Error | null } => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const data: User = await response.json();
        setUser(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  return { user, loading, error };
};
```

---

## Troubleshooting

### Common Errors and Solutions

#### Error: "Cannot find module '@/types'"
**Solution:** Check `tsconfig.json` has correct path mapping:
```json
{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

#### Error: "Type 'X' is not assignable to type 'Y'"
**Solution:** Check type definitions match. Use type assertions if needed:
```typescript
const data = response.data as User[];
```

#### Error: "Property 'X' does not exist on type 'Y'"
**Solution:** Add property to type definition or use optional chaining:
```typescript
user?.propertyThatMightNotExist
```

#### Error: "Parameter 'event' implicitly has an 'any' type"
**Solution:** Add explicit type for event handlers:
```typescript
const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  // ...
};
```

---

## Progress Tracking

### Completed ✅
- TypeScript setup
- Type definitions
- tsconfig.json

### In Progress 🔄
- Design system components
- Contexts
- Hooks

### Pending 📋
- Pages migration
- Utilities migration
- Storybook stories update

---

## Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch"
  }
}
```

Run type checking:
```bash
yarn type-check
```

---

## Benefits After Migration

1. **Type Safety**: Catch errors at compile time
2. **Better IDE Support**: Autocomplete and inline documentation
3. **Refactoring Confidence**: Know what breaks when you change code
4. **Self-Documenting**: Types serve as inline documentation
5. **Fewer Bugs**: Eliminate entire classes of runtime errors

---

## Next Steps

1. Migrate design system components (2-3 hours)
2. Migrate contexts and hooks (1.5 hours)
3. Migrate key pages (3-4 hours)
4. Update Storybook stories (1 hour)
5. Run full type check: `yarn type-check`
6. Test thoroughly

**Estimated Remaining Time:** 7-9 hours

---

For questions or issues, refer to:
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
