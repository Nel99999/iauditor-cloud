# COMPREHENSIVE APPLICATION TESTING PLAN
## v2.0 Operational Management Platform - Complete System Review

**Version**: 2.0
**Date**: January 13, 2025
**Status**: Pre-Deployment Review
**Target Quality**: 98%+ Success Rate

---

## TABLE OF CONTENTS
1. [Application Overview](#application-overview)
2. [Navigation Structure](#navigation-structure)
3. [Page-by-Page Functionality Matrix](#page-by-page-functionality-matrix)
4. [Integration Testing Matrix](#integration-testing-matrix)
5. [Comprehensive Testing Plan](#comprehensive-testing-plan)
6. [Risk Assessment](#risk-assessment)
7. [Test Execution Strategy](#test-execution-strategy)

---

## APPLICATION OVERVIEW

### Technology Stack
- **Frontend**: React 18+ with Vite, TailwindCSS, shadcn/ui
- **Backend**: FastAPI (Python), Motor (Async MongoDB)
- **Database**: MongoDB
- **Authentication**: JWT tokens
- **State Management**: React Context API

### Application Scope
The v2.0 Operational Management Platform is a comprehensive enterprise system for managing:
- Organizational hierarchies and structures
- User management with 10-level role system
- Workflow approvals and delegations
- Inspections, checklists, and tasks
- Analytics, reporting, and audit trails
- API integrations (SendGrid, Twilio)

---

## NAVIGATION STRUCTURE

### 1. MAIN SECTION
#### Dashboard
- **Path**: `/dashboard`
- **Icon**: LayoutDashboard
- **Status**: Active ✅
- **Badge**: None

### 2. ORGANIZATION SECTION
#### Organization Structure
- **Path**: `/organization`
- **Icon**: Building2
- **Status**: Active ✅
- **Badge**: None
- **Description**: Manage hierarchy

#### User Management
- **Path**: `/users`
- **Icon**: Users
- **Status**: Active ✅
- **Badge**: New
- **Description**: Manage team members

#### Roles
- **Path**: `/roles`
- **Icon**: Shield
- **Status**: Active ✅
- **Badge**: None
- **Description**: 10 system roles

#### Groups & Teams
- **Path**: `/groups`
- **Icon**: Users
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Manage groups

#### Invitations
- **Path**: `/invitations`
- **Icon**: Mail
- **Status**: Active ✅
- **Badge**: None
- **Description**: Track invites

#### Bulk Import
- **Path**: `/bulk-import`
- **Icon**: Upload
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: CSV user import

#### Settings
- **Path**: `/settings`
- **Icon**: Settings
- **Status**: Active ✅
- **Badge**: New
- **Description**: Account & preferences

#### Developer Admin (Developer role only)
- **Path**: `/developer-admin`
- **Icon**: Shield
- **Status**: Active ✅
- **Badge**: DEV
- **Description**: System admin panel

### 3. WORKFLOWS SECTION
#### My Approvals
- **Path**: `/approvals`
- **Icon**: CheckCircle2
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Pending approvals

#### Workflow Designer
- **Path**: `/workflows`
- **Icon**: GitBranch
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Manage workflows

#### Delegations
- **Path**: `/delegations`
- **Icon**: UserCheck
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Authority delegation

#### Audit Trail
- **Path**: `/audit`
- **Icon**: Shield
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Compliance & logs

#### Analytics
- **Path**: `/analytics`
- **Icon**: Activity
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Charts & insights

### 4. OPERATIONS SECTION
#### Inspections
- **Path**: `/inspections`
- **Icon**: ClipboardCheck
- **Status**: Active ✅
- **Badge**: New
- **Description**: Templates & execution

#### Checklists
- **Path**: `/checklists`
- **Icon**: CheckSquare
- **Status**: Active ✅
- **Badge**: New
- **Description**: Daily operations

#### Tasks
- **Path**: `/tasks`
- **Icon**: ListTodo
- **Status**: Active ✅
- **Badge**: ✓
- **Description**: Task management

#### Schedule
- **Path**: `/schedule`
- **Icon**: Calendar
- **Status**: Inactive ⏸️
- **Badge**: Soon
- **Description**: Team scheduling

### 5. INSIGHTS SECTION
#### Reports
- **Path**: `/reports`
- **Icon**: FileText
- **Status**: Active ✅
- **Badge**: ✓
- **Description**: Analytics & reports

#### Analytics (duplicate in Workflows)
- **Path**: `/analytics`
- **Icon**: BarChart3
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Performance metrics

#### Webhooks
- **Path**: `/webhooks`
- **Icon**: Webhook
- **Status**: Active ✅
- **Badge**: NEW
- **Description**: Event notifications

### 6. RESOURCES SECTION
#### Documents
- **Path**: `/documents`
- **Icon**: FolderOpen
- **Status**: Inactive ⏸️
- **Badge**: Soon
- **Description**: Document library

### 7. HEADER COMPONENTS
#### Global Search
- **Trigger**: Cmd+K / Ctrl+K
- **Status**: Active ✅
- **Functionality**: Search across tasks, users, groups, inspections

#### Notification Center
- **Trigger**: Bell icon
- **Status**: Active ✅
- **Functionality**: Real-time notifications with 30s polling

#### User Menu
- **Trigger**: Avatar
- **Status**: Active ✅
- **Options**: Profile, Settings, Logout

---

## PAGE-BY-PAGE FUNCTIONALITY MATRIX

### 1. AUTHENTICATION PAGES

#### Login Page (`/login`)
**Components**:
- Email input
- Password input (with show/hide toggle)
- Remember me checkbox
- Sign in button
- "Forgot password?" link
- "Sign in with Google" button
- "Sign up" link

**Functionality to Test**:
- [ ] Email validation
- [ ] Password visibility toggle
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (error message)
- [ ] "Forgot password" navigation
- [ ] "Sign up" navigation
- [ ] Google sign-in integration
- [ ] Redirect to dashboard after login
- [ ] JWT token storage
- [ ] Remember me persistence

#### Register Page (`/register`)
**Components**:
- Name input
- Email input
- Password input (with strength indicator)
- Confirm password input
- "Create organization" checkbox
- Organization name input (conditional)
- Sign up button
- "Sign in with Google" button
- "Sign in" link

**Functionality to Test**:
- [ ] Name validation
- [ ] Email validation
- [ ] Password strength validation (min 8 chars, uppercase, lowercase, number)
- [ ] Password confirmation match
- [ ] Organization checkbox toggle
- [ ] Organization name field appears/hides
- [ ] Registration with organization creation
- [ ] Registration without organization
- [ ] Auto-login after registration
- [ ] Google sign-up integration
- [ ] "Sign in" navigation
- [ ] Role assignment (master for org creator, user for joiners)

#### Forgot Password Page (`/forgot-password`)
**Components**:
- Email input
- Send reset link button
- Back to login link

**Functionality to Test**:
- [ ] Email validation
- [ ] Send reset email (with valid email)
- [ ] Error handling (email not found)
- [ ] Success message display
- [ ] Back to login navigation

#### Reset Password Page (`/reset-password`)
**Components**:
- New password input
- Confirm password input
- Reset password button

**Functionality to Test**:
- [ ] Token validation from URL
- [ ] New password validation
- [ ] Password confirmation match
- [ ] Password reset success
- [ ] Expired token handling
- [ ] Invalid token handling
- [ ] Redirect to login after success

---

### 2. DASHBOARD PAGE (`/dashboard`)

**Tabs**: None (single page)

**Components**:
- Welcome message with user name
- 4 Statistics cards
  - Total Users (with active count)
  - Active Inspections (with completed today)
  - Pending Tasks (with completed count)
  - Checklists Today (with completed count)
- System Overview section
  - Inspections card (total, pass rate, avg score)
  - Tasks card (by status breakdown)
  - Checklists card (completion rate)
  - Organization card (total units, levels)
- 4 Quick Action cards
  - Start Inspection → `/inspections`
  - Manage Tasks → `/tasks`
  - View Organization → `/organization`
  - View Reports → `/reports`

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Welcome message displays user name correctly
- [ ] Statistics cards show real data from `/api/dashboard/stats`
- [ ] Loading states show while fetching data
- [ ] System Overview cards display correctly
- [ ] All quick action buttons navigate correctly
- [ ] Data updates on page refresh
- [ ] Responsive design (desktop, tablet, mobile)
- [ ] Statistics are accurate (match backend data)
- [ ] Error handling if API fails

---

### 3. ORGANIZATION PAGES

#### Organization Structure Page (`/organization`)
**Tabs**: None

**Components**:
- Page title "Organization Structure"
- 5-level hierarchy explanation
  - Level 1: Company
  - Level 2: Region
  - Level 3: Location
  - Level 4: Department
  - Level 5: Team
- Hierarchy tree display
- Add Root Unit button
- Unit cards with:
  - Unit name
  - Level indicator
  - Parent unit (if applicable)
  - Edit button
  - Delete button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Hierarchy explanation displays correctly
- [ ] Add Root Unit button opens dialog
- [ ] Root unit creation (Level 1)
- [ ] Child unit creation with parent selection
- [ ] Level validation (cannot skip levels)
- [ ] Unit name validation
- [ ] Unit edit functionality
- [ ] Unit delete with children protection
- [ ] Leaf unit deletion (no children)
- [ ] Unit list/tree display
- [ ] Empty state display (no units)
- [ ] Photo upload for units
- [ ] Search/filter units

#### User Management Page (`/users`)
**Tabs**: None

**Components**:
- 4 Statistics cards
  - Total Users
  - Active Users
  - Pending Invites
  - Admin Users
- Invite User button
- Search/filter users
- Users table with:
  - Name, email, role, status
  - Last login timestamp
  - Edit button (pencil icon)
  - Delete button (trash icon)
- Edit User Dialog
  - Name input
  - Email input
  - Role dropdown (10 roles)
  - Save changes button
- Delete User Dialog
  - Confirmation message
  - User details display
  - Cancel button
  - Delete User button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Statistics cards show accurate counts
- [ ] User list loads from `/api/users`
- [ ] Search functionality works
- [ ] Filter by role works
- [ ] Invite User button opens dialog
- [ ] User invitation sends email
- [ ] Edit button opens dialog with user data
- [ ] Edit user name, email, role
- [ ] Role dropdown shows all 10 roles
- [ ] Save changes updates user
- [ ] Delete button opens confirmation dialog
- [ ] Delete user (soft delete)
- [ ] Cannot delete self (error message)
- [ ] Deleted users removed from list
- [ ] Last login displays correctly
- [ ] Photo display for users
- [ ] Pagination for large user lists
- [ ] Organization isolation (only see same org users)

#### Roles Page (`/roles`)
**Tabs**: Roles, Permission Matrix

**Components - Roles Tab**:
- Create Custom Role button
- Roles table with:
  - Role name with color badge
  - Role code
  - Level (1-10)
  - System/Custom badge
  - Permission count
  - Edit button
  - Delete button
- 10 System Roles:
  - Developer (Indigo, Lv1)
  - Master (Purple, Lv2)
  - Admin (Red, Lv3)
  - Operations Manager (Orange, Lv4)
  - Team Lead (Cyan, Lv5)
  - Manager (Blue, Lv6)
  - Supervisor (Teal, Lv7)
  - Inspector (Yellow, Lv8)
  - Operator (Gray, Lv9)
  - Viewer (Green, Lv10)

**Components - Permission Matrix Tab**:
- Role selector dropdown
- Permission categories (23 permissions)
- Bulk assign/remove permissions
- Permission checkboxes

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Roles tab displays all system roles
- [ ] System roles show correct colors (Developer=Indigo, Supervisor=Teal)
- [ ] System roles cannot be deleted
- [ ] Custom role creation
- [ ] Custom role name, code, level, color selection
- [ ] Custom role edit
- [ ] Custom role delete
- [ ] Permission Matrix tab loads
- [ ] Select role to view permissions
- [ ] Bulk permission assignment
- [ ] Permission checkboxes toggle correctly
- [ ] Developer role has ALL 23 permissions
- [ ] Master role permissions
- [ ] Save permission changes
- [ ] Permission count updates in roles tab

#### Groups & Teams Page (`/groups`)
**Tabs**: None

**Components**:
- Create New Group button
- Groups list/table with:
  - Group name
  - Description
  - Member count
  - Parent group (if any)
  - Level indicator
  - Edit button
  - Delete button
- Create Group Dialog
  - Group name input
  - Description textarea
  - Parent group selector
  - Save button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Create New Group button opens dialog
- [ ] Group creation with name and description
- [ ] Hierarchical groups (parent-child)
- [ ] Group list displays correctly
- [ ] Member count accurate
- [ ] Add members to group
- [ ] Remove members from group
- [ ] Edit group details
- [ ] Delete group
- [ ] Cannot delete group with children
- [ ] Search/filter groups
- [ ] Empty state display

#### Invitations Page (`/invitations`)
**Tabs**: Pending Invitations, All Invitations

**Components**:
- Send Invitation button
- Tabs for Pending/All
- Invitations table with:
  - Email
  - Role
  - Sent date
  - Expiration date (7 days)
  - Status (Pending/Accepted/Expired)
  - Days left indicator (red if <2 days)
  - Resend button
  - Cancel/Delete button
- Send Invitation Dialog
  - Email input
  - Role dropdown (10 roles)
  - Send button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Send Invitation button opens dialog
- [ ] Email validation
- [ ] Role selection (all 10 roles)
- [ ] Send invitation (creates invitation + sends email)
- [ ] Pending tab shows only pending invitations
- [ ] All tab shows all invitations
- [ ] Expiration countdown (7 days from sent)
- [ ] Days left indicator (red warning <2 days)
- [ ] Resend invitation (resets 7-day expiry)
- [ ] Cancel invitation
- [ ] Delete invitation
- [ ] Role-based delete permissions
- [ ] Cannot send duplicate invitations (same email)
- [ ] Invitation acceptance flow
- [ ] Expired invitations handling

#### Bulk Import Page (`/bulk-import`)
**Tabs**: None

**Components**:
- Download CSV Template button
- File upload area (drag & drop or click)
- Preview section (after upload)
  - Valid users count
  - Invalid users count
  - Error messages
  - User preview table
- Import button
- Progress indicator

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Download CSV template generates correct file
- [ ] File upload (drag & drop)
- [ ] File upload (click to select)
- [ ] CSV validation
- [ ] Duplicate email detection
- [ ] Invalid data detection
- [ ] Preview display with errors highlighted
- [ ] Import valid users
- [ ] Skip invalid users
- [ ] Progress indicator during import
- [ ] Success/error summary after import
- [ ] Users added to database
- [ ] Auto-assign to groups (if specified)

#### Settings Page (`/settings`)
**Tabs**: 8 tabs - Profile, Appearance, Regional, Privacy, Notifications, Security, GDPR & Privacy, API Settings (Master/Dev only), Organization (Admin+)

**Components - Profile Tab**:
- Profile photo with upload button
- Name input
- Email display (read-only)
- Phone input
- Bio textarea
- Save Changes button

**Components - Appearance Tab**:
- Theme toggle (Light/Dark)
- Accent color selector (7 colors)
- View density (Compact/Comfortable/Spacious)
- Font size (Small/Medium/Large)

**Components - Regional Tab**:
- Language dropdown (5 languages)
- Timezone selector
- Date format dropdown
- Time format (12h/24h)
- Currency dropdown
- Save Regional Settings button

**Components - Privacy Tab**:
- Profile visibility (Public/Organization/Private)
- Show activity status toggle
- Show last seen toggle
- Save Privacy Settings button

**Components - Notifications Tab**:
- Email notifications toggle
- Push notifications toggle
- Weekly reports toggle
- Marketing emails toggle
- Save Notification Preferences button

**Components - Security Tab**:
- Current password input
- New password input
- Confirm password input
- Update Password button
- Two-factor authentication section
- Session timeout selector

**Components - GDPR & Privacy Tab**:
- Data Export section
  - Export My Data button
- Consent Management section
  - Marketing communications toggle
  - Analytics toggle
  - Third-party sharing toggle
- Account Deletion section
  - Delete My Account button

**Components - API Settings Tab** (Master/Developer only):
- SendGrid API Key section
  - API key input (password field)
  - Configured badge
  - Save API Key button
  - Test Connection button
  - How to get SendGrid key guide
- Twilio SMS & WhatsApp section
  - Account SID input
  - Auth Token input (password field)
  - Phone Number input
  - WhatsApp Number input
  - Configured badge
  - Save Twilio Settings button
  - Test Connection button
  - Test SMS section (if configured)
    - Phone number input
    - Send Test SMS button
    - Success/failure result display
  - Test WhatsApp section (if configured)
    - Phone number input
    - Send Test WhatsApp button
    - Success/failure result display
  - How to get Twilio credentials guide

**Components - Organization Tab** (Admin+):
- Organization name
- Organization details
- Organization settings

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] All 8 tabs visible (API Settings only for Master/Dev)
- [ ] Tab navigation works
- [ ] **Profile Tab**:
  - [ ] Photo upload
  - [ ] Update name, phone, bio
  - [ ] Save changes persists data
  - [ ] Profile photo displays in header
- [ ] **Appearance Tab**:
  - [ ] Theme toggle (Light/Dark) changes UI
  - [ ] Accent color selection applies immediately
  - [ ] View density changes (visible differences)
  - [ ] Font size changes (visible differences)
  - [ ] Settings persist after refresh
- [ ] **Regional Tab**:
  - [ ] Language selection changes UI language
  - [ ] Timezone selection
  - [ ] Date format selection
  - [ ] Time format (12h/24h)
  - [ ] Currency selection
  - [ ] Save button persists settings
- [ ] **Privacy Tab**:
  - [ ] Profile visibility options
  - [ ] Activity status toggle
  - [ ] Last seen toggle
  - [ ] Save button persists settings
- [ ] **Notifications Tab**:
  - [ ] All 4 toggles work
  - [ ] Save button persists settings
- [ ] **Security Tab**:
  - [ ] Password change requires current password
  - [ ] New password validation
  - [ ] Password confirmation match
  - [ ] Successful password change
  - [ ] MFA setup link works
- [ ] **GDPR & Privacy Tab**:
  - [ ] Export data button downloads JSON
  - [ ] Consent toggles work
  - [ ] Account deletion warning
- [ ] **API Settings Tab** (Master/Developer only):
  - [ ] Tab NOT visible to Admin and below
  - [ ] Tab visible to Master and Developer
  - [ ] SendGrid API key save
  - [ ] SendGrid test connection
  - [ ] API key masking display
  - [ ] Twilio credentials save
  - [ ] Twilio test connection
  - [ ] Account SID masking display
  - [ ] Test SMS functionality (with phone number)
  - [ ] Test WhatsApp functionality (with phone number)
  - [ ] Success/failure messages display
  - [ ] Help guides display correctly

---

### 4. WORKFLOW PAGES

#### My Approvals Page (`/approvals`)
**Tabs**: None

**Components**:
- Page title "My Approvals"
- Pending approvals list
- Approval cards with:
  - Workflow name
  - Resource type
  - Requester
  - Request date
  - Approve button
  - Reject button
  - View Details button
- Empty state "No pending approvals"

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Pending approvals load from `/api/workflows/instances/my-approvals`
- [ ] Approval cards display correctly
- [ ] Approve button approves workflow
- [ ] Reject button rejects workflow (with reason)
- [ ] View Details shows full workflow info
- [ ] Empty state displays when no approvals
- [ ] Real-time updates (if implemented)
- [ ] Notification badge updates

#### Workflow Designer Page (`/workflows`)
**Tabs**: None

**Components**:
- New Workflow button
- Workflow templates list
- Template cards with:
  - Workflow name
  - Resource type
  - Steps count
  - Edit button
  - Delete button
  - Activate/Deactivate toggle
- Create Workflow Template Dialog
  - Workflow name input
  - Resource type dropdown (Inspection, Checklist, Task, etc.)
  - Description textarea
  - Approval steps builder
    - Step name input
    - Approver role dropdown
    - Context dropdown (Organization, Department, etc.)
    - Approval type (Any One, All, Majority)
    - Escalate to dropdown (or "No escalation")
    - Add Step button
  - Save Template button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] New Workflow button opens dialog
- [ ] Template creation form opens
- [ ] All dropdown fields populate correctly
- [ ] **CRITICAL**: Select dropdowns have valid non-empty values
- [ ] Resource type selection
- [ ] Approval steps can be added
- [ ] Approval steps can be removed
- [ ] Step ordering
- [ ] Approver role dropdown shows all roles
- [ ] Context dropdown options
- [ ] Approval type selection
- [ ] Escalation configuration
- [ ] Save template creates workflow
- [ ] Template list displays
- [ ] Edit template loads existing data
- [ ] Delete template (with active workflow protection)
- [ ] Activate/deactivate toggle

#### Delegations Page (`/delegations`)
**Tabs**: None

**Components**:
- Create Delegation button
- Delegations list
- Delegation cards with:
  - Delegate (user name)
  - Start date
  - End date
  - Scope
  - Status (Active/Expired)
  - Revoke button
- Create Delegation Dialog
  - Delegate selector (user dropdown)
  - Start date picker
  - End date picker
  - Scope selector
  - Create button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Create Delegation button opens dialog
- [ ] Delegate user selection
- [ ] Date range validation (end > start)
- [ ] Scope selection
- [ ] Create delegation
- [ ] Delegations list displays
- [ ] Active delegations shown
- [ ] Expired delegations marked
- [ ] Revoke delegation
- [ ] Delegation auto-expiry

#### Audit Trail Page (`/audit`)
**Tabs**: None

**Components**:
- Date range filter
- Event type filter
- User filter
- Search input
- Audit log table with:
  - Timestamp
  - User
  - Action
  - Resource type
  - Resource ID
  - Details
  - View Details button
- Export button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Audit logs load from `/api/audit/logs`
- [ ] Date range filter works
- [ ] Event type filter works
- [ ] User filter works
- [ ] Search functionality
- [ ] View Details shows full event
- [ ] Export to CSV
- [ ] Pagination for large datasets
- [ ] Real-time log updates

---

### 5. OPERATIONS PAGES

#### Inspections Page (`/inspections`)
**Tabs**: Templates, Executions

**Components - Templates Tab**:
- Statistics cards (Pending, Completed Today, Pass Rate, Avg Score)
- New Template button
- Templates list
- Template cards with:
  - Template name
  - Question count
  - Edit button
  - Delete button

**Components - Executions Tab**:
- Executions list
- Execution cards with:
  - Inspection name
  - Inspector name
  - Date
  - Score
  - Status (Pending/Completed)
  - View button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Statistics cards show real data
- [ ] Templates tab displays templates
- [ ] New Template button navigates to builder
- [ ] Template creation (separate page)
- [ ] Template edit
- [ ] Template delete
- [ ] Executions tab shows executions
- [ ] Start new execution
- [ ] Execution workflow (answer questions)
- [ ] Photo uploads in inspections
- [ ] Score calculation
- [ ] Complete inspection
- [ ] View completed inspection

#### Checklists Page (`/checklists`)
**Tabs**: Templates, Executions

**Components - Templates Tab**:
- Statistics cards (Total, Completed Today, Pending Today, Completion Rate)
- New Template button
- Templates list

**Components - Executions Tab**:
- Today's checklists
- Execution cards

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Statistics cards show real data
- [ ] Templates tab displays templates
- [ ] New Template button navigates to builder
- [ ] Template creation
- [ ] Template edit
- [ ] Template delete
- [ ] Executions tab shows today's checklists
- [ ] Start checklist execution
- [ ] Check off items
- [ ] Complete checklist
- [ ] View completed checklist

#### Tasks Page (`/tasks`)
**Tabs**: None (Kanban board)

**Components**:
- Statistics cards (Total, To Do, In Progress, Completed, Overdue)
- New Task button
- Kanban board with 3 columns:
  - To Do
  - In Progress
  - Done
- Task cards with:
  - Title
  - Description
  - Priority badge
  - Due date
  - Assignee avatar
  - Drag handle
- Create Task Dialog
  - Title input
  - Description textarea
  - Priority dropdown (Low/Medium/High)
  - Due date picker
  - Assignee selector
  - Save button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Statistics cards show real data
- [ ] New Task button opens dialog
- [ ] Task creation with all fields
- [ ] Task appears in correct column
- [ ] Drag and drop tasks between columns
- [ ] Task status updates on column change
- [ ] Edit task (click on card)
- [ ] Delete task
- [ ] Task priority colors
- [ ] Overdue tasks highlighted
- [ ] Assignee display
- [ ] Due date formatting
- [ ] Search/filter tasks
- [ ] Task details view

---

### 6. INSIGHTS PAGES

#### Reports Page (`/reports`)
**Tabs**: 5 tabs - Overview, Inspections, Checklists, Tasks, Insights

**Components - Overview Tab**:
- Date range selector (30 Days default)
- Activity trends chart
- Key metrics cards

**Components - Inspections Tab**:
- Inspections report data
- Charts/graphs

**Components - Checklists Tab**:
- Checklists report data
- Charts/graphs

**Components - Tasks Tab**:
- Tasks report data
- Charts/graphs

**Components - Insights Tab**:
- AI-powered insights
- Performance metrics
- Custom Report Builder dialog

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] All 5 tabs visible
- [ ] Tab navigation works
- [ ] Date range selector works
- [ ] Overview charts display
- [ ] Inspections data accurate
- [ ] Checklists data accurate
- [ ] Tasks data accurate
- [ ] Insights display
- [ ] Custom Report Builder opens
- [ ] Export functionality
- [ ] Refresh data button

#### Analytics Dashboard Page (`/analytics`)
**Tabs**: None

**Components**:
- Period selector dropdown (Today, Week, Month, Quarter, Year)
- 4 Overview metric cards (Tasks, Time Tracked, Active Users, Inspections)
- Refresh button
- Export button
- 5 Chart sections:
  - Task Trends (line chart)
  - Tasks by Status (pie chart)
  - Tasks by Priority (bar chart)
  - Time Tracking Trends (area chart)
  - Top Active Users (table)

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Period selector changes data
- [ ] Overview cards show real data
- [ ] Refresh button reloads data
- [ ] Export button generates report
- [ ] Task Trends chart displays
- [ ] Tasks by Status chart displays
- [ ] Tasks by Priority chart displays
- [ ] Time Tracking chart displays
- [ ] Top Active Users table displays
- [ ] Charts respond to period changes
- [ ] Responsive design
- [ ] Loading states

#### Webhooks Page (`/webhooks`)
**Tabs**: None

**Components**:
- Create Webhook button
- Webhooks list
- Webhook cards with:
  - URL
  - Events subscribed
  - Status (Active/Inactive)
  - Last delivery
  - Edit button
  - Delete button
  - Test button
- Create Webhook Dialog
  - URL input
  - Events checklist (21 events, 6 categories)
  - Secret input
  - Save button

**Functionality to Test**:
- [ ] Page loads without errors
- [ ] Create Webhook button opens dialog
- [ ] URL validation
- [ ] Events selection (21 events)
- [ ] Event categories (user, task, inspection, checklist, workflow, group)
- [ ] Create webhook
- [ ] Webhook list displays
- [ ] Edit webhook
- [ ] Delete webhook
- [ ] Test webhook (send test payload)
- [ ] Delivery tracking
- [ ] Webhook logs
- [ ] Secret regeneration

---

### 7. DEVELOPER ADMIN PAGE (`/developer-admin`)
**Access**: Developer role only

**Tabs**: System Status, Users & Passwords, Database, Logs, Settings

**Components - System Status Tab**:
- Service status indicators
- System health metrics

**Components - Users & Passwords Tab**:
- User list with visible passwords
- User search
- Copy password buttons

**Components - Database Tab**:
- Database stats
- Collection viewer

**Components - Logs Tab**:
- System logs viewer
- Log filtering

**Components - Settings Tab**:
- System configuration
- Feature flags

**Functionality to Test**:
- [ ] Page NOT accessible to non-Developer roles (403)
- [ ] Page loads for Developer role
- [ ] All tabs visible
- [ ] System Status displays correctly
- [ ] User list with passwords visible
- [ ] Copy password to clipboard works
- [ ] Database stats accurate
- [ ] Logs viewer works
- [ ] Log filtering works
- [ ] System settings can be changed

---

## INTEGRATION TESTING MATRIX

### Cross-Feature Integration Tests

#### 1. User Creation → Organization Assignment → Role Assignment
- [ ] Register user with organization creation
- [ ] User assigned Master role automatically
- [ ] User appears in User Management
- [ ] User can access appropriate menu items based on role

#### 2. User Invitation → Email → Acceptance
- [ ] Send invitation from Invitations page
- [ ] Email sent via SendGrid
- [ ] Invitation appears in Pending tab
- [ ] Accept invitation creates user account
- [ ] User assigned correct role
- [ ] Invitation moves to accepted status

#### 3. Workflow Creation → Approval Process → Notification
- [ ] Create workflow template
- [ ] Start workflow instance
- [ ] Approval notification sent
- [ ] Approver sees in My Approvals
- [ ] Approve/Reject updates workflow
- [ ] Requester notified of decision

#### 4. Delegation → Approval Authority → Workflow
- [ ] Create delegation
- [ ] Delegate can see approvals
- [ ] Delegate can approve on behalf
- [ ] Delegation expires correctly

#### 5. Task Creation → Assignment → Notification → Completion
- [ ] Create task
- [ ] Assign to user
- [ ] User receives notification
- [ ] Task appears in user's view
- [ ] User completes task
- [ ] Statistics update

#### 6. Inspection Template → Execution → Photo Upload → Completion
- [ ] Create inspection template with photo questions
- [ ] Start inspection execution
- [ ] Upload photos during inspection
- [ ] Photos stored in GridFS
- [ ] Calculate score
- [ ] Complete inspection
- [ ] View completed inspection with photos

#### 7. Settings Changes → UI Updates
- [ ] Change theme (Light/Dark)
- [ ] UI updates immediately across all pages
- [ ] Change accent color
- [ ] All components reflect new color
- [ ] Change font size
- [ ] Text resizes visibly

#### 8. API Key Configuration → Test Connection → Send Message
- [ ] Save Twilio credentials (Master/Developer)
- [ ] Test connection succeeds
- [ ] Send test SMS
- [ ] SMS received
- [ ] Send test WhatsApp
- [ ] WhatsApp received

#### 9. Bulk Import → User Creation → Group Assignment
- [ ] Download CSV template
- [ ] Fill with user data
- [ ] Upload CSV
- [ ] Preview validates data
- [ ] Import creates users
- [ ] Users assigned to groups (if specified)
- [ ] Users appear in User Management

#### 10. Global Search → Multi-Resource Results
- [ ] Open search (Cmd+K)
- [ ] Search for term
- [ ] Results from multiple resources (tasks, users, groups, inspections)
- [ ] Click result navigates to resource

#### 11. Notification System → Real-time Updates
- [ ] Action triggers notification (task assignment)
- [ ] Notification appears in bell dropdown
- [ ] Unread count updates
- [ ] Mark as read works
- [ ] Clear all works

#### 12. Audit Logging → Action Tracking
- [ ] Perform various actions
- [ ] Actions logged in Audit Trail
- [ ] Audit entries include user, timestamp, action, resource
- [ ] Audit can be filtered and searched

---

## RISK ASSESSMENT

### Critical Risks (Must Pass 100%)
1. **Authentication System** - Login, registration, password reset
2. **Authorization/Permissions** - Role-based access control
3. **Data Persistence** - Save/load data correctly
4. **API Key Security** - Master/Developer only access
5. **User Management** - CRUD operations, soft delete

### High Risks (Must Pass 95%+)
1. **Workflow System** - Template creation, approval flow
2. **Settings Persistence** - All 8 tabs save correctly
3. **Navigation** - All menu items accessible
4. **Dashboard Statistics** - Accurate real-time data
5. **File Uploads** - Photos, CSV imports

### Medium Risks (Must Pass 90%+)
1. **Charts/Analytics** - Data visualization
2. **Notifications** - Real-time updates
3. **Search** - Global search accuracy
4. **Webhooks** - Event notifications
5. **Bulk Operations** - Import, export

### Low Risks (Must Pass 80%+)
1. **UI/UX Polish** - Animations, transitions
2. **Mobile Responsiveness** - Layout on small screens
3. **Help Text** - Tooltips, guides
4. **Empty States** - "No data" messages

---

## TEST EXECUTION STRATEGY

### Phase 1: Backend API Testing (Priority: CRITICAL)
**Estimated Time**: 2-3 hours

**Test Scope**:
- All 150+ API endpoints
- Authentication and authorization
- CRUD operations for all resources
- Data validation
- Error handling
- API key security (Master/Developer only)

**Success Criteria**: 95%+ success rate

**Testing Method**: Use `deep_testing_backend_v2` agent with comprehensive curl tests

---

### Phase 2: Frontend Component Testing (Priority: HIGH)
**Estimated Time**: 3-4 hours

**Test Scope**:
- All 24 pages load without errors
- All tabs on multi-tab pages work
- All buttons and links functional
- Forms validate and submit
- Data displays correctly
- Navigation works

**Success Criteria**: 95%+ success rate

**Testing Method**: Use `auto_frontend_testing_agent` with Playwright scripts

---

### Phase 3: Integration Testing (Priority: HIGH)
**Estimated Time**: 2-3 hours

**Test Scope**:
- End-to-end user flows
- Cross-feature integration
- Data flow between components
- Real-time updates
- Notification system
- File uploads

**Success Criteria**: 90%+ success rate

**Testing Method**: Manual testing + Playwright E2E tests

---

### Phase 4: UI/UX & Responsiveness (Priority: MEDIUM)
**Estimated Time**: 1-2 hours

**Test Scope**:
- Responsive design (desktop, tablet, mobile)
- Theme switching
- Visual consistency
- Loading states
- Error messages
- Empty states

**Success Criteria**: 85%+ success rate

**Testing Method**: Manual testing across different screen sizes

---

### Phase 5: Performance & Security (Priority: HIGH)
**Estimated Time**: 1 hour

**Test Scope**:
- Page load times
- API response times
- Large dataset handling
- API key security
- Role-based restrictions
- Data isolation (organization level)

**Success Criteria**: 95%+ success rate

**Testing Method**: Manual testing + performance profiling

---

## TESTING CHECKLIST

### Pre-Testing Setup
- [ ] Backend and frontend services running
- [ ] Database populated with test data
- [ ] Test user accounts created (Master, Admin, Developer roles)
- [ ] API keys configured (SendGrid, Twilio) for testing
- [ ] Browser console cleared
- [ ] Network tab open for debugging

### During Testing
- [ ] Log all issues in test_result.md
- [ ] Take screenshots of errors
- [ ] Capture network requests for API failures
- [ ] Test on multiple browsers (Chrome, Firefox, Safari)
- [ ] Test responsive design (desktop, tablet, mobile)

### Post-Testing
- [ ] Review all test results
- [ ] Calculate success rate
- [ ] Prioritize critical failures
- [ ] Create fix plan for failures
- [ ] Re-test after fixes
- [ ] Final acceptance testing

---

## SUCCESS METRICS

### Target Quality Gates
- **Critical Features**: 100% success rate (Authentication, Authorization, Data Persistence)
- **High Priority Features**: 95%+ success rate (Workflows, Settings, Navigation)
- **Medium Priority Features**: 90%+ success rate (Analytics, Notifications, Search)
- **Overall Application**: 98%+ success rate

### Acceptance Criteria
✅ All menu items accessible
✅ All pages load without errors
✅ All tabs on multi-tab pages functional
✅ All CRUD operations working
✅ All integrations functional (SendGrid, Twilio)
✅ API key security enforced (Master/Developer only)
✅ No critical bugs or blockers
✅ Performance acceptable (< 3s page load)

---

## TESTING EXECUTION PLAN

### Step 1: Backend Testing (MUST DO FIRST)
```bash
# Test all backend APIs
# Focus areas:
# - Authentication endpoints
# - User management endpoints
# - API settings endpoints (Master/Developer restriction)
# - Workflow endpoints
# - All CRUD operations
```

### Step 2: Frontend Component Testing
```bash
# Test all pages and components
# Focus areas:
# - Page loads
# - Tab navigation
# - Button clicks
# - Form submissions
# - Data display
```

### Step 3: Integration Testing
```bash
# Test end-to-end flows
# Focus areas:
# - User registration → login → dashboard
# - Workflow creation → approval → notification
# - Task creation → assignment → completion
# - Settings changes → UI updates
# - API key config → test messages
```

### Step 4: Manual Verification
```bash
# Manual checks
# - Responsive design
# - Theme switching
# - Search functionality
# - Notification bell
# - User menu
```

---

## NOTES FOR TESTING EXECUTION

1. **Test Order Matters**: Always test backend first, then frontend, then integration
2. **Use Real Data**: Test with actual data, not mocks
3. **Test Edge Cases**: Empty states, errors, validation failures
4. **Test Security**: Role restrictions, data isolation, API key access
5. **Test Performance**: Large datasets, slow networks
6. **Document Everything**: All passes and failures
7. **Re-test Fixes**: After fixing issues, re-run tests

---

**READY TO BEGIN TESTING**

This comprehensive plan covers every aspect of the application. Once approved, I will execute this testing plan systematically using the testing agents and provide detailed results.

**Estimated Total Testing Time**: 8-12 hours
**Estimated Issues to Find**: 20-40 (based on 98% target)
**Estimated Fix Time**: 2-4 hours

**AWAITING USER APPROVAL TO PROCEED**
