#!/usr/bin/env python3
"""
ABSOLUTE FINAL COMPREHENSIVE BACKEND TEST - ALL FIXES APPLIED
Test all 20 modules with correct paths and real operations
Target: 95%+ success rate
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend/.env
BASE_URL = "https://twilio-ops.preview.emergentagent.com/api"

# Production user credentials
EMAIL = "llewellyn@bluedawncapital.co.za"
PASSWORD = "Test@1234"

# Test results tracking
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(module, test_name, passed, status_code=None, message=""):
    """Log test result"""
    results["total"] += 1
    if passed:
        results["passed"] += 1
        status = "✅ PASS"
    else:
        results["failed"] += 1
        status = "❌ FAIL"
    
    result = {
        "module": module,
        "test": test_name,
        "passed": passed,
        "status_code": status_code,
        "message": message
    }
    results["tests"].append(result)
    
    print(f"{status} | {module} | {test_name} | {message}")
    return passed

def test_endpoint(method, endpoint, headers=None, json_data=None, expected_status=200, test_name="", module=""):
    """Generic endpoint test"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return log_test(module, test_name, False, None, f"Invalid method: {method}"), None
        
        passed = response.status_code == expected_status
        message = f"Status: {response.status_code}"
        
        if not passed:
            try:
                error_detail = response.json()
                message += f" | Error: {error_detail}"
            except:
                message += f" | Response: {response.text[:100]}"
        
        return log_test(module, test_name, passed, response.status_code, message), response
    
    except Exception as e:
        return log_test(module, test_name, False, None, f"Exception: {str(e)}"), None

print("=" * 100)
print("ABSOLUTE FINAL COMPREHENSIVE BACKEND TEST - ALL 20 MODULES")
print("=" * 100)
print(f"Backend URL: {BASE_URL}")
print(f"Test User: {EMAIL}")
print(f"Started: {datetime.now().isoformat()}")
print("=" * 100)

# ============================================================================
# PHASE 1: AUTHENTICATION
# ============================================================================
print("\n" + "=" * 100)
print("PHASE 1: AUTHENTICATION & SECURITY")
print("=" * 100)

# Test 1.1: Login
passed, response = test_endpoint(
    "POST", "/auth/login",
    json_data={"email": EMAIL, "password": PASSWORD},
    expected_status=200,
    test_name="Login with production user",
    module="Authentication"
)

if not passed or not response:
    print("\n❌ CRITICAL: Cannot authenticate. Stopping tests.")
    sys.exit(1)

auth_data = response.json()
token = auth_data.get("access_token")
user_id = auth_data.get("user", {}).get("id")
org_id = auth_data.get("user", {}).get("organization_id")

if not token:
    print("\n❌ CRITICAL: No access token received. Stopping tests.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

print(f"\n✅ Authentication successful!")
print(f"   User ID: {user_id}")
print(f"   Organization ID: {org_id}")
print(f"   Token: {token[:20]}...")

# Test 1.2: Get current user profile
test_endpoint(
    "GET", "/users/me",
    headers=headers,
    expected_status=200,
    test_name="Get current user profile",
    module="Authentication"
)

# Test 1.3: Token validation
test_endpoint(
    "GET", "/users/me",
    headers={"Authorization": "Bearer invalid_token"},
    expected_status=401,
    test_name="Invalid token rejection",
    module="Authentication"
)

# ============================================================================
# PHASE 2: CORE MANAGEMENT
# ============================================================================
print("\n" + "=" * 100)
print("PHASE 2: CORE MANAGEMENT (Users, Roles, Organizations)")
print("=" * 100)

# Test 2.1: List users
test_endpoint(
    "GET", "/users",
    headers=headers,
    expected_status=200,
    test_name="List users",
    module="Users"
)

# Test 2.2: List roles
test_endpoint(
    "GET", "/roles",
    headers=headers,
    expected_status=200,
    test_name="List roles",
    module="Roles"
)

# Test 2.3: List permissions
test_endpoint(
    "GET", "/permissions",
    headers=headers,
    expected_status=200,
    test_name="List permissions",
    module="Permissions"
)

# Test 2.4: Organization units
test_endpoint(
    "GET", "/organizations/units",
    headers=headers,
    expected_status=200,
    test_name="List organization units",
    module="Organizations"
)

# Test 2.5: Organization stats (NEW ENDPOINT)
test_endpoint(
    "GET", "/organizations/stats",
    headers=headers,
    expected_status=200,
    test_name="Organization statistics",
    module="Organizations"
)

# ============================================================================
# PHASE 3: OPERATIONAL MODULES (20 MODULES)
# ============================================================================
print("\n" + "=" * 100)
print("PHASE 3: ALL 20 OPERATIONAL MODULES")
print("=" * 100)

# MODULE 1: INSPECTIONS
print("\n--- Module 1: Inspections ---")
test_endpoint(
    "GET", "/inspections/templates",
    headers=headers,
    expected_status=200,
    test_name="List inspection templates",
    module="Inspections"
)

test_endpoint(
    "GET", "/inspections/executions",
    headers=headers,
    expected_status=200,
    test_name="List inspection executions",
    module="Inspections"
)

# Create inspection template
passed, response = test_endpoint(
    "POST", "/inspections/templates",
    headers=headers,
    json_data={
        "name": f"Test Inspection {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test inspection",
        "category": "Safety",
        "sections": [
            {
                "title": "Section 1",
                "questions": [
                    {
                        "text": "Test question?",
                        "type": "yes_no",
                        "required": True
                    }
                ]
            }
        ]
    },
    expected_status=201,
    test_name="Create inspection template",
    module="Inspections"
)

# MODULE 2: CHECKLISTS
print("\n--- Module 2: Checklists ---")
test_endpoint(
    "GET", "/checklists/templates",
    headers=headers,
    expected_status=200,
    test_name="List checklist templates",
    module="Checklists"
)

test_endpoint(
    "GET", "/checklists/executions",
    headers=headers,
    expected_status=200,
    test_name="List checklist executions",
    module="Checklists"
)

# Create checklist template
passed, response = test_endpoint(
    "POST", "/checklists/templates",
    headers=headers,
    json_data={
        "name": f"Test Checklist {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test checklist",
        "category": "Operations",
        "items": [
            {
                "text": "Test item 1",
                "required": True
            }
        ]
    },
    expected_status=201,
    test_name="Create checklist template",
    module="Checklists"
)

# MODULE 3: TASKS
print("\n--- Module 3: Tasks ---")
test_endpoint(
    "GET", "/tasks",
    headers=headers,
    expected_status=200,
    test_name="List tasks",
    module="Tasks"
)

# Create task
passed, response = test_endpoint(
    "POST", "/tasks",
    headers=headers,
    json_data={
        "title": f"Test Task {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test task",
        "priority": "medium",
        "status": "pending",
        "assigned_to": user_id
    },
    expected_status=201,
    test_name="Create task",
    module="Tasks"
)

if passed and response:
    task_id = response.json().get("id")
    
    # Update task
    test_endpoint(
        "PUT", f"/tasks/{task_id}",
        headers=headers,
        json_data={
            "title": f"Updated Test Task {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "in_progress"
        },
        expected_status=200,
        test_name="Update task",
        module="Tasks"
    )
    
    # Delete task
    test_endpoint(
        "DELETE", f"/tasks/{task_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete task",
        module="Tasks"
    )

# MODULE 4: ASSETS
print("\n--- Module 4: Assets ---")
test_endpoint(
    "GET", "/assets",
    headers=headers,
    expected_status=200,
    test_name="List assets",
    module="Assets"
)

# Test asset types alias
test_endpoint(
    "GET", "/assets/types",
    headers=headers,
    expected_status=200,
    test_name="List asset types (alias endpoint)",
    module="Assets"
)

# Create asset (auto-generates asset_tag)
passed, response = test_endpoint(
    "POST", "/assets",
    headers=headers,
    json_data={
        "name": f"Test Asset {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "Equipment",
        "status": "active",
        "location": "Warehouse A"
    },
    expected_status=201,
    test_name="Create asset (auto-generate asset_tag)",
    module="Assets"
)

if passed and response:
    asset_id = response.json().get("id")
    asset_tag = response.json().get("asset_tag")
    print(f"   Asset created with auto-generated tag: {asset_tag}")
    
    # Update asset
    test_endpoint(
        "PUT", f"/assets/{asset_id}",
        headers=headers,
        json_data={
            "name": f"Updated Asset {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "maintenance"
        },
        expected_status=200,
        test_name="Update asset",
        module="Assets"
    )
    
    # Delete asset
    test_endpoint(
        "DELETE", f"/assets/{asset_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete asset",
        module="Assets"
    )

# MODULE 5: WORK ORDERS (CORRECT PATH: /work-orders)
print("\n--- Module 5: Work Orders ---")
test_endpoint(
    "GET", "/work-orders",
    headers=headers,
    expected_status=200,
    test_name="List work orders (correct path)",
    module="Work Orders"
)

# Create work order
passed, response = test_endpoint(
    "POST", "/work-orders",
    headers=headers,
    json_data={
        "title": f"Test Work Order {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test work order",
        "priority": "high",
        "status": "open",
        "assigned_to": user_id
    },
    expected_status=201,
    test_name="Create work order",
    module="Work Orders"
)

if passed and response:
    wo_id = response.json().get("id")
    
    # Update work order
    test_endpoint(
        "PUT", f"/work-orders/{wo_id}",
        headers=headers,
        json_data={
            "status": "in_progress"
        },
        expected_status=200,
        test_name="Update work order",
        module="Work Orders"
    )
    
    # Delete work order
    test_endpoint(
        "DELETE", f"/work-orders/{wo_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete work order",
        module="Work Orders"
    )

# MODULE 6: INVENTORY (CORRECT PATH: /inventory/items)
print("\n--- Module 6: Inventory ---")
test_endpoint(
    "GET", "/inventory/items",
    headers=headers,
    expected_status=200,
    test_name="List inventory items (correct path)",
    module="Inventory"
)

# Create inventory item
passed, response = test_endpoint(
    "POST", "/inventory/items",
    headers=headers,
    json_data={
        "name": f"Test Item {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sku": f"SKU-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "quantity": 100,
        "unit": "pieces",
        "location": "Warehouse B"
    },
    expected_status=201,
    test_name="Create inventory item",
    module="Inventory"
)

if passed and response:
    item_id = response.json().get("id")
    
    # Update inventory item
    test_endpoint(
        "PUT", f"/inventory/items/{item_id}",
        headers=headers,
        json_data={
            "quantity": 150
        },
        expected_status=200,
        test_name="Update inventory item",
        module="Inventory"
    )
    
    # Delete inventory item
    test_endpoint(
        "DELETE", f"/inventory/items/{item_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete inventory item",
        module="Inventory"
    )

# MODULE 7: PROJECTS
print("\n--- Module 7: Projects ---")
test_endpoint(
    "GET", "/projects",
    headers=headers,
    expected_status=200,
    test_name="List projects",
    module="Projects"
)

# Create project
passed, response = test_endpoint(
    "POST", "/projects",
    headers=headers,
    json_data={
        "name": f"Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test project",
        "status": "planning",
        "start_date": datetime.now().isoformat(),
        "manager_id": user_id
    },
    expected_status=201,
    test_name="Create project",
    module="Projects"
)

if passed and response:
    project_id = response.json().get("id")
    
    # Update project
    test_endpoint(
        "PUT", f"/projects/{project_id}",
        headers=headers,
        json_data={
            "status": "in_progress"
        },
        expected_status=200,
        test_name="Update project",
        module="Projects"
    )
    
    # Delete project
    test_endpoint(
        "DELETE", f"/projects/{project_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete project",
        module="Projects"
    )

# MODULE 8: INCIDENTS
print("\n--- Module 8: Incidents ---")
test_endpoint(
    "GET", "/incidents",
    headers=headers,
    expected_status=200,
    test_name="List incidents",
    module="Incidents"
)

# Create incident
passed, response = test_endpoint(
    "POST", "/incidents",
    headers=headers,
    json_data={
        "title": f"Test Incident {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test incident",
        "severity": "medium",
        "status": "open",
        "reported_by": user_id
    },
    expected_status=201,
    test_name="Create incident",
    module="Incidents"
)

if passed and response:
    incident_id = response.json().get("id")
    
    # Update incident
    test_endpoint(
        "PUT", f"/incidents/{incident_id}",
        headers=headers,
        json_data={
            "status": "investigating"
        },
        expected_status=200,
        test_name="Update incident",
        module="Incidents"
    )
    
    # Delete incident
    test_endpoint(
        "DELETE", f"/incidents/{incident_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete incident",
        module="Incidents"
    )

# MODULE 9: TRAINING (CORRECT PATH: /training/courses)
print("\n--- Module 9: Training ---")
test_endpoint(
    "GET", "/training/courses",
    headers=headers,
    expected_status=200,
    test_name="List training courses (correct path)",
    module="Training"
)

# Create training course
passed, response = test_endpoint(
    "POST", "/training/courses",
    headers=headers,
    json_data={
        "title": f"Test Course {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test course",
        "duration_hours": 8,
        "instructor": "Test Instructor"
    },
    expected_status=201,
    test_name="Create training course",
    module="Training"
)

if passed and response:
    course_id = response.json().get("id")
    
    # Update training course
    test_endpoint(
        "PUT", f"/training/courses/{course_id}",
        headers=headers,
        json_data={
            "duration_hours": 10
        },
        expected_status=200,
        test_name="Update training course",
        module="Training"
    )
    
    # Delete training course
    test_endpoint(
        "DELETE", f"/training/courses/{course_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete training course",
        module="Training"
    )

# MODULE 10: FINANCIAL
print("\n--- Module 10: Financial ---")
test_endpoint(
    "GET", "/financial/transactions",
    headers=headers,
    expected_status=200,
    test_name="List financial transactions",
    module="Financial"
)

# Create financial transaction
passed, response = test_endpoint(
    "POST", "/financial/transactions",
    headers=headers,
    json_data={
        "description": f"Test Transaction {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "amount": 1000.00,
        "type": "expense",
        "category": "Operations",
        "date": datetime.now().isoformat()
    },
    expected_status=201,
    test_name="Create financial transaction",
    module="Financial"
)

# MODULE 11: HR (CORRECT: auto-generates employee_number and hire_date)
print("\n--- Module 11: HR ---")
test_endpoint(
    "GET", "/hr/employees",
    headers=headers,
    expected_status=200,
    test_name="List employees",
    module="HR"
)

# Create employee (auto-generates employee_number and hire_date)
passed, response = test_endpoint(
    "POST", "/hr/employees",
    headers=headers,
    json_data={
        "first_name": "Test",
        "last_name": f"Employee{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test.employee.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "position": "Test Position",
        "department": "Testing"
    },
    expected_status=201,
    test_name="Create employee (auto-generate employee_number & hire_date)",
    module="HR"
)

if passed and response:
    employee_id = response.json().get("id")
    employee_number = response.json().get("employee_number")
    hire_date = response.json().get("hire_date")
    print(f"   Employee created with auto-generated number: {employee_number}, hire_date: {hire_date}")
    
    # Update employee
    test_endpoint(
        "PUT", f"/hr/employees/{employee_id}",
        headers=headers,
        json_data={
            "position": "Updated Position"
        },
        expected_status=200,
        test_name="Update employee",
        module="HR"
    )
    
    # Delete employee
    test_endpoint(
        "DELETE", f"/hr/employees/{employee_id}",
        headers=headers,
        expected_status=200,
        test_name="Delete employee",
        module="HR"
    )

# MODULE 12: EMERGENCIES
print("\n--- Module 12: Emergencies ---")
test_endpoint(
    "GET", "/emergencies",
    headers=headers,
    expected_status=200,
    test_name="List emergencies",
    module="Emergencies"
)

# Create emergency
passed, response = test_endpoint(
    "POST", "/emergencies",
    headers=headers,
    json_data={
        "title": f"Test Emergency {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Automated test emergency",
        "severity": "high",
        "status": "active",
        "location": "Building A"
    },
    expected_status=201,
    test_name="Create emergency",
    module="Emergencies"
)

# MODULE 13: TEAM CHAT
print("\n--- Module 13: Team Chat ---")
test_endpoint(
    "GET", "/chat/channels",
    headers=headers,
    expected_status=200,
    test_name="List chat channels",
    module="Team Chat"
)

# MODULE 14: CONTRACTORS
print("\n--- Module 14: Contractors ---")
test_endpoint(
    "GET", "/contractors",
    headers=headers,
    expected_status=200,
    test_name="List contractors",
    module="Contractors"
)

# Create contractor
passed, response = test_endpoint(
    "POST", "/contractors",
    headers=headers,
    json_data={
        "name": f"Test Contractor {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "company": "Test Company",
        "email": f"contractor.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "phone": "+1234567890",
        "specialty": "Testing"
    },
    expected_status=201,
    test_name="Create contractor",
    module="Contractors"
)

# MODULE 15: ANNOUNCEMENTS
print("\n--- Module 15: Announcements ---")
test_endpoint(
    "GET", "/announcements",
    headers=headers,
    expected_status=200,
    test_name="List announcements",
    module="Announcements"
)

# Create announcement
passed, response = test_endpoint(
    "POST", "/announcements",
    headers=headers,
    json_data={
        "title": f"Test Announcement {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "content": "Automated test announcement",
        "priority": "normal"
    },
    expected_status=201,
    test_name="Create announcement",
    module="Announcements"
)

# MODULE 16: GROUPS
print("\n--- Module 16: Groups ---")
test_endpoint(
    "GET", "/groups",
    headers=headers,
    expected_status=200,
    test_name="List groups",
    module="Groups"
)

# MODULE 17: INVITATIONS
print("\n--- Module 17: Invitations ---")
test_endpoint(
    "GET", "/invitations",
    headers=headers,
    expected_status=200,
    test_name="List invitations",
    module="Invitations"
)

# MODULE 18: WORKFLOWS
print("\n--- Module 18: Workflows ---")
test_endpoint(
    "GET", "/workflows",
    headers=headers,
    expected_status=200,
    test_name="List workflows",
    module="Workflows"
)

# MODULE 19: REPORTS
print("\n--- Module 19: Reports ---")
test_endpoint(
    "GET", "/reports/overview",
    headers=headers,
    expected_status=200,
    test_name="Reports overview",
    module="Reports"
)

# MODULE 20: AUDIT LOGS
print("\n--- Module 20: Audit Logs ---")
test_endpoint(
    "GET", "/audit/logs",
    headers=headers,
    expected_status=200,
    test_name="List audit logs",
    module="Audit Logs"
)

# ============================================================================
# PHASE 4: ADVANCED FEATURES
# ============================================================================
print("\n" + "=" * 100)
print("PHASE 4: ADVANCED FEATURES")
print("=" * 100)

# DASHBOARDS (CORRECT PATH: /dashboards/*)
print("\n--- Dashboards ---")
test_endpoint(
    "GET", "/dashboards/main",
    headers=headers,
    expected_status=200,
    test_name="Main dashboard (correct path)",
    module="Dashboards"
)

test_endpoint(
    "GET", "/dashboards/operations",
    headers=headers,
    expected_status=200,
    test_name="Operations dashboard",
    module="Dashboards"
)

test_endpoint(
    "GET", "/dashboards/financial",
    headers=headers,
    expected_status=200,
    test_name="Financial dashboard",
    module="Dashboards"
)

# SEARCH (CORRECT PATHS: /search OR /search/global)
print("\n--- Search ---")
test_endpoint(
    "GET", "/search?q=test",
    headers=headers,
    expected_status=200,
    test_name="Search endpoint (alias)",
    module="Search"
)

test_endpoint(
    "GET", "/search/global?q=test",
    headers=headers,
    expected_status=200,
    test_name="Global search endpoint",
    module="Search"
)

# WEBHOOKS
print("\n--- Webhooks ---")
test_endpoint(
    "GET", "/webhooks",
    headers=headers,
    expected_status=200,
    test_name="List webhooks",
    module="Webhooks"
)

# BULK IMPORT (CORRECT PATHS: /bulk-import/template OR /bulk-import/users/template)
print("\n--- Bulk Import ---")
test_endpoint(
    "GET", "/bulk-import/template",
    headers=headers,
    expected_status=200,
    test_name="Bulk import template (alias)",
    module="Bulk Import"
)

test_endpoint(
    "GET", "/bulk-import/users/template",
    headers=headers,
    expected_status=200,
    test_name="Bulk import users template",
    module="Bulk Import"
)

# NOTIFICATIONS
print("\n--- Notifications ---")
test_endpoint(
    "GET", "/notifications",
    headers=headers,
    expected_status=200,
    test_name="List notifications",
    module="Notifications"
)

# TIME TRACKING
print("\n--- Time Tracking ---")
test_endpoint(
    "GET", "/time-tracking/entries",
    headers=headers,
    expected_status=200,
    test_name="List time tracking entries",
    module="Time Tracking"
)

# ANALYTICS
print("\n--- Analytics ---")
test_endpoint(
    "GET", "/analytics/overview",
    headers=headers,
    expected_status=200,
    test_name="Analytics overview",
    module="Analytics"
)

# ============================================================================
# FINAL RESULTS
# ============================================================================
print("\n" + "=" * 100)
print("FINAL RESULTS")
print("=" * 100)

success_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0

print(f"\nTotal Tests: {results['total']}")
print(f"Passed: {results['passed']} ✅")
print(f"Failed: {results['failed']} ❌")
print(f"Success Rate: {success_rate:.1f}%")

# Group results by module
modules = {}
for test in results["tests"]:
    module = test["module"]
    if module not in modules:
        modules[module] = {"total": 0, "passed": 0, "failed": 0}
    modules[module]["total"] += 1
    if test["passed"]:
        modules[module]["passed"] += 1
    else:
        modules[module]["failed"] += 1

print("\n" + "=" * 100)
print("MODULE-BY-MODULE BREAKDOWN")
print("=" * 100)

for module, stats in sorted(modules.items()):
    module_success = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    status = "✅" if module_success >= 90 else "⚠️" if module_success >= 70 else "❌"
    print(f"{status} {module:20s} | {stats['passed']:2d}/{stats['total']:2d} passed | {module_success:5.1f}%")

print("\n" + "=" * 100)
print("FAILED TESTS DETAILS")
print("=" * 100)

failed_tests = [t for t in results["tests"] if not t["passed"]]
if failed_tests:
    for test in failed_tests:
        print(f"\n❌ {test['module']} | {test['test']}")
        print(f"   Status Code: {test['status_code']}")
        print(f"   Message: {test['message']}")
else:
    print("\n🎉 NO FAILED TESTS!")

print("\n" + "=" * 100)
print(f"FINAL VERDICT: {'✅ PASS' if success_rate >= 95 else '⚠️ NEEDS IMPROVEMENT' if success_rate >= 85 else '❌ FAIL'}")
print(f"Target: 95%+ | Achieved: {success_rate:.1f}%")
print("=" * 100)

# Exit with appropriate code
sys.exit(0 if success_rate >= 95 else 1)
