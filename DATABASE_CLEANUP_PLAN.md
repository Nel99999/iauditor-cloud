# Database Cleanup Plan

## Executive Summary
**Objective**: Clean all databases while preserving only 1 production user and their associated data

## Current Database State

**Database**: `operational_platform`
- **Total Collections**: 38
- **Total Documents**: 34,304

### Target User to KEEP:
- **Email**: llewellyn@bluedawncapital.co.za
- **Name**: Llewellyn Nel 2
- **Role**: developer
- **User ID**: e9522a08-754c-4643-9e76-94a99abf8566
- **Organization ID**: 315fa36c-4555-4b2b-8ba3-fdbde31cb940

---

## Cleanup Strategy

### Phase 1: Identify Data to PRESERVE
**Keep ALL data associated with:**
- User ID: `e9522a08-754c-4643-9e76-94a99abf8566`
- Organization ID: `315fa36c-4555-4b2b-8ba3-fdbde31cb940`

### Phase 2: Collections to Clean

#### A. Delete ALL Documents From These Collections:
*No preservation needed - pure test data*

1. `approval_chains` (0 docs) ✅ Empty
2. `approvals` (0 docs) ✅ Empty
3. `audit_logs` (147 docs) - **DELETE ALL**
4. `delegations` (11 docs) - **DELETE ALL**
5. `gdpr_exports` (7 docs) - **DELETE ALL**
6. `mentions` (5 docs) - **DELETE ALL**
7. `notification_preferences` (6 docs) - **DELETE ALL**
8. `notifications` (11 docs) - **DELETE ALL**
9. `sla_configs` (3 docs) - **DELETE ALL**
10. `subtasks` (22 docs) - **DELETE ALL**
11. `time_based_permissions` (6 docs) - **DELETE ALL**
12. `time_entries` (26 docs) - **DELETE ALL**
13. `user_consents` (6 docs) - **DELETE ALL**
14. `user_deactivations` (0 docs) ✅ Empty
15. `user_function_overrides` (0 docs) ✅ Empty
16. `user_groups` (23 docs) - **DELETE ALL**
17. `user_invitations` (6 docs) - **DELETE ALL**
18. `webhook_deliveries` (7 docs) - **DELETE ALL**
19. `webhooks` (20 docs) - **DELETE ALL**
20. `workflow_instances` (22 docs) - **DELETE ALL**
21. `workflow_templates` (47 docs) - **DELETE ALL**

#### B. Delete SPECIFIC Documents From These Collections:
*Keep only data for target organization/user*

22. `users` (412 docs)
    - **KEEP**: 1 user (llewellyn@bluedawncapital.co.za)
    - **DELETE**: 411 users

23. `organizations` (305 docs)
    - **KEEP**: 1 org (ID: 315fa36c-4555-4b2b-8ba3-fdbde31cb940)
    - **DELETE**: 304 organizations

24. `organization_units` (70 docs)
    - **KEEP**: Units where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other units

25. `organization_settings` (6 docs)
    - **KEEP**: Settings where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other settings

26. `inspection_templates` (20 docs)
    - **KEEP**: Templates where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other templates

27. `inspection_executions` (15 docs)
    - **KEEP**: Executions where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other executions

28. `checklist_templates` (35 docs)
    - **KEEP**: Templates where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other templates

29. `checklist_executions` (6 docs)
    - **KEEP**: Executions where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other executions

30. `tasks` (259 docs)
    - **KEEP**: Tasks where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other tasks

31. `invitations` (212 docs)
    - **KEEP**: Invitations where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`
    - **DELETE**: All other invitations

32. `user_preferences` (2 docs)
    - **KEEP**: Preferences where `user_id = e9522a08-754c-4643-9e76-94a99abf8566`
    - **DELETE**: All other preferences

#### C. System/Permission Collections - DELETE ALL:
*Will be recreated on next app initialization*

33. `roles` (3,017 docs) - **DELETE ALL**
34. `permissions` (26 docs) - **DELETE ALL**
35. `role_permissions` (29,477 docs) - **DELETE ALL**
36. `permission_contexts` (12 docs) - **DELETE ALL**

#### D. GridFS File Storage:
*Delete test files*

37. `fs.files` (27 docs) - **DELETE ALL**
38. `fs.chunks` (28 docs) - **DELETE ALL**

---

## Cleanup Execution Plan

### Step 1: Backup Current State (Optional)
```bash
# Create backup before cleanup
mongodump --uri="mongodb://localhost:27017" --db=operational_platform --out=/tmp/db_backup_before_cleanup
```

### Step 2: Delete Test Collections (Complete Wipe)
Delete all documents from 21 collections that contain only test data.

### Step 3: Clean Organization-Specific Data
Keep only documents where `organization_id = 315fa36c-4555-4b2b-8ba3-fdbde31cb940`

### Step 4: Clean User Data
Keep only: `llewellyn@bluedawncapital.co.za`

### Step 5: Clean System Collections
Delete all roles, permissions, and role_permissions (will auto-recreate on app start)

### Step 6: Clean File Storage
Delete all GridFS files (test uploads)

### Step 7: Verification
Count documents in each collection to verify cleanup

---

## Expected Results After Cleanup

### Collections with 0 Documents (Empty):
- All test-only collections (approval_chains, approvals, audit_logs, delegations, etc.)
- System collections (roles, permissions, role_permissions will auto-recreate)
- File storage (fs.files, fs.chunks)

### Collections with Production Data:
- `users`: 1 document (llewellyn@bluedawncapital.co.za)
- `organizations`: 1 document (Blue Dawn Capital org)
- `organization_units`: X documents (org-specific units)
- `organization_settings`: X documents (org-specific settings)
- `inspection_templates`: X documents (org-specific templates)
- `inspection_executions`: X documents (org-specific executions)
- `checklist_templates`: X documents (org-specific templates)
- `checklist_executions`: X documents (org-specific executions)
- `tasks`: X documents (org-specific tasks)
- `invitations`: X documents (org-specific invitations)
- `user_preferences`: X documents (user-specific preferences)

### Estimated Cleanup Impact:
- **Before**: 34,304 total documents
- **After**: ~50-100 documents (production data only)
- **Reduction**: ~99% data removal

---

## Safety Measures

1. ✅ **No Code Changes** - Only database operations
2. ✅ **Preserve Production User** - llewellyn@bluedawncapital.co.za
3. ✅ **Preserve Production Org** - All associated organization data
4. ✅ **System Auto-Recovery** - Roles/permissions will auto-recreate on app restart
5. ✅ **Reversible** - Can restore from backup if needed

---

## Approval Required

**Please confirm:**
1. ✅ You want to keep ONLY user: llewellyn@bluedawncapital.co.za
2. ✅ You want to keep ALL data associated with organization: 315fa36c-4555-4b2b-8ba3-fdbde31cb940
3. ✅ You want to DELETE all other test users and organizations
4. ✅ You want to DELETE all test-related collections (audit logs, notifications, etc.)
5. ✅ You understand roles/permissions will auto-recreate on next app start

**Once approved, I will execute the cleanup script.**
