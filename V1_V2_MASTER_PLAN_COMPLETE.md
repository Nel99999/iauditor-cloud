# 🎯 V1.0 & V2.0 OPERATIONAL PLATFORM - MASTER IMPLEMENTATION PLAN

**Strategic Roadmap** | **16-Month Build Cycle** | **Complete System**

---

## 📊 EXECUTIVE OVERVIEW

### **Launch V1 Scope (Months 1-8):**
- 18 modules across 9 domains
- Foundation + Core Operations + Safety + Financial
- Target: Production-ready operational platform

### **Launch V2 Scope (Months 9-16):**
- 25 additional modules
- Advanced Safety + EHS + Facilities + Production + Specialized
- Target: Enterprise-grade complete platform

**Total: 43 modules, 12 domains, fully integrated ecosystem**

---

# 🚀 LAUNCH V1 - DETAILED BREAKDOWN

## **Timeline: 32-36 weeks (8-9 months)**

---

## PHASE 1: FOUNDATION (Weeks 1-4) - CRITICAL INFRASTRUCTURE

### **Deliverables:**
1. ✅ Unified Services Layer (attachments, comments, notifications, activity logging)
2. ✅ Enhanced RBAC (scope-based permissions)
3. ✅ Base data model updates (all work items)
4. ✅ Migration scripts (existing data)

### **Modules:**

#### **Module 1.1: Attachment Service**
- **What:** Universal file upload/management for ALL modules
- **Features:** GridFS storage, photo/video/PDF support, thumbnails, metadata
- **API:** 4 endpoints (upload, list, download, delete)
- **Frontend:** AttachmentManager component (reusable)
- **Effort:** 3-4 days

#### **Module 1.2: Comment Service**
- **What:** Threaded discussions on any work item
- **Features:** @mentions, notifications, threading, rich text
- **API:** 4 endpoints (create, list, update, delete)
- **Frontend:** CommentThread component (reusable)
- **Effort:** 3-4 days

#### **Module 1.3: Notification Service**
- **What:** Multi-channel notifications (in-app, email, SMS, push)
- **Features:** Preferences, priorities, read/unread, channels
- **API:** 3 endpoints (list, mark read, preferences)
- **Frontend:** NotificationCenter (enhance existing)
- **Effort:** 2-3 days

#### **Module 1.4: Activity Service**
- **What:** Audit trail for all entities
- **Features:** Change tracking, timeline view, user attribution
- **API:** 2 endpoints (log, get timeline)
- **Frontend:** ActivityTimeline component
- **Effort:** 2 days

#### **Module 1.5: Scope-Based Access**
- **What:** Hierarchical visibility (own/unit/children/org)
- **Features:** Scope filtering, permission resolution, unit hierarchy
- **Backend:** ScopeService class, permission enhancements
- **Effort:** 4-5 days

#### **Module 1.6: Base Data Migration**
- **What:** Add new fields to existing work items
- **Fields:** unit_id, asset_id, assigned_to, due_date, tags, scope
- **Collections:** inspections, checklists, tasks
- **Scripts:** Migration + rollback scripts
- **Effort:** 2 days

**Phase 1 Total:** 16-20 days (3-4 weeks)  
**Team:** 1 senior backend + 1 senior frontend  
**Testing:** 3-4 days

---

## PHASE 2: ASSET MANAGEMENT (Weeks 5-10) - CORE FOUNDATION

### **Objective:** Asset-centric operations foundation

---

### **Module 2.1: Asset Register** (Weeks 5-7)

**What:** Comprehensive asset database

**Data Model (25 fields):**
```
Core: id, asset_tag, name, description, organization_id
Classification: asset_type, category, criticality (A/B/C)
Location: unit_id, location_details, gps_coordinates
Hierarchy: parent_asset_id, has_children
Technical: make, model, serial_number, manufacturer, specifications
Financial: purchase_date, purchase_cost, current_value, depreciation_rate
Lifecycle: status, installation_date, expected_life_years
Maintenance: maintenance_schedule, last_maintenance, next_maintenance
Calibration: requires_calibration, calibration_frequency, next_calibration
```

**API Endpoints (10):**
1. POST /assets - Create asset
2. GET /assets - List assets (filtered, scoped)
3. GET /assets/{id} - Get asset details
4. PUT /assets/{id} - Update asset
5. DELETE /assets/{id} - Soft delete
6. GET /assets/{id}/history - Complete history (all linked work)
7. POST /assets/{id}/qr-code - Generate QR code
8. GET /assets/types - Asset type catalog
9. GET /assets/stats - Asset statistics
10. POST /assets/import - Bulk import (CSV)

**Frontend Pages (4):**
1. AssetsPage.tsx - Main list (grid/list views, filters, search)
2. AssetDetailPage.tsx - Detail view (6 tabs)
3. AssetCreatePage.tsx - Creation wizard (multi-step)
4. AssetEditPage.tsx - Edit form

**Frontend Components (3):**
1. AssetCard.tsx - Grid view card
2. AssetSelector.tsx - Dropdown selector (for linking to inspections/tasks)
3. AssetHierarchyTree.tsx - Parent-child visualization

**RBAC:**
- asset.create.organization (Master, Admin, Asset Manager)
- asset.read.{own|unit|children|organization}
- asset.update.organization
- asset.delete.organization

**Effort:** 12-15 days  
**Dependencies:** Phase 1 complete

---

### **Module 2.2: Work Order System (CMMS)** (Weeks 7-9)

**What:** Maintenance work order management

**Data Model (30 fields):**
```
Core: id, wo_number (auto-increment), title, description
Classification: work_type (corrective/preventive/predictive/project/emergency)
Asset: asset_id, asset_tag, asset_name (denormalized)
Assignment: requested_by, assigned_to, approved_by, completed_by
Org: organization_id, unit_id, location
Status: status (requested/approved/scheduled/in_progress/completed/cancelled)
Priority: priority, urgency
Scheduling: scheduled_date, actual_start, actual_end, estimated_hours, actual_hours
Labor: labor_cost, hourly_rate
Parts: parts_used (array), parts_cost, total_cost
Downtime: causes_downtime, downtime_hours, downtime_start, downtime_end
Workflow: requires_approval, approval_status, approval_notes
Performance: completed_on_time, exceeded_estimate
Linking: parent_wo_id, child_wo_ids, triggered_by (inspection_id, incident_id)
```

**API Endpoints (15):**
1. POST /work-orders - Create work order
2. GET /work-orders - List (filtered by status, asset, type, assigned_to)
3. GET /work-orders/{id} - Get details
4. PUT /work-orders/{id} - Update
5. PUT /work-orders/{id}/status - Change status
6. POST /work-orders/{id}/assign - Assign to technician
7. POST /work-orders/{id}/approve - Approve work order
8. POST /work-orders/{id}/start - Start work
9. POST /work-orders/{id}/complete - Complete work
10. POST /work-orders/{id}/add-labor - Log labor hours
11. POST /work-orders/{id}/add-parts - Log parts used
12. GET /work-orders/{id}/timeline - Activity timeline
13. GET /work-orders/stats - WO statistics
14. GET /work-orders/backlog - Maintenance backlog
15. POST /work-orders/schedule - Schedule multiple WOs

**Work Order Statuses:**
```
requested → approved → scheduled → in_progress → completed
                ↓           ↓            ↓
            rejected    on_hold      cancelled
```

**Frontend Pages (3):**
1. WorkOrdersPage.tsx - Main page (kanban by status, list view)
2. WorkOrderDetailPage.tsx - Detail view (all info, timeline)
3. WorkOrderCreatePage.tsx - Creation form

**Frontend Components:**
1. WorkOrderCard.tsx - Kanban card
2. WorkOrderStatusBadge.tsx - Color-coded status
3. LaborLogForm.tsx - Log labor hours
4. PartsUsageForm.tsx - Log parts used

**Integration Points:**
- Failed inspection → Auto-create corrective WO
- Incident → Auto-create corrective WO
- PM schedule → Auto-create preventive WO
- Asset → Link all WOs to asset history

**Effort:** 15-18 days  
**Dependencies:** Asset Register, Inventory (for parts)

---

### **Module 2.3: Inventory & Spare Parts** (Weeks 9-10)

**What:** Parts inventory and stock management

**Data Model (20 fields):**
```
Core: id, part_number, description, organization_id
Classification: category, sub_category, unit_of_measure
Supplier: supplier_id, supplier_part_number, preferred_supplier
Stock: quantity_on_hand, quantity_reserved, quantity_available
Reorder: reorder_point, reorder_quantity, lead_time_days
Storage: warehouse_id, bin_location, storage_conditions
Financial: unit_cost, total_value, last_purchase_cost
Asset Linking: compatible_asset_ids (which assets use this part)
```

**API Endpoints (12):**
1. POST /inventory/items - Create stock item
2. GET /inventory/items - List (filtered, searchable)
3. GET /inventory/items/{id} - Get item details
4. PUT /inventory/items/{id} - Update item
5. POST /inventory/items/{id}/adjust - Stock adjustment (add/remove)
6. POST /inventory/items/{id}/reserve - Reserve for work order
7. POST /inventory/items/{id}/issue - Issue to work order
8. POST /inventory/items/{id}/transfer - Transfer between warehouses
9. GET /inventory/items/reorder - Items below reorder point
10. GET /inventory/items/{id}/history - Transaction history
11. POST /inventory/count - Physical count entry
12. GET /inventory/stats - Inventory statistics

**Frontend Pages (2):**
1. InventoryPage.tsx - Main list with stock levels
2. InventoryItemPage.tsx - Item details, transaction history

**Integration:**
- Work orders use parts from inventory
- Auto-create purchase requisition when below reorder point
- Track parts cost per work order

**Effort:** 8-10 days  
**Dependencies:** Asset Register

---

**PHASE 2 TOTAL:** 35-43 days (5-6 weeks)  
**Team:** 2 backend + 2 frontend developers  
**Testing:** 5-7 days

---

## PHASE 3: ENHANCED WORK MANAGEMENT (Weeks 11-16)

### **Objective:** Upgrade existing modules + add Projects

---

### **Module 3.1: Inspections (Enhanced)** (Weeks 11-12)

**Current:** Basic inspection templates and executions  
**Add:**
- ✅ Asset linking (inspect specific assets)
- ✅ Unit assignment (which units use which templates)
- ✅ Recurring schedules (daily, weekly, monthly)
- ✅ Auto-assignment (round-robin, least-loaded)
- ✅ Conditional questions (show Q2 if Q1 = yes)
- ✅ Photo requirements per question
- ✅ Signature capture (digital sign-off)
- ✅ Auto-create work order (if fails)
- ✅ Follow-up inspection tracking
- ✅ Inspection trends & analytics

**New Fields:**
```python
# inspection_templates:
unit_ids: list[str]  # Which units use this template
asset_type_ids: list[str]  # Which asset types this applies to
recurrence_rule: Optional[str]  # "daily", "weekly", "monthly", cron
auto_assign_logic: Optional[str]  # "round_robin", "least_loaded", "specific_users"
assigned_inspector_ids: list[str]
requires_competency: Optional[str]  # Competency required to perform
conditional_logic: dict  # {question_id: {show_if: {question_id: value}}}

# inspection_executions:
asset_id: str (add)
unit_id: str (add)
due_date: datetime (add)
auto_created_wo_id: Optional[str]  # Link to work order if created
follow_up_inspection_id: Optional[str]
```

**New API Endpoints (8):**
1. POST /inspections/templates/{id}/schedule - Set recurring schedule
2. POST /inspections/templates/{id}/assign-units - Assign to units
3. GET /inspections/due - Inspections due today/this week
4. POST /inspections/executions/{id}/create-work-order - Manual WO creation
5. GET /inspections/templates/{id}/analytics - Template performance
6. GET /inspections/executions/{id}/follow-ups - Follow-up history
7. POST /inspections/templates/bulk-schedule - Schedule multiple
8. GET /inspections/calendar - Calendar view of scheduled inspections

**Frontend Enhancements:**
1. Template builder - Add conditional logic UI
2. Schedule configurator - Recurring schedule setup
3. Calendar view - See all scheduled inspections
4. Asset selector - Link inspection to asset
5. Auto-WO trigger - Configure failed inspection actions

**Integration:**
- Link to assets
- Link to work orders (auto-create)
- Link to training (competency check)
- Link to units (org hierarchy)

**Effort:** 10-12 days  
**Dependencies:** Assets, Work Orders

---

### **Module 3.2: Checklists (Enhanced)** (Week 13)

**Current:** Basic checklist templates and executions  
**Add:**
- ✅ Asset linking
- ✅ Unit assignment  
- ✅ Time-based auto-scheduling
- ✅ Multi-person sign-off
- ✅ Conditional items
- ✅ Photo requirements
- ✅ Score/pass-fail (like inspections)

**New Fields:**
```python
# checklist_templates:
unit_ids: list[str]
asset_type_ids: list[str]
frequency: str  # "daily", "per_shift", "weekly"
shift_based: bool  # Auto-create per shift
time_limit_minutes: Optional[int]  # Must complete within X minutes
requires_supervisor_approval: bool
scoring_enabled: bool
pass_percentage: Optional[float]

# checklist_executions:
asset_id: str (add)
unit_id: str (add)
shift: Optional[str]  # "day", "night", "swing"
started_by: str
completed_by: Optional[str]
approved_by: Optional[str]
time_taken_minutes: Optional[int]
score: Optional[float]
passed: Optional[bool]
```

**New API Endpoints (5):**
1. POST /checklists/templates/{id}/schedule - Configure auto-schedule
2. GET /checklists/due - Due checklists
3. POST /checklists/executions/{id}/approve - Supervisor approval
4. GET /checklists/templates/{id}/compliance - Completion rate tracking
5. GET /checklists/shift - Checklists for current shift

**Frontend Enhancements:**
1. Shift-based view
2. Timer (if time_limit set)
3. Multi-signature capture
4. Score display

**Effort:** 6-8 days  
**Dependencies:** Assets

---

### **Module 3.3: Tasks (Enhanced)** (Week 14)

**Current:** Basic task management  
**Add:**
- ✅ Task templates (recurring tasks)
- ✅ Task dependencies (predecessor/successor)
- ✅ Subtasks (hierarchical breakdown)
- ✅ Asset linking
- ✅ Labor tracking (actual hours)
- ✅ Parts usage (link to inventory)
- ✅ Checklist integration (task completion requires checklist)

**New Fields:**
```python
# tasks:
asset_id: str (add)
unit_id: str (add)
task_type: str  # "standard", "corrective_action", "project_task", "recurring"
template_id: Optional[str]  # If created from template
parent_task_id: Optional[str]  # For subtasks
predecessor_task_ids: list[str]  # Dependencies
estimated_hours: Optional[float]
actual_hours: Optional[float]
labor_cost: Optional[float]
parts_used: list[dict]
requires_checklist: Optional[str]  # Checklist template ID
linked_inspection_id: Optional[str]  # If created from inspection
linked_incident_id: Optional[str]  # If corrective action
```

**New API Endpoints (8):**
1. POST /tasks/templates - Create task template
2. GET /tasks/templates - List templates
3. POST /tasks/from-template - Create from template
4. POST /tasks/{id}/subtasks - Create subtask
5. GET /tasks/{id}/subtasks - List subtasks
6. POST /tasks/{id}/log-time - Log work hours
7. POST /tasks/{id}/log-parts - Log parts used
8. GET /tasks/{id}/dependencies - View dependency chain

**Frontend Enhancements:**
1. Subtask view (collapsible tree)
2. Dependency visualizer (Gantt-style)
3. Time logging form
4. Parts usage form
5. Task templates library

**Effort:** 8-10 days  
**Dependencies:** Assets, Inventory, Work Orders

---

### **Module 3.4: Projects** (Weeks 15-16)

**What:** NEW - Multi-task initiatives with milestones

**Data Model (25 fields):**
```python
class Project(BaseModel):
    # Core
    id: str
    organization_id: str
    project_code: str  # Auto-generated (PRJ-2025-001)
    name: str
    description: str
    
    # Classification
    project_type: str  # "capital", "improvement", "maintenance", "strategic"
    status: str  # "planning", "active", "on_hold", "completed", "cancelled"
    priority: str
    
    # Ownership
    project_manager_id: str
    sponsor_id: Optional[str]
    unit_id: str
    stakeholder_ids: list[str]
    
    # Timeline
    planned_start: datetime
    planned_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    
    # Financial
    budget: float
    actual_cost: float = 0.0
    currency: str = "USD"
    capex_request_id: Optional[str]  # Linked CAPEX approval
    
    # Scope
    objectives: list[str]
    deliverables: list[str]
    success_criteria: list[str]
    
    # Risk
    risk_level: str  # "low", "medium", "high"
    risks: list[dict]  # [{description, probability, impact, mitigation}]
    
    # Progress
    completion_percentage: float = 0.0
    milestone_count: int = 0
    completed_milestones: int = 0
    task_count: int = 0
    completed_tasks: int = 0
    
    # Assets Affected
    related_asset_ids: list[str]
    
    # Metadata
    tags: list[str]
    custom_fields: dict
    is_active: bool = True
    created_by: str
    created_at: datetime
    updated_at: datetime
```

**Milestone Model:**
```python
class Milestone(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    due_date: datetime
    status: str  # "pending", "in_progress", "completed", "missed"
    completion_percentage: float = 0.0
    dependencies: list[str]  # Other milestone IDs
    deliverables: list[str]
    completed_at: Optional[datetime]
    order: int  # Sequence
```

**API Endpoints (20):**
1. POST /projects - Create project
2. GET /projects - List projects (active, by unit, by PM)
3. GET /projects/{id} - Get project details
4. PUT /projects/{id} - Update project
5. PUT /projects/{id}/status - Change status
6. DELETE /projects/{id} - Cancel project
7. POST /projects/{id}/milestones - Create milestone
8. GET /projects/{id}/milestones - List milestones
9. PUT /milestones/{id} - Update milestone
10. PUT /milestones/{id}/complete - Mark milestone complete
11. POST /projects/{id}/tasks - Create project task
12. GET /projects/{id}/tasks - List project tasks
13. POST /projects/{id}/risks - Add risk
14. GET /projects/{id}/risks - List risks
15. POST /projects/{id}/costs - Log cost
16. GET /projects/{id}/costs - Cost breakdown
17. GET /projects/{id}/timeline - Gantt chart data
18. GET /projects/{id}/status-report - Auto-generated report
19. GET /projects/dashboard - Portfolio dashboard
20. GET /projects/{id}/export-report - PDF export

**Frontend Pages (4):**
1. ProjectsPage.tsx - Portfolio view (list/grid)
2. ProjectDetailPage.tsx - Full project view (8 tabs)
3. ProjectCreatePage.tsx - Wizard (5 steps)
4. ProjectDashboardPage.tsx - Portfolio analytics

**Frontend Components:**
1. ProjectCard.tsx - Grid view
2. MilestoneTimeline.tsx - Milestone visualization
3. GanttChart.tsx - Timeline view (using Recharts)
4. ProjectKanban.tsx - Projects by status
5. RiskMatrix.tsx - Risk visualization

**Tabs in Project Detail:**
1. Overview - Summary, status, progress
2. Milestones - Timeline, status
3. Tasks - All project tasks
4. Budget - Cost tracking
5. Risks - Risk register
6. Team - Stakeholders, resources
7. Documents - Linked documents
8. Activity - Audit trail

**RBAC:**
- project.create.organization (Project Manager role)
- project.read.{own|unit|organization}
- project.update.own (if PM)
- project.manage.organization (any project)

**Effort:** 15-18 days  
**Dependencies:** Tasks, CAPEX (for linking)

---

**PHASE 3 TOTAL:** 39-48 days (6-7 weeks)  
**Team:** 2 backend + 2 frontend  
**Testing:** 6-8 days

---

## PHASE 4: SAFETY & INCIDENTS (Weeks 17-20)

### **Module 4.1: Incident Management** (Weeks 17-19)

**What:** NEW - Safety events, near-misses, accidents, injuries

**Data Model (35 fields):**
```python
class Incident(BaseModel):
    # Core
    id: str
    incident_number: str  # Auto (INC-2025-001)
    organization_id: str
    unit_id: str
    
    # Classification
    incident_type: str  # "injury", "near_miss", "property_damage", "environmental", "security"
    severity: str  # "minor", "moderate", "serious", "critical", "catastrophic"
    category: Optional[str]  # Industry-specific
    
    # Event Details
    occurred_at: datetime
    location: str
    location_details: Optional[str]
    gps_coordinates: Optional[dict]
    
    # People Involved
    reported_by: str  # User who reported
    reporter_name: str
    injured_person_id: Optional[str]  # If injury
    injured_person_name: Optional[str]
    witness_ids: list[str]
    
    # Description
    description: str  # What happened
    immediate_actions_taken: str
    injury_details: Optional[str]  # Body part, nature of injury
    injury_type: Optional[str]  # "first_aid", "medical_treatment", "lost_time", "fatality"
    days_away_from_work: int = 0
    
    # Asset/Equipment
    asset_id: Optional[str]  # Asset involved
    equipment_involved: Optional[str]
    
    # Investigation
    investigation_required: bool = False
    investigation_status: str = "not_started"  # "not_started", "in_progress", "completed"
    investigator_ids: list[str] = []
    investigation_due_date: Optional[datetime]
    
    # Root Cause
    root_causes: list[dict] = []  # [{cause, category, contributing_factors}]
    contributing_factors: list[str] = []
    
    # Corrective Actions (CAPA)
    corrective_action_task_ids: list[str] = []  # Linked tasks
    preventive_actions: list[dict] = []
    
    # Impact
    property_damage_cost: float = 0.0
    environmental_impact: Optional[str]
    production_lost_hours: float = 0.0
    
    # Compliance
    osha_recordable: bool = False
    reported_to_authorities: bool = False
    authority_reference_numbers: list[str] = []
    
    # Status
    status: str = "reported"  # "reported", "under_investigation", "closed", "pending_capa"
    closed_at: Optional[datetime]
    closed_by: Optional[str]
    
    # Workflow
    workflow_id: Optional[str]  # Investigation workflow
    
    # Metadata
    tags: list[str]
    attachments_count: int = 0  # Photos of incident
    created_at: datetime
    updated_at: datetime
```

**API Endpoints (18):**
1. POST /incidents - Report incident
2. GET /incidents - List incidents (filtered)
3. GET /incidents/{id} - Get details
4. PUT /incidents/{id} - Update incident
5. POST /incidents/{id}/investigate - Start investigation
6. POST /incidents/{id}/root-cause - Add root cause
7. POST /incidents/{id}/corrective-action - Create corrective action task
8. POST /incidents/{id}/close - Close incident
9. POST /incidents/{id}/witnesses - Add witness
10. POST /incidents/{id}/reopen - Reopen if needed
11. GET /incidents/stats - Incident statistics
12. GET /incidents/trending - Incident trends
13. GET /incidents/hotspots - Location-based analysis
14. GET /incidents/osha-log - OSHA 300 log data
15. POST /incidents/emergency-report - Quick emergency report (simplified)
16. GET /incidents/calendar - Incident calendar
17. GET /incidents/{id}/export-report - PDF investigation report
18. GET /incidents/dashboard - Safety dashboard data

**Incident Workflow:**
```
Reported → Under Investigation → CAPA Assigned → CAPA Completed → Closed
              ↓
    (If critical: Auto-escalate to Emergency Management)
```

**Frontend Pages (4):**
1. IncidentsPage.tsx - Main list with filters
2. IncidentDetailPage.tsx - Full incident view (7 tabs)
3. IncidentReportPage.tsx - Quick report form (mobile-friendly)
4. IncidentInvestigationPage.tsx - Investigation tools

**Frontend Components:**
1. IncidentCard.tsx - Color-coded by severity
2. RootCauseAnalysisTool.tsx - 5 Whys, Fishbone diagram
3. IncidentTimeline.tsx - Event reconstruction
4. OSHALogTable.tsx - OSHA 300 log view
5. IncidentHeatMap.tsx - Geographical incident mapping

**Tabs in Incident Detail:**
1. Overview - Basic info, severity, people involved
2. Investigation - RCA, findings, evidence
3. CAPA - Corrective/preventive actions (linked tasks)
4. Witnesses - Statements
5. Photos/Evidence - Attachments
6. Timeline - Event sequence
7. Activity - Audit trail

**Integration:**
- Auto-create corrective action tasks
- Link to assets (equipment involved)
- Link to training (identify training gaps)
- Link to permits (if permit violation)
- Trigger workflows (investigation approval)

**Effort:** 15-18 days  
**Dependencies:** Tasks, Assets, Workflows

---

### **Module 4.2: Training & Competency** (Week 20)

**What:** NEW - Learning management and competency tracking

**Data Model:**

**Training Course:**
```python
class TrainingCourse(BaseModel):
    id: str
    organization_id: str
    course_code: str
    name: str
    description: str
    course_type: str  # "safety", "technical", "compliance", "soft_skill"
    duration_hours: float
    valid_for_years: Optional[int]  # Certification validity
    competency_ids: list[str]  # Grants these competencies
    required_for_roles: list[str]  # Which roles must take this
    regulatory_requirement: bool
    online_content_url: Optional[str]  # LMS link
    pass_score: Optional[float]
    is_active: bool
```

**Competency:**
```python
class Competency(BaseModel):
    id: str
    organization_id: str
    code: str  # "INSP-01", "FORKLIFT", "CONFINED-SPACE"
    name: str
    description: str
    category: str  # "safety", "technical", "operational"
    level: str  # "basic", "intermediate", "advanced", "expert"
    required_for_tasks: list[str]  # Task types requiring this
    required_for_permits: list[str]  # Permit types requiring this
    assessment_method: str  # "training", "test", "observation", "certification"
    valid_for_years: Optional[int]
```

**Employee Training Record:**
```python
class EmployeeTraining(BaseModel):
    id: str
    employee_id: str  # user_id
    course_id: str
    completed_at: datetime
    score: Optional[float]
    passed: bool
    expires_at: Optional[datetime]
    certification_number: Optional[str]
    instructor_id: Optional[str]
    competencies_granted: list[str]
```

**API Endpoints (15):**
1. POST /training/courses - Create course
2. GET /training/courses - List courses
3. POST /training/enrollments - Enroll employee
4. POST /training/completions - Record completion
5. GET /training/employees/{id}/transcript - Training history
6. GET /training/employees/{id}/competencies - Current competencies
7. GET /training/employees/{id}/gaps - Training gaps
8. GET /training/competencies - Competency catalog
9. POST /training/competencies - Create competency
10. GET /training/due - Training due soon
11. GET /training/expired - Expired certifications
12. GET /training/matrix - Training matrix (employees × courses)
13. GET /training/compliance - Compliance percentage by unit
14. POST /training/bulk-enroll - Bulk enrollment
15. GET /training/stats - Training statistics

**Frontend Pages (3):**
1. TrainingPage.tsx - Course catalog, my training
2. CompetencyMatrixPage.tsx - Matrix view (employees × competencies)
3. TrainingDetailPage.tsx - Course details, enrollments

**Integration:**
- Block inspection assignment if not competent
- Block permit issuance if not trained
- Auto-enroll on role assignment
- Link to incidents (training gaps)

**Effort:** 10-12 days  
**Dependencies:** None (standalone initially)

---

**PHASE 4 TOTAL:** 25-30 days (4 weeks)  
**Team:** 2 backend + 2 frontend  
**Testing:** 4-5 days

---

## PHASE 5: SUPPLY CHAIN & FINANCIAL (Weeks 21-24)

### **Module 5.1: Contractor Management** (Week 21)

**What:** Manage contractors, suppliers, vendors

**Data Model:**
```python
class Contractor(BaseModel):
    id: str
    organization_id: str
    company_name: str
    contact_person: str
    email: str
    phone: str
    address: dict
    
    # Classification
    contractor_type: str  # "maintenance", "construction", "cleaning", "security", "professional_services"
    trade: Optional[str]  # "electrical", "plumbing", "HVAC", etc.
    
    # Insurance & Compliance
    insurance_general_liability: bool
    insurance_expiry: Optional[datetime]
    insurance_amount: Optional[float]
    workers_comp_certificate: bool
    workers_comp_expiry: Optional[datetime]
    safety_rating: Optional[float]  # 0-100
    
    # Performance
    performance_score: float = 0.0
    completed_jobs: int = 0
    on_time_percentage: float = 0.0
    quality_rating: float = 0.0
    safety_incidents: int = 0
    
    # Financial
    payment_terms: Optional[str]
    credit_limit: Optional[float]
    total_spend_ytd: float = 0.0
    
    # Status
    status: str  # "active", "inactive", "blacklisted"
    onboarded_at: datetime
    last_work_date: Optional[datetime]
```

**API Endpoints (10):**
1. POST /contractors - Create contractor
2. GET /contractors - List contractors
3. GET /contractors/{id} - Get details
4. PUT /contractors/{id} - Update
5. POST /contractors/{id}/onboard - Onboarding workflow
6. GET /contractors/{id}/work-history - All work orders
7. GET /contractors/{id}/performance - Performance metrics
8. GET /contractors/{id}/safety - Safety statistics
9. POST /contractors/{id}/insurance - Upload insurance cert
10. GET /contractors/expiring-insurance - Insurance expiring soon

**Frontend Pages (2):**
1. ContractorsPage.tsx - List view
2. ContractorDetailPage.tsx - Details, work history, performance

**Integration:**
- Work orders can be assigned to contractors
- Permit to work (contractor permits)
- Incidents (contractor incidents tracked separately)

**Effort:** 6-8 days

---

### **Module 5.2: CAPEX Management** (Week 22)

**What:** Capital expenditure requests and approvals

**Data Model:**
```python
class CapexRequest(BaseModel):
    id: str
    capex_number: str  # AUTO (CAP-2025-001)
    organization_id: str
    unit_id: str
    
    # Request
    title: str
    description: str
    justification: str  # Business case
    request_type: str  # "new_asset", "replacement", "expansion", "upgrade"
    
    # Financial
    estimated_cost: float
    actual_cost: float = 0.0
    budget_year: int
    roi_years: Optional[float]
    payback_period_months: Optional[float]
    npv: Optional[float]  # Net Present Value
    irr: Optional[float]  # Internal Rate of Return
    
    # Asset Details
    asset_type: str
    quantity: int = 1
    specifications: dict
    preferred_vendor: Optional[str]
    
    # Approval
    requested_by: str
    requested_at: datetime
    workflow_id: Optional[str]
    approval_status: str  # "draft", "pending", "approved", "rejected", "cancelled"
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    
    # Execution
    project_id: Optional[str]  # Linked project if approved
    asset_ids: list[str] = []  # Assets created from this CAPEX
    status: str  # "requested", "approved", "in_progress", "completed", "cancelled"
    
    # Documents
    business_case_doc_id: Optional[str]
    quotes_doc_ids: list[str] = []
```

**API Endpoints (12):**
1. POST /capex/requests - Create request
2. GET /capex/requests - List (filtered by status, year, unit)
3. GET /capex/requests/{id} - Get details
4. PUT /capex/requests/{id} - Update (if draft)
5. POST /capex/requests/{id}/submit - Submit for approval
6. POST /capex/requests/{id}/approve - Approve
7. POST /capex/requests/{id}/reject - Reject
8. POST /capex/requests/{id}/link-project - Link to project
9. POST /capex/requests/{id}/link-asset - Link to asset (after purchase)
10. GET /capex/budget-summary - Budget by year/unit
11. GET /capex/dashboard - CAPEX portfolio view
12. GET /capex/requests/{id}/export-business-case - PDF export

**Frontend Pages (3):**
1. CapexPage.tsx - List view (filter by year, status)
2. CapexDetailPage.tsx - Request details, approval history
3. CapexCreatePage.tsx - Business case wizard

**Approval Workflow Integration:**
- Routes based on amount (>$10k to VP, >$100k to CFO, etc.)
- Multi-level approvals
- Budget availability check

**Effort:** 8-10 days  
**Dependencies:** Workflows, Projects, Assets

---

### **Module 5.3: OPEX & Cost Allocation** (Week 23)

**What:** Operational expense tracking and cost allocation

**Data Model:**
```python
class OpexTransaction(BaseModel):
    id: str
    transaction_number: str
    organization_id: str
    unit_id: str
    cost_center: str
    
    # Classification
    category: str  # "labor", "materials", "utilities", "services", "repairs"
    sub_category: Optional[str]
    
    # Financial
    amount: float
    currency: str = "USD"
    transaction_date: datetime
    fiscal_year: int
    fiscal_period: int  # Month (1-12)
    
    # Linking
    work_order_id: Optional[str]  # If from work order
    project_id: Optional[str]  # If from project
    asset_id: Optional[str]  # If asset-related
    vendor_id: Optional[str]
    invoice_number: Optional[str]
    
    # Approval
    requires_approval: bool
    approval_status: Optional[str]
    approved_by: Optional[str]
    
    # Allocation
    allocated_to_units: list[dict] = []  # [{unit_id, percentage, amount}]
    
    # Metadata
    description: str
    notes: Optional[str]
    created_by: str
    created_at: datetime
```

**API Endpoints (10):**
1. POST /opex/transactions - Create transaction
2. GET /opex/transactions - List (filtered)
3. GET /opex/summary - Summary by category/unit/period
4. GET /opex/trends - Spending trends
5. GET /opex/by-unit - Cost by unit
6. GET /opex/by-asset - Cost by asset
7. POST /opex/allocate - Allocate cost to units
8. GET /opex/dashboard - OPEX dashboard
9. POST /opex/import - Import from accounting system
10. GET /opex/export - Export for accounting

**Frontend Pages (2):**
1. OpexPage.tsx - Transaction list, filters
2. OpexDashboardPage.tsx - Analytics, charts, trends

**Charts (Using Recharts):**
- Spending by category (pie chart)
- Spending trend (line chart)
- Spending by unit (bar chart)
- Budget vs actual (stacked bar)

**Effort:** 6-8 days  
**Dependencies:** Budgets

---

### **Module 5.4: Budget Management** (Week 24)

**What:** Budget planning and tracking

**Data Model:**
```python
class Budget(BaseModel):
    id: str
    organization_id: str
    unit_id: str
    cost_center: str
    
    # Period
    fiscal_year: int
    budget_type: str  # "annual", "quarterly", "monthly"
    
    # Amounts
    category: str  # "labor", "materials", "capex", "opex", etc.
    planned_amount: float
    revised_amount: Optional[float]  # After revisions
    committed_amount: float = 0.0  # POs, reservations
    actual_amount: float = 0.0  # Spent
    available_amount: float  # Calculated
    
    # Status
    status: str  # "draft", "submitted", "approved", "active", "closed"
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    
    # Tracking
    variance: float = 0.0  # Actual vs planned
    variance_percentage: float = 0.0
    forecast_amount: Optional[float]  # End-of-year forecast
    
    # Metadata
    notes: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
```

**API Endpoints (12):**
1. POST /budgets - Create budget
2. GET /budgets - List budgets (by year, unit)
3. GET /budgets/{id} - Get budget details
4. PUT /budgets/{id} - Update budget
5. POST /budgets/{id}/revise - Revise budget (create new version)
6. GET /budgets/summary - Budget summary (all units/categories)
7. GET /budgets/variance - Variance analysis
8. GET /budgets/forecast - Forecast vs budget
9. POST /budgets/check-available - Check if funds available (before approval)
10. POST /budgets/commit - Commit funds (reserve)
11. POST /budgets/release - Release committed funds
12. GET /budgets/dashboard - Budget dashboard

**Frontend Pages (3):**
1. BudgetsPage.tsx - Budget list by unit
2. BudgetDetailPage.tsx - Budget tracking, variance
3. BudgetDashboardPage.tsx - Portfolio view

**Charts:**
- Budget vs actual by category
- Variance analysis
- Spending pace (forecast)
- Unit comparison

**Effort:** 7-9 days  
**Dependencies:** OPEX tracking

---

**PHASE 5 TOTAL:** 27-35 days (4-5 weeks)  
**Team:** 2 backend + 2 frontend  
**Testing:** 4-5 days

---

## PHASE 6: HR & COMMUNICATION (Weeks 25-28)

### **Module 6.1: Employee Management** (Weeks 25-26)

**What:** HR administration integrated with operations

**Data Model:**
```python
class Employee(BaseModel):
    id: str
    user_id: str  # Link to auth user
    organization_id: str
    unit_id: str
    
    # Identity
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: str
    
    # Employment
    position: str
    department: str
    manager_id: Optional[str]
    hire_date: datetime
    employment_type: str  # "full_time", "part_time", "contractor", "temp"
    employment_status: str  # "active", "on_leave", "terminated"
    
    # Competencies
    competency_ids: list[str]
    certification_ids: list[str]
    
    # Safety
    safety_training_current: bool
    last_safety_training: Optional[datetime]
    incident_count_ytd: int = 0
    
    # Performance
    performance_rating: Optional[float]
    last_review_date: Optional[datetime]
    
    # Metadata
    tags: list[str]
    custom_fields: dict
```

**API Endpoints (8):**
1. POST /employees - Create employee profile
2. GET /employees - List employees
3. GET /employees/{id} - Get profile
4. PUT /employees/{id} - Update profile
5. GET /employees/{id}/competencies - Competency status
6. GET /employees/{id}/certifications - Active certifications
7. GET /employees/org-chart - Organization chart data
8. GET /employees/{id}/work-history - All assigned work

**Frontend Pages (2):**
1. EmployeesPage.tsx - Employee directory
2. EmployeeProfilePage.tsx - Full profile, competencies, work history

**Effort:** 8-10 days

---

### **Module 6.2: Team Chat** (Week 27)

**What:** Real-time messaging platform

**Data Model:**
```python
class Channel(BaseModel):
    id: str
    organization_id: str
    name: str
    channel_type: str  # "unit", "team", "project", "incident", "direct"
    description: Optional[str]
    
    # Membership
    member_ids: list[str]
    owner_id: str
    
    # Linked Entity
    entity_type: Optional[str]  # "project", "incident", "work_order"
    entity_id: Optional[str]
    
    # Settings
    is_private: bool = False
    is_archived: bool = False
    
    # Metadata
    created_by: str
    created_at: datetime

class Message(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    content: str
    mentions: list[str] = []  # @mentioned user IDs
    
    # Threading
    parent_message_id: Optional[str]
    reply_count: int = 0
    
    # Attachments
    attachment_ids: list[str] = []
    
    # Reactions
    reactions: dict = {}  # {emoji: [user_ids]}
    
    # Metadata
    edited: bool = False
    deleted: bool = False
    sent_at: datetime
```

**API Endpoints (12):**
1. POST /chat/channels - Create channel
2. GET /chat/channels - List user's channels
3. GET /chat/channels/{id}/messages - Get messages
4. POST /chat/channels/{id}/messages - Send message
5. PUT /chat/messages/{id} - Edit message
6. DELETE /chat/messages/{id} - Delete message
7. POST /chat/messages/{id}/react - Add reaction
8. POST /chat/channels/{id}/members - Add member
9. DELETE /chat/channels/{id}/members/{user_id} - Remove member
10. PUT /chat/channels/{id}/archive - Archive channel
11. GET /chat/search - Search messages
12. WebSocket /chat/ws - Real-time updates

**Frontend Components:**
1. ChatSidebar.tsx - Channel list
2. ChatWindow.tsx - Message view
3. MessageComposer.tsx - Input with @mentions
4. MessageItem.tsx - Individual message

**Effort:** 10-12 days (includes WebSocket)

---

### **Module 6.3: Announcements** (Week 28)

**What:** Org-wide broadcasts

**Data Model:**
```python
class Announcement(BaseModel):
    id: str
    organization_id: str
    title: str
    content: str
    
    # Targeting
    target_audience: str  # "all", "unit", "role", "custom"
    unit_ids: list[str] = []
    role_codes: list[str] = []
    user_ids: list[str] = []
    
    # Settings
    priority: str  # "normal", "important", "urgent"
    published: bool
    published_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    # Engagement
    read_count: int = 0
    acknowledgement_required: bool = False
    acknowledged_by: list[str] = []
    
    # Metadata
    created_by: str
    created_at: datetime
```

**API Endpoints (8):**
1. POST /announcements - Create
2. GET /announcements - List active
3. GET /announcements/{id} - Get details
4. PUT /announcements/{id} - Update
5. POST /announcements/{id}/publish - Publish
6. POST /announcements/{id}/acknowledge - User acknowledges
7. GET /announcements/{id}/stats - Read/acknowledge stats
8. DELETE /announcements/{id} - Delete

**Frontend:**
1. Banner notification (top of page for urgent)
2. Announcements page
3. Read/acknowledge tracking

**Effort:** 4-5 days

---

### **Module 6.4: Activity Feeds** (Part of unified service)

**Already covered in Phase 1 - Activity Service**

---

**PHASE 6 TOTAL:** 22-27 days (3-4 weeks)  
**Team:** 2 backend + 2 frontend  
**Testing:** 3-4 days

---

## PHASE 7: ANALYTICS & DASHBOARDS (Weeks 29-32)

### **Module 7.1: Executive Dashboards** (Week 29-30)

**What:** KPI dashboards for all roles

**Dashboard Types:**
1. **Executive Dashboard** - Org-wide KPIs
2. **Unit Manager Dashboard** - Unit performance
3. **Safety Dashboard** - Incident rates, leading indicators
4. **Maintenance Dashboard** - Backlog, PM compliance, MTBF/MTTR
5. **Asset Dashboard** - Asset health, criticality, utilization
6. **Financial Dashboard** - Budget vs actual, spending trends
7. **Personal Dashboard** - My work, my metrics

**KPI Catalog (50+ metrics):**

**Safety:**
- Total Recordable Incident Rate (TRIR)
- Days Away/Restricted/Transfer (DART) rate
- Lost Time Injury Frequency (LTIF)
- Near miss count
- Safety observation count
- Permit violations

**Maintenance:**
- Work order backlog
- PM compliance percentage
- Mean Time Between Failures (MTBF)
- Mean Time To Repair (MTTR)
- Maintenance cost per asset
- Preventive vs corrective ratio

**Operations:**
- Inspections completed vs due
- Checklist compliance rate
- Task completion rate
- Overdue task count
- Project on-time delivery
- Asset uptime percentage

**Quality:**
- Inspection pass rate
- Defect rate
- Non-conformance count
- Audit findings
- Corrective actions on time

**Financial:**
- Budget variance
- CAPEX spend vs plan
- OPEX trend
- Cost per unit produced
- Maintenance cost as % of asset value

**API Endpoints (10):**
1. GET /dashboards/executive - Executive KPIs
2. GET /dashboards/unit/{unit_id} - Unit KPIs
3. GET /dashboards/safety - Safety metrics
4. GET /dashboards/maintenance - Maintenance metrics
5. GET /dashboards/assets - Asset metrics
6. GET /dashboards/financial - Financial metrics
7. GET /dashboards/personal - User's personal dashboard
8. POST /dashboards/custom - Create custom dashboard
9. GET /dashboards/kpi-catalog - Available KPIs
10. GET /dashboards/{id}/export - Export dashboard as PDF

**Frontend Pages (2):**
1. DashboardsPage.tsx - Dashboard gallery (choose dashboard)
2. DashboardViewPage.tsx - Interactive dashboard (drill-down)

**Frontend Components:**
1. KPICard.tsx - Metric card with trend
2. KPIChart.tsx - Chart visualization
3. DashboardBuilder.tsx - Drag-drop dashboard builder

**Charts (Recharts):**
- Line charts (trends)
- Bar charts (comparisons)
- Pie charts (distributions)
- Area charts (stacked metrics)
- Gauge charts (KPI vs target)

**Effort:** 12-15 days  
**Dependencies:** All data modules

---

### **Module 7.2: Reports** (Week 31)

**What:** Standard and custom reports

**Report Categories:**

**Safety Reports:**
1. OSHA 300 Log
2. Incident summary report
3. Near-miss analysis
4. Safety observation report
5. Permit register
6. Training compliance matrix

**Maintenance Reports:**
7. Work order summary
8. PM compliance report
9. Asset maintenance history
10. Downtime analysis
11. Parts usage report
12. Contractor performance

**Operations Reports:**
13. Inspection completion report
14. Checklist compliance
15. Task completion summary
16. Project status report
17. Overdue items report

**Financial Reports:**
18. Budget variance report
19. CAPEX status report
20. OPEX analysis
21. Cost by unit
22. Cost by asset

**API Endpoints (8):**
1. POST /reports/generate - Generate report
2. GET /reports/templates - Report templates
3. GET /reports/history - Report history
4. GET /reports/{id}/download - Download PDF/Excel
5. POST /reports/schedule - Schedule recurring report
6. GET /reports/scheduled - List scheduled reports
7. POST /reports/email - Email report to recipients
8. GET /reports/catalog - Available reports

**Frontend Pages (2):**
1. ReportsPage.tsx - Report catalog, history
2. ReportViewerPage.tsx - View/download report

**Report Engine:**
- Use library for PDF generation (ReportLab, WeasyPrint)
- Excel export (openpyxl)
- Template-based (customizable headers, footers, logos)

**Effort:** 10-12 days

---

### **Module 7.3: Advanced Analytics** (Week 32)

**What:** Predictive analytics and insights

**Features:**
1. Trend forecasting (predict future failures)
2. Anomaly detection (unusual patterns)
3. Comparative analysis (unit benchmarking)
4. Root cause analysis (incident clustering)
5. Predictive maintenance (failure prediction)
6. What-if scenarios
7. Correlation analysis

**API Endpoints (6):**
1. GET /analytics/predict-failures - Asset failure predictions
2. GET /analytics/anomalies - Detected anomalies
3. GET /analytics/trends - Trend analysis
4. GET /analytics/benchmarks - Unit benchmarking
5. GET /analytics/correlations - Find correlations
6. POST /analytics/scenario - Run what-if scenario

**Frontend:**
1. AnalyticsPage.tsx - Analytics hub
2. Charts and visualizations

**Effort:** 8-10 days  
**Dependencies:** Historical data from all modules

---

**PHASE 7 TOTAL:** 30-37 days (4-5 weeks)  
**Team:** 2 backend + 2 frontend + 1 data analyst  
**Testing:** 5-6 days

---

## PHASE 8: EMERGENCY MANAGEMENT (Week 33)

### **Module 8.1: Emergency Management**

**What:** Emergency response and business continuity

**Data Model:**
```python
class Emergency(BaseModel):
    id: str
    emergency_number: str  # AUTO (EMG-2025-001)
    organization_id: str
    unit_id: str
    
    # Classification
    emergency_type: str  # "fire", "medical", "chemical_spill", "evacuation", "natural_disaster", "security"
    severity: str  # "low", "moderate", "high", "critical"
    
    # Event
    occurred_at: datetime
    location: str
    gps_coordinates: Optional[dict]
    
    # Response
    reported_by: str
    incident_commander_id: Optional[str]
    response_team_ids: list[str] = []
    
    # Status
    status: str  # "active", "contained", "resolved", "closed"
    resolved_at: Optional[datetime]
    
    # Impact
    evacuated: bool
    evacuated_count: int = 0
    injuries: int = 0
    fatalities: int = 0
    property_damage: bool
    environmental_impact: bool
    
    # Response Actions
    actions_taken: list[dict] = []
    resources_deployed: list[dict] = []
    
    # Linked Incidents
    incident_ids: list[str] = []  # Formal incident reports
    
    # Metadata
    created_at: datetime
    updated_at: datetime
```

**Features:**
1. Emergency alert (broadcast to all users in unit)
2. Evacuation tracking (muster point check-in)
3. Incident command center (real-time status)
4. Resource deployment tracking
5. Timeline reconstruction
6. Post-event report generation
7. Emergency contact list (auto-call tree)
8. Integration with incidents (auto-create incident report)

**API Endpoints (10):**
1. POST /emergencies - Declare emergency
2. GET /emergencies - List emergencies
3. GET /emergencies/{id} - Get status
4. PUT /emergencies/{id}/status - Update status
5. POST /emergencies/{id}/broadcast - Send alert
6. POST /emergencies/{id}/evacuate - Trigger evacuation
7. GET /emergencies/{id}/accountability - Who's accounted for
8. POST /emergencies/{id}/muster-checkin - Check in at muster point
9. POST /emergencies/{id}/resolve - Resolve emergency
10. GET /emergencies/contacts - Emergency contacts

**Frontend Pages (2):**
1. EmergenciesPage.tsx - Emergency list, active emergencies
2. EmergencyCommandCenter.tsx - Real-time status, actions

**Mobile Features:**
1. SOS button (one-tap emergency report)
2. Evacuation notification (push alert)
3. Muster point check-in (QR code scan)
4. Emergency contact quick-dial

**Effort:** 8-10 days  
**Dependencies:** Notifications, Incidents

---

**PHASE 8 TOTAL:** 8-10 days (1-2 weeks)  
**Team:** 1 backend + 1 frontend  
**Testing:** 2-3 days

---

## 🎯 LAUNCH V1 - SUMMARY

### **Total Scope:**
- **18 Modules** across 9 domains
- **200+ API endpoints**
- **50+ frontend pages**
- **30+ reusable components**
- **15+ database collections**

### **Timeline:**
- **Development:** 28-32 weeks (7-8 months)
- **Testing & QA:** 4-6 weeks
- **Total:** 32-38 weeks (8-9.5 months)

### **Team Requirements:**
- 2 Senior Backend Developers
- 2 Senior Frontend Developers
- 1 Data/Analytics Developer
- 1 QA Engineer
- 1 Product Manager / Architect (you/me)

### **Launch V1 Deliverables:**

**Work Management:**
✅ Enhanced Inspections (asset-linked, recurring, auto-WO)  
✅ Enhanced Checklists (shift-based, scoring)  
✅ Enhanced Tasks (templates, dependencies, subtasks)  
✅ Projects (full project management)

**Asset Management:**
✅ Asset Register (complete database)  
✅ CMMS (work orders, PM scheduling)  
✅ Inventory (spare parts, stock control)

**Safety:**
✅ Incident Management (full CAPA, investigations)  
✅ Training & Competency (LMS, competency matrix)

**Supply Chain:**
✅ Contractor Management (onboarding, performance)

**Financial:**
✅ CAPEX Management (requests, approvals, tracking)  
✅ OPEX Tracking (cost allocation)  
✅ Budget Management (planning, variance)

**HR:**
✅ Employee Management (profiles, competencies)

**Communication:**
✅ Team Chat (channels, DMs, @mentions)  
✅ Announcements (org-wide broadcasts)  
✅ Activity Feeds (universal audit trail)

**Analytics:**
✅ Dashboards (7 dashboard types, 50+ KPIs)  
✅ Reports (20+ standard reports, PDF/Excel)  
✅ Advanced Analytics (predictive, trends)

**Emergency:**
✅ Emergency Management (response, evacuation)

**Plus Foundation:**
✅ Unified Services (attachments, comments, notifications)  
✅ Enhanced RBAC (scope-based, hierarchical)  
✅ Mobile optimization  
✅ Complete integration (cross-module workflows)

---

# 🚀 LAUNCH V2 - DETAILED BREAKDOWN

## **Timeline: 32-36 weeks (8-9 months) after V1**

---

## PHASE 9: ADVANCED SAFETY (Weeks 33-38) - 6 weeks

### **Module 9.1: Permit to Work** (Weeks 33-34)
- 8 permit types (hot work, confined space, height, electrical, excavation, chemical, radiation, cold work)
- Multi-step approval workflows
- Pre-work checklists (gas testing, isolation verification)
- Active permit tracking
- Permit register & analytics
- Integration with LOTO
- **15 API endpoints, 4 frontend pages**
- **Effort:** 12-15 days

### **Module 9.2: Lockout/Tagout (LOTO)** (Week 35)
- Equipment-specific procedures
- Energy source mapping
- Lock/tag inventory
- Group lockout management
- Integration with permits & work orders
- **10 API endpoints, 3 frontend pages**
- **Effort:** 8-10 days

### **Module 9.3: Risk Assessments (JSA/JHA)** (Weeks 36-37)
- Job Safety Analysis templates
- Risk matrix (probability × severity)
- Hazard library
- Control measures hierarchy
- Integration with permits
- **12 API endpoints, 3 frontend pages**
- **Effort:** 10-12 days

### **Module 9.4: Environmental Monitoring** (Week 38)
- Emission tracking
- Waste management
- IoT sensor integration
- Regulatory reporting
- **10 API endpoints, 2 frontend pages**
- **Effort:** 7-9 days

### **Module 9.5: Occupational Health** (Week 38)
- Medical surveillance
- Exposure monitoring
- Health assessments
- **8 API endpoints, 2 frontend pages**
- **Effort:** 6-8 days

### **Module 9.6: Safety Observations** (Week 38)
- Behavior-based safety
- Observation cards
- Safety culture metrics
- **6 API endpoints, 1 frontend page**
- **Effort:** 4-5 days

**Phase 9 Total:** 47-59 days (6-8 weeks)

---

## PHASE 10: FACILITIES MANAGEMENT (Weeks 39-42) - 4 weeks

### **Module 10.1: Space Management (CAFM)** (Weeks 39-40)
- Floor plans (interactive)
- Desk/office booking (hot-desking, hoteling)
- Occupancy tracking
- Move management
- Space utilization analytics
- **15 API endpoints, 4 frontend pages**
- **Effort:** 12-15 days

### **Module 10.2: Meeting Room Booking** (Week 41)
- Room scheduling
- Equipment booking
- Check-in/no-show management
- Utilization analytics
- **8 API endpoints, 2 frontend pages**
- **Effort:** 5-7 days

### **Module 10.3: Visitor Management** (Week 42)
- Pre-registration
- Check-in kiosk
- Badge printing
- Watchlist screening
- **8 API endpoints, 2 frontend pages**
- **Effort:** 5-7 days

**Phase 10 Total:** 22-29 days (3-4 weeks)

---

## PHASE 11: ADVANCED SUPPLY CHAIN (Weeks 43-46) - 4 weeks

### **Module 11.1: Procurement** (Weeks 43-44)
- Purchase requisitions
- Purchase orders
- Vendor management
- 3-way matching
- Approval workflows
- **20 API endpoints, 5 frontend pages**
- **Effort:** 15-18 days

### **Module 11.2: Advanced Inventory** (Weeks 45-46)
- Warehouse management (WMS)
- Barcode/RFID integration
- Cycle counting
- ABC analysis
- **15 API endpoints, 3 frontend pages**
- **Effort:** 12-15 days

**Phase 11 Total:** 27-33 days (4 weeks)

---

## PHASE 12: PRODUCTION & QUALITY (Weeks 47-54) - 8 weeks

### **Module 12.1: Production Tracking (MES)** (Weeks 47-50)
- Production orders
- Shop floor control
- Work instructions
- OEE calculation
- Downtime tracking
- **25 API endpoints, 6 frontend pages**
- **Effort:** 25-30 days

### **Module 12.2: Quality Management (QMS)** (Weeks 51-54)
- Non-conformance reports
- CAPA system
- Audit management
- SPC charts
- Document control
- **30 API endpoints, 8 frontend pages**
- **Effort:** 28-32 days

**Phase 12 Total:** 53-62 days (7-9 weeks)

---

## PHASE 13: WORKFORCE MANAGEMENT (Weeks 55-58) - 4 weeks

### **Module 13.1: Workforce Scheduling** (Weeks 55-56)
- Shift scheduling
- Skill matching
- Shift swaps
- **12 API endpoints, 3 frontend pages**
- **Effort:** 10-12 days

### **Module 13.2: Time & Attendance** (Weeks 57-58)
- Clock in/out
- Timesheet approvals
- Geofencing
- Labor cost allocation
- **15 API endpoints, 4 frontend pages**
- **Effort:** 12-15 days

**Phase 13 Total:** 22-27 days (3-4 weeks)

---

## PHASE 14: SPECIALIZED MODULES (Weeks 59-68) - 10 weeks

### **Modules (9 specialized modules):**
1. **Fleet Management** - 15 endpoints, 4 pages (2 weeks)
2. **Energy Management** - 12 endpoints, 3 pages (1.5 weeks)
3. **ESG Reporting** - 10 endpoints, 3 pages (1.5 weeks)
4. **Document Control** - 12 endpoints, 3 pages (1.5 weeks)
5. **Change Management (MOC)** - 10 endpoints, 2 pages (1 week)
6. **Tooling Management** - 8 endpoints, 2 pages (1 week)
7. **Energy Isolation** - 10 endpoints, 2 pages (1 week)
8. **Shift Handover** - 6 endpoints, 1 page (0.5 weeks)
9. **SOP Management** - 10 endpoints, 3 pages (1 week)
10. **Calibration** - 10 endpoints, 2 pages (1 week)
11. **Contractor Safety** - 8 endpoints, 2 pages (1 week)

**Phase 14 Total:** 50-60 days (7-9 weeks)

---

## PHASE 15: PROCESS SAFETY (Weeks 69-72) - 4 weeks

### **Module 15.1: Process Safety Management (PSM)**
- Process hazard analysis (PHA)
- HAZOP studies
- Mechanical integrity
- Pre-startup safety review (PSSR)
- **20 API endpoints, 5 frontend pages**
- **Effort:** 25-30 days

**Phase 15 Total:** 25-30 days (3.5-4 weeks)

---

## 🎯 LAUNCH V2 - SUMMARY

### **Total Scope:**
- **25 Additional Modules**
- **300+ API endpoints**
- **70+ frontend pages**
- **40+ components**

### **Timeline:**
- **Development:** 28-32 weeks (7-8 months)
- **Testing & QA:** 4-6 weeks
- **Total:** 32-38 weeks (8-9.5 months)

### **Combined V1 + V2:**
- **43 Total Modules**
- **500+ API endpoints**
- **120+ frontend pages**
- **70+ reusable components**
- **40+ database collections**
- **16-18 months total build**

---

## 📊 RESOURCE REQUIREMENTS

### **Development Team:**
- 3 Senior Backend Developers (Python, FastAPI, MongoDB)
- 3 Senior Frontend Developers (React, TypeScript)
- 1 Full-Stack Developer (backend + frontend)
- 1 Data Engineer (analytics, reporting)
- 2 QA Engineers (automated testing)
- 1 DevOps Engineer (deployment, CI/CD)
- 1 Product Manager / Architect
- 1 UX/UI Designer (part-time)

**Total:** 13 people (10 FTE)

### **Technology Stack:**

**Backend:**
- FastAPI (Python 3.11+)
- MongoDB (database)
- GridFS (file storage)
- Redis (caching, real-time)
- Celery (background jobs)
- WebSockets (real-time updates)
- ReportLab (PDF generation)

**Frontend:**
- React 19
- TypeScript
- Shadcn UI components
- Recharts (analytics)
- Framer Motion (animations)
- React Query (data fetching)
- Zustand (state management)

**Infrastructure:**
- Kubernetes (container orchestration)
- CI/CD (GitHub Actions)
- Monitoring (logging, metrics)

---

## 🎯 SUCCESS METRICS

### **V1 Launch Success Criteria:**
- ✅ 500+ users onboarded
- ✅ 95%+ uptime
- ✅ <2s page load time
- ✅ Mobile app adoption >60%
- ✅ 20+ assets per organization
- ✅ 50+ work orders per month per org
- ✅ Incident reporting <5 min average
- ✅ User satisfaction >8/10

### **V2 Launch Success Criteria:**
- ✅ 2000+ users
- ✅ All 43 modules in production
- ✅ API performance <100ms avg
- ✅ 99.5% uptime
- ✅ Full mobile parity
- ✅ Predictive analytics accuracy >85%
- ✅ Platform expansion to 5+ industries

---

## 📋 NEXT IMMEDIATE STEPS

**For You:**
1. Review this master plan
2. Confirm V1 scope is acceptable
3. Approve Phase 1 (Foundation) start
4. Provide any industry-specific requirements

**For Me:**
1. Create detailed technical specifications for Phase 1
2. Set up development environment
3. Create database schema designs
4. Start implementation (Week 1)

---

**This is the complete, systematic, comprehensive plan you requested. Ready to build something truly world-class!**

**Should I proceed with Phase 1: Foundation?**
