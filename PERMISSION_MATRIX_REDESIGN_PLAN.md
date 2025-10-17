# Permission Matrix Redesign - Comprehensive Plan

**Date:** October 17, 2025  
**Status:** Planning Complete - Awaiting Approval

---

## 🔍 CURRENT STATE ANALYSIS

### **Permissions Summary**
**Total: 26 Permissions**

| Resource Type | Count | Permissions |
|---------------|-------|-------------|
| **Inspection** | 8 | create.own, create.team, read.own, read.team, read.all, update.own, delete.own, approve.team |
| **Task** | 6 | create.own, read.own, read.team, update.own, assign.team, delete.own |
| **User** | 7 | create.organization, read.organization, update.organization, delete.organization, invite.organization, approve.organization, reject.organization |
| **Report** | 3 | read.own, read.all, export.all |
| **API** | 1 | manage.all |
| **Webhook** | 1 | manage.all |

### **Role-Permission Assignments**

| Role | Level | Permissions | Status |
|------|-------|-------------|--------|
| Developer | 1 | 26/26 (100%) | ✅ Full access |
| Master | 2 | 26/26 (100%) | ✅ Full access |
| Admin | 3 | 18/26 (69%) | ✅ Complete |
| Operations Manager | 4 | 6/26 (23%) | ✅ Complete |
| Team Lead | 5 | 9/26 (35%) | ✅ Complete |
| Manager | 6 | 5/26 (19%) | ✅ Complete |
| Supervisor | 7 | 6/26 (23%) | ✅ Complete |
| Inspector | 8 | 5/26 (19%) | ✅ Complete |
| Operator | 9 | 2/26 (8%) | ✅ Complete |
| Viewer | 10 | 3/26 (12%) | ✅ Complete |

---

## ⚠️ MISSING PERMISSIONS IDENTIFIED

Based on your application features, these permissions are **MISSING**:

### **Checklist Management** (0 permissions)
- ❌ checklist.create.own
- ❌ checklist.read.own/team/all
- ❌ checklist.update.own
- ❌ checklist.delete.own
- ❌ checklist.execute.team

### **Organization Structure** (0 permissions)
- ❌ org_unit.create.organization
- ❌ org_unit.read.organization
- ❌ org_unit.update.organization
- ❌ org_unit.delete.organization

### **Role Management** (0 permissions)
- ❌ role.create.organization
- ❌ role.read.organization
- ❌ role.update.organization
- ❌ role.delete.organization

### **Settings & Configuration** (1 permission - API only)
- ✅ api.manage.all (exists)
- ❌ settings.manage.organization
- ❌ settings.read.organization

### **Analytics & Dashboard** (0 permissions)
- ❌ dashboard.read.organization
- ❌ analytics.read.own/team/all

### **Groups & Teams** (0 permissions)
- ❌ group.create.organization
- ❌ group.read.organization
- ❌ group.update.organization
- ❌ group.delete.organization

**Total Missing: ~25 permissions across 6 resource types**

---

## 📋 PROPOSED COMPLETE PERMISSION SET

### **Recommended Additions:**

**1. Checklist (6 permissions)**
```
checklist.create.own         - Create own checklists
checklist.read.own           - View own checklists
checklist.read.team          - View team checklists
checklist.read.all           - View all checklists
checklist.update.own         - Update own checklists
checklist.execute.team       - Execute team checklists
```

**2. Organization Structure (4 permissions)**
```
org_unit.create.organization - Create organizational units
org_unit.read.organization   - View organizational structure
org_unit.update.organization - Update organizational units
org_unit.delete.organization - Delete organizational units
```

**3. Role Management (4 permissions)**
```
role.create.organization     - Create custom roles
role.read.organization       - View roles
role.update.organization     - Update roles
role.delete.organization     - Delete custom roles
```

**4. Settings (2 permissions)**
```
settings.manage.organization - Manage organization settings
settings.read.organization   - View organization settings
```

**5. Dashboard & Analytics (3 permissions)**
```
dashboard.read.organization  - Access dashboard
analytics.read.organization  - View analytics
analytics.export.all         - Export analytics data
```

**6. Groups (4 permissions)**
```
group.create.organization    - Create groups
group.read.organization      - View groups
group.update.organization    - Update groups
group.delete.organization    - Delete groups
```

**Total Recommended: 26 current + 23 new = 49 permissions**

---

## 🎨 PERMISSION MATRIX UI DESIGN

### **Modern Interactive Matrix**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Permission Matrix                                    [💾 Save Changes]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ [Filter by Resource: All ▼] [Search permissions...]                     │
│                                                                           │
│ ┌───────────────────────────────────────────────────────────────────┐  │
│ │        │ Dev │ Mstr│ Adm │ OpMgr│TmLd │ Mgr │Sup │Insp│Oper│View│  │
│ ├────────┼─────┼─────┼─────┼──────┼─────┼─────┼────┼────┼────┼────┤  │
│ │ INSPECTIONS                                                        │  │
│ │ Create Own     │  ✅  │  ✅  │  ✅  │  ☐   │  ✅  │  ☐  │ ✅ │ ✅ │ ☐ │ ☐ │  │
│ │ Create Team    │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │ ✅ │ ☐ │ ☐ │ ☐ │  │
│ │ Read Own       │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │ ✅ │ ✅ │ ✅ │ ✅ │  │
│ │ Read Team      │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │ ✅ │ ✅ │ ☐ │ ☐ │  │
│ │ Read All       │  ✅  │  ✅  │  ✅  │  ✅  │  ☐  │  ☐  │ ☐ │ ☐ │ ☐ │ ☐ │  │
│ │ Update Own     │  ✅  │  ✅  │  ✅  │  ☐   │  ✅  │  ☐  │ ✅ │ ✅ │ ☐ │ ☐ │  │
│ │ Delete Own     │  ✅  │  ✅  │  ✅  │  ☐   │  ✅  │  ☐  │ ✅ │ ☐ │ ☐ │ ☐ │  │
│ │ Approve Team   │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │ ✅ │ ☐ │ ☐ │ ☐ │  │
│ ├────────────────────────────────────────────────────────────────────┤  │
│ │ TASKS                                                              │  │
│ │ Create Own     │  ✅  │  ✅  │  ✅  │  ☐   │  ✅  │  ✅  │ ✅ │ ✅ │ ☐ │ ☐ │  │
│ │ Read Own       │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │  ✅  │ ✅ │ ✅ │ ✅ │ ✅ │  │
│ │ ...            │  ... │  ... │  ... │  ... │  ... │  ... │... │... │... │... │  │
│ └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│ Legend:                                                                   │
│ ✅ = Enabled (clickable for custom roles)                                │
│ 🔒 = Locked (system roles, Developer-only edit)                         │
│ ☐ = Disabled                                                             │
└───────────────────────────────────────────────────────────────────────────┘
```

### **Key Features:**

**1. Compact Matrix View:**
- Resource groups (collapsible sections)
- Checkboxes for each role-permission combination
- Color-coded cells (green=enabled, gray=disabled)

**2. Access Control:**
- **System Roles (Master, Admin, etc.):**
  - 🔒 Locked by default
  - Only DEVELOPER role can edit
  - Visual lock icon indicator
  
- **Custom Roles:**
  - ✅ Fully editable
  - Click to toggle on/off
  - Changes tracked

**3. Batch Save:**
- Single "Save Changes" button
- Tracks all modifications
- Saves all changes in one operation
- Shows confirmation toast

**4. Smart Features:**
- Filter by resource type
- Search permissions
- Expand/collapse resource sections
- Visual diff highlighting (changed cells)
- Undo/reset button

---

## 🛡️ ACCESS CONTROL RULES

### **Who Can Edit System Roles?**

**ONLY Developer Role:**
```javascript
const canEditSystemRoles = currentUser.role === 'developer';
```

**Master CANNOT Edit System Roles:**
- Master can only edit custom roles
- This prevents Master from elevating their own permissions
- Security best practice

### **Implementation:**

**For System Role Cells:**
```jsx
{role.is_system_role ? (
  currentUser.role === 'developer' ? (
    <Checkbox checked={hasPermission} onChange={handleToggle} />
  ) : (
    <Lock className="h-4 w-4 text-muted-foreground" title="Developer only" />
  )
) : (
  <Checkbox checked={hasPermission} onChange={handleToggle} />
)}
```

---

## 💾 SAVE FUNCTIONALITY

### **Data Structure:**

**Changes Tracked:**
```javascript
{
  "role_id_1": {
    "added": ["permission_id_a", "permission_id_b"],
    "removed": ["permission_id_c"]
  },
  "role_id_2": {
    "added": ["permission_id_d"],
    "removed": []
  }
}
```

**Save Process:**
1. User toggles checkboxes → track changes in state
2. Click "Save Changes" button
3. For each modified role:
   - Call `POST /api/roles/{role_id}/permissions/bulk` with added permissions
   - Call `DELETE /api/roles/{role_id}/permissions/{perm_id}` for removed permissions
4. Show success/error toast
5. Reload matrix to confirm changes

---

## 📱 RESPONSIVE DESIGN

**Desktop (1920px):**
- Full matrix with all roles visible
- Scrollable for many permissions

**Tablet (1024px):**
- Horizontal scroll for role columns
- Sticky first column (permission names)

**Mobile (768px):**
- Switch to accordion view
- One role at a time with toggle switches

---

## 🎯 PROPOSED IMPLEMENTATION PHASES

### **Phase 1: Add Missing Permissions (30 mins)**
1. Create migration script to add 23 missing permissions
2. Assign appropriate permissions to each role
3. Test permission checks in backend

### **Phase 2: Permission Matrix UI (1.5 hours)**
1. Create modern matrix component
2. Implement checkbox grid with color coding
3. Add filter and search functionality
4. Implement access control (Developer-only for system roles)
5. Add visual indicators (locks, colors)

### **Phase 3: Save Functionality (1 hour)**
1. Implement change tracking
2. Batch save API calls
3. Optimistic updates
4. Error handling and rollback
5. Success confirmation

### **Phase 4: Testing & Polish (30 mins)**
1. Test as Developer (can edit all roles)
2. Test as Master (can only edit custom roles)
3. Test as other roles (view only)
4. Verify database saves correctly
5. Test responsive design

**Total Time: 3.5 hours**

---

## 🎨 MOCKUP: PERMISSION MATRIX

### **Visual Design:**

**Header Section:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🛡️ Permission Matrix              [Filter: All Resources ▼] │
│ Manage role permissions across your organization             │
│                                                               │
│ ⚠️ System roles can only be edited by Developer              │
│ [💾 Save All Changes]  [↺ Reset]  [Changes: 3 pending]      │
└─────────────────────────────────────────────────────────────┘
```

**Matrix Body (Grouped by Resource):**
```
╔═══════════════════════════════════════════════════════════════╗
║ INSPECTIONS (8 permissions)                          [▼ Expand]║
╠═══════════════════════════════════════════════════════════════╣
║ Permission         │ Dev │ Mstr│ Adm │OpMgr│TmLd│ Mgr│ ...   ║
║────────────────────┼─────┼─────┼─────┼─────┼────┼────┼────   ║
║ Create Own         │ 🔒✅│ 🔒✅│ 🔒✅│  ☐  │ ✅ │ ☐  │ ...   ║
║ Create Team        │ 🔒✅│ 🔒✅│ 🔒✅│ ✅  │ ✅ │ ✅ │ ...   ║
║ Read Own           │ 🔒✅│ 🔒✅│ 🔒✅│ ✅  │ ✅ │ ✅ │ ...   ║
║ Read Team          │ 🔒✅│ 🔒✅│ 🔒✅│ ✅  │ ✅ │ ✅ │ ...   ║
║ Read All           │ 🔒✅│ 🔒✅│ 🔒✅│ ✅  │ ☐  │ ☐  │ ...   ║
║ Update Own         │ 🔒✅│ 🔒✅│ 🔒✅│ ☐   │ ✅ │ ☐  │ ...   ║
║ Delete Own         │ 🔒✅│ 🔒✅│ 🔒✅│ ☐   │ ✅ │ ☐  │ ...   ║
║ Approve Team       │ 🔒✅│ 🔒✅│ 🔒✅│ ✅  │ ✅ │ ✅ │ ...   ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║ TASKS (6 permissions)                                [▼ Expand]║
╠═══════════════════════════════════════════════════════════════╣
║ ... (similar layout)                                          ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║ USERS (7 permissions)                                [▼ Expand]║
╠═══════════════════════════════════════════════════════════════╣
║ ... (similar layout)                                          ║
╚═══════════════════════════════════════════════════════════════╝
```

**Color Legend:**
- 🔒 = Locked (Developer-only can edit)
- ✅ = Enabled (green background)
- ☐ = Disabled (gray background)
- 🟡 = Modified (yellow background - pending save)

---

## 🔐 ROLE EDITABILITY MATRIX

| Your Role | Can Edit System Roles? | Can Edit Custom Roles? | Notes |
|-----------|------------------------|------------------------|-------|
| Developer | ✅ YES | ✅ YES | Full control |
| Master | ❌ NO | ✅ YES | Cannot edit system roles (security) |
| Admin | ❌ NO | ❌ NO | View only |
| Others | ❌ NO | ❌ NO | View only |

---

## 💡 PROPOSED USER EXPERIENCE

### **Scenario 1: Developer User**
1. Opens Permission Matrix tab
2. Sees full matrix with all roles and permissions
3. **Can click ANY checkbox** (system or custom roles)
4. Checkboxes change color to yellow (pending save)
5. "Save Changes" button highlights with count
6. Clicks save → all changes applied
7. Success toast: "3 permissions updated for 2 roles"

### **Scenario 2: Master User**
1. Opens Permission Matrix tab
2. Sees full matrix
3. System role cells show **🔒 lock icon** (disabled)
4. Custom role cells are **clickable checkboxes**
5. Can only modify custom roles
6. Saves changes → only custom role updates applied

### **Scenario 3: Admin/Other User**
1. Opens Permission Matrix tab
2. Sees full matrix in **read-only mode**
3. All checkboxes disabled
4. No save button visible
5. Can view but not modify

---

## 🚀 IMPLEMENTATION PLAN

### **STEP 1: Add Missing Permissions (HIGH PRIORITY)**
**Estimated Time:** 30 minutes

**Action:**
- Create migration script to add 23 missing permissions
- Group by resource type
- Assign to appropriate roles based on hierarchy

**Deliverable:**
- All 49 permissions in database
- Proper role assignments

---

### **STEP 2: Build Permission Matrix Component**
**Estimated Time:** 1.5 hours

**Components to Build:**
1. **PermissionMatrixView.tsx**
   - Main matrix container
   - Resource grouping (collapsible sections)
   - Role columns (10 system + N custom)
   - Permission rows

2. **PermissionCell.tsx**
   - Checkbox component
   - Lock icon for system roles (non-Developer)
   - Color states (enabled/disabled/modified)
   - Click handlers

3. **MatrixHeader.tsx**
   - Filter dropdown
   - Search input
   - Save/Reset buttons
   - Change counter

**Features:**
- Responsive grid layout
- Sticky headers (role names stay visible)
- Collapsible resource sections
- Visual feedback on changes
- Keyboard navigation support

---

### **STEP 3: Implement Save Logic**
**Estimated Time:** 1 hour

**Functionality:**
1. **Change Tracking:**
   ```javascript
   const [changes, setChanges] = useState({});
   // Format: { role_id: { added: [perm_ids], removed: [perm_ids] } }
   ```

2. **Toggle Handler:**
   ```javascript
   const handleTogglePermission = (roleId, permId, currentState) => {
     // Track addition or removal
     // Update UI optimistically
     // Mark cell as modified
   }
   ```

3. **Batch Save:**
   ```javascript
   const handleSaveAll = async () => {
     for (const [roleId, change] of Object.entries(changes)) {
       // Add permissions
       if (change.added.length > 0) {
         await axios.post(`/api/roles/${roleId}/permissions/bulk`, change.added);
       }
       // Remove permissions
       for (const permId of change.removed) {
         await axios.delete(`/api/roles/${roleId}/permissions/${permId}`);
       }
     }
     // Show success, reload matrix
   }
   ```

---

### **STEP 4: Access Control Implementation**
**Estimated Time:** 30 minutes

**Rules:**
1. Get current user role from context
2. If role === 'developer':
   - All cells clickable
3. If role === 'master':
   - System role cells locked
   - Custom role cells clickable
4. Else:
   - All cells read-only
   - Save button hidden

---

### **STEP 5: Testing & Refinement**
**Estimated Time:** 30 minutes

**Test Cases:**
1. Load matrix as Developer → can edit all
2. Load matrix as Master → can edit custom only
3. Toggle permission → cell changes color
4. Save changes → database updated
5. Reload page → changes persisted
6. Create custom role → appears in matrix
7. Delete custom role → removed from matrix

---

## 📊 RECOMMENDED PERMISSION HIERARCHY

**Full Access (Developer, Master):**
- All 49 permissions

**High Level (Admin):**
- All read permissions
- Most create/update permissions
- Limited delete permissions
- No API/settings management

**Mid Level (Operations Manager, Team Lead, Manager):**
- Read team/organization scope
- Create/update own scope
- Limited delete
- Team-level approval

**Low Level (Supervisor, Inspector):**
- Read own/team
- Create/update own
- Execute assigned tasks

**Minimal (Operator, Viewer):**
- Read own
- Basic execution rights

---

## ⚙️ TECHNICAL REQUIREMENTS

### **Backend APIs Needed:**
- ✅ GET `/api/permissions` (exists)
- ✅ GET `/api/roles` (exists)
- ✅ GET `/api/roles/{id}/permissions` (exists)
- ✅ POST `/api/roles/{id}/permissions/bulk` (need to verify)
- ✅ DELETE `/api/roles/{id}/permissions/{perm_id}` (exists)

### **Frontend State Management:**
```typescript
interface MatrixState {
  roles: Role[];
  permissions: Permission[];
  assignments: { [roleId: string]: string[] }; // permission IDs
  changes: { [roleId: string]: { added: string[], removed: string[] } };
  loading: boolean;
  saving: boolean;
}
```

---

## 🎯 SUCCESS CRITERIA

**Functionality:**
- [ ] All 49 permissions visible and organized
- [ ] Matrix displays all roles and permissions
- [ ] Checkboxes toggle correctly
- [ ] Developer can edit all roles
- [ ] Master can only edit custom roles
- [ ] Other roles are read-only
- [ ] Save button applies all changes
- [ ] Database persists changes
- [ ] Changes reload correctly

**Design:**
- [ ] Compact and fits in viewport
- [ ] Professional appearance
- [ ] Clear visual hierarchy
- [ ] Responsive on all devices
- [ ] Intuitive to use

---

## 📋 DELIVERABLES

1. **Migration Script:** Add 23 missing permissions
2. **PermissionMatrix Component:** Modern interactive matrix
3. **Access Control:** Role-based editing
4. **Save Functionality:** Batch update with validation
5. **Documentation:** User guide for permission management

---

## ⏱️ ESTIMATED TIMELINE

- **Phase 1:** Add Missing Permissions - 30 mins
- **Phase 2:** Build Matrix UI - 1.5 hours
- **Phase 3:** Save Logic - 1 hour
- **Phase 4:** Access Control - 30 mins
- **Phase 5:** Testing - 30 mins

**Total: 3.5 hours**

---

## ❓ QUESTIONS FOR APPROVAL

1. **Missing Permissions:** Should I add all 23 recommended permissions, or only specific ones?

2. **Design Preference:** Do you like the card-based matrix with collapsible sections?

3. **Save Behavior:** Single "Save All" button or auto-save on each change?

4. **Custom Roles:** Should Master users be able to edit system roles, or only Developer?

---

**Please review and approve this plan, and I'll proceed with full implementation!** 🚀
