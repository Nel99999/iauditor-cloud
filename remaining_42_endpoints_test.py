#!/usr/bin/env python3
"""
Comprehensive Backend Testing - 42 Remaining Endpoints
Test all remaining untested endpoints to achieve 100% coverage
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://ops-control-center.preview.emergentagent.com/api"
TEST_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "TestPassword123!"
}

# Global variables
token = None
user_id = None
org_id = None
test_results = []

def log_test(group, test_name, status, details=""):
    """Log test result"""
    result = {
        "group": group,
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} [{group}] {test_name}: {status}")
    if details:
        print(f"   Details: {details}")

def login():
    """Authenticate and get token"""
    global token, user_id, org_id
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            org_id = data.get("user", {}).get("organization_id")
            
            if token and user_id:
                log_test("AUTH", "Login", "PASS", f"User ID: {user_id}")
                return True
            else:
                log_test("AUTH", "Login", "FAIL", "No token or user_id in response")
                return False
        else:
            log_test("AUTH", "Login", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("AUTH", "Login", "FAIL", str(e))
        return False

def get_headers():
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# ==================== INSPECTION TESTS ====================

def test_inspection_endpoints():
    """Test 3 remaining inspection endpoints"""
    print("\n" + "="*60)
    print("TESTING INSPECTION ENDPOINTS (3 endpoints)")
    print("="*60)
    
    # First, create an inspection execution for testing
    templates_resp = requests.get(f"{BASE_URL}/inspections/templates", headers=get_headers(), timeout=10)
    if templates_resp.status_code == 200 and templates_resp.json():
        template_id = templates_resp.json()[0]["id"]
        
        # Create execution
        exec_data = {
            "template_id": template_id,
            "location": "Test Location"
        }
        create_resp = requests.post(f"{BASE_URL}/inspections/executions", json=exec_data, headers=get_headers(), timeout=10)
        if create_resp.status_code == 201:
            execution_id = create_resp.json()["id"]
            
            # Test 1: GET /inspections/executions/{id}
            try:
                response = requests.get(f"{BASE_URL}/inspections/executions/{execution_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == execution_id:
                        log_test("INSPECTION", "GET /inspections/executions/{id}", "PASS", f"Retrieved execution {execution_id}")
                    else:
                        log_test("INSPECTION", "GET /inspections/executions/{id}", "FAIL", "ID mismatch")
                else:
                    log_test("INSPECTION", "GET /inspections/executions/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("INSPECTION", "GET /inspections/executions/{id}", "FAIL", str(e))
            
            # Test 2: PUT /inspections/executions/{id}
            try:
                update_data = {
                    "notes": "Updated inspection notes"
                }
                response = requests.put(f"{BASE_URL}/inspections/executions/{execution_id}", json=update_data, headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("notes") == "Updated inspection notes":
                        log_test("INSPECTION", "PUT /inspections/executions/{id}", "PASS", "Execution updated successfully")
                    else:
                        log_test("INSPECTION", "PUT /inspections/executions/{id}", "FAIL", "Notes not updated")
                else:
                    log_test("INSPECTION", "PUT /inspections/executions/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("INSPECTION", "PUT /inspections/executions/{id}", "FAIL", str(e))
        else:
            log_test("INSPECTION", "GET /inspections/executions/{id}", "SKIP", "Could not create test execution")
            log_test("INSPECTION", "PUT /inspections/executions/{id}", "SKIP", "Could not create test execution")
    else:
        log_test("INSPECTION", "GET /inspections/executions/{id}", "SKIP", "No templates available")
        log_test("INSPECTION", "PUT /inspections/executions/{id}", "SKIP", "No templates available")
    
    # Test 3: DELETE /inspections/templates/{id}
    # Create a test template first
    try:
        template_data = {
            "name": "Test Template for Deletion",
            "description": "Template to be deleted",
            "category": "safety",
            "questions": [
                {
                    "question_text": "Test question?",
                    "question_type": "yes_no",
                    "required": True
                }
            ],
            "scoring_enabled": False,
            "pass_percentage": 80.0,
            "require_gps": False,
            "require_photos": False
        }
        create_resp = requests.post(f"{BASE_URL}/inspections/templates", json=template_data, headers=get_headers(), timeout=10)
        if create_resp.status_code == 201:
            template_id = create_resp.json()["id"]
            
            # Now delete it
            response = requests.delete(f"{BASE_URL}/inspections/templates/{template_id}", headers=get_headers(), timeout=10)
            if response.status_code == 200:
                log_test("INSPECTION", "DELETE /inspections/templates/{id}", "PASS", "Template deleted successfully")
            else:
                log_test("INSPECTION", "DELETE /inspections/templates/{id}", "FAIL", f"Status: {response.status_code}")
        else:
            log_test("INSPECTION", "DELETE /inspections/templates/{id}", "SKIP", "Could not create test template")
    except Exception as e:
        log_test("INSPECTION", "DELETE /inspections/templates/{id}", "FAIL", str(e))

# ==================== CHECKLIST TESTS ====================

def test_checklist_endpoints():
    """Test 3 remaining checklist endpoints"""
    print("\n" + "="*60)
    print("TESTING CHECKLIST ENDPOINTS (3 endpoints)")
    print("="*60)
    
    # Test 1: GET /checklists/executions/today
    try:
        response = requests.get(f"{BASE_URL}/checklists/executions/today", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "executions" in data and "pending_templates" in data:
                log_test("CHECKLIST", "GET /checklists/executions/today", "PASS", f"Found {len(data['executions'])} executions today")
            else:
                log_test("CHECKLIST", "GET /checklists/executions/today", "FAIL", "Missing required fields")
        else:
            log_test("CHECKLIST", "GET /checklists/executions/today", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("CHECKLIST", "GET /checklists/executions/today", "FAIL", str(e))
    
    # Create a checklist execution for testing
    templates_resp = requests.get(f"{BASE_URL}/checklists/templates", headers=get_headers(), timeout=10)
    if templates_resp.status_code == 200 and templates_resp.json():
        template_id = templates_resp.json()[0]["id"]
        
        # Create execution
        create_resp = requests.post(f"{BASE_URL}/checklists/executions?template_id={template_id}", headers=get_headers(), timeout=10)
        if create_resp.status_code == 201:
            execution_id = create_resp.json()["id"]
            
            # Test 2: GET /checklists/executions/{id}
            try:
                response = requests.get(f"{BASE_URL}/checklists/executions/{execution_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") == execution_id:
                        log_test("CHECKLIST", "GET /checklists/executions/{id}", "PASS", f"Retrieved execution {execution_id}")
                    else:
                        log_test("CHECKLIST", "GET /checklists/executions/{id}", "FAIL", "ID mismatch")
                else:
                    log_test("CHECKLIST", "GET /checklists/executions/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("CHECKLIST", "GET /checklists/executions/{id}", "FAIL", str(e))
    
    # Test 3: DELETE /checklists/templates/{id}
    try:
        template_data = {
            "name": "Test Checklist Template for Deletion",
            "description": "Template to be deleted",
            "category": "safety",
            "items": [
                {
                    "text": "Test item",
                    "required": True
                }
            ],
            "frequency": "daily"
        }
        create_resp = requests.post(f"{BASE_URL}/checklists/templates", json=template_data, headers=get_headers(), timeout=10)
        if create_resp.status_code == 201:
            template_id = create_resp.json()["id"]
            
            # Now delete it
            response = requests.delete(f"{BASE_URL}/checklists/templates/{template_id}", headers=get_headers(), timeout=10)
            if response.status_code == 200:
                log_test("CHECKLIST", "DELETE /checklists/templates/{id}", "PASS", "Template deleted successfully")
            else:
                log_test("CHECKLIST", "DELETE /checklists/templates/{id}", "FAIL", f"Status: {response.status_code}")
        else:
            log_test("CHECKLIST", "DELETE /checklists/templates/{id}", "SKIP", "Could not create test template")
    except Exception as e:
        log_test("CHECKLIST", "DELETE /checklists/templates/{id}", "FAIL", str(e))

# ==================== TASK TESTS ====================

def test_task_endpoints():
    """Test 4 remaining task endpoints"""
    print("\n" + "="*60)
    print("TESTING TASK ENDPOINTS (4 endpoints)")
    print("="*60)
    
    # Create a task for testing
    task_data = {
        "title": "Test Task for Endpoint Testing",
        "description": "Task for testing remaining endpoints",
        "status": "todo",
        "priority": "medium"
    }
    create_resp = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=get_headers(), timeout=10)
    if create_resp.status_code == 201:
        task_id = create_resp.json()["id"]
        
        # Test 1: PUT /tasks/{id}
        try:
            update_data = {
                "title": "Updated Task Title",
                "status": "in_progress"
            }
            response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("title") == "Updated Task Title":
                    log_test("TASK", "PUT /tasks/{id}", "PASS", "Task updated successfully")
                else:
                    log_test("TASK", "PUT /tasks/{id}", "FAIL", "Title not updated")
            else:
                log_test("TASK", "PUT /tasks/{id}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("TASK", "PUT /tasks/{id}", "FAIL", str(e))
        
        # Test 2: POST /tasks/{id}/comments
        try:
            comment_data = {
                "text": "This is a test comment on the task"
            }
            response = requests.post(f"{BASE_URL}/tasks/{task_id}/comments", json=comment_data, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "comment" in data:
                    log_test("TASK", "POST /tasks/{id}/comments", "PASS", "Comment added successfully")
                else:
                    log_test("TASK", "POST /tasks/{id}/comments", "FAIL", "No comment in response")
            else:
                log_test("TASK", "POST /tasks/{id}/comments", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("TASK", "POST /tasks/{id}/comments", "FAIL", str(e))
        
        # Test 3: DELETE /tasks/{id}
        try:
            response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=get_headers(), timeout=10)
            if response.status_code == 200:
                log_test("TASK", "DELETE /tasks/{id}", "PASS", "Task deleted successfully")
            else:
                log_test("TASK", "DELETE /tasks/{id}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("TASK", "DELETE /tasks/{id}", "FAIL", str(e))
    
    # Test 4: GET /tasks/stats/overview
    try:
        response = requests.get(f"{BASE_URL}/tasks/stats/overview", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "total_tasks" in data and "completed" in data:
                log_test("TASK", "GET /tasks/stats/overview", "PASS", f"Total tasks: {data['total_tasks']}")
            else:
                log_test("TASK", "GET /tasks/stats/overview", "FAIL", "Missing required fields")
        else:
            log_test("TASK", "GET /tasks/stats/overview", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("TASK", "GET /tasks/stats/overview", "FAIL", str(e))

# ==================== USER/AUTH TESTS ====================

def test_user_auth_endpoints():
    """Test 8 remaining user/auth endpoints"""
    print("\n" + "="*60)
    print("TESTING USER/AUTH ENDPOINTS (8 endpoints)")
    print("="*60)
    
    # Test 1: GET /users
    try:
        response = requests.get(f"{BASE_URL}/users", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("USER/AUTH", "GET /users", "PASS", f"Found {len(data)} users")
            else:
                log_test("USER/AUTH", "GET /users", "FAIL", "Response not a list")
        else:
            log_test("USER/AUTH", "GET /users", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("USER/AUTH", "GET /users", "FAIL", str(e))
    
    # Test 2: GET /users/me
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("id") == user_id:
                log_test("USER/AUTH", "GET /users/me", "PASS", f"User: {data.get('name')}")
            else:
                log_test("USER/AUTH", "GET /users/me", "FAIL", "User ID mismatch")
        else:
            log_test("USER/AUTH", "GET /users/me", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("USER/AUTH", "GET /users/me", "FAIL", str(e))
    
    # Test 3: PUT /users/profile
    try:
        profile_data = {
            "phone": "+27123456789"
        }
        response = requests.put(f"{BASE_URL}/users/profile", json=profile_data, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            log_test("USER/AUTH", "PUT /users/profile", "PASS", "Profile updated successfully")
        else:
            log_test("USER/AUTH", "PUT /users/profile", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("USER/AUTH", "PUT /users/profile", "FAIL", str(e))
    
    # Test 4: POST /users/invite
    try:
        invite_data = {
            "email": f"test_invite_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "name": "Test Invited User",
            "role": "viewer"
        }
        response = requests.post(f"{BASE_URL}/users/invite", json=invite_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            log_test("USER/AUTH", "POST /users/invite", "PASS", "User invited successfully")
        else:
            log_test("USER/AUTH", "POST /users/invite", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("USER/AUTH", "POST /users/invite", "FAIL", str(e))
    
    # Test 5: GET /users/pending-approvals
    try:
        response = requests.get(f"{BASE_URL}/users/pending-approvals", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("USER/AUTH", "GET /users/pending-approvals", "PASS", f"Found {len(data)} pending approvals")
            else:
                log_test("USER/AUTH", "GET /users/pending-approvals", "FAIL", "Response not a list")
        else:
            log_test("USER/AUTH", "GET /users/pending-approvals", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("USER/AUTH", "GET /users/pending-approvals", "FAIL", str(e))
    
    # Test 6 & 7: Approve/Reject user - Skip to avoid affecting production data
    log_test("USER/AUTH", "POST /users/{id}/approve", "SKIP", "Skipped to avoid affecting production data")
    log_test("USER/AUTH", "POST /users/{id}/reject", "SKIP", "Skipped to avoid affecting production data")
    
    # Test 8: DELETE /users/{id} - Skip to avoid deleting production users
    log_test("USER/AUTH", "DELETE /users/{id}", "SKIP", "Skipped to avoid deleting production users")

# ==================== ROLE MANAGEMENT TESTS ====================

def test_role_endpoints():
    """Test 4 role management endpoints"""
    print("\n" + "="*60)
    print("TESTING ROLE MANAGEMENT ENDPOINTS (4 endpoints)")
    print("="*60)
    
    # Test 1: GET /roles
    try:
        response = requests.get(f"{BASE_URL}/roles", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("ROLE", "GET /roles", "PASS", f"Found {len(data)} roles")
            else:
                log_test("ROLE", "GET /roles", "FAIL", "Response not a list")
        else:
            log_test("ROLE", "GET /roles", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ROLE", "GET /roles", "FAIL", str(e))
    
    # Test 2: POST /roles
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        role_data = {
            "name": f"Test Role {timestamp}",
            "code": f"test_role_{timestamp}",
            "color": "#10b981",
            "description": "Test role for endpoint testing",
            "level": 5
        }
        response = requests.post(f"{BASE_URL}/roles", json=role_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            created_role = response.json()
            role_id = created_role.get("id")
            log_test("ROLE", "POST /roles", "PASS", f"Role created: {role_id}")
            
            # Test 3: PUT /roles/{id}
            try:
                update_data = {
                    "name": role_data["name"],
                    "code": role_data["code"],
                    "color": role_data["color"],
                    "level": role_data["level"],
                    "description": "Updated role description"
                }
                response = requests.put(f"{BASE_URL}/roles/{role_id}", json=update_data, headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("ROLE", "PUT /roles/{id}", "PASS", "Role updated successfully")
                else:
                    log_test("ROLE", "PUT /roles/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("ROLE", "PUT /roles/{id}", "FAIL", str(e))
            
            # Test 4: DELETE /roles/{id}
            try:
                response = requests.delete(f"{BASE_URL}/roles/{role_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("ROLE", "DELETE /roles/{id}", "PASS", "Role deleted successfully")
                else:
                    log_test("ROLE", "DELETE /roles/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("ROLE", "DELETE /roles/{id}", "FAIL", str(e))
        else:
            log_test("ROLE", "POST /roles", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            log_test("ROLE", "PUT /roles/{id}", "SKIP", "Role creation failed")
            log_test("ROLE", "DELETE /roles/{id}", "SKIP", "Role creation failed")
    except Exception as e:
        log_test("ROLE", "POST /roles", "FAIL", str(e))
        log_test("ROLE", "PUT /roles/{id}", "SKIP", "Role creation failed")
        log_test("ROLE", "DELETE /roles/{id}", "SKIP", "Role creation failed")

# ==================== ORGANIZATION TESTS ====================

def test_organization_endpoints():
    """Test 4 organization endpoints"""
    print("\n" + "="*60)
    print("TESTING ORGANIZATION ENDPOINTS (4 endpoints)")
    print("="*60)
    
    # Test 1: GET /organizations/units
    try:
        response = requests.get(f"{BASE_URL}/organizations/units", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("ORGANIZATION", "GET /organizations/units", "PASS", f"Found {len(data)} units")
            else:
                log_test("ORGANIZATION", "GET /organizations/units", "FAIL", "Response not a list")
        else:
            log_test("ORGANIZATION", "GET /organizations/units", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ORGANIZATION", "GET /organizations/units", "FAIL", str(e))
    
    # Test 2: POST /organizations/units
    try:
        unit_data = {
            "name": f"Test Unit {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Test organizational unit",
            "level": 1  # Root unit must be level 1
        }
        response = requests.post(f"{BASE_URL}/organizations/units", json=unit_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            created_unit = response.json()
            unit_id = created_unit.get("id")
            log_test("ORGANIZATION", "POST /organizations/units", "PASS", f"Unit created: {unit_id}")
            
            # Test 3: PUT /organizations/units/{id}
            try:
                update_data = {
                    "description": "Updated unit description"
                }
                response = requests.put(f"{BASE_URL}/organizations/units/{unit_id}", json=update_data, headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("ORGANIZATION", "PUT /organizations/units/{id}", "PASS", "Unit updated successfully")
                else:
                    log_test("ORGANIZATION", "PUT /organizations/units/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("ORGANIZATION", "PUT /organizations/units/{id}", "FAIL", str(e))
            
            # Test 4: DELETE /organizations/units/{id}
            try:
                response = requests.delete(f"{BASE_URL}/organizations/units/{unit_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("ORGANIZATION", "DELETE /organizations/units/{id}", "PASS", "Unit deleted successfully")
                else:
                    log_test("ORGANIZATION", "DELETE /organizations/units/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("ORGANIZATION", "DELETE /organizations/units/{id}", "FAIL", str(e))
        else:
            log_test("ORGANIZATION", "POST /organizations/units", "FAIL", f"Status: {response.status_code}")
            log_test("ORGANIZATION", "PUT /organizations/units/{id}", "SKIP", "Unit creation failed")
            log_test("ORGANIZATION", "DELETE /organizations/units/{id}", "SKIP", "Unit creation failed")
    except Exception as e:
        log_test("ORGANIZATION", "POST /organizations/units", "FAIL", str(e))
        log_test("ORGANIZATION", "PUT /organizations/units/{id}", "SKIP", "Unit creation failed")
        log_test("ORGANIZATION", "DELETE /organizations/units/{id}", "SKIP", "Unit creation failed")

# ==================== WORKFLOW TESTS ====================

def test_workflow_endpoints():
    """Test 5 workflow endpoints"""
    print("\n" + "="*60)
    print("TESTING WORKFLOW ENDPOINTS (5 endpoints)")
    print("="*60)
    
    # Test 1: GET /workflows/templates
    try:
        response = requests.get(f"{BASE_URL}/workflows/templates", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("WORKFLOW", "GET /workflows/templates", "PASS", f"Found {len(data)} workflow templates")
            else:
                log_test("WORKFLOW", "GET /workflows/templates", "FAIL", "Response not a list")
        else:
            log_test("WORKFLOW", "GET /workflows/templates", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("WORKFLOW", "GET /workflows/templates", "FAIL", str(e))
    
    # Test 2: POST /workflows/templates
    try:
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Test workflow template",
            "resource_type": "task",  # Required field
            "steps": [
                {
                    "step_number": 1,
                    "step_name": "Review",
                    "approver_role": "manager",
                    "required": True
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/workflows/templates", json=workflow_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            log_test("WORKFLOW", "POST /workflows/templates", "PASS", "Workflow template created")
        else:
            log_test("WORKFLOW", "POST /workflows/templates", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("WORKFLOW", "POST /workflows/templates", "FAIL", str(e))
    
    # Test 3: GET /workflows/instances
    try:
        response = requests.get(f"{BASE_URL}/workflows/instances", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("WORKFLOW", "GET /workflows/instances", "PASS", f"Found {len(data)} workflow instances")
            else:
                log_test("WORKFLOW", "GET /workflows/instances", "FAIL", "Response not a list")
        else:
            log_test("WORKFLOW", "GET /workflows/instances", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("WORKFLOW", "GET /workflows/instances", "FAIL", str(e))
    
    # Test 4 & 5: Approve/Reject workflow - Skip to avoid affecting production workflows
    log_test("WORKFLOW", "POST /workflows/instances/{id}/approve", "SKIP", "Skipped to avoid affecting production workflows")
    log_test("WORKFLOW", "POST /workflows/instances/{id}/reject", "SKIP", "Skipped to avoid affecting production workflows")

# ==================== SETTINGS TESTS ====================

def test_settings_endpoints():
    """Test 4 settings endpoints"""
    print("\n" + "="*60)
    print("TESTING SETTINGS ENDPOINTS (4 endpoints)")
    print("="*60)
    
    # Test 1: GET /settings/email
    try:
        response = requests.get(f"{BASE_URL}/settings/email", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "sendgrid_api_key" in data or "configured" in data:
                log_test("SETTINGS", "GET /settings/email", "PASS", "Email settings retrieved")
            else:
                log_test("SETTINGS", "GET /settings/email", "FAIL", "Missing expected fields")
        else:
            log_test("SETTINGS", "GET /settings/email", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("SETTINGS", "GET /settings/email", "FAIL", str(e))
    
    # Test 2: PUT /settings/email - Skip to avoid changing production settings
    log_test("SETTINGS", "PUT /settings/email", "SKIP", "Skipped to avoid changing production email settings")
    
    # Test 3: GET /settings/sms - Endpoint does not exist
    log_test("SETTINGS", "GET /settings/sms", "SKIP", "Endpoint not implemented (SMS settings are under /sms route)")
    
    # Test 4: PUT /settings/sms - Skip to avoid changing production settings
    log_test("SETTINGS", "PUT /settings/sms", "SKIP", "Endpoint not implemented (SMS settings are under /sms route)")

# ==================== BULK IMPORT TESTS ====================

def test_bulk_import_endpoints():
    """Test 2 bulk import endpoints"""
    print("\n" + "="*60)
    print("TESTING BULK IMPORT ENDPOINTS (2 endpoints)")
    print("="*60)
    
    # Test 1: POST /bulk-import/validate
    try:
        csv_data = "name,email,role\nJohn Doe,john@example.com,viewer\nJane Smith,jane@example.com,viewer"
        response = requests.post(
            f"{BASE_URL}/bulk-import/validate",
            data=csv_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "text/csv"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "valid" in data or "errors" in data:
                log_test("BULK_IMPORT", "POST /bulk-import/validate", "PASS", "CSV validation completed")
            else:
                log_test("BULK_IMPORT", "POST /bulk-import/validate", "FAIL", "Missing validation results")
        else:
            log_test("BULK_IMPORT", "POST /bulk-import/validate", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("BULK_IMPORT", "POST /bulk-import/validate", "FAIL", str(e))
    
    # Test 2: POST /bulk-import/users - Skip to avoid creating test users
    log_test("BULK_IMPORT", "POST /bulk-import/users", "SKIP", "Skipped to avoid creating bulk test users")

# ==================== GROUPS TESTS ====================

def test_groups_endpoints():
    """Test 4 groups endpoints"""
    print("\n" + "="*60)
    print("TESTING GROUPS ENDPOINTS (4 endpoints)")
    print("="*60)
    
    # Test 1: GET /groups
    try:
        response = requests.get(f"{BASE_URL}/groups", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("GROUPS", "GET /groups", "PASS", f"Found {len(data)} groups")
            else:
                log_test("GROUPS", "GET /groups", "FAIL", "Response not a list")
        else:
            log_test("GROUPS", "GET /groups", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("GROUPS", "GET /groups", "FAIL", str(e))
    
    # Test 2: POST /groups
    try:
        group_data = {
            "name": f"Test Group {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Test group for endpoint testing",
            "member_ids": []
        }
        response = requests.post(f"{BASE_URL}/groups", json=group_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            created_group = response.json()
            group_id = created_group.get("id")
            log_test("GROUPS", "POST /groups", "PASS", f"Group created: {group_id}")
            
            # Test 3: PUT /groups/{id}
            try:
                update_data = {
                    "description": "Updated group description"
                }
                response = requests.put(f"{BASE_URL}/groups/{group_id}", json=update_data, headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("GROUPS", "PUT /groups/{id}", "PASS", "Group updated successfully")
                else:
                    log_test("GROUPS", "PUT /groups/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("GROUPS", "PUT /groups/{id}", "FAIL", str(e))
            
            # Test 4: DELETE /groups/{id}
            try:
                response = requests.delete(f"{BASE_URL}/groups/{group_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("GROUPS", "DELETE /groups/{id}", "PASS", "Group deleted successfully")
                else:
                    log_test("GROUPS", "DELETE /groups/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("GROUPS", "DELETE /groups/{id}", "FAIL", str(e))
        else:
            log_test("GROUPS", "POST /groups", "FAIL", f"Status: {response.status_code}")
            log_test("GROUPS", "PUT /groups/{id}", "SKIP", "Group creation failed")
            log_test("GROUPS", "DELETE /groups/{id}", "SKIP", "Group creation failed")
    except Exception as e:
        log_test("GROUPS", "POST /groups", "FAIL", str(e))
        log_test("GROUPS", "PUT /groups/{id}", "SKIP", "Group creation failed")
        log_test("GROUPS", "DELETE /groups/{id}", "SKIP", "Group creation failed")

# ==================== WEBHOOKS TESTS ====================

def test_webhooks_endpoints():
    """Test 3 webhooks endpoints"""
    print("\n" + "="*60)
    print("TESTING WEBHOOKS ENDPOINTS (3 endpoints)")
    print("="*60)
    
    # Test 1: GET /webhooks
    try:
        response = requests.get(f"{BASE_URL}/webhooks", headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("WEBHOOKS", "GET /webhooks", "PASS", f"Found {len(data)} webhooks")
            else:
                log_test("WEBHOOKS", "GET /webhooks", "FAIL", "Response not a list")
        else:
            log_test("WEBHOOKS", "GET /webhooks", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("WEBHOOKS", "GET /webhooks", "FAIL", str(e))
    
    # Test 2: POST /webhooks
    try:
        webhook_data = {
            "name": f"Test Webhook {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "url": "https://example.com/webhook",
            "events": ["task.created", "task.completed"],
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/webhooks", json=webhook_data, headers=get_headers(), timeout=10)
        if response.status_code in [200, 201]:
            created_webhook = response.json()
            webhook_id = created_webhook.get("id")
            log_test("WEBHOOKS", "POST /webhooks", "PASS", f"Webhook created: {webhook_id}")
            
            # Test 3: DELETE /webhooks/{id}
            try:
                response = requests.delete(f"{BASE_URL}/webhooks/{webhook_id}", headers=get_headers(), timeout=10)
                if response.status_code == 200:
                    log_test("WEBHOOKS", "DELETE /webhooks/{id}", "PASS", "Webhook deleted successfully")
                else:
                    log_test("WEBHOOKS", "DELETE /webhooks/{id}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                log_test("WEBHOOKS", "DELETE /webhooks/{id}", "FAIL", str(e))
        else:
            log_test("WEBHOOKS", "POST /webhooks", "FAIL", f"Status: {response.status_code}")
            log_test("WEBHOOKS", "DELETE /webhooks/{id}", "SKIP", "Webhook creation failed")
    except Exception as e:
        log_test("WEBHOOKS", "POST /webhooks", "FAIL", str(e))
        log_test("WEBHOOKS", "DELETE /webhooks/{id}", "SKIP", "Webhook creation failed")

# ==================== MAIN EXECUTION ====================

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(test_results)
    passed = len([r for r in test_results if r["status"] == "PASS"])
    failed = len([r for r in test_results if r["status"] == "FAIL"])
    skipped = len([r for r in test_results if r["status"] == "SKIP"])
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"\nSuccess Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n" + "="*60)
        print("FAILED TESTS:")
        print("="*60)
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"\n❌ [{result['group']}] {result['test']}")
                print(f"   Details: {result['details']}")
    
    # Save results to file
    with open("/app/remaining_42_endpoints_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Detailed results saved to: /app/remaining_42_endpoints_test_results.json")

def main():
    """Main test execution"""
    print("="*60)
    print("COMPREHENSIVE BACKEND TESTING - 42 REMAINING ENDPOINTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['email']}")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    # Login
    if not login():
        print("\n❌ Login failed. Cannot proceed with tests.")
        sys.exit(1)
    
    # Run all test groups
    test_inspection_endpoints()
    test_checklist_endpoints()
    test_task_endpoints()
    test_user_auth_endpoints()
    test_role_endpoints()
    test_organization_endpoints()
    test_workflow_endpoints()
    test_settings_endpoints()
    test_bulk_import_endpoints()
    test_groups_endpoints()
    test_webhooks_endpoints()
    
    # Print summary
    print_summary()
    
    print(f"\n✅ Testing completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
