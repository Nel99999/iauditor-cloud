# QUICK TESTING CHECKLIST
## Visual Guide for Manual Verification

**Use this checklist for quick manual spot-checks during or after automated testing**

---

## 🔐 AUTHENTICATION (4 pages)

### Login Page
- [ ] Page loads without errors
- [ ] Email field accepts input
- [ ] Password field has show/hide eye icon
- [ ] "Forgot password?" link visible
- [ ] "Sign in" button works
- [ ] "Sign up" link works
- [ ] Error message shows for wrong credentials
- [ ] Successful login redirects to dashboard

### Register Page
- [ ] Page loads without errors
- [ ] All fields accept input (name, email, password, confirm password)
- [ ] "Create organization" checkbox toggles org name field
- [ ] Password strength indicator works
- [ ] "Sign up" button works
- [ ] Successful registration redirects to dashboard

### Forgot Password
- [ ] Page loads without errors
- [ ] Email field accepts input
- [ ] "Send reset link" button works
- [ ] Success message appears

### Reset Password
- [ ] Page loads with token in URL
- [ ] New password fields accept input
- [ ] "Reset password" button works
- [ ] Successful reset redirects to login

---

## 📊 DASHBOARD (1 page)

- [ ] Page loads without errors
- [ ] Welcome message shows user name
- [ ] 4 statistics cards display numbers
- [ ] System Overview section shows 4 cards
- [ ] 4 Quick Action buttons navigate correctly

---

## 🏢 ORGANIZATION SECTION (8 pages)

### Organization Structure
- [ ] Page loads without errors
- [ ] "Add Root Unit" button visible
- [ ] Hierarchy tree displays (if units exist)
- [ ] Empty state shows (if no units)

### User Management
- [ ] Page loads without errors
- [ ] Statistics cards show numbers
- [ ] "Invite User" button visible
- [ ] User table displays users
- [ ] Edit button (pencil icon) opens dialog
- [ ] Delete button (trash icon) opens confirmation
- [ ] Search field works

### Roles
- [ ] Page loads without errors
- [ ] "Roles" and "Permission Matrix" tabs visible
- [ ] Roles table shows 10 system roles
- [ ] Developer role color is Indigo (#6366f1)
- [ ] Supervisor role color is Teal (#14b8a6)
- [ ] "Create Custom Role" button visible
- [ ] Permission Matrix tab works

### Groups & Teams
- [ ] Page loads without errors
- [ ] "Create New Group" button visible
- [ ] Groups list displays

### Invitations
- [ ] Page loads without errors
- [ ] "Pending" and "All" tabs visible
- [ ] "Send Invitation" button visible
- [ ] Invitations table displays

### Bulk Import
- [ ] Page loads without errors
- [ ] "Download CSV Template" button visible
- [ ] File upload area visible

### Settings (8 tabs)
**Tab Visibility Check:**
- [ ] Profile tab visible to everyone
- [ ] Appearance tab visible to everyone
- [ ] Regional tab visible to everyone
- [ ] Privacy tab visible to everyone
- [ ] Notifications tab visible to everyone
- [ ] Security tab visible to everyone
- [ ] GDPR & Privacy tab visible to everyone
- [ ] **API Settings tab ONLY visible to Master/Developer** ⚠️
- [ ] Organization tab visible to Admin+

**Profile Tab:**
- [ ] Profile photo displays
- [ ] "Change Photo" button visible
- [ ] Name, phone, bio fields editable
- [ ] "Save Changes" button works

**Appearance Tab:**
- [ ] Theme toggle (Light/Dark) works
- [ ] Accent color selector shows 7 colors
- [ ] View density options (Compact/Comfortable/Spacious) visible
- [ ] Font size options (Small/Medium/Large) visible
- [ ] Changes apply immediately

**API Settings Tab (Master/Developer ONLY):**
- [ ] Tab NOT visible to Admin and below ⚠️
- [ ] Tab visible to Master and Developer
- [ ] SendGrid section displays
  - [ ] API key input field (password type)
  - [ ] "Save API Key" button
  - [ ] "Test Connection" button
  - [ ] Help guide visible
- [ ] Twilio section displays
  - [ ] Account SID input
  - [ ] Auth Token input (password type)
  - [ ] Phone Number input
  - [ ] WhatsApp Number input
  - [ ] "Save Twilio Settings" button
  - [ ] "Test Connection" button
  - [ ] **"Test SMS" section (if configured)**
  - [ ] **"Test WhatsApp" section (if configured)**
  - [ ] Help guide visible

### Developer Admin (Developer ONLY)
- [ ] Page NOT accessible to non-Developer roles
- [ ] Page loads for Developer
- [ ] Tabs visible

---

## 🔄 WORKFLOWS SECTION (5 pages)

### My Approvals
- [ ] Page loads without errors
- [ ] Pending approvals list displays (or empty state)
- [ ] Approval cards show details
- [ ] "Approve" and "Reject" buttons visible

### Workflow Designer
- [ ] Page loads without errors
- [ ] "New Workflow" button visible
- [ ] Workflow templates list displays (or empty state)
- [ ] Click "New Workflow" opens dialog
- [ ] **Dialog opens WITHOUT Select validation errors** ⚠️
- [ ] All dropdown fields populate correctly

### Delegations
- [ ] Page loads without errors
- [ ] "Create Delegation" button visible
- [ ] Delegations list displays (or empty state)

### Audit Trail
- [ ] Page loads without errors
- [ ] Date range filter visible
- [ ] Audit log table displays
- [ ] Search functionality visible

### Analytics
- [ ] Page loads without errors
- [ ] Period selector dropdown visible
- [ ] 4 overview metric cards display
- [ ] 5 charts/sections visible
- [ ] "Refresh" and "Export" buttons visible

---

## 📋 OPERATIONS SECTION (3 active pages)

### Inspections
- [ ] Page loads without errors
- [ ] "Templates" and "Executions" tabs visible
- [ ] Statistics cards display (Pending, Completed, Pass Rate, Avg Score)
- [ ] "New Template" button visible

### Checklists
- [ ] Page loads without errors
- [ ] "Templates" and "Executions" tabs visible
- [ ] Statistics cards display
- [ ] "New Template" button visible

### Tasks
- [ ] Page loads without errors
- [ ] Statistics cards display
- [ ] "New Task" button visible
- [ ] Kanban board shows 3 columns (To Do, In Progress, Done)
- [ ] Task cards visible (if any tasks exist)

---

## 📈 INSIGHTS SECTION (3 pages)

### Reports
- [ ] Page loads without errors
- [ ] 5 tabs visible (Overview, Inspections, Checklists, Tasks, Insights)
- [ ] Date range selector visible
- [ ] "Custom Report" button visible
- [ ] "Export" button visible

### Analytics (duplicate)
- [ ] Same as Workflows → Analytics

### Webhooks
- [ ] Page loads without errors
- [ ] "Create Webhook" button visible
- [ ] Webhooks list displays (or empty state)

---

## 🔝 HEADER COMPONENTS

### Global Search (Cmd+K)
- [ ] Press Cmd+K (Mac) or Ctrl+K (Windows) opens search modal
- [ ] Search input visible and auto-focused
- [ ] Placeholder text displays
- [ ] Type query shows results
- [ ] Results grouped by type
- [ ] ESC key closes modal
- [ ] Click outside closes modal

### Notification Center (Bell Icon)
- [ ] Bell icon visible in header (top right)
- [ ] Click opens dropdown
- [ ] Notifications list displays (or "No notifications")
- [ ] Unread count badge shows (if unread notifications)
- [ ] "Mark all as read" button visible
- [ ] "Clear all" button visible

### User Menu (Avatar)
- [ ] Avatar displays in header (top right)
- [ ] Click opens dropdown menu
- [ ] User name displays
- [ ] User email displays
- [ ] "Profile" option visible
- [ ] "Settings" option visible
- [ ] "Logout" option visible
- [ ] Click "Logout" logs out and redirects to login

---

## 🎨 UI/UX CHECKS

### Theme Switching
- [ ] Light theme works (white background)
- [ ] Dark theme works (dark background)
- [ ] All text readable in both themes
- [ ] Accent colors apply correctly

### Responsive Design
- [ ] Desktop view (1920x1080) looks good
- [ ] Tablet view (768x1024) looks good
- [ ] Mobile view (390x844) looks good
- [ ] Sidebar collapses on mobile
- [ ] Hamburger menu visible on mobile

### Loading States
- [ ] Loading spinners show while fetching data
- [ ] Skeleton loaders (if implemented)
- [ ] No content flashing

### Error Handling
- [ ] 404 page shows for invalid routes
- [ ] Error messages display for API failures
- [ ] Toast notifications appear for actions
- [ ] Error messages are clear and helpful

---

## 🔒 SECURITY CHECKS

### Role-Based Access
- [ ] Developer sees "Developer Admin" menu item
- [ ] Non-Developer does NOT see "Developer Admin"
- [ ] Master/Developer sees "API Settings" tab in Settings
- [ ] Admin does NOT see "API Settings" tab
- [ ] Lower roles do NOT see "API Settings" tab

### Data Isolation
- [ ] Users only see users from their organization
- [ ] Organization data is isolated
- [ ] Cannot access other organization's data

### API Key Security
- [ ] API keys are masked when displayed (SG.xxx...xxx)
- [ ] Auth tokens never displayed
- [ ] Admin role blocked from API Settings (403 error if they try)

---

## ✅ CRITICAL SUCCESS CRITERIA

### Must Work (100% Success Required)
- [ ] Login/logout works
- [ ] User registration works
- [ ] Password reset works
- [ ] Dashboard loads and shows data
- [ ] Navigation menu works (all items clickable)
- [ ] Settings page loads all tabs
- [ ] API Settings tab ONLY for Master/Developer
- [ ] User management CRUD works
- [ ] Cannot delete self
- [ ] Data persists after page refresh

### Should Work (95% Success Target)
- [ ] Workflow Designer opens without errors
- [ ] All settings tabs save correctly
- [ ] Charts/analytics display
- [ ] Task creation and management
- [ ] Inspection/checklist workflows
- [ ] Notification system
- [ ] Search functionality

### Nice to Have (80% Success Target)
- [ ] Mobile responsiveness perfect
- [ ] All animations smooth
- [ ] Empty states look good
- [ ] Help text everywhere
- [ ] Tooltips work

---

## 📝 TESTING NOTES

### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Screen Sizes
- [ ] Desktop: 1920x1080
- [ ] Laptop: 1366x768
- [ ] Tablet: 768x1024
- [ ] Mobile: 390x844

### Network Conditions
- [ ] Fast connection (normal)
- [ ] Slow connection (throttled)
- [ ] Offline (error handling)

---

## 🚨 KNOWN ISSUES TO VERIFY

### Previous Reported Issues
- [ ] Workflow Designer Select dropdowns (were reported as having validation errors)
- [ ] Settings persistence (verify all 8 tabs save correctly)
- [ ] Mobile hamburger menu (verify it exists and works)
- [ ] Task creation dialog (verify inputs work)

---

## QUICK PASS/FAIL SCORING

**Critical Features (Must be 100%):**
- Authentication: ___/10 ✅ or ❌
- API Key Security: ___/5 ✅ or ❌
- User Management: ___/8 ✅ or ❌
- Navigation: ___/24 ✅ or ❌

**High Priority Features (Target 95%):**
- Settings (8 tabs): ___/8
- Workflows: ___/5
- Operations: ___/3
- Dashboard: ___/1

**Medium Priority Features (Target 90%):**
- Analytics: ___/2
- Header Components: ___/3
- UI/UX: ___/5

**Overall Score: ___% (Target: 98%+)**

---

**This checklist is for quick manual spot-checks. For comprehensive testing, refer to COMPREHENSIVE_TESTING_PLAN.md**
