# 📋 ORGANIZATIONAL STRUCTURE GUIDE - v2.0 Operational Management Platform

## 🎯 Overview

The platform uses a **5-level hierarchical structure** to organize your entire business operations. This allows you to manage operations from the highest level (Profile) down to individual brands.

---

## 🏢 Hierarchy Levels Explained

```
Level 1: PROFILE (Top Level)
    └── Level 2: ORGANISATION
            └── Level 3: COMPANY
                    └── Level 4: BRANCH
                            └── Level 5: BRAND (Bottom Level)
```

### **Level 1: PROFILE** (Root Level)
- **Purpose**: The top-most container representing your entire business entity or portfolio
- **Example**: "Blue Dawn Capital Holdings"
- **Use Case**: If you manage multiple organizations or have a holding company structure
- **Users**: Executive leadership, C-level executives
- **Permissions**: Can see all data across all organizations

### **Level 2: ORGANISATION**
- **Purpose**: Individual organizations or business divisions under the profile
- **Example**: "Blue Dawn Real Estate", "Blue Dawn Investments"
- **Use Case**: Separate legal entities or major business divisions
- **Users**: Organization directors, VPs
- **Permissions**: Can see all data within their organization

### **Level 3: COMPANY**
- **Purpose**: Individual companies or operational units within an organization
- **Example**: "Property Management Services", "Development Projects"
- **Use Case**: Distinct operational units with their own P&L
- **Users**: General managers, department heads
- **Permissions**: Can see all data within their company

### **Level 4: BRANCH**
- **Purpose**: Physical locations or regional branches
- **Example**: "Johannesburg Branch", "Cape Town Office"
- **Use Case**: Geographic locations or regional operations
- **Users**: Branch managers, regional supervisors
- **Permissions**: Can see all data within their branch

### **Level 5: BRAND**
- **Purpose**: Specific brands, products, or teams within a branch
- **Example**: "Premium Property Brand", "Budget Rentals", "Maintenance Team"
- **Use Case**: Final operational level where day-to-day work happens
- **Users**: Team leaders, inspectors, front-line staff
- **Permissions**: Can see only their brand's data

---

## 👥 How Users Connect to the Structure

### **User Assignment Model**

Each user can be assigned to **ONE primary organizational unit** at any level. However, they can **view and access data hierarchically**:

1. **Hierarchical Access Rule**: 
   - Users assigned at a **higher level** can see ALL data from lower levels
   - Users assigned at a **lower level** can ONLY see their level and below

2. **Example Scenarios**:

   **Scenario A: Executive at Profile Level**
   ```
   User: John (CEO)
   Assigned to: Blue Dawn Capital Holdings (Level 1 - Profile)
   Can access: ALL organizations, companies, branches, and brands
   ```

   **Scenario B: Manager at Company Level**
   ```
   User: Sarah (GM)
   Assigned to: Property Management Services (Level 3 - Company)
   Can access: 
     ✅ Property Management Services (her company)
     ✅ All branches under this company
     ✅ All brands under those branches
     ❌ Other companies in the organization
   ```

   **Scenario C: Team Member at Brand Level**
   ```
   User: Mike (Inspector)
   Assigned to: Maintenance Team (Level 5 - Brand)
   Can access: 
     ✅ Only Maintenance Team data
     ❌ Other brands
     ❌ Other branches
   ```

### **Assigning Users to Organizational Units**

**Method 1: During User Invitation**
1. Go to "User Management" page
2. Click "Invite User"
3. Enter email and select role
4. The system automatically assigns them to your current organizational unit
5. You can change their assignment later

**Method 2: Manual Assignment**
1. Go to "Organization Structure" page
2. Navigate to the organizational unit (Profile/Organisation/Company/Branch/Brand)
3. Click the "Users" icon (👥) on the unit
4. Click "Invite User to This Unit"
5. Enter email, role, and they'll be assigned to that specific unit

**Method 3: Bulk Assignment (Future Feature)**
- CSV import for multiple user assignments
- Coming in Phase 2

---

## 🔐 Role-Based Permissions

Users have **TWO properties**:
1. **Role**: Defines what actions they can perform
2. **Organizational Unit Assignment**: Defines what data they can see

### **Roles Explained**

| Role | Permissions |
|------|-------------|
| **Admin** | Full access: Create/edit/delete everything, manage users, change settings |
| **Manager** | Can create inspections, checklists, tasks; assign to team; view reports |
| **Inspector** | Can execute inspections and checklists; update tasks; view own data |
| **Viewer** | Read-only access to data within their organizational scope |

### **Combined Access Example**

```
User: Lisa
Role: Manager
Assigned to: Johannesburg Branch (Level 4)

✅ CAN DO:
- Create inspections for Johannesburg Branch
- Assign tasks to all brands under Johannesburg
- View reports for Johannesburg and its brands
- Execute checklists within her branch

❌ CANNOT DO:
- See data from Cape Town Branch
- Manage users (not admin)
- Access other branches' data
```

---

## 📊 Database Structure (Backend)

### **Collections Schema**

**1. `org_units` Collection**
```json
{
  "id": "uuid",
  "name": "Johannesburg Branch",
  "description": "Main JHB office",
  "level": 4,
  "parent_id": "uuid-of-company",
  "organization_id": "uuid-of-root-org",
  "path": ["profile-id", "org-id", "company-id", "branch-id"],
  "user_count": 15,
  "created_at": "ISO timestamp",
  "created_by": "user-id"
}
```

**2. `users` Collection**
```json
{
  "id": "uuid",
  "name": "Llewellyn Nel",
  "email": "llewellyn@bluedawncapital.co.za",
  "role": "admin",
  "organization_id": "uuid-of-root-org",
  "org_unit_id": "uuid-of-assigned-unit",
  "org_unit_path": ["profile-id", "org-id", "company-id"],
  "created_at": "ISO timestamp"
}
```

**3. Data Filtering Logic**

When a user queries inspections/checklists/tasks:
```javascript
// Backend automatically filters based on user's org_unit_path
query = {
  org_unit_id: { $in: user.accessible_unit_ids }
}
```

---

## 🎨 UI/UX Explanation

### **Organization Structure Page**

**Visual Tree Display**:
```
📁 Blue Dawn Capital Holdings (Profile)
  ├─ 🏢 Blue Dawn Real Estate (Organisation)
  │   ├─ 🏪 Property Management (Company)
  │   │   ├─ 📍 Johannesburg Branch (Branch)
  │   │   │   ├─ 🏷️ Premium Rentals (Brand) [15 users]
  │   │   │   └─ 🏷️ Maintenance Team (Brand) [8 users]
  │   │   └─ 📍 Cape Town Branch (Branch)
  │   └─ 🏪 Development Projects (Company)
  └─ 🏢 Blue Dawn Investments (Organisation)
```

**Interactive Features**:
- **Expand/Collapse**: Click arrow to show/hide children
- **Add Child**: Click "+" to add a unit below current level
- **View Users**: Click 👥 to see users assigned to that unit
- **Edit**: Click ✏️ to rename or update description
- **Delete**: Click 🗑️ to remove (only if no children or users)

---

## 🔧 Common Use Cases

### **Use Case 1: Property Management Company**
```
Level 1: Nel Property Group (Profile)
Level 2: Residential Division (Organisation)
Level 3: Rental Management Co. (Company)
Level 4: Sandton Office (Branch)
Level 5: Luxury Properties Team (Brand)
```

### **Use Case 2: Multi-Brand Retail**
```
Level 1: Retail Holdings (Profile)
Level 2: Fashion Division (Organisation)
Level 3: Clothing Stores (Company)
Level 4: Mall of Africa Store (Branch)
Level 5: Men's Fashion Brand (Brand)
```

### **Use Case 3: Service Provider**
```
Level 1: Service Group (Profile)
Level 2: Cleaning Services (Organisation)
Level 3: Commercial Cleaning (Company)
Level 4: Northern Region (Branch)
Level 5: Office Buildings Team (Brand)
```

---

## 🚀 Creating Your First Structure

### **Step-by-Step Guide**

**Step 1: Create Root Profile**
1. Go to "Organization Structure" page
2. Click "Create Profile" button
3. Enter your business name (e.g., "Nel Property Group")
4. Click "Create Unit"
5. ✅ Your Level 1 (Profile) is created

**Step 2: Add Organisation**
1. Click "+" icon next to your Profile
2. Enter organisation name (e.g., "Residential Division")
3. Click "Create Unit"
4. ✅ Your Level 2 (Organisation) is created

**Step 3: Add Company**
1. Click "+" icon next to your Organisation
2. Enter company name (e.g., "Rental Management")
3. Click "Create Unit"
4. ✅ Your Level 3 (Company) is created

**Step 4: Add Branch**
1. Click "+" icon next to your Company
2. Enter branch name (e.g., "Sandton Office")
3. Click "Create Unit"
4. ✅ Your Level 4 (Branch) is created

**Step 5: Add Brand/Team**
1. Click "+" icon next to your Branch
2. Enter brand/team name (e.g., "Luxury Properties")
3. Click "Create Unit"
4. ✅ Your Level 5 (Brand) is created

**Step 6: Assign Users**
1. Click 👥 icon on any unit
2. Click "Invite User to This Unit"
3. Enter email and role
4. User receives invitation and is assigned to that unit

---

## 🔍 Data Flow Example

### **Inspector Creates an Inspection**

1. **User**: Mike (Inspector) assigned to "Maintenance Team" (Level 5)
2. **Action**: Creates inspection for property check
3. **Database Record**:
```json
{
  "inspection_id": "uuid",
  "created_by": "mike-user-id",
  "org_unit_id": "maintenance-team-id",
  "org_unit_path": ["profile-id", "org-id", "company-id", "branch-id", "brand-id"]
}
```
4. **Who Can See This Inspection?**
   - ✅ Mike (creator - Brand level)
   - ✅ Branch Manager (Branch level - parent)
   - ✅ Company GM (Company level - grandparent)
   - ✅ Organization Director (Organisation level)
   - ✅ CEO (Profile level - top)
   - ❌ Other brands in different branches

---

## 📈 Reporting & Analytics

### **Hierarchical Reporting**

Reports automatically filter based on user's position:

**Example: Completion Rate Report**
- **CEO (Profile level)**: Sees completion rate across ALL units
- **Branch Manager**: Sees completion rate for their branch + all brands
- **Brand Leader**: Sees completion rate only for their brand

**Implementation**:
```javascript
// Frontend calls: GET /api/reports/overview
// Backend automatically filters:
const userUnits = getUserAccessibleUnits(user.org_unit_path);
const data = await db.inspections.aggregate([
  { $match: { org_unit_id: { $in: userUnits } } },
  // ... aggregation pipeline
]);
```

---

## ⚠️ Important Notes

1. **Deleting Units**: Cannot delete if it has children or assigned users
2. **Moving Users**: Edit user's assignment in User Management page
3. **Renaming Levels**: You can customize level names in code if needed
4. **Maximum Levels**: System supports exactly 5 levels (not more, not less)
5. **Root Units**: You can have multiple root units (multiple Profiles)

---

## 🆘 Troubleshooting

### **Issue: Can't see data after creating unit**
- **Solution**: Ensure your user is assigned to that unit or a parent unit

### **Issue: "Create Profile" doesn't work**
- **Solution**: Check browser console for errors, verify backend is running

### **Issue: User can see too much data**
- **Solution**: Check their org_unit assignment - they might be assigned too high in hierarchy

### **Issue: Need more than 5 levels**
- **Solution**: Current system supports 5 levels. Consider combining levels or restructuring.

---

## 📞 Support

For more help, contact: llewellyn@bluedawncapital.co.za

---

**Last Updated**: January 2025  
**Version**: MVP Phase 1
