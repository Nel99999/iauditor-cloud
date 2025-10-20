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

# Backend URL from frontend/.env
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"

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
    "modules": {}
}

def log_test(module, test_name, passed, details=""):
    """Log test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
    
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
    
    print(f"{status} - {module}: {test_name}")
    if details and not passed:
        print(f"   Details: {details}")

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
            log_test("Authentication", "Login", True, f"Token obtained, org_id: {org_id}")
            return True
        else:
            log_test("Authentication", "Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        log_test("Authentication", "Login", False, str(e))
        return False

def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ============================================================================
# MODULE 1: AUTHENTICATION & USERS
# ============================================================================

def test_authentication_users():
    """Test authentication and user management"""
    module = "Authentication & Users"
    
    # Test 1: Get current user profile
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
        if response.status_code == 200:
            user = response.json()
            log_test(module, "Get current user profile", True, f"User: {user.get('email')}")
        else:
            log_test(module, "Get current user profile", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get current user profile", False, str(e))
    
    # Test 2: Update user profile
    try:
        response = requests.put(f"{BASE_URL}/users/profile", 
            headers=get_headers(),
            json={"phone": "+27123456789"}
        )
        log_test(module, "Update user profile", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Update user profile", False, str(e))
    
    # Test 3: List users
    try:
        response = requests.get(f"{BASE_URL}/users", headers=get_headers())
        log_test(module, "List users", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List users", False, str(e))

# ============================================================================
# MODULE 2: ROLES & PERMISSIONS
# ============================================================================

def test_roles_permissions():
    """Test roles and permissions"""
    module = "Roles & Permissions"
    
    # Test 1: List roles
    try:
        response = requests.get(f"{BASE_URL}/roles", headers=get_headers())
        if response.status_code == 200:
            roles = response.json()
            log_test(module, "List roles", True, f"Found {len(roles)} roles")
            
            # Test 2: Verify developer role has 121 permissions
            dev_role = next((r for r in roles if r.get("code") == "developer"), None)
            if dev_role:
                perm_count = len(dev_role.get("permission_ids", []))
                log_test(module, "Developer role has 121 permissions", 
                        perm_count == 121, f"Found {perm_count} permissions")
            else:
                log_test(module, "Developer role has 121 permissions", False, "Developer role not found")
        else:
            log_test(module, "List roles", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List roles", False, str(e))
    
    # Test 3: List all permissions
    try:
        response = requests.get(f"{BASE_URL}/permissions", headers=get_headers())
        if response.status_code == 200:
            permissions = response.json()
            log_test(module, "List all permissions", True, f"Found {len(permissions)} permissions")
        else:
            log_test(module, "List all permissions", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List all permissions", False, str(e))

# ============================================================================
# MODULE 3: ORGANIZATIONS
# ============================================================================

def test_organizations():
    """Test organization management"""
    module = "Organizations"
    
    # Test 1: Get organization units
    try:
        response = requests.get(f"{BASE_URL}/organizations/units", headers=get_headers())
        if response.status_code == 200:
            units = response.json()
            log_test(module, "Get organization units", True, f"Found {len(units)} units")
        else:
            log_test(module, "Get organization units", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get organization units", False, str(e))
    
    # Test 2: Get organization stats
    try:
        response = requests.get(f"{BASE_URL}/organizations/stats", headers=get_headers())
        log_test(module, "Get organization stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get organization stats", False, str(e))
    
    # Test 3: Create organization unit
    try:
        unit_data = {
            "name": f"Test Unit {uuid.uuid4().hex[:8]}",
            "level": 1,
            "parent_id": None
        }
        response = requests.post(f"{BASE_URL}/organizations/units", 
            headers=get_headers(), json=unit_data)
        log_test(module, "Create organization unit", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create organization unit", False, str(e))

# ============================================================================
# MODULE 4: INSPECTIONS
# ============================================================================

def test_inspections():
    """Test inspections module"""
    module = "Inspections"
    
    # Test 1: List inspection templates
    try:
        response = requests.get(f"{BASE_URL}/inspections/templates", headers=get_headers())
        if response.status_code == 200:
            templates = response.json()
            log_test(module, "List inspection templates", True, f"Found {len(templates)} templates")
        else:
            log_test(module, "List inspection templates", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List inspection templates", False, str(e))
    
    # Test 2: Create inspection template
    try:
        template_data = {
            "title": f"Test Inspection {uuid.uuid4().hex[:8]}",
            "description": "Test inspection template",
            "category": "Safety",
            "sections": [
                {
                    "title": "Section 1",
                    "questions": [
                        {
                            "text": "Test question",
                            "type": "yes_no",
                            "required": True
                        }
                    ]
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/inspections/templates", 
            headers=get_headers(), json=template_data)
        log_test(module, "Create inspection template", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create inspection template", False, str(e))
    
    # Test 3: List inspection executions
    try:
        response = requests.get(f"{BASE_URL}/inspections/executions", headers=get_headers())
        log_test(module, "List inspection executions", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List inspection executions", False, str(e))
    
    # Test 4: Get inspection analytics
    try:
        response = requests.get(f"{BASE_URL}/inspections/analytics", headers=get_headers())
        log_test(module, "Get inspection analytics", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get inspection analytics", False, str(e))

# ============================================================================
# MODULE 5: CHECKLISTS
# ============================================================================

def test_checklists():
    """Test checklists module"""
    module = "Checklists"
    
    # Test 1: List checklist templates
    try:
        response = requests.get(f"{BASE_URL}/checklists/templates", headers=get_headers())
        if response.status_code == 200:
            templates = response.json()
            log_test(module, "List checklist templates", True, f"Found {len(templates)} templates")
        else:
            log_test(module, "List checklist templates", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List checklist templates", False, str(e))
    
    # Test 2: Create checklist template
    try:
        template_data = {
            "title": f"Test Checklist {uuid.uuid4().hex[:8]}",
            "description": "Test checklist template",
            "category": "Maintenance",
            "items": [
                {
                    "text": "Test item 1",
                    "required": True
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/checklists/templates", 
            headers=get_headers(), json=template_data)
        log_test(module, "Create checklist template", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create checklist template", False, str(e))
    
    # Test 3: List checklist executions
    try:
        response = requests.get(f"{BASE_URL}/checklists/executions", headers=get_headers())
        log_test(module, "List checklist executions", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List checklist executions", False, str(e))
    
    # Test 4: Get checklist analytics
    try:
        response = requests.get(f"{BASE_URL}/checklists/analytics", headers=get_headers())
        log_test(module, "Get checklist analytics", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get checklist analytics", False, str(e))

# ============================================================================
# MODULE 6: TASKS
# ============================================================================

def test_tasks():
    """Test tasks module"""
    module = "Tasks"
    created_task_id = None
    
    # Test 1: List tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=get_headers())
        if response.status_code == 200:
            tasks = response.json()
            log_test(module, "List tasks", True, f"Found {len(tasks)} tasks")
        else:
            log_test(module, "List tasks", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List tasks", False, str(e))
    
    # Test 2: Create task
    try:
        task_data = {
            "title": f"Test Task {uuid.uuid4().hex[:8]}",
            "description": "Test task description",
            "priority": "high",
            "status": "open",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        response = requests.post(f"{BASE_URL}/tasks", 
            headers=get_headers(), json=task_data)
        if response.status_code == 200:
            created_task_id = response.json().get("id")
            log_test(module, "Create task", True, f"Task ID: {created_task_id}")
        else:
            log_test(module, "Create task", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create task", False, str(e))
    
    # Test 3: Update task
    if created_task_id:
        try:
            response = requests.put(f"{BASE_URL}/tasks/{created_task_id}", 
                headers=get_headers(), 
                json={"status": "in_progress"})
            log_test(module, "Update task", response.status_code == 200, 
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test(module, "Update task", False, str(e))
    
    # Test 4: Get task stats
    try:
        response = requests.get(f"{BASE_URL}/tasks/stats", headers=get_headers())
        log_test(module, "Get task stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get task stats", False, str(e))
    
    # Test 5: Get task analytics
    try:
        response = requests.get(f"{BASE_URL}/tasks/analytics", headers=get_headers())
        log_test(module, "Get task analytics", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get task analytics", False, str(e))

# ============================================================================
# MODULE 7: ASSETS
# ============================================================================

def test_assets():
    """Test assets module"""
    module = "Assets"
    created_asset_id = None
    
    # Test 1: List assets
    try:
        response = requests.get(f"{BASE_URL}/assets", headers=get_headers())
        if response.status_code == 200:
            assets = response.json()
            log_test(module, "List assets", True, f"Found {len(assets)} assets")
        else:
            log_test(module, "List assets", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List assets", False, str(e))
    
    # Test 2: Create asset (verify auto-generate asset_tag)
    try:
        asset_data = {
            "name": f"Test Asset {uuid.uuid4().hex[:8]}",
            "description": "Test asset",
            "type": "Equipment",
            "status": "active"
        }
        response = requests.post(f"{BASE_URL}/assets", 
            headers=get_headers(), json=asset_data)
        if response.status_code == 200:
            asset = response.json()
            created_asset_id = asset.get("id")
            asset_tag = asset.get("asset_tag")
            log_test(module, "Create asset with auto-generated asset_tag", 
                    bool(asset_tag), f"Asset tag: {asset_tag}")
        else:
            log_test(module, "Create asset with auto-generated asset_tag", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create asset with auto-generated asset_tag", False, str(e))
    
    # Test 3: Get asset stats
    try:
        response = requests.get(f"{BASE_URL}/assets/stats", headers=get_headers())
        log_test(module, "Get asset stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get asset stats", False, str(e))
    
    # Test 4: Get asset QR code
    if created_asset_id:
        try:
            response = requests.get(f"{BASE_URL}/assets/{created_asset_id}/qr", 
                headers=get_headers())
            log_test(module, "Get asset QR code", response.status_code == 200, 
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test(module, "Get asset QR code", False, str(e))

# ============================================================================
# MODULE 8: WORK ORDERS
# ============================================================================

def test_work_orders():
    """Test work orders module"""
    module = "Work Orders"
    created_wo_id = None
    
    # Test 1: List work orders
    try:
        response = requests.get(f"{BASE_URL}/workorders", headers=get_headers())
        if response.status_code == 200:
            wos = response.json()
            log_test(module, "List work orders", True, f"Found {len(wos)} work orders")
        else:
            log_test(module, "List work orders", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List work orders", False, str(e))
    
    # Test 2: Create work order
    try:
        wo_data = {
            "title": f"Test Work Order {uuid.uuid4().hex[:8]}",
            "description": "Test work order",
            "priority": "medium",
            "status": "open",
            "type": "corrective"
        }
        response = requests.post(f"{BASE_URL}/workorders", 
            headers=get_headers(), json=wo_data)
        if response.status_code == 200:
            created_wo_id = response.json().get("id")
            log_test(module, "Create work order", True, f"WO ID: {created_wo_id}")
        else:
            log_test(module, "Create work order", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create work order", False, str(e))
    
    # Test 3: Get work order stats
    try:
        response = requests.get(f"{BASE_URL}/workorders/stats", headers=get_headers())
        log_test(module, "Get work order stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get work order stats", False, str(e))
    
    # Test 4: Get work order backlog
    try:
        response = requests.get(f"{BASE_URL}/workorders/backlog", headers=get_headers())
        log_test(module, "Get work order backlog", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get work order backlog", False, str(e))

# ============================================================================
# MODULE 9: INVENTORY
# ============================================================================

def test_inventory():
    """Test inventory module"""
    module = "Inventory"
    created_item_id = None
    
    # Test 1: List inventory items
    try:
        response = requests.get(f"{BASE_URL}/inventory/items", headers=get_headers())
        if response.status_code == 200:
            items = response.json()
            log_test(module, "List inventory items", True, f"Found {len(items)} items")
        else:
            log_test(module, "List inventory items", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List inventory items", False, str(e))
    
    # Test 2: Create inventory item
    try:
        item_data = {
            "name": f"Test Item {uuid.uuid4().hex[:8]}",
            "description": "Test inventory item",
            "sku": f"SKU-{uuid.uuid4().hex[:8]}",
            "quantity": 100,
            "unit": "pieces",
            "reorder_point": 20
        }
        response = requests.post(f"{BASE_URL}/inventory/items", 
            headers=get_headers(), json=item_data)
        if response.status_code == 200:
            created_item_id = response.json().get("id")
            log_test(module, "Create inventory item", True, f"Item ID: {created_item_id}")
        else:
            log_test(module, "Create inventory item", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create inventory item", False, str(e))
    
    # Test 3: Get inventory stats
    try:
        response = requests.get(f"{BASE_URL}/inventory/stats", headers=get_headers())
        log_test(module, "Get inventory stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get inventory stats", False, str(e))
    
    # Test 4: Get reorder items
    try:
        response = requests.get(f"{BASE_URL}/inventory/reorder", headers=get_headers())
        log_test(module, "Get reorder items", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get reorder items", False, str(e))

# ============================================================================
# MODULE 10: PROJECTS
# ============================================================================

def test_projects():
    """Test projects module"""
    module = "Projects"
    created_project_id = None
    
    # Test 1: List projects
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=get_headers())
        if response.status_code == 200:
            projects = response.json()
            log_test(module, "List projects", True, f"Found {len(projects)} projects")
        else:
            log_test(module, "List projects", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List projects", False, str(e))
    
    # Test 2: Create project
    try:
        project_data = {
            "name": f"Test Project {uuid.uuid4().hex[:8]}",
            "description": "Test project",
            "status": "planning",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        response = requests.post(f"{BASE_URL}/projects", 
            headers=get_headers(), json=project_data)
        if response.status_code == 200:
            created_project_id = response.json().get("id")
            log_test(module, "Create project", True, f"Project ID: {created_project_id}")
        else:
            log_test(module, "Create project", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create project", False, str(e))
    
    # Test 3: Get project stats
    try:
        response = requests.get(f"{BASE_URL}/projects/stats", headers=get_headers())
        log_test(module, "Get project stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get project stats", False, str(e))
    
    # Test 4: Get project dashboard
    try:
        response = requests.get(f"{BASE_URL}/projects/dashboard", headers=get_headers())
        log_test(module, "Get project dashboard", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get project dashboard", False, str(e))

# ============================================================================
# MODULE 11: INCIDENTS
# ============================================================================

def test_incidents():
    """Test incidents module"""
    module = "Incidents"
    created_incident_id = None
    
    # Test 1: List incidents
    try:
        response = requests.get(f"{BASE_URL}/incidents", headers=get_headers())
        if response.status_code == 200:
            incidents = response.json()
            log_test(module, "List incidents", True, f"Found {len(incidents)} incidents")
        else:
            log_test(module, "List incidents", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List incidents", False, str(e))
    
    # Test 2: Create incident
    try:
        incident_data = {
            "title": f"Test Incident {uuid.uuid4().hex[:8]}",
            "description": "Test incident",
            "severity": "medium",
            "status": "open",
            "incident_date": datetime.now().isoformat()
        }
        response = requests.post(f"{BASE_URL}/incidents", 
            headers=get_headers(), json=incident_data)
        if response.status_code == 200:
            created_incident_id = response.json().get("id")
            log_test(module, "Create incident", True, f"Incident ID: {created_incident_id}")
        else:
            log_test(module, "Create incident", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create incident", False, str(e))
    
    # Test 3: Get incident stats
    try:
        response = requests.get(f"{BASE_URL}/incidents/stats", headers=get_headers())
        log_test(module, "Get incident stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get incident stats", False, str(e))

# ============================================================================
# MODULE 12: TRAINING
# ============================================================================

def test_training():
    """Test training module"""
    module = "Training"
    created_course_id = None
    
    # Test 1: List training courses
    try:
        response = requests.get(f"{BASE_URL}/training/courses", headers=get_headers())
        if response.status_code == 200:
            courses = response.json()
            log_test(module, "List training courses", True, f"Found {len(courses)} courses")
        else:
            log_test(module, "List training courses", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List training courses", False, str(e))
    
    # Test 2: Create training course
    try:
        course_data = {
            "title": f"Test Course {uuid.uuid4().hex[:8]}",
            "description": "Test training course",
            "duration_hours": 8,
            "category": "Safety"
        }
        response = requests.post(f"{BASE_URL}/training/courses", 
            headers=get_headers(), json=course_data)
        if response.status_code == 200:
            created_course_id = response.json().get("id")
            log_test(module, "Create training course", True, f"Course ID: {created_course_id}")
        else:
            log_test(module, "Create training course", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create training course", False, str(e))
    
    # Test 3: Get training stats
    try:
        response = requests.get(f"{BASE_URL}/training/stats", headers=get_headers())
        log_test(module, "Get training stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get training stats", False, str(e))

# ============================================================================
# MODULE 13: FINANCIAL
# ============================================================================

def test_financial():
    """Test financial module"""
    module = "Financial"
    
    # Test 1: List financial transactions
    try:
        response = requests.get(f"{BASE_URL}/financial/transactions", headers=get_headers())
        if response.status_code == 200:
            transactions = response.json()
            log_test(module, "List financial transactions", True, 
                    f"Found {len(transactions)} transactions")
        else:
            log_test(module, "List financial transactions", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List financial transactions", False, str(e))
    
    # Test 2: Create financial transaction
    try:
        transaction_data = {
            "description": f"Test Transaction {uuid.uuid4().hex[:8]}",
            "amount": 1000.00,
            "type": "expense",
            "category": "maintenance",
            "date": datetime.now().isoformat()
        }
        response = requests.post(f"{BASE_URL}/financial/transactions", 
            headers=get_headers(), json=transaction_data)
        log_test(module, "Create financial transaction", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create financial transaction", False, str(e))
    
    # Test 3: Get CAPEX data
    try:
        response = requests.get(f"{BASE_URL}/financial/capex", headers=get_headers())
        log_test(module, "Get CAPEX data", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get CAPEX data", False, str(e))
    
    # Test 4: Get OPEX data
    try:
        response = requests.get(f"{BASE_URL}/financial/opex", headers=get_headers())
        log_test(module, "Get OPEX data", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get OPEX data", False, str(e))
    
    # Test 5: Get budgets
    try:
        response = requests.get(f"{BASE_URL}/financial/budgets", headers=get_headers())
        log_test(module, "Get budgets", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get budgets", False, str(e))
    
    # Test 6: Get financial summary
    try:
        response = requests.get(f"{BASE_URL}/financial/summary", headers=get_headers())
        log_test(module, "Get financial summary", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get financial summary", False, str(e))
    
    # Test 7: Get financial stats
    try:
        response = requests.get(f"{BASE_URL}/financial/stats", headers=get_headers())
        log_test(module, "Get financial stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get financial stats", False, str(e))

# ============================================================================
# MODULE 14: HR
# ============================================================================

def test_hr():
    """Test HR module"""
    module = "HR"
    
    # Test 1: List employees
    try:
        response = requests.get(f"{BASE_URL}/hr/employees", headers=get_headers())
        if response.status_code == 200:
            employees = response.json()
            log_test(module, "List employees", True, f"Found {len(employees)} employees")
        else:
            log_test(module, "List employees", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List employees", False, str(e))
    
    # Test 2: Create employee (verify auto-generate fields)
    try:
        employee_data = {
            "first_name": "Test",
            "last_name": f"Employee{uuid.uuid4().hex[:8]}",
            "email": f"test.employee.{uuid.uuid4().hex[:8]}@example.com",
            "position": "Technician",
            "department": "Maintenance"
        }
        response = requests.post(f"{BASE_URL}/hr/employees", 
            headers=get_headers(), json=employee_data)
        if response.status_code == 200:
            employee = response.json()
            employee_number = employee.get("employee_number")
            log_test(module, "Create employee with auto-generated employee_number", 
                    bool(employee_number), f"Employee number: {employee_number}")
        else:
            log_test(module, "Create employee with auto-generated employee_number", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create employee with auto-generated employee_number", False, str(e))
    
    # Test 3: Get HR stats
    try:
        response = requests.get(f"{BASE_URL}/hr/stats", headers=get_headers())
        log_test(module, "Get HR stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get HR stats", False, str(e))
    
    # Test 4: List announcements
    try:
        response = requests.get(f"{BASE_URL}/hr/announcements", headers=get_headers())
        log_test(module, "List HR announcements", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List HR announcements", False, str(e))

# ============================================================================
# MODULE 15: EMERGENCY
# ============================================================================

def test_emergency():
    """Test emergency module"""
    module = "Emergency"
    
    # Test 1: List emergencies
    try:
        response = requests.get(f"{BASE_URL}/emergencies", headers=get_headers())
        if response.status_code == 200:
            emergencies = response.json()
            log_test(module, "List emergencies", True, f"Found {len(emergencies)} emergencies")
        else:
            log_test(module, "List emergencies", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List emergencies", False, str(e))
    
    # Test 2: Get active emergencies
    try:
        response = requests.get(f"{BASE_URL}/emergencies/active", headers=get_headers())
        log_test(module, "Get active emergencies", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get active emergencies", False, str(e))

# ============================================================================
# MODULE 16: DASHBOARDS
# ============================================================================

def test_dashboards():
    """Test dashboard endpoints"""
    module = "Dashboards"
    
    # Test 1: Get dashboard stats
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=get_headers())
        log_test(module, "Get dashboard stats", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get dashboard stats", False, str(e))
    
    # Test 2: Get financial dashboard
    try:
        response = requests.get(f"{BASE_URL}/dashboard/financial", headers=get_headers())
        log_test(module, "Get financial dashboard", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get financial dashboard", False, str(e))
    
    # Test 3: Get executive dashboard
    try:
        response = requests.get(f"{BASE_URL}/dashboard/executive", headers=get_headers())
        log_test(module, "Get executive dashboard", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get executive dashboard", False, str(e))
    
    # Test 4: Get safety dashboard
    try:
        response = requests.get(f"{BASE_URL}/dashboard/safety", headers=get_headers())
        log_test(module, "Get safety dashboard", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get safety dashboard", False, str(e))
    
    # Test 5: Get maintenance dashboard
    try:
        response = requests.get(f"{BASE_URL}/dashboard/maintenance", headers=get_headers())
        log_test(module, "Get maintenance dashboard", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get maintenance dashboard", False, str(e))

# ============================================================================
# MODULE 17: TEAM CHAT
# ============================================================================

def test_team_chat():
    """Test team chat module"""
    module = "Team Chat"
    created_channel_id = None
    
    # Test 1: List chat channels
    try:
        response = requests.get(f"{BASE_URL}/chat/channels", headers=get_headers())
        if response.status_code == 200:
            channels = response.json()
            log_test(module, "List chat channels", True, f"Found {len(channels)} channels")
        else:
            log_test(module, "List chat channels", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List chat channels", False, str(e))
    
    # Test 2: Create chat channel
    try:
        channel_data = {
            "name": f"test-channel-{uuid.uuid4().hex[:8]}",
            "description": "Test chat channel",
            "type": "public"
        }
        response = requests.post(f"{BASE_URL}/chat/channels", 
            headers=get_headers(), json=channel_data)
        if response.status_code == 200:
            created_channel_id = response.json().get("id")
            log_test(module, "Create chat channel", True, f"Channel ID: {created_channel_id}")
        else:
            log_test(module, "Create chat channel", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create chat channel", False, str(e))
    
    # Test 3: Send message
    if created_channel_id:
        try:
            message_data = {
                "content": "Test message",
                "channel_id": created_channel_id
            }
            response = requests.post(f"{BASE_URL}/chat/messages", 
                headers=get_headers(), json=message_data)
            log_test(module, "Send chat message", response.status_code == 200, 
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test(module, "Send chat message", False, str(e))

# ============================================================================
# MODULE 18: CONTRACTORS
# ============================================================================

def test_contractors():
    """Test contractors module"""
    module = "Contractors"
    created_contractor_id = None
    
    # Test 1: List contractors
    try:
        response = requests.get(f"{BASE_URL}/contractors", headers=get_headers())
        if response.status_code == 200:
            contractors = response.json()
            log_test(module, "List contractors", True, f"Found {len(contractors)} contractors")
        else:
            log_test(module, "List contractors", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List contractors", False, str(e))
    
    # Test 2: Create contractor
    try:
        contractor_data = {
            "name": f"Test Contractor {uuid.uuid4().hex[:8]}",
            "company": "Test Company",
            "email": f"contractor.{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+27123456789",
            "specialty": "Electrical"
        }
        response = requests.post(f"{BASE_URL}/contractors", 
            headers=get_headers(), json=contractor_data)
        if response.status_code == 200:
            created_contractor_id = response.json().get("id")
            log_test(module, "Create contractor", True, f"Contractor ID: {created_contractor_id}")
        else:
            log_test(module, "Create contractor", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create contractor", False, str(e))

# ============================================================================
# MODULE 19: ANNOUNCEMENTS
# ============================================================================

def test_announcements():
    """Test announcements module"""
    module = "Announcements"
    created_announcement_id = None
    
    # Test 1: List announcements
    try:
        response = requests.get(f"{BASE_URL}/announcements", headers=get_headers())
        if response.status_code == 200:
            announcements = response.json()
            log_test(module, "List announcements", True, 
                    f"Found {len(announcements)} announcements")
        else:
            log_test(module, "List announcements", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List announcements", False, str(e))
    
    # Test 2: Create announcement
    try:
        announcement_data = {
            "title": f"Test Announcement {uuid.uuid4().hex[:8]}",
            "content": "Test announcement content",
            "priority": "normal",
            "target_audience": "all"
        }
        response = requests.post(f"{BASE_URL}/announcements", 
            headers=get_headers(), json=announcement_data)
        if response.status_code == 200:
            created_announcement_id = response.json().get("id")
            log_test(module, "Create announcement", True, 
                    f"Announcement ID: {created_announcement_id}")
        else:
            log_test(module, "Create announcement", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Create announcement", False, str(e))

# ============================================================================
# MODULE 20: ADDITIONAL FEATURES
# ============================================================================

def test_additional_features():
    """Test additional features"""
    module = "Additional Features"
    
    # Test 1: List groups
    try:
        response = requests.get(f"{BASE_URL}/groups", headers=get_headers())
        log_test(module, "List groups", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List groups", False, str(e))
    
    # Test 2: List webhooks
    try:
        response = requests.get(f"{BASE_URL}/webhooks", headers=get_headers())
        log_test(module, "List webhooks", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List webhooks", False, str(e))
    
    # Test 3: List workflows
    try:
        response = requests.get(f"{BASE_URL}/workflows", headers=get_headers())
        log_test(module, "List workflows", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "List workflows", False, str(e))
    
    # Test 4: Get audit logs
    try:
        response = requests.get(f"{BASE_URL}/audit/logs", headers=get_headers())
        log_test(module, "Get audit logs", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get audit logs", False, str(e))
    
    # Test 5: Get notifications
    try:
        response = requests.get(f"{BASE_URL}/notifications", headers=get_headers())
        log_test(module, "Get notifications", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get notifications", False, str(e))
    
    # Test 6: Get analytics
    try:
        response = requests.get(f"{BASE_URL}/analytics/overview", headers=get_headers())
        log_test(module, "Get analytics overview", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get analytics overview", False, str(e))
    
    # Test 7: Get reports overview
    try:
        response = requests.get(f"{BASE_URL}/reports/overview", headers=get_headers())
        log_test(module, "Get reports overview", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Get reports overview", False, str(e))
    
    # Test 8: Search (verify aliases)
    try:
        response = requests.get(f"{BASE_URL}/search?q=test", headers=get_headers())
        log_test(module, "Search with aliases", response.status_code == 200, 
                f"Status: {response.status_code}")
    except Exception as e:
        log_test(module, "Search with aliases", False, str(e))

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("FINAL VERIFICATION - BACKEND TEST SUMMARY")
    print("="*80)
    
    success_rate = (test_results["passed"] / test_results["total"] * 100) if test_results["total"] > 0 else 0
    
    print(f"\nOVERALL RESULTS:")
    print(f"  Total Tests: {test_results['total']}")
    print(f"  Passed: {test_results['passed']} ✅")
    print(f"  Failed: {test_results['failed']} ❌")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print(f"\n🎉 SUCCESS TARGET ACHIEVED: {success_rate:.1f}% >= 95%")
    else:
        print(f"\n⚠️  SUCCESS TARGET NOT MET: {success_rate:.1f}% < 95%")
    
    print(f"\nRESULTS BY MODULE:")
    for module, results in test_results["modules"].items():
        total = results["passed"] + results["failed"]
        rate = (results["passed"] / total * 100) if total > 0 else 0
        status = "✅" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
        print(f"  {status} {module}: {results['passed']}/{total} ({rate:.1f}%)")
    
    # Show failed tests
    print(f"\nFAILED TESTS DETAILS:")
    has_failures = False
    for module, results in test_results["modules"].items():
        failed_tests = [t for t in results["tests"] if not t["passed"]]
        if failed_tests:
            has_failures = True
            print(f"\n  {module}:")
            for test in failed_tests:
                print(f"    ❌ {test['name']}")
                if test['details']:
                    print(f"       {test['details']}")
    
    if not has_failures:
        print("  None - All tests passed! 🎉")
    
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
    print(f"   User ID: {user_id}")
    print("\n" + "="*80)
    print("STARTING MODULE TESTS")
    print("="*80 + "\n")
    
    # Run all module tests
    test_authentication_users()
    test_roles_permissions()
    test_organizations()
    test_inspections()
    test_checklists()
    test_tasks()
    test_assets()
    test_work_orders()
    test_inventory()
    test_projects()
    test_incidents()
    test_training()
    test_financial()
    test_hr()
    test_emergency()
    test_dashboards()
    test_team_chat()
    test_contractors()
    test_announcements()
    test_additional_features()
    
    # Print summary
    print_summary()
    
    # Save results to file
    with open("/app/final_verification_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/final_verification_test_results.json")

if __name__ == "__main__":
    main()
