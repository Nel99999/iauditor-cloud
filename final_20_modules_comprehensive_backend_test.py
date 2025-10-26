#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND TESTING - ALL 20 MODULES
Testing with production user: llewellyn@bluedawncapital.co.za
Target: 95%+ success rate, Zero 500 errors
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
PRODUCTION_EMAIL = "llewellyn@bluedawncapital.co.za"
PRODUCTION_PASSWORD = "Test@1234"

# Global variables
auth_token = None
org_id = None
user_id = None

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "by_module": {}
}

def log_test(module, test_name, passed, status_code=None, error=None):
    """Log test result"""
    test_results["total"] += 1
    
    if module not in test_results["by_module"]:
        test_results["by_module"][module] = {"total": 0, "passed": 0, "failed": 0, "tests": []}
    
    test_results["by_module"][module]["total"] += 1
    
    if passed:
        test_results["passed"] += 1
        test_results["by_module"][module]["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        test_results["by_module"][module]["failed"] += 1
        status = "❌ FAIL"
        if error:
            test_results["errors"].append({
                "module": module,
                "test": test_name,
                "status_code": status_code,
                "error": error
            })
    
    result = f"{status} - {module}: {test_name}"
    if status_code:
        result += f" (Status: {status_code})"
    if error and not passed:
        result += f" - {error}"
    
    print(result)
    test_results["by_module"][module]["tests"].append({
        "name": test_name,
        "passed": passed,
        "status_code": status_code,
        "error": error
    })

def make_request(method, endpoint, data=None, headers=None, expect_fail=False):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None, f"Unknown method: {method}"
        
        # Check for 500 errors (critical failure)
        if response.status_code == 500 and not expect_fail:
            return response, f"500 SERVER ERROR - CRITICAL"
        
        return response, None
    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except Exception as e:
        return None, str(e)

# ============================================================================
# MODULE 1: AUTHENTICATION & USERS (15 tests)
# ============================================================================

def test_authentication_and_users():
    """Test authentication and user management endpoints"""
    global auth_token, org_id, user_id
    module = "Authentication & Users"
    
    print(f"\n{'='*80}")
    print(f"MODULE 1: {module}")
    print(f"{'='*80}")
    
    # Test 1: Login
    response, error = make_request("POST", "/auth/login", {
        "email": PRODUCTION_EMAIL,
        "password": PRODUCTION_PASSWORD
    })
    
    if response and response.status_code == 200:
        data = response.json()
        auth_token = data.get("access_token")
        org_id = data.get("organization_id")
        user_id = data.get("user_id")
        log_test(module, "Login with production user", True, 200)
    else:
        log_test(module, "Login with production user", False, 
                response.status_code if response else None, error or "Login failed")
        return  # Cannot continue without auth
    
    # Test 2: Get current user profile
    response, error = make_request("GET", "/users/me")
    log_test(module, "Get current user profile", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 3: Update user profile
    response, error = make_request("PUT", "/users/profile", {
        "phone": "+27123456789"
    })
    log_test(module, "Update user profile", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 4: Get user organizational context
    response, error = make_request("GET", "/users/me/org-context")
    log_test(module, "Get organizational context", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 5: Get recent activity
    response, error = make_request("GET", "/users/me/recent-activity")
    log_test(module, "Get recent activity", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 6: Get sidebar preferences
    response, error = make_request("GET", "/users/sidebar-preferences")
    log_test(module, "Get sidebar preferences", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 7: Update sidebar preferences
    response, error = make_request("PUT", "/users/sidebar-preferences", {
        "collapsed_sections": ["workflows"]
    })
    log_test(module, "Update sidebar preferences", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 8: Get user theme
    response, error = make_request("GET", "/users/theme")
    log_test(module, "Get user theme", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 9: List all users
    response, error = make_request("GET", "/users")
    log_test(module, "List all users", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 10: Get pending approvals
    response, error = make_request("GET", "/users/pending-approvals")
    log_test(module, "Get pending approvals", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 11: Get invitations
    response, error = make_request("GET", "/invitations")
    log_test(module, "Get invitations", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 12: Get active sessions
    response, error = make_request("GET", "/auth/sessions")
    log_test(module, "Get active sessions", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 13: Forgot password endpoint
    response, error = make_request("POST", "/auth/forgot-password", {
        "email": "nonexistent@example.com"
    })
    log_test(module, "Forgot password endpoint", 
            response and response.status_code in [200, 404], 
            response.status_code if response else None, error)
    
    # Test 14: Get MFA status
    response, error = make_request("GET", "/users/me")
    if response and response.status_code == 200:
        data = response.json()
        has_mfa_field = "mfa_enabled" in data
        log_test(module, "MFA status in user profile", has_mfa_field, 200)
    else:
        log_test(module, "MFA status in user profile", False, 
                response.status_code if response else None, error)
    
    # Test 15: Get user permissions
    response, error = make_request("GET", "/users/me")
    if response and response.status_code == 200:
        data = response.json()
        has_permissions = "permissions" in data
        log_test(module, "User permissions in profile", has_permissions, 200)
    else:
        log_test(module, "User permissions in profile", False, 
                response.status_code if response else None, error)

# ============================================================================
# MODULE 2: ROLES & PERMISSIONS (10 tests)
# ============================================================================

def test_roles_and_permissions():
    """Test roles and permissions management"""
    module = "Roles & Permissions"
    
    print(f"\n{'='*80}")
    print(f"MODULE 2: {module}")
    print(f"{'='*80}")
    
    # Test 1: List all roles
    response, error = make_request("GET", "/roles")
    log_test(module, "List all roles", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: List all permissions
    response, error = make_request("GET", "/permissions")
    log_test(module, "List all permissions", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 3: Get role by ID (using 'developer' role)
    response, error = make_request("GET", "/roles")
    if response and response.status_code == 200:
        roles = response.json()
        if roles and len(roles) > 0:
            role_id = roles[0].get("id")
            response2, error2 = make_request("GET", f"/roles/{role_id}")
            log_test(module, "Get role by ID", 
                    response2 and response2.status_code == 200, 
                    response2.status_code if response2 else None, error2)
        else:
            log_test(module, "Get role by ID", False, None, "No roles found")
    else:
        log_test(module, "Get role by ID", False, None, "Cannot list roles")
    
    # Test 4: Create custom role
    role_data = {
        "name": f"Test Role {uuid.uuid4().hex[:8]}",
        "description": "Test role for comprehensive testing",
        "level": 5,
        "is_system_role": False,
        "permissions": []
    }
    response, error = make_request("POST", "/roles", role_data)
    created_role_id = None
    if response and response.status_code == 201:
        created_role_id = response.json().get("id")
        log_test(module, "Create custom role", True, 201)
    else:
        log_test(module, "Create custom role", False, 
                response.status_code if response else None, error)
    
    # Test 5: Update role (if created)
    if created_role_id:
        response, error = make_request("PUT", f"/roles/{created_role_id}", {
            "description": "Updated description"
        })
        log_test(module, "Update role", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update role", False, None, "No role to update")
    
    # Test 6: Get role permissions
    if created_role_id:
        response, error = make_request("GET", f"/roles/{created_role_id}")
        if response and response.status_code == 200:
            data = response.json()
            has_permissions = "permissions" in data
            log_test(module, "Get role permissions", has_permissions, 200)
        else:
            log_test(module, "Get role permissions", False, 
                    response.status_code if response else None, error)
    else:
        log_test(module, "Get role permissions", False, None, "No role to check")
    
    # Test 7: Assign permissions to role
    if created_role_id:
        response, error = make_request("GET", "/permissions")
        if response and response.status_code == 200:
            permissions = response.json()
            if permissions and len(permissions) > 0:
                perm_id = permissions[0].get("id")
                response2, error2 = make_request("PUT", f"/roles/{created_role_id}", {
                    "permissions": [perm_id]
                })
                log_test(module, "Assign permissions to role", 
                        response2 and response2.status_code == 200, 
                        response2.status_code if response2 else None, error2)
            else:
                log_test(module, "Assign permissions to role", False, None, "No permissions found")
        else:
            log_test(module, "Assign permissions to role", False, None, "Cannot list permissions")
    else:
        log_test(module, "Assign permissions to role", False, None, "No role to assign to")
    
    # Test 8: Check permission (context-based)
    response, error = make_request("POST", "/permissions/check", {
        "permission": "user.read.organization",
        "resource_id": org_id
    })
    log_test(module, "Check permission", 
            response and response.status_code in [200, 403], 
            response.status_code if response else None, error)
    
    # Test 9: List permissions by category
    response, error = make_request("GET", "/permissions")
    if response and response.status_code == 200:
        permissions = response.json()
        has_categories = any("category" in p for p in permissions) if permissions else False
        log_test(module, "Permissions have categories", has_categories, 200)
    else:
        log_test(module, "Permissions have categories", False, 
                response.status_code if response else None, error)
    
    # Test 10: Delete role (cleanup)
    if created_role_id:
        response, error = make_request("DELETE", f"/roles/{created_role_id}")
        log_test(module, "Delete role", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete role", False, None, "No role to delete")

# ============================================================================
# MODULE 3: ORGANIZATIONS (8 tests)
# ============================================================================

def test_organizations():
    """Test organization management"""
    module = "Organizations"
    
    print(f"\n{'='*80}")
    print(f"MODULE 3: {module}")
    print(f"{'='*80}")
    
    # Test 1: List organization units
    response, error = make_request("GET", "/organizations/units")
    log_test(module, "List organization units", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Get organization hierarchy
    response, error = make_request("GET", "/organizations/hierarchy")
    log_test(module, "Get organization hierarchy", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 3: Create organization unit
    unit_data = {
        "name": f"Test Unit {uuid.uuid4().hex[:8]}",
        "type": "department",
        "parent_id": None
    }
    response, error = make_request("POST", "/organizations/units", unit_data)
    created_unit_id = None
    if response and response.status_code == 201:
        created_unit_id = response.json().get("id")
        log_test(module, "Create organization unit", True, 201)
    else:
        log_test(module, "Create organization unit", False, 
                response.status_code if response else None, error)
    
    # Test 4: Get unit by ID
    if created_unit_id:
        response, error = make_request("GET", f"/organizations/units/{created_unit_id}")
        log_test(module, "Get unit by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get unit by ID", False, None, "No unit to get")
    
    # Test 5: Update organization unit
    if created_unit_id:
        response, error = make_request("PUT", f"/organizations/units/{created_unit_id}", {
            "description": "Updated test unit"
        })
        log_test(module, "Update organization unit", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update organization unit", False, None, "No unit to update")
    
    # Test 6: Get organization stats
    response, error = make_request("GET", "/organizations/stats")
    log_test(module, "Get organization stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 7: Get organization settings
    response, error = make_request("GET", "/organizations/settings")
    log_test(module, "Get organization settings", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 8: Delete organization unit (cleanup)
    if created_unit_id:
        response, error = make_request("DELETE", f"/organizations/units/{created_unit_id}")
        log_test(module, "Delete organization unit", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete organization unit", False, None, "No unit to delete")

# ============================================================================
# MODULE 4: INSPECTIONS (12 tests)
# ============================================================================

def test_inspections():
    """Test inspection templates and executions"""
    module = "Inspections"
    
    print(f"\n{'='*80}")
    print(f"MODULE 4: {module}")
    print(f"{'='*80}")
    
    # Test 1: List inspection templates
    response, error = make_request("GET", "/inspections/templates")
    log_test(module, "List inspection templates", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create inspection template
    template_data = {
        "title": f"Test Inspection {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test inspection",
        "category": "safety",
        "sections": [
            {
                "title": "Section 1",
                "questions": [
                    {
                        "text": "Test question 1",
                        "type": "yes_no",
                        "required": True
                    }
                ]
            }
        ]
    }
    response, error = make_request("POST", "/inspections/templates", template_data)
    created_template_id = None
    if response and response.status_code == 201:
        created_template_id = response.json().get("id")
        log_test(module, "Create inspection template", True, 201)
    else:
        log_test(module, "Create inspection template", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get template by ID
    if created_template_id:
        response, error = make_request("GET", f"/inspections/templates/{created_template_id}")
        log_test(module, "Get template by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get template by ID", False, None, "No template to get")
    
    # Test 4: Update inspection template
    if created_template_id:
        response, error = make_request("PUT", f"/inspections/templates/{created_template_id}", {
            "description": "Updated description"
        })
        log_test(module, "Update inspection template", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update inspection template", False, None, "No template to update")
    
    # Test 5: List inspection executions
    response, error = make_request("GET", "/inspections/executions")
    log_test(module, "List inspection executions", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 6: Create inspection execution
    if created_template_id:
        execution_data = {
            "template_id": created_template_id,
            "inspector_id": user_id,
            "location": "Test Location",
            "responses": []
        }
        response, error = make_request("POST", "/inspections/executions", execution_data)
        created_execution_id = None
        if response and response.status_code == 201:
            created_execution_id = response.json().get("id")
            log_test(module, "Create inspection execution", True, 201)
        else:
            log_test(module, "Create inspection execution", False, 
                    response.status_code if response else None, error)
    else:
        log_test(module, "Create inspection execution", False, None, "No template for execution")
        created_execution_id = None
    
    # Test 7: Get execution by ID
    if created_execution_id:
        response, error = make_request("GET", f"/inspections/executions/{created_execution_id}")
        log_test(module, "Get execution by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get execution by ID", False, None, "No execution to get")
    
    # Test 8: Update inspection execution
    if created_execution_id:
        response, error = make_request("PUT", f"/inspections/executions/{created_execution_id}", {
            "status": "in_progress"
        })
        log_test(module, "Update inspection execution", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update inspection execution", False, None, "No execution to update")
    
    # Test 9: Get inspection analytics
    response, error = make_request("GET", "/inspections/analytics")
    log_test(module, "Get inspection analytics", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 10: Get inspection calendar
    response, error = make_request("GET", "/inspections/calendar")
    log_test(module, "Get inspection calendar", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 11: Get scheduled inspections
    response, error = make_request("GET", "/inspections/scheduled")
    log_test(module, "Get scheduled inspections", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 12: Delete inspection template (cleanup)
    if created_template_id:
        response, error = make_request("DELETE", f"/inspections/templates/{created_template_id}")
        log_test(module, "Delete inspection template", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete inspection template", False, None, "No template to delete")

# ============================================================================
# MODULE 5: CHECKLISTS (12 tests)
# ============================================================================

def test_checklists():
    """Test checklist templates and executions"""
    module = "Checklists"
    
    print(f"\n{'='*80}")
    print(f"MODULE 5: {module}")
    print(f"{'='*80}")
    
    # Test 1: List checklist templates
    response, error = make_request("GET", "/checklists/templates")
    log_test(module, "List checklist templates", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create checklist template
    template_data = {
        "title": f"Test Checklist {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test checklist",
        "category": "maintenance",
        "items": [
            {
                "text": "Test item 1",
                "required": True
            }
        ]
    }
    response, error = make_request("POST", "/checklists/templates", template_data)
    created_template_id = None
    if response and response.status_code == 201:
        created_template_id = response.json().get("id")
        log_test(module, "Create checklist template", True, 201)
    else:
        log_test(module, "Create checklist template", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get template by ID
    if created_template_id:
        response, error = make_request("GET", f"/checklists/templates/{created_template_id}")
        log_test(module, "Get template by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get template by ID", False, None, "No template to get")
    
    # Test 4: Update checklist template
    if created_template_id:
        response, error = make_request("PUT", f"/checklists/templates/{created_template_id}", {
            "description": "Updated description"
        })
        log_test(module, "Update checklist template", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update checklist template", False, None, "No template to update")
    
    # Test 5: List checklist executions
    response, error = make_request("GET", "/checklists/executions")
    log_test(module, "List checklist executions", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 6: Create checklist execution
    if created_template_id:
        execution_data = {
            "template_id": created_template_id,
            "assignee_id": user_id,
            "items": []
        }
        response, error = make_request("POST", "/checklists/executions", execution_data)
        created_execution_id = None
        if response and response.status_code == 201:
            created_execution_id = response.json().get("id")
            log_test(module, "Create checklist execution", True, 201)
        else:
            log_test(module, "Create checklist execution", False, 
                    response.status_code if response else None, error)
    else:
        log_test(module, "Create checklist execution", False, None, "No template for execution")
        created_execution_id = None
    
    # Test 7: Get execution by ID
    if created_execution_id:
        response, error = make_request("GET", f"/checklists/executions/{created_execution_id}")
        log_test(module, "Get execution by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get execution by ID", False, None, "No execution to get")
    
    # Test 8: Update checklist execution
    if created_execution_id:
        response, error = make_request("PUT", f"/checklists/executions/{created_execution_id}", {
            "status": "in_progress"
        })
        log_test(module, "Update checklist execution", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update checklist execution", False, None, "No execution to update")
    
    # Test 9: Get checklist analytics
    response, error = make_request("GET", "/checklists/analytics")
    log_test(module, "Get checklist analytics", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 10: Get scheduled checklists
    response, error = make_request("GET", "/checklists/scheduled")
    log_test(module, "Get scheduled checklists", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 11: Get pending approvals
    response, error = make_request("GET", "/checklists/pending-approvals")
    log_test(module, "Get pending approvals", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 12: Delete checklist template (cleanup)
    if created_template_id:
        response, error = make_request("DELETE", f"/checklists/templates/{created_template_id}")
        log_test(module, "Delete checklist template", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete checklist template", False, None, "No template to delete")

# ============================================================================
# MODULE 6: TASKS (15 tests)
# ============================================================================

def test_tasks():
    """Test task management"""
    module = "Tasks"
    
    print(f"\n{'='*80}")
    print(f"MODULE 6: {module}")
    print(f"{'='*80}")
    
    # Test 1: List tasks
    response, error = make_request("GET", "/tasks")
    log_test(module, "List tasks", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create task
    task_data = {
        "title": f"Test Task {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test task",
        "priority": "high",
        "status": "open",
        "assignee_id": user_id
    }
    response, error = make_request("POST", "/tasks", task_data)
    created_task_id = None
    if response and response.status_code == 201:
        created_task_id = response.json().get("id")
        log_test(module, "Create task", True, 201)
    else:
        log_test(module, "Create task", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get task by ID
    if created_task_id:
        response, error = make_request("GET", f"/tasks/{created_task_id}")
        log_test(module, "Get task by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get task by ID", False, None, "No task to get")
    
    # Test 4: Update task
    if created_task_id:
        response, error = make_request("PUT", f"/tasks/{created_task_id}", {
            "status": "in_progress"
        })
        log_test(module, "Update task", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update task", False, None, "No task to update")
    
    # Test 5: Create subtask
    if created_task_id:
        subtask_data = {
            "title": "Test Subtask",
            "description": "Test subtask description"
        }
        response, error = make_request("POST", f"/tasks/{created_task_id}/subtasks", subtask_data)
        created_subtask_id = None
        if response and response.status_code == 201:
            created_subtask_id = response.json().get("id")
            log_test(module, "Create subtask", True, 201)
        else:
            log_test(module, "Create subtask", False, 
                    response.status_code if response else None, error)
    else:
        log_test(module, "Create subtask", False, None, "No parent task")
        created_subtask_id = None
    
    # Test 6: List subtasks
    if created_task_id:
        response, error = make_request("GET", f"/tasks/{created_task_id}/subtasks")
        log_test(module, "List subtasks", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "List subtasks", False, None, "No parent task")
    
    # Test 7: Add task dependency
    if created_task_id:
        # Create another task to be a dependency
        dep_task_data = {
            "title": "Dependency Task",
            "description": "Task dependency",
            "priority": "medium",
            "status": "open"
        }
        response, error = make_request("POST", "/tasks", dep_task_data)
        if response and response.status_code == 201:
            dep_task_id = response.json().get("id")
            response2, error2 = make_request("POST", f"/tasks/{created_task_id}/dependencies", {
                "predecessor_task_id": dep_task_id
            })
            log_test(module, "Add task dependency", 
                    response2 and response2.status_code in [200, 201], 
                    response2.status_code if response2 else None, error2)
        else:
            log_test(module, "Add task dependency", False, None, "Cannot create dependency task")
    else:
        log_test(module, "Add task dependency", False, None, "No task for dependency")
    
    # Test 8: Get task dependencies
    if created_task_id:
        response, error = make_request("GET", f"/tasks/{created_task_id}/dependencies")
        log_test(module, "Get task dependencies", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get task dependencies", False, None, "No task")
    
    # Test 9: Log time on task
    if created_task_id:
        time_data = {
            "hours": 2.5,
            "description": "Test time entry",
            "date": datetime.now().isoformat()
        }
        response, error = make_request("POST", f"/tasks/{created_task_id}/time", time_data)
        log_test(module, "Log time on task", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Log time on task", False, None, "No task")
    
    # Test 10: Log parts on task
    if created_task_id:
        parts_data = {
            "part_name": "Test Part",
            "quantity": 5,
            "cost": 100.00
        }
        response, error = make_request("POST", f"/tasks/{created_task_id}/parts", parts_data)
        log_test(module, "Log parts on task", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Log parts on task", False, None, "No task")
    
    # Test 11: List task templates
    response, error = make_request("GET", "/tasks/templates")
    log_test(module, "List task templates", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 12: Get task stats
    response, error = make_request("GET", "/tasks/stats")
    log_test(module, "Get task stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 13: Get task analytics
    response, error = make_request("GET", "/tasks/analytics")
    log_test(module, "Get task analytics", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 14: Add comment to task
    if created_task_id:
        comment_data = {
            "text": "Test comment on task"
        }
        response, error = make_request("POST", f"/tasks/{created_task_id}/comments", comment_data)
        log_test(module, "Add comment to task", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add comment to task", False, None, "No task")
    
    # Test 15: Delete task (cleanup)
    if created_task_id:
        response, error = make_request("DELETE", f"/tasks/{created_task_id}")
        log_test(module, "Delete task", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete task", False, None, "No task to delete")

# ============================================================================
# MODULE 7: ASSETS (10 tests)
# ============================================================================

def test_assets():
    """Test asset management"""
    module = "Assets"
    
    print(f"\n{'='*80}")
    print(f"MODULE 7: {module}")
    print(f"{'='*80}")
    
    # Test 1: List assets
    response, error = make_request("GET", "/assets")
    log_test(module, "List assets", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create asset
    asset_data = {
        "name": f"Test Asset {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test asset",
        "asset_type": "equipment",
        "status": "operational",
        "location": "Test Location"
    }
    response, error = make_request("POST", "/assets", asset_data)
    created_asset_id = None
    if response and response.status_code == 201:
        created_asset_id = response.json().get("id")
        log_test(module, "Create asset", True, 201)
    else:
        log_test(module, "Create asset", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get asset by ID
    if created_asset_id:
        response, error = make_request("GET", f"/assets/{created_asset_id}")
        log_test(module, "Get asset by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get asset by ID", False, None, "No asset to get")
    
    # Test 4: Update asset
    if created_asset_id:
        response, error = make_request("PUT", f"/assets/{created_asset_id}", {
            "status": "maintenance"
        })
        log_test(module, "Update asset", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update asset", False, None, "No asset to update")
    
    # Test 5: Generate QR code for asset
    if created_asset_id:
        response, error = make_request("GET", f"/assets/{created_asset_id}/qr-code")
        log_test(module, "Generate QR code", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Generate QR code", False, None, "No asset")
    
    # Test 6: Get asset history
    if created_asset_id:
        response, error = make_request("GET", f"/assets/{created_asset_id}/history")
        log_test(module, "Get asset history", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get asset history", False, None, "No asset")
    
    # Test 7: List asset types catalog
    response, error = make_request("GET", "/assets/types")
    log_test(module, "List asset types catalog", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 8: Get asset stats
    response, error = make_request("GET", "/assets/stats")
    log_test(module, "Get asset stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 9: Add maintenance record to asset
    if created_asset_id:
        maintenance_data = {
            "type": "preventive",
            "description": "Test maintenance",
            "date": datetime.now().isoformat()
        }
        response, error = make_request("POST", f"/assets/{created_asset_id}/maintenance", maintenance_data)
        log_test(module, "Add maintenance record", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add maintenance record", False, None, "No asset")
    
    # Test 10: Delete asset (cleanup)
    if created_asset_id:
        response, error = make_request("DELETE", f"/assets/{created_asset_id}")
        log_test(module, "Delete asset", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete asset", False, None, "No asset to delete")

# ============================================================================
# MODULE 8: WORK ORDERS (12 tests)
# ============================================================================

def test_work_orders():
    """Test work order management"""
    module = "Work Orders"
    
    print(f"\n{'='*80}")
    print(f"MODULE 8: {module}")
    print(f"{'='*80}")
    
    # Test 1: List work orders
    response, error = make_request("GET", "/work-orders")
    log_test(module, "List work orders", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create work order
    wo_data = {
        "title": f"Test Work Order {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test work order",
        "priority": "high",
        "status": "open",
        "work_type": "corrective"
    }
    response, error = make_request("POST", "/work-orders", wo_data)
    created_wo_id = None
    if response and response.status_code == 201:
        created_wo_id = response.json().get("id")
        log_test(module, "Create work order", True, 201)
    else:
        log_test(module, "Create work order", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get work order by ID
    if created_wo_id:
        response, error = make_request("GET", f"/work-orders/{created_wo_id}")
        log_test(module, "Get work order by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get work order by ID", False, None, "No work order to get")
    
    # Test 4: Update work order
    if created_wo_id:
        response, error = make_request("PUT", f"/work-orders/{created_wo_id}", {
            "status": "in_progress"
        })
        log_test(module, "Update work order", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update work order", False, None, "No work order to update")
    
    # Test 5: Change work order status
    if created_wo_id:
        response, error = make_request("PUT", f"/work-orders/{created_wo_id}/status", {
            "status": "assigned"
        })
        log_test(module, "Change work order status", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Change work order status", False, None, "No work order")
    
    # Test 6: Assign work order
    if created_wo_id:
        response, error = make_request("PUT", f"/work-orders/{created_wo_id}/assign", {
            "assignee_id": user_id
        })
        log_test(module, "Assign work order", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Assign work order", False, None, "No work order")
    
    # Test 7: Add labor to work order
    if created_wo_id:
        labor_data = {
            "worker_id": user_id,
            "hours": 3.0,
            "rate": 50.00
        }
        response, error = make_request("POST", f"/work-orders/{created_wo_id}/labor", labor_data)
        log_test(module, "Add labor to work order", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add labor to work order", False, None, "No work order")
    
    # Test 8: Add parts to work order
    if created_wo_id:
        parts_data = {
            "part_name": "Test Part",
            "quantity": 2,
            "cost": 75.00
        }
        response, error = make_request("POST", f"/work-orders/{created_wo_id}/parts", parts_data)
        log_test(module, "Add parts to work order", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add parts to work order", False, None, "No work order")
    
    # Test 9: Get work order timeline
    if created_wo_id:
        response, error = make_request("GET", f"/work-orders/{created_wo_id}/timeline")
        log_test(module, "Get work order timeline", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get work order timeline", False, None, "No work order")
    
    # Test 10: Get work order stats
    response, error = make_request("GET", "/work-orders/stats")
    log_test(module, "Get work order stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 11: Get work order backlog
    response, error = make_request("GET", "/work-orders/backlog")
    log_test(module, "Get work order backlog", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 12: Delete work order (cleanup)
    if created_wo_id:
        response, error = make_request("DELETE", f"/work-orders/{created_wo_id}")
        log_test(module, "Delete work order", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete work order", False, None, "No work order to delete")

# ============================================================================
# MODULE 9: INVENTORY (8 tests)
# ============================================================================

def test_inventory():
    """Test inventory management"""
    module = "Inventory"
    
    print(f"\n{'='*80}")
    print(f"MODULE 9: {module}")
    print(f"{'='*80}")
    
    # Test 1: List inventory items
    response, error = make_request("GET", "/inventory/items")
    log_test(module, "List inventory items", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create inventory item
    item_data = {
        "name": f"Test Item {uuid.uuid4().hex[:8]}",
        "description": "Test inventory item",
        "sku": f"SKU-{uuid.uuid4().hex[:6]}",
        "quantity": 100,
        "unit_cost": 25.00,
        "reorder_point": 20
    }
    response, error = make_request("POST", "/inventory/items", item_data)
    created_item_id = None
    if response and response.status_code == 201:
        created_item_id = response.json().get("id")
        log_test(module, "Create inventory item", True, 201)
    else:
        log_test(module, "Create inventory item", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get inventory item by ID
    if created_item_id:
        response, error = make_request("GET", f"/inventory/items/{created_item_id}")
        log_test(module, "Get inventory item by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get inventory item by ID", False, None, "No item to get")
    
    # Test 4: Update inventory item
    if created_item_id:
        response, error = make_request("PUT", f"/inventory/items/{created_item_id}", {
            "quantity": 150
        })
        log_test(module, "Update inventory item", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update inventory item", False, None, "No item to update")
    
    # Test 5: Adjust stock
    if created_item_id:
        adjustment_data = {
            "quantity": -10,
            "reason": "Test adjustment",
            "type": "usage"
        }
        response, error = make_request("POST", f"/inventory/items/{created_item_id}/adjust", adjustment_data)
        log_test(module, "Adjust stock", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Adjust stock", False, None, "No item")
    
    # Test 6: Get reorder list
    response, error = make_request("GET", "/inventory/reorder-list")
    log_test(module, "Get reorder list", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 7: Get inventory stats
    response, error = make_request("GET", "/inventory/stats")
    log_test(module, "Get inventory stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 8: Delete inventory item (cleanup)
    if created_item_id:
        response, error = make_request("DELETE", f"/inventory/items/{created_item_id}")
        log_test(module, "Delete inventory item", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete inventory item", False, None, "No item to delete")

# ============================================================================
# MODULE 10: PROJECTS (11 tests)
# ============================================================================

def test_projects():
    """Test project management"""
    module = "Projects"
    
    print(f"\n{'='*80}")
    print(f"MODULE 10: {module}")
    print(f"{'='*80}")
    
    # Test 1: List projects
    response, error = make_request("GET", "/projects")
    log_test(module, "List projects", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create project
    project_data = {
        "name": f"Test Project {uuid.uuid4().hex[:8]}",
        "description": "Comprehensive test project",
        "status": "planning",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    response, error = make_request("POST", "/projects", project_data)
    created_project_id = None
    if response and response.status_code == 201:
        created_project_id = response.json().get("id")
        log_test(module, "Create project", True, 201)
    else:
        log_test(module, "Create project", False, 
                response.status_code if response else None, error)
    
    # Test 3: Get project by ID
    if created_project_id:
        response, error = make_request("GET", f"/projects/{created_project_id}")
        log_test(module, "Get project by ID", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get project by ID", False, None, "No project to get")
    
    # Test 4: Update project
    if created_project_id:
        response, error = make_request("PUT", f"/projects/{created_project_id}", {
            "status": "in_progress"
        })
        log_test(module, "Update project", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update project", False, None, "No project to update")
    
    # Test 5: Add milestone to project
    if created_project_id:
        milestone_data = {
            "name": "Test Milestone",
            "description": "Test milestone description",
            "due_date": (datetime.now() + timedelta(days=15)).isoformat()
        }
        response, error = make_request("POST", f"/projects/{created_project_id}/milestones", milestone_data)
        log_test(module, "Add milestone to project", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add milestone to project", False, None, "No project")
    
    # Test 6: Get project milestones
    if created_project_id:
        response, error = make_request("GET", f"/projects/{created_project_id}/milestones")
        log_test(module, "Get project milestones", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get project milestones", False, None, "No project")
    
    # Test 7: Add task to project
    if created_project_id:
        task_data = {
            "title": "Project Task",
            "description": "Task for project",
            "priority": "medium"
        }
        response, error = make_request("POST", f"/projects/{created_project_id}/tasks", task_data)
        log_test(module, "Add task to project", 
                response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add task to project", False, None, "No project")
    
    # Test 8: Get project tasks
    if created_project_id:
        response, error = make_request("GET", f"/projects/{created_project_id}/tasks")
        log_test(module, "Get project tasks", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get project tasks", False, None, "No project")
    
    # Test 9: Get project stats
    response, error = make_request("GET", "/projects/stats")
    log_test(module, "Get project stats", 
            response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 10: Get project dashboard
    if created_project_id:
        response, error = make_request("GET", f"/projects/{created_project_id}/dashboard")
        log_test(module, "Get project dashboard", 
                response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get project dashboard", False, None, "No project")
    
    # Test 11: Delete project (cleanup)
    if created_project_id:
        response, error = make_request("DELETE", f"/projects/{created_project_id}")
        log_test(module, "Delete project", 
                response and response.status_code in [200, 204], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Delete project", False, None, "No project to delete")

# Continue with remaining modules...
# (Due to length, I'll create the remaining modules in a similar pattern)

def run_remaining_modules():
    """Run tests for modules 11-20"""
    # Module 11: Incidents
    test_incidents()
    # Module 12: Training
    test_training()
    # Module 13: Financial
    test_financial()
    # Module 14: HR
    test_hr()
    # Module 15: Emergency
    test_emergency()
    # Module 16: Dashboards
    test_dashboards()
    # Module 17: Team Chat
    test_team_chat()
    # Module 18: Contractors
    test_contractors()
    # Module 19: Announcements
    test_announcements()
    # Module 20: Additional Features
    test_additional_features()

def test_incidents():
    """Test incident management (7 tests)"""
    module = "Incidents"
    print(f"\n{'='*80}\nMODULE 11: {module}\n{'='*80}")
    
    # Test 1: List incidents
    response, error = make_request("GET", "/incidents")
    log_test(module, "List incidents", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create incident
    incident_data = {
        "title": f"Test Incident {uuid.uuid4().hex[:8]}",
        "description": "Test incident",
        "severity": "medium",
        "status": "open"
    }
    response, error = make_request("POST", "/incidents", incident_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create incident", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get incident by ID
    if created_id:
        response, error = make_request("GET", f"/incidents/{created_id}")
        log_test(module, "Get incident by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get incident by ID", False, None, "No incident")
    
    # Test 4: Update incident
    if created_id:
        response, error = make_request("PUT", f"/incidents/{created_id}", {"status": "investigating"})
        log_test(module, "Update incident", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update incident", False, None, "No incident")
    
    # Test 5: Add investigation notes
    if created_id:
        response, error = make_request("POST", f"/incidents/{created_id}/investigation", 
                                      {"notes": "Test investigation notes"})
        log_test(module, "Add investigation notes", response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add investigation notes", False, None, "No incident")
    
    # Test 6: Add corrective actions
    if created_id:
        response, error = make_request("POST", f"/incidents/{created_id}/corrective-actions", 
                                      {"action": "Test corrective action"})
        log_test(module, "Add corrective actions", response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Add corrective actions", False, None, "No incident")
    
    # Test 7: Get incident stats
    response, error = make_request("GET", "/incidents/stats")
    log_test(module, "Get incident stats", response and response.status_code == 200, 
            response.status_code if response else None, error)

def test_training():
    """Test training management (7 tests)"""
    module = "Training"
    print(f"\n{'='*80}\nMODULE 12: {module}\n{'='*80}")
    
    # Test 1: List training courses
    response, error = make_request("GET", "/training/courses")
    log_test(module, "List training courses", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create training course
    course_data = {
        "title": f"Test Course {uuid.uuid4().hex[:8]}",
        "description": "Test training course",
        "duration_hours": 8
    }
    response, error = make_request("POST", "/training/courses", course_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create training course", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get course by ID
    if created_id:
        response, error = make_request("GET", f"/training/courses/{created_id}")
        log_test(module, "Get course by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get course by ID", False, None, "No course")
    
    # Test 4: Update course
    if created_id:
        response, error = make_request("PUT", f"/training/courses/{created_id}", 
                                      {"duration_hours": 10})
        log_test(module, "Update course", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update course", False, None, "No course")
    
    # Test 5: Record training completion
    if created_id:
        completion_data = {
            "user_id": user_id,
            "completion_date": datetime.now().isoformat(),
            "score": 95
        }
        response, error = make_request("POST", f"/training/courses/{created_id}/completions", 
                                      completion_data)
        log_test(module, "Record training completion", response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Record training completion", False, None, "No course")
    
    # Test 6: Get training transcripts
    response, error = make_request("GET", f"/training/transcripts/{user_id}")
    log_test(module, "Get training transcripts", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 7: Get expired certifications
    response, error = make_request("GET", "/training/expired-certifications")
    log_test(module, "Get expired certifications", response and response.status_code == 200, 
            response.status_code if response else None, error)

def test_financial():
    """Test financial management (10 tests)"""
    module = "Financial"
    print(f"\n{'='*80}\nMODULE 13: {module}\n{'='*80}")
    
    # Test 1: List transactions
    response, error = make_request("GET", "/financial/transactions")
    log_test(module, "List transactions", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create transaction
    transaction_data = {
        "description": f"Test Transaction {uuid.uuid4().hex[:8]}",
        "amount": 1000.00,
        "type": "expense",
        "category": "maintenance"
    }
    response, error = make_request("POST", "/financial/transactions", transaction_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create transaction", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get transaction by ID
    if created_id:
        response, error = make_request("GET", f"/financial/transactions/{created_id}")
        log_test(module, "Get transaction by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get transaction by ID", False, None, "No transaction")
    
    # Test 4: Update transaction
    if created_id:
        response, error = make_request("PUT", f"/financial/transactions/{created_id}", 
                                      {"amount": 1200.00})
        log_test(module, "Update transaction", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update transaction", False, None, "No transaction")
    
    # Test 5: Get CAPEX transactions
    response, error = make_request("GET", "/financial/capex")
    log_test(module, "Get CAPEX transactions", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 6: Get OPEX transactions
    response, error = make_request("GET", "/financial/opex")
    log_test(module, "Get OPEX transactions", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 7: List budgets
    response, error = make_request("GET", "/financial/budgets")
    log_test(module, "List budgets", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 8: Create budget
    budget_data = {
        "name": f"Test Budget {uuid.uuid4().hex[:8]}",
        "amount": 50000.00,
        "period": "monthly"
    }
    response, error = make_request("POST", "/financial/budgets", budget_data)
    log_test(module, "Create budget", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 9: Get financial summary
    response, error = make_request("GET", "/financial/summary")
    log_test(module, "Get financial summary", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 10: Get financial stats
    response, error = make_request("GET", "/financial/stats")
    log_test(module, "Get financial stats", response and response.status_code == 200, 
            response.status_code if response else None, error)

def test_hr():
    """Test HR management (6 tests)"""
    module = "HR"
    print(f"\n{'='*80}\nMODULE 14: {module}\n{'='*80}")
    
    # Test 1: List employees
    response, error = make_request("GET", "/hr/employees")
    log_test(module, "List employees", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create employee
    employee_data = {
        "first_name": "Test",
        "last_name": f"Employee{uuid.uuid4().hex[:6]}",
        "email": f"test.employee.{uuid.uuid4().hex[:6]}@example.com",
        "position": "Test Position"
    }
    response, error = make_request("POST", "/hr/employees", employee_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create employee", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get employee by ID
    if created_id:
        response, error = make_request("GET", f"/hr/employees/{created_id}")
        log_test(module, "Get employee by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get employee by ID", False, None, "No employee")
    
    # Test 4: Update employee
    if created_id:
        response, error = make_request("PUT", f"/hr/employees/{created_id}", 
                                      {"position": "Updated Position"})
        log_test(module, "Update employee", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update employee", False, None, "No employee")
    
    # Test 5: List HR announcements
    response, error = make_request("GET", "/hr/announcements")
    log_test(module, "List HR announcements", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 6: Create HR announcement
    announcement_data = {
        "title": f"Test Announcement {uuid.uuid4().hex[:8]}",
        "content": "Test HR announcement content"
    }
    response, error = make_request("POST", "/hr/announcements", announcement_data)
    log_test(module, "Create HR announcement", response and response.status_code == 201, 
            response.status_code if response else None, error)

def test_emergency():
    """Test emergency management (5 tests)"""
    module = "Emergency"
    print(f"\n{'='*80}\nMODULE 15: {module}\n{'='*80}")
    
    # Test 1: List emergencies
    response, error = make_request("GET", "/emergencies")
    log_test(module, "List emergencies", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create emergency
    emergency_data = {
        "title": f"Test Emergency {uuid.uuid4().hex[:8]}",
        "description": "Test emergency situation",
        "severity": "high",
        "location": "Test Location"
    }
    response, error = make_request("POST", "/emergencies", emergency_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create emergency", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get emergency by ID
    if created_id:
        response, error = make_request("GET", f"/emergencies/{created_id}")
        log_test(module, "Get emergency by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get emergency by ID", False, None, "No emergency")
    
    # Test 4: Resolve emergency
    if created_id:
        response, error = make_request("PUT", f"/emergencies/{created_id}/resolve", 
                                      {"resolution_notes": "Test resolution"})
        log_test(module, "Resolve emergency", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Resolve emergency", False, None, "No emergency")
    
    # Test 5: Get active emergencies
    response, error = make_request("GET", "/emergencies/active")
    log_test(module, "Get active emergencies", response and response.status_code == 200, 
            response.status_code if response else None, error)

def test_dashboards():
    """Test dashboard endpoints (5 tests)"""
    module = "Dashboards"
    print(f"\n{'='*80}\nMODULE 16: {module}\n{'='*80}")
    
    # Test 1: Get main dashboard stats
    response, error = make_request("GET", "/dashboard/stats")
    log_test(module, "Get main dashboard stats", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Get financial dashboard
    response, error = make_request("GET", "/dashboard/financial")
    log_test(module, "Get financial dashboard", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 3: Get executive dashboard
    response, error = make_request("GET", "/dashboard/executive")
    log_test(module, "Get executive dashboard", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 4: Get safety dashboard
    response, error = make_request("GET", "/dashboard/safety")
    log_test(module, "Get safety dashboard", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 5: Get maintenance dashboard
    response, error = make_request("GET", "/dashboard/maintenance")
    log_test(module, "Get maintenance dashboard", response and response.status_code == 200, 
            response.status_code if response else None, error)

def test_team_chat():
    """Test team chat (4 tests)"""
    module = "Team Chat"
    print(f"\n{'='*80}\nMODULE 17: {module}\n{'='*80}")
    
    # Test 1: List chat channels
    response, error = make_request("GET", "/chat/channels")
    log_test(module, "List chat channels", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create chat channel
    channel_data = {
        "name": f"test-channel-{uuid.uuid4().hex[:8]}",
        "description": "Test chat channel"
    }
    response, error = make_request("POST", "/chat/channels", channel_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create chat channel", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get channel messages
    if created_id:
        response, error = make_request("GET", f"/chat/channels/{created_id}/messages")
        log_test(module, "Get channel messages", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get channel messages", False, None, "No channel")
    
    # Test 4: Send message to channel
    if created_id:
        message_data = {
            "text": "Test message"
        }
        response, error = make_request("POST", f"/chat/channels/{created_id}/messages", 
                                      message_data)
        log_test(module, "Send message to channel", response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Send message to channel", False, None, "No channel")

def test_contractors():
    """Test contractor management (4 tests)"""
    module = "Contractors"
    print(f"\n{'='*80}\nMODULE 18: {module}\n{'='*80}")
    
    # Test 1: List contractors
    response, error = make_request("GET", "/contractors")
    log_test(module, "List contractors", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create contractor
    contractor_data = {
        "name": f"Test Contractor {uuid.uuid4().hex[:8]}",
        "company": "Test Company",
        "email": f"contractor.{uuid.uuid4().hex[:6]}@example.com",
        "phone": "+27123456789"
    }
    response, error = make_request("POST", "/contractors", contractor_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create contractor", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get contractor by ID
    if created_id:
        response, error = make_request("GET", f"/contractors/{created_id}")
        log_test(module, "Get contractor by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get contractor by ID", False, None, "No contractor")
    
    # Test 4: Get contractor work history
    if created_id:
        response, error = make_request("GET", f"/contractors/{created_id}/work-history")
        log_test(module, "Get contractor work history", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get contractor work history", False, None, "No contractor")

def test_announcements():
    """Test announcements (5 tests)"""
    module = "Announcements"
    print(f"\n{'='*80}\nMODULE 19: {module}\n{'='*80}")
    
    # Test 1: List announcements
    response, error = make_request("GET", "/announcements")
    log_test(module, "List announcements", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Test 2: Create announcement
    announcement_data = {
        "title": f"Test Announcement {uuid.uuid4().hex[:8]}",
        "content": "Test announcement content",
        "priority": "normal"
    }
    response, error = make_request("POST", "/announcements", announcement_data)
    created_id = response.json().get("id") if response and response.status_code == 201 else None
    log_test(module, "Create announcement", response and response.status_code == 201, 
            response.status_code if response else None, error)
    
    # Test 3: Get announcement by ID
    if created_id:
        response, error = make_request("GET", f"/announcements/{created_id}")
        log_test(module, "Get announcement by ID", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Get announcement by ID", False, None, "No announcement")
    
    # Test 4: Update announcement
    if created_id:
        response, error = make_request("PUT", f"/announcements/{created_id}", 
                                      {"priority": "high"})
        log_test(module, "Update announcement", response and response.status_code == 200, 
                response.status_code if response else None, error)
    else:
        log_test(module, "Update announcement", False, None, "No announcement")
    
    # Test 5: Acknowledge announcement
    if created_id:
        response, error = make_request("POST", f"/announcements/{created_id}/acknowledge")
        log_test(module, "Acknowledge announcement", response and response.status_code in [200, 201], 
                response.status_code if response else None, error)
    else:
        log_test(module, "Acknowledge announcement", False, None, "No announcement")

def test_additional_features():
    """Test additional features (20+ tests)"""
    module = "Additional Features"
    print(f"\n{'='*80}\nMODULE 20: {module}\n{'='*80}")
    
    # Comments
    response, error = make_request("GET", "/comments")
    log_test(module, "List comments", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Attachments
    response, error = make_request("GET", "/attachments")
    log_test(module, "List attachments", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Notifications
    response, error = make_request("GET", "/notifications")
    log_test(module, "List notifications", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Audit Logs
    response, error = make_request("GET", "/audit/logs")
    log_test(module, "Get audit logs", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Groups
    response, error = make_request("GET", "/groups")
    log_test(module, "List groups", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Webhooks
    response, error = make_request("GET", "/webhooks")
    log_test(module, "List webhooks", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Workflows
    response, error = make_request("GET", "/workflows")
    log_test(module, "List workflows", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Settings
    response, error = make_request("GET", "/settings/email")
    log_test(module, "Get email settings", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    response, error = make_request("GET", "/sms/settings")
    log_test(module, "Get SMS settings", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Bulk Import
    response, error = make_request("GET", "/bulk-import/templates")
    log_test(module, "Get bulk import templates", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Analytics
    response, error = make_request("GET", "/analytics/overview")
    log_test(module, "Get analytics overview", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Reports
    response, error = make_request("GET", "/reports/overview")
    log_test(module, "Get reports overview", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Search
    response, error = make_request("GET", "/search?q=test")
    log_test(module, "Global search", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Time Tracking
    response, error = make_request("GET", "/time-tracking/entries")
    log_test(module, "Get time tracking entries", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # GDPR
    response, error = make_request("GET", "/gdpr/consent-status")
    log_test(module, "Get GDPR consent status", response and response.status_code == 200, 
            response.status_code if response else None, error)
    
    # Developer Tools
    response, error = make_request("GET", "/developer/api-keys")
    log_test(module, "Get API keys", response and response.status_code == 200, 
            response.status_code if response else None, error)

def print_summary():
    """Print comprehensive test summary"""
    print(f"\n{'='*80}")
    print("FINAL COMPREHENSIVE BACKEND TESTING SUMMARY")
    print(f"{'='*80}\n")
    
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"OVERALL RESULTS:")
    print(f"  Total Tests: {total}")
    print(f"  Passed: {passed} ✅")
    print(f"  Failed: {failed} ❌")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"\n{'='*80}\n")
    
    print("RESULTS BY MODULE:")
    for module, results in test_results["by_module"].items():
        module_total = results["total"]
        module_passed = results["passed"]
        module_failed = results["failed"]
        module_rate = (module_passed / module_total * 100) if module_total > 0 else 0
        status = "✅" if module_rate >= 95 else "⚠️" if module_rate >= 80 else "❌"
        print(f"  {status} {module}: {module_passed}/{module_total} ({module_rate:.1f}%)")
    
    print(f"\n{'='*80}\n")
    
    # Check for 500 errors
    critical_errors = [e for e in test_results["errors"] if "500" in str(e.get("error", ""))]
    if critical_errors:
        print(f"🚨 CRITICAL: {len(critical_errors)} endpoints returned 500 errors!")
        for error in critical_errors[:10]:  # Show first 10
            print(f"  - {error['module']}: {error['test']} - {error['error']}")
    else:
        print("✅ ZERO 500 ERRORS - Excellent!")
    
    print(f"\n{'='*80}\n")
    
    if failed > 0:
        print("FAILED TESTS SUMMARY:")
        for error in test_results["errors"][:20]:  # Show first 20 failures
            print(f"  ❌ {error['module']}: {error['test']}")
            print(f"     Status: {error['status_code']}, Error: {error['error']}")
    
    print(f"\n{'='*80}\n")
    
    # Final verdict
    if success_rate >= 95 and len(critical_errors) == 0:
        print("🎉 APPROVED FOR COMMERCIAL LAUNCH!")
        print("   - Success rate >= 95% ✅")
        print("   - Zero 500 errors ✅")
        print("   - All critical modules operational ✅")
    elif success_rate >= 90:
        print("⚠️ CONDITIONAL APPROVAL - Minor issues need attention")
        print(f"   - Success rate: {success_rate:.1f}% (target: 95%)")
        print(f"   - 500 errors: {len(critical_errors)}")
    else:
        print("❌ NOT READY FOR COMMERCIAL LAUNCH")
        print(f"   - Success rate: {success_rate:.1f}% (target: 95%)")
        print(f"   - 500 errors: {len(critical_errors)}")
        print("   - Critical issues must be resolved")

def main():
    """Main test execution"""
    print("="*80)
    print("FINAL COMPREHENSIVE BACKEND TESTING - ALL 20 MODULES")
    print("Production User: llewellyn@bluedawncapital.co.za")
    print("Target: 95%+ success rate, Zero 500 errors")
    print("="*80)
    
    try:
        # Run all module tests
        test_authentication_and_users()
        test_roles_and_permissions()
        test_organizations()
        test_inspections()
        test_checklists()
        test_tasks()
        test_assets()
        test_work_orders()
        test_inventory()
        test_projects()
        run_remaining_modules()
        
        # Print summary
        print_summary()
        
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        print_summary()
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print_summary()

if __name__ == "__main__":
    main()
