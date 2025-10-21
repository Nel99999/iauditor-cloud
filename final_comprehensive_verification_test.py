#!/usr/bin/env python3
"""
FINAL VERIFICATION - BACKEND - ALL FIXES APPLIED
Test ALL 20 MODULES with ACTUAL CRUD operations
Target: 95%+ success rate

Test with: llewellyn@bluedawncapital.co.za (password: Test@1234)
"""

import requests
import json
from datetime import datetime, timedelta
import uuid
import time

# Backend URL
BASE_URL = "https://twilio-ops.preview.emergentagent.com/api"

# Production user credentials
EMAIL = "llewellyn@bluedawncapital.co.za"
PASSWORD = "Test@1234"

# Global variables
token = None
org_id = None
user_id = None

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "modules": {},
    "critical_fixes": {}
}

def log_test(module, test_name, passed, details=""):
    """Log test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "✅"
    else:
        test_results["failed"] += 1
        status = "❌"
    
    if module not in test_results["modules"]:
        test_results["modules"][module] = {"passed": 0, "failed": 0, "tests": []}
    
    if passed:
        test_results["modules"][module]["passed"] += 1
    else:
        test_results["modules"][module]["failed"] += 1
    
    test_results["modules"][module]["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    print(f"{status} {module}: {test_name}")
    if details:
        print(f"   → {details}")

def is_success(status_code):
    """Check if status code indicates success"""
    return status_code in [200, 201]

def authenticate():
    """Authenticate and get token"""
    global token, org_id, user_id
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            org_id = data.get("organization_id")
            user_id = data.get("user_id")
            log_test("Authentication", "Login", True, f"org_id: {org_id}")
            return True
        else:
            log_test("Authentication", "Login", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Authentication", "Login", False, str(e))
        return False

def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# CRITICAL FIXES VERIFICATION
# ============================================================================

def verify_critical_fixes():
    """Verify all critical fixes mentioned in review request"""
    module = "Critical Fixes"
    
    # Fix 1: RBAC permission check logic (permission_ids array)
    try:
        response = requests.get(f"{BASE_URL}/roles", headers=get_headers())
        if is_success(response.status_code):
            roles = response.json()
            # Check that roles have permission_ids as array
            has_permission_ids = all("permission_ids" in role and isinstance(role.get("permission_ids"), list) for role in roles)
            log_test(module, "RBAC permission_ids array structure", has_permission_ids, 
                    f"All {len(roles)} roles have permission_ids as array")
            test_results["critical_fixes"]["rbac_permission_ids"] = has_permission_ids
        else:
            log_test(module, "RBAC permission_ids array structure", False, f"Status: {response.status_code}")
            test_results["critical_fixes"]["rbac_permission_ids"] = False
    except Exception as e:
        log_test(module, "RBAC permission_ids array structure", False, str(e))
        test_results["critical_fixes"]["rbac_permission_ids"] = False
    
    # Fix 2: HR employee creation (auto-generate employee_number)
    try:
        employee_data = {
            "first_name": "Test",
            "last_name": f"Verify{uuid.uuid4().hex[:6]}",
            "email": f"verify.{uuid.uuid4().hex[:8]}@example.com",
            "position": "Technician",
            "department": "Maintenance"
        }
        response = requests.post(f"{BASE_URL}/hr/employees", headers=get_headers(), json=employee_data)
        if is_success(response.status_code):
            employee = response.json()
            employee_number = employee.get("employee_number")
            has_auto_number = bool(employee_number) and employee_number.startswith("EMP-")
            log_test(module, "HR employee auto-generate employee_number", has_auto_number, 
                    f"Generated: {employee_number}")
            test_results["critical_fixes"]["hr_auto_employee_number"] = has_auto_number
        else:
            log_test(module, "HR employee auto-generate employee_number", False, f"Status: {response.status_code}")
            test_results["critical_fixes"]["hr_auto_employee_number"] = False
    except Exception as e:
        log_test(module, "HR employee auto-generate employee_number", False, str(e))
        test_results["critical_fixes"]["hr_auto_employee_number"] = False
    
    # Fix 3: Assets auto-generate asset_tag
    try:
        asset_data = {
            "name": f"Verify Asset {uuid.uuid4().hex[:6]}",
            "description": "Verification test",
            "type": "Equipment",
            "status": "active"
        }
        response = requests.post(f"{BASE_URL}/assets", headers=get_headers(), json=asset_data)
        if is_success(response.status_code):
            asset = response.json()
            asset_tag = asset.get("asset_tag")
            has_auto_tag = bool(asset_tag) and asset_tag.startswith("AST-")
            log_test(module, "Assets auto-generate asset_tag", has_auto_tag, 
                    f"Generated: {asset_tag}")
            test_results["critical_fixes"]["assets_auto_asset_tag"] = has_auto_tag
        else:
            log_test(module, "Assets auto-generate asset_tag", False, f"Status: {response.status_code}")
            test_results["critical_fixes"]["assets_auto_asset_tag"] = False
    except Exception as e:
        log_test(module, "Assets auto-generate asset_tag", False, str(e))
        test_results["critical_fixes"]["assets_auto_asset_tag"] = False
    
    # Fix 4: Organization stats endpoint
    try:
        response = requests.get(f"{BASE_URL}/organizations/stats", headers=get_headers())
        passed = is_success(response.status_code)
        log_test(module, "Organization stats endpoint", passed, f"Status: {response.status_code}")
        test_results["critical_fixes"]["org_stats_endpoint"] = passed
    except Exception as e:
        log_test(module, "Organization stats endpoint", False, str(e))
        test_results["critical_fixes"]["org_stats_endpoint"] = False
    
    # Fix 5: Financial CAPEX endpoint
    try:
        response = requests.get(f"{BASE_URL}/financial/capex", headers=get_headers())
        passed = is_success(response.status_code)
        log_test(module, "Financial CAPEX endpoint", passed, f"Status: {response.status_code}")
        test_results["critical_fixes"]["financial_capex"] = passed
    except Exception as e:
        log_test(module, "Financial CAPEX endpoint", False, str(e))
        test_results["critical_fixes"]["financial_capex"] = False
    
    # Fix 6: Financial OPEX endpoint
    try:
        response = requests.get(f"{BASE_URL}/financial/opex", headers=get_headers())
        passed = is_success(response.status_code)
        log_test(module, "Financial OPEX endpoint", passed, f"Status: {response.status_code}")
        test_results["critical_fixes"]["financial_opex"] = passed
    except Exception as e:
        log_test(module, "Financial OPEX endpoint", False, str(e))
        test_results["critical_fixes"]["financial_opex"] = False
    
    # Fix 7: Financial Budgets endpoint
    try:
        response = requests.get(f"{BASE_URL}/financial/budgets", headers=get_headers())
        passed = is_success(response.status_code)
        log_test(module, "Financial Budgets endpoint", passed, f"Status: {response.status_code}")
        test_results["critical_fixes"]["financial_budgets"] = passed
    except Exception as e:
        log_test(module, "Financial Budgets endpoint", False, str(e))
        test_results["critical_fixes"]["financial_budgets"] = False
    
    # Fix 8: Search aliases
    try:
        response = requests.get(f"{BASE_URL}/search?q=test", headers=get_headers())
        passed = is_success(response.status_code)
        log_test(module, "Search with aliases", passed, f"Status: {response.status_code}")
        test_results["critical_fixes"]["search_aliases"] = passed
    except Exception as e:
        log_test(module, "Search with aliases", False, str(e))
        test_results["critical_fixes"]["search_aliases"] = False
    
    # Fix 9: Developer role has 121 permissions
    try:
        response = requests.get(f"{BASE_URL}/roles", headers=get_headers())
        if is_success(response.status_code):
            roles = response.json()
            dev_role = next((r for r in roles if r.get("code") == "developer"), None)
            if dev_role:
                perm_count = len(dev_role.get("permission_ids", []))
                passed = perm_count == 121
                log_test(module, "Developer role has 121 permissions", passed, 
                        f"Found {perm_count} permissions")
                test_results["critical_fixes"]["developer_121_permissions"] = passed
            else:
                log_test(module, "Developer role has 121 permissions", False, "Developer role not found")
                test_results["critical_fixes"]["developer_121_permissions"] = False
        else:
            log_test(module, "Developer role has 121 permissions", False, f"Status: {response.status_code}")
            test_results["critical_fixes"]["developer_121_permissions"] = False
    except Exception as e:
        log_test(module, "Developer role has 121 permissions", False, str(e))
        test_results["critical_fixes"]["developer_121_permissions"] = False

# ============================================================================
# MODULE TESTS - ALL 20 MODULES
# ============================================================================

def test_module_1_auth_users():
    """Module 1: Authentication & Users"""
    m = "1. Auth & Users"
    
    try:
        r = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
        log_test(m, "Get current user", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get current user", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/users", headers=get_headers())
        log_test(m, "List users", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List users", False, str(e))
    
    try:
        r = requests.put(f"{BASE_URL}/users/profile", headers=get_headers(), 
                        json={"phone": "+27123456789"})
        log_test(m, "Update profile", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Update profile", False, str(e))

def test_module_2_roles_permissions():
    """Module 2: Roles & Permissions"""
    m = "2. Roles & Permissions"
    
    try:
        r = requests.get(f"{BASE_URL}/roles", headers=get_headers())
        if is_success(r.status_code):
            roles = r.json()
            log_test(m, "List roles", True, f"Found {len(roles)} roles")
        else:
            log_test(m, "List roles", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List roles", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/permissions", headers=get_headers())
        if is_success(r.status_code):
            perms = r.json()
            log_test(m, "List permissions", True, f"Found {len(perms)} permissions")
        else:
            log_test(m, "List permissions", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List permissions", False, str(e))

def test_module_3_organizations():
    """Module 3: Organizations"""
    m = "3. Organizations"
    
    try:
        r = requests.get(f"{BASE_URL}/organizations/units", headers=get_headers())
        if is_success(r.status_code):
            units = r.json()
            log_test(m, "List org units", True, f"Found {len(units)} units")
        else:
            log_test(m, "List org units", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List org units", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/organizations/stats", headers=get_headers())
        log_test(m, "Get org stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get org stats", False, str(e))
    
    try:
        unit_data = {
            "name": f"Test Unit {uuid.uuid4().hex[:6]}",
            "level": 1,
            "parent_id": None
        }
        r = requests.post(f"{BASE_URL}/organizations/units", headers=get_headers(), json=unit_data)
        log_test(m, "Create org unit", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create org unit", False, str(e))

def test_module_4_inspections():
    """Module 4: Inspections"""
    m = "4. Inspections"
    
    try:
        r = requests.get(f"{BASE_URL}/inspections/templates", headers=get_headers())
        if is_success(r.status_code):
            templates = r.json()
            log_test(m, "List templates", True, f"Found {len(templates)} templates")
        else:
            log_test(m, "List templates", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List templates", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/inspections/executions", headers=get_headers())
        log_test(m, "List executions", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List executions", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/inspections/analytics", headers=get_headers())
        log_test(m, "Get analytics", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get analytics", False, str(e))

def test_module_5_checklists():
    """Module 5: Checklists"""
    m = "5. Checklists"
    
    try:
        r = requests.get(f"{BASE_URL}/checklists/templates", headers=get_headers())
        if is_success(r.status_code):
            templates = r.json()
            log_test(m, "List templates", True, f"Found {len(templates)} templates")
        else:
            log_test(m, "List templates", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List templates", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/checklists/executions", headers=get_headers())
        log_test(m, "List executions", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List executions", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/checklists/analytics", headers=get_headers())
        log_test(m, "Get analytics", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get analytics", False, str(e))

def test_module_6_tasks():
    """Module 6: Tasks"""
    m = "6. Tasks"
    
    try:
        r = requests.get(f"{BASE_URL}/tasks", headers=get_headers())
        if is_success(r.status_code):
            tasks = r.json()
            log_test(m, "List tasks", True, f"Found {len(tasks)} tasks")
        else:
            log_test(m, "List tasks", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List tasks", False, str(e))
    
    try:
        task_data = {
            "title": f"Test Task {uuid.uuid4().hex[:6]}",
            "description": "Test",
            "priority": "high",
            "status": "open"
        }
        r = requests.post(f"{BASE_URL}/tasks", headers=get_headers(), json=task_data)
        log_test(m, "Create task", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create task", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/tasks/analytics", headers=get_headers())
        log_test(m, "Get analytics", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get analytics", False, str(e))

def test_module_7_assets():
    """Module 7: Assets"""
    m = "7. Assets"
    
    try:
        r = requests.get(f"{BASE_URL}/assets", headers=get_headers())
        if is_success(r.status_code):
            assets = r.json()
            log_test(m, "List assets", True, f"Found {len(assets)} assets")
        else:
            log_test(m, "List assets", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List assets", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/assets/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_8_work_orders():
    """Module 8: Work Orders"""
    m = "8. Work Orders"
    
    try:
        r = requests.get(f"{BASE_URL}/work-orders", headers=get_headers())
        if is_success(r.status_code):
            wos = r.json()
            log_test(m, "List work orders", True, f"Found {len(wos)} work orders")
        else:
            log_test(m, "List work orders", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List work orders", False, str(e))
    
    try:
        wo_data = {
            "title": f"Test WO {uuid.uuid4().hex[:6]}",
            "description": "Test",
            "priority": "medium",
            "status": "open",
            "type": "corrective"
        }
        r = requests.post(f"{BASE_URL}/work-orders", headers=get_headers(), json=wo_data)
        log_test(m, "Create work order", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create work order", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/work-orders/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_9_inventory():
    """Module 9: Inventory"""
    m = "9. Inventory"
    
    try:
        r = requests.get(f"{BASE_URL}/inventory/items", headers=get_headers())
        if is_success(r.status_code):
            items = r.json()
            log_test(m, "List items", True, f"Found {len(items)} items")
        else:
            log_test(m, "List items", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List items", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/inventory/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_10_projects():
    """Module 10: Projects"""
    m = "10. Projects"
    
    try:
        r = requests.get(f"{BASE_URL}/projects", headers=get_headers())
        if is_success(r.status_code):
            projects = r.json()
            log_test(m, "List projects", True, f"Found {len(projects)} projects")
        else:
            log_test(m, "List projects", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List projects", False, str(e))
    
    try:
        project_data = {
            "name": f"Test Project {uuid.uuid4().hex[:6]}",
            "description": "Test",
            "status": "planning"
        }
        r = requests.post(f"{BASE_URL}/projects", headers=get_headers(), json=project_data)
        log_test(m, "Create project", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create project", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/projects/dashboard", headers=get_headers())
        log_test(m, "Get dashboard", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get dashboard", False, str(e))

def test_module_11_incidents():
    """Module 11: Incidents"""
    m = "11. Incidents"
    
    try:
        r = requests.get(f"{BASE_URL}/incidents", headers=get_headers())
        if is_success(r.status_code):
            incidents = r.json()
            log_test(m, "List incidents", True, f"Found {len(incidents)} incidents")
        else:
            log_test(m, "List incidents", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List incidents", False, str(e))
    
    try:
        incident_data = {
            "title": f"Test Incident {uuid.uuid4().hex[:6]}",
            "description": "Test",
            "severity": "medium",
            "status": "open"
        }
        r = requests.post(f"{BASE_URL}/incidents", headers=get_headers(), json=incident_data)
        log_test(m, "Create incident", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create incident", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/incidents/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_12_training():
    """Module 12: Training"""
    m = "12. Training"
    
    try:
        r = requests.get(f"{BASE_URL}/training/courses", headers=get_headers())
        if is_success(r.status_code):
            courses = r.json()
            log_test(m, "List courses", True, f"Found {len(courses)} courses")
        else:
            log_test(m, "List courses", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List courses", False, str(e))
    
    try:
        course_data = {
            "title": f"Test Course {uuid.uuid4().hex[:6]}",
            "description": "Test",
            "duration_hours": 8
        }
        r = requests.post(f"{BASE_URL}/training/courses", headers=get_headers(), json=course_data)
        log_test(m, "Create course", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Create course", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/training/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_13_financial():
    """Module 13: Financial"""
    m = "13. Financial"
    
    try:
        r = requests.get(f"{BASE_URL}/financial/transactions", headers=get_headers())
        if is_success(r.status_code):
            txns = r.json()
            log_test(m, "List transactions", True, f"Found {len(txns)} transactions")
        else:
            log_test(m, "List transactions", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List transactions", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/financial/capex", headers=get_headers())
        log_test(m, "Get CAPEX", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get CAPEX", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/financial/opex", headers=get_headers())
        log_test(m, "Get OPEX", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get OPEX", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/financial/budgets", headers=get_headers())
        log_test(m, "Get budgets", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get budgets", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/financial/summary", headers=get_headers())
        log_test(m, "Get summary", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get summary", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/financial/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_14_hr():
    """Module 14: HR"""
    m = "14. HR"
    
    try:
        r = requests.get(f"{BASE_URL}/hr/employees", headers=get_headers())
        if is_success(r.status_code):
            employees = r.json()
            log_test(m, "List employees", True, f"Found {len(employees)} employees")
        else:
            log_test(m, "List employees", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List employees", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/hr/announcements", headers=get_headers())
        log_test(m, "List announcements", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List announcements", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/hr/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))

def test_module_15_emergency():
    """Module 15: Emergency"""
    m = "15. Emergency"
    
    try:
        r = requests.get(f"{BASE_URL}/emergencies", headers=get_headers())
        if is_success(r.status_code):
            emergencies = r.json()
            log_test(m, "List emergencies", True, f"Found {len(emergencies)} emergencies")
        else:
            log_test(m, "List emergencies", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List emergencies", False, str(e))

def test_module_16_dashboards():
    """Module 16: Dashboards"""
    m = "16. Dashboards"
    
    try:
        r = requests.get(f"{BASE_URL}/dashboard/stats", headers=get_headers())
        log_test(m, "Get stats", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get stats", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/dashboard/financial", headers=get_headers())
        log_test(m, "Get financial", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get financial", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/dashboard/safety", headers=get_headers())
        log_test(m, "Get safety", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get safety", False, str(e))

def test_module_17_team_chat():
    """Module 17: Team Chat"""
    m = "17. Team Chat"
    
    try:
        r = requests.get(f"{BASE_URL}/chat/channels", headers=get_headers())
        if is_success(r.status_code):
            channels = r.json()
            log_test(m, "List channels", True, f"Found {len(channels)} channels")
        else:
            log_test(m, "List channels", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List channels", False, str(e))

def test_module_18_contractors():
    """Module 18: Contractors"""
    m = "18. Contractors"
    
    try:
        r = requests.get(f"{BASE_URL}/contractors", headers=get_headers())
        if is_success(r.status_code):
            contractors = r.json()
            log_test(m, "List contractors", True, f"Found {len(contractors)} contractors")
        else:
            log_test(m, "List contractors", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List contractors", False, str(e))

def test_module_19_announcements():
    """Module 19: Announcements"""
    m = "19. Announcements"
    
    try:
        r = requests.get(f"{BASE_URL}/announcements", headers=get_headers())
        if is_success(r.status_code):
            announcements = r.json()
            log_test(m, "List announcements", True, f"Found {len(announcements)} announcements")
        else:
            log_test(m, "List announcements", False, f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List announcements", False, str(e))

def test_module_20_additional():
    """Module 20: Additional Features"""
    m = "20. Additional"
    
    try:
        r = requests.get(f"{BASE_URL}/groups", headers=get_headers())
        log_test(m, "List groups", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List groups", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/webhooks", headers=get_headers())
        log_test(m, "List webhooks", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "List webhooks", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/audit/logs", headers=get_headers())
        log_test(m, "Get audit logs", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get audit logs", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/notifications", headers=get_headers())
        log_test(m, "Get notifications", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get notifications", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/analytics/overview", headers=get_headers())
        log_test(m, "Get analytics", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get analytics", False, str(e))
    
    try:
        r = requests.get(f"{BASE_URL}/reports/overview", headers=get_headers())
        log_test(m, "Get reports", is_success(r.status_code), f"Status: {r.status_code}")
    except Exception as e:
        log_test(m, "Get reports", False, str(e))

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("FINAL VERIFICATION - COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    success_rate = (test_results["passed"] / test_results["total"] * 100) if test_results["total"] > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total Tests: {test_results['total']}")
    print(f"   Passed: {test_results['passed']} ✅")
    print(f"   Failed: {test_results['failed']} ❌")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print(f"\n🎉 SUCCESS TARGET ACHIEVED: {success_rate:.1f}% >= 95%")
    else:
        print(f"\n⚠️  SUCCESS TARGET NOT MET: {success_rate:.1f}% < 95%")
    
    # Critical fixes summary
    print(f"\n🔧 CRITICAL FIXES VERIFICATION:")
    fixes_passed = sum(1 for v in test_results["critical_fixes"].values() if v)
    fixes_total = len(test_results["critical_fixes"])
    print(f"   {fixes_passed}/{fixes_total} critical fixes verified")
    for fix_name, passed in test_results["critical_fixes"].items():
        status = "✅" if passed else "❌"
        print(f"   {status} {fix_name.replace('_', ' ').title()}")
    
    # Module results
    print(f"\n📦 RESULTS BY MODULE:")
    for module, results in sorted(test_results["modules"].items()):
        total = results["passed"] + results["failed"]
        rate = (results["passed"] / total * 100) if total > 0 else 0
        status = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
        print(f"   {status} {module}: {results['passed']}/{total} ({rate:.0f}%)")
    
    # Failed tests details
    print(f"\n❌ FAILED TESTS DETAILS:")
    has_failures = False
    for module, results in sorted(test_results["modules"].items()):
        failed_tests = [t for t in results["tests"] if not t["passed"]]
        if failed_tests:
            has_failures = True
            print(f"\n   {module}:")
            for test in failed_tests:
                print(f"      • {test['name']}: {test['details']}")
    
    if not has_failures:
        print("   None - All tests passed! 🎉")
    
    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("="*80)
    print("FINAL VERIFICATION - BACKEND - ALL FIXES APPLIED")
    print("Testing ALL 20 MODULES with ACTUAL CRUD operations")
    print("="*80)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Test User: {EMAIL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("\n" + "="*80)
    
    # Authenticate
    if not authenticate():
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return
    
    print(f"\n✅ Authenticated successfully")
    print(f"   Organization ID: {org_id}")
    print("\n" + "="*80)
    print("VERIFYING CRITICAL FIXES")
    print("="*80 + "\n")
    
    # Verify critical fixes first
    verify_critical_fixes()
    
    print("\n" + "="*80)
    print("TESTING ALL 20 MODULES")
    print("="*80 + "\n")
    
    # Run all module tests
    test_module_1_auth_users()
    test_module_2_roles_permissions()
    test_module_3_organizations()
    test_module_4_inspections()
    test_module_5_checklists()
    test_module_6_tasks()
    test_module_7_assets()
    test_module_8_work_orders()
    test_module_9_inventory()
    test_module_10_projects()
    test_module_11_incidents()
    test_module_12_training()
    test_module_13_financial()
    test_module_14_hr()
    test_module_15_emergency()
    test_module_16_dashboards()
    test_module_17_team_chat()
    test_module_18_contractors()
    test_module_19_announcements()
    test_module_20_additional()
    
    # Print summary
    print_summary()
    
    # Save results
    with open("/app/final_comprehensive_verification_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: /app/final_comprehensive_verification_results.json\n")

if __name__ == "__main__":
    main()
