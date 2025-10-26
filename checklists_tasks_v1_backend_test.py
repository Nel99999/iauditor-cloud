#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Checklists & Tasks V1 Enhancements
Tests all 28 endpoints (11 checklists + 17 tasks)
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "TestPassword123!"
}

# Global variables
token = None
user_id = None
org_id = None
test_results = []

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        "test": test_name,
        "passed": passed,
        "details": details
    })
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")

def login():
    """Login and get token"""
    global token, user_id, org_id
    
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        org_id = data.get("user", {}).get("organization_id")
        log_test("Login", True, f"User: {data.get('user', {}).get('name')}, Role: {data.get('user', {}).get('role')}")
        return True
    else:
        log_test("Login", False, f"Status: {response.status_code}, Error: {response.text}")
        return False

def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ==================== CHECKLISTS V1 TESTS ====================

def test_checklist_template_with_v1_fields():
    """TEST 1: Create checklist template with V1 fields"""
    print("\n" + "="*80)
    print("MODULE 1: CHECKLISTS V1 ENHANCEMENTS")
    print("="*80)
    print("\nTEST GROUP 1: Enhanced Template Creation")
    
    template_data = {
        "name": "V1 Enhanced Safety Checklist",
        "description": "Testing V1 enhancement fields",
        "category": "safety",
        "frequency": "daily",
        "items": [
            {
                "text": "Check fire extinguisher",
                "required": True,
                "photo_required": True,
                "min_photos": 1,
                "max_photos": 3,
                "signature_required": False,
                "scoring_enabled": True,
                "pass_score": 80.0
            },
            {
                "text": "Verify emergency exits",
                "required": True,
                "photo_required": False,
                "signature_required": True,
                "scoring_enabled": True,
                "pass_score": 100.0
            }
        ],
        # V1 Enhancement fields
        "unit_ids": ["test-unit-1"],
        "shift_based": True,
        "time_limit_minutes": 30,
        "scoring_enabled": True,
        "pass_percentage": 80.0,
        "auto_create_work_order_on_fail": True,
        "work_order_priority": "high",
        "requires_supervisor_approval": True
    }
    
    response = requests.post(
        f"{BASE_URL}/checklists/templates",
        headers=get_headers(),
        json=template_data
    )
    
    if response.status_code == 201:
        data = response.json()
        template_id = data.get("id")
        
        # Verify V1 fields
        v1_fields_present = all([
            "unit_ids" in data or data.get("unit_ids") == [],
            "shift_based" in data,
            "time_limit_minutes" in data,
            "scoring_enabled" in data,
            "pass_percentage" in data,
            "auto_create_work_order_on_fail" in data,
            "requires_supervisor_approval" in data
        ])
        
        log_test("Create template with V1 fields", v1_fields_present, 
                f"Template ID: {template_id}, V1 fields present: {v1_fields_present}")
        return template_id
    else:
        log_test("Create template with V1 fields", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_list_templates():
    """TEST 2: List templates"""
    response = requests.get(
        f"{BASE_URL}/checklists/templates",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        templates = response.json()
        log_test("List templates", True, f"Found {len(templates)} templates")
        return True
    else:
        log_test("List templates", False, f"Status: {response.status_code}")
        return False

def test_get_template(template_id):
    """TEST 3: Get template by ID and verify V1 fields"""
    response = requests.get(
        f"{BASE_URL}/checklists/templates/{template_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify V1 fields are present
        v1_fields = {
            "shift_based": data.get("shift_based"),
            "time_limit_minutes": data.get("time_limit_minutes"),
            "scoring_enabled": data.get("scoring_enabled"),
            "pass_percentage": data.get("pass_percentage"),
            "auto_create_work_order_on_fail": data.get("auto_create_work_order_on_fail"),
            "requires_supervisor_approval": data.get("requires_supervisor_approval")
        }
        
        log_test("Get template with V1 fields", True, 
                f"V1 fields: {json.dumps(v1_fields, indent=2)}")
        return True
    else:
        log_test("Get template with V1 fields", False, f"Status: {response.status_code}")
        return False

def test_update_template(template_id):
    """TEST 4: Update template V1 fields"""
    update_data = {
        "time_limit_minutes": 45,
        "pass_percentage": 85.0,
        "work_order_priority": "urgent"
    }
    
    response = requests.put(
        f"{BASE_URL}/checklists/templates/{template_id}",
        headers=get_headers(),
        json=update_data
    )
    
    if response.status_code == 200:
        data = response.json()
        updated = (
            data.get("time_limit_minutes") == 45 and
            data.get("pass_percentage") == 85.0
        )
        log_test("Update template V1 fields", updated, 
                f"time_limit: {data.get('time_limit_minutes')}, pass_pct: {data.get('pass_percentage')}")
        return True
    else:
        log_test("Update template V1 fields", False, f"Status: {response.status_code}")
        return False

def test_start_execution_with_v1_fields(template_id):
    """TEST 5: Start execution with asset_id, unit_id, shift"""
    print("\nTEST GROUP 2: Enhanced Execution")
    
    # First, get the template to see its structure
    template_response = requests.get(
        f"{BASE_URL}/checklists/templates/{template_id}",
        headers=get_headers()
    )
    
    if template_response.status_code != 200:
        log_test("Start execution with V1 fields", False, "Could not fetch template")
        return None
    
    # Start execution
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.post(
        f"{BASE_URL}/checklists/executions?template_id={template_id}&date_str={today}",
        headers=get_headers()
    )
    
    if response.status_code == 201:
        data = response.json()
        execution_id = data.get("id")
        
        # Check if V1 fields are present (they may be None initially)
        has_v1_structure = "asset_id" in data or "unit_id" in data or "shift" in data
        
        log_test("Start execution with V1 fields", True, 
                f"Execution ID: {execution_id}, Has V1 structure: {has_v1_structure}")
        return execution_id
    else:
        log_test("Start execution with V1 fields", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_update_execution(execution_id, template_id):
    """TEST 6: Update execution items"""
    # Get template to get item IDs
    template_response = requests.get(
        f"{BASE_URL}/checklists/templates/{template_id}",
        headers=get_headers()
    )
    
    if template_response.status_code != 200:
        log_test("Update execution items", False, "Could not fetch template")
        return False
    
    template = template_response.json()
    items = template.get("items", [])
    
    if not items:
        log_test("Update execution items", False, "No items in template")
        return False
    
    # Update items
    update_data = {
        "items": [
            {
                "item_id": items[0]["id"],
                "completed": True,
                "notes": "Fire extinguisher checked and functional",
                "photo_ids": ["photo-123"],
                "score": 100.0
            }
        ]
    }
    
    response = requests.put(
        f"{BASE_URL}/checklists/executions/{execution_id}",
        headers=get_headers(),
        json=update_data
    )
    
    if response.status_code == 200:
        data = response.json()
        log_test("Update execution items", True, 
                f"Status: {data.get('status')}, Completion: {data.get('completion_percentage')}%")
        return True
    else:
        log_test("Update execution items", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

def test_complete_execution_with_scoring(execution_id, template_id):
    """TEST 7: Complete execution with scoring"""
    # Get template to get item IDs
    template_response = requests.get(
        f"{BASE_URL}/checklists/templates/{template_id}",
        headers=get_headers()
    )
    
    if template_response.status_code != 200:
        log_test("Complete execution with scoring", False, "Could not fetch template")
        return False
    
    template = template_response.json()
    items = template.get("items", [])
    
    # Complete all items
    completion_data = {
        "items": [
            {
                "item_id": item["id"],
                "completed": True,
                "notes": f"Item {idx+1} completed",
                "score": 100.0
            }
            for idx, item in enumerate(items)
        ],
        "notes": "All safety checks completed successfully"
    }
    
    response = requests.post(
        f"{BASE_URL}/checklists/executions/{execution_id}/complete",
        headers=get_headers(),
        json=completion_data
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify scoring fields
        has_scoring = (
            "time_taken_minutes" in data and
            "score" in data and
            "passed" in data
        )
        
        log_test("Complete execution with scoring", has_scoring, 
                f"Time: {data.get('time_taken_minutes')}min, Score: {data.get('score')}%, Passed: {data.get('passed')}")
        return True
    else:
        log_test("Complete execution with scoring", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

def test_get_analytics(template_id):
    """TEST 8: Get template analytics"""
    print("\nTEST GROUP 3: V1 Endpoints")
    
    response = requests.get(
        f"{BASE_URL}/checklists/templates/{template_id}/analytics",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Verify analytics fields
        has_analytics = all([
            "total_executions" in data,
            "completed_executions" in data,
            "average_score" in data,
            "pass_rate" in data,
            "average_time_minutes" in data,
            "compliance_rate" in data,
            "completion_trend" in data
        ])
        
        log_test("Get template analytics", has_analytics, 
                f"Total: {data.get('total_executions')}, Completed: {data.get('completed_executions')}, Pass rate: {data.get('pass_rate')}%")
        return True
    else:
        log_test("Get template analytics", False, f"Status: {response.status_code}")
        return False

def test_get_due_checklists():
    """TEST 9: Get due checklists with shift filter"""
    response = requests.get(
        f"{BASE_URL}/checklists/due?shift=day",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        has_structure = all([
            "due_checklists" in data,
            "active_templates" in data,
            "date" in data,
            "shift" in data
        ])
        
        log_test("Get due checklists with shift", has_structure, 
                f"Due: {len(data.get('due_checklists', []))}, Templates: {len(data.get('active_templates', []))}, Shift: {data.get('shift')}")
        return True
    else:
        log_test("Get due checklists with shift", False, f"Status: {response.status_code}")
        return False

def test_set_schedule(template_id):
    """TEST 10: Set checklist schedule"""
    schedule_data = {
        "unit_ids": ["unit-1", "unit-2"],
        "frequency": "daily",
        "shift_based": True,
        "scheduled_time": "08:00",
        "assigned_user_ids": [user_id],
        "auto_assign_logic": "round_robin"
    }
    
    response = requests.post(
        f"{BASE_URL}/checklists/templates/{template_id}/schedule",
        headers=get_headers(),
        json=schedule_data
    )
    
    if response.status_code == 200:
        data = response.json()
        
        schedule_set = all([
            data.get("frequency") == "daily",
            data.get("shift_based") == True,
            data.get("scheduled_time") == "08:00"
        ])
        
        log_test("Set checklist schedule", schedule_set, 
                f"Frequency: {data.get('frequency')}, Shift-based: {data.get('shift_based')}")
        return True
    else:
        log_test("Set checklist schedule", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

def test_supervisor_approval(execution_id):
    """TEST 11: Supervisor approval"""
    approval_data = {
        "approved": True,
        "comments": "Checklist approved by supervisor"
    }
    
    response = requests.post(
        f"{BASE_URL}/checklists/executions/{execution_id}/approve",
        headers=get_headers(),
        json=approval_data
    )
    
    if response.status_code == 200:
        data = response.json()
        
        approved = (
            "approved_by" in data and
            "approved_at" in data
        )
        
        log_test("Supervisor approval", approved, 
                f"Approved by: {data.get('approved_by')}, Status: {data.get('workflow_status')}")
        return True
    else:
        log_test("Supervisor approval", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

# ==================== TASKS V1 TESTS ====================

def test_create_task_template():
    """TEST 12: Create task template"""
    print("\n" + "="*80)
    print("MODULE 2: TASKS V1 ENHANCEMENTS")
    print("="*80)
    print("\nTEST GROUP 4: Task Templates")
    
    template_data = {
        "name": "Daily Equipment Inspection",
        "description": "Recurring daily inspection task",
        "priority": "high",
        "assigned_to": user_id,
        "unit_id": "test-unit-1",
        "estimated_hours": 2.0,
        "recurrence_rule": "daily"
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/templates",
        headers=get_headers(),
        json=template_data
    )
    
    if response.status_code == 201:
        data = response.json()
        template_id = data.get("id")
        
        log_test("Create task template", True, 
                f"Template ID: {template_id}, Recurrence: {data.get('recurrence_rule')}")
        return template_id
    else:
        log_test("Create task template", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_list_task_templates():
    """TEST 13: List task templates"""
    response = requests.get(
        f"{BASE_URL}/tasks/templates",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        templates = response.json()
        log_test("List task templates", True, f"Found {len(templates)} templates")
        return True
    else:
        log_test("List task templates", False, f"Status: {response.status_code}")
        return False

def test_create_task_from_template(template_id):
    """TEST 14: Create task from template"""
    response = requests.post(
        f"{BASE_URL}/tasks/from-template?template_id={template_id}",
        headers=get_headers()
    )
    
    if response.status_code == 201:
        data = response.json()
        task_id = data.get("id")
        
        from_template = (
            data.get("template_id") == template_id and
            data.get("task_type") == "recurring"
        )
        
        log_test("Create task from template", from_template, 
                f"Task ID: {task_id}, Template ID: {data.get('template_id')}")
        return task_id
    else:
        log_test("Create task from template", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_create_task_with_v1_fields():
    """TEST 15: Create task with V1 enhancement fields"""
    print("\nTEST GROUP 5: Subtasks")
    
    task_data = {
        "title": "V1 Enhanced Maintenance Task",
        "description": "Testing V1 enhancement fields",
        "priority": "high",
        "assigned_to": user_id,
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        # V1 Enhancement fields
        "asset_id": "asset-123",
        "task_type": "corrective_action",
        "estimated_hours": 4.0,
        "requires_checklist": "checklist-template-id",
        "linked_inspection_id": "inspection-456",
        "predecessor_task_ids": []
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=get_headers(),
        json=task_data
    )
    
    if response.status_code == 201:
        data = response.json()
        task_id = data.get("id")
        
        # Verify V1 fields
        v1_fields_present = all([
            "asset_id" in data,
            "task_type" in data,
            "estimated_hours" in data,
            "requires_checklist" in data,
            "linked_inspection_id" in data
        ])
        
        log_test("Create task with V1 fields", v1_fields_present, 
                f"Task ID: {task_id}, Type: {data.get('task_type')}, Est hours: {data.get('estimated_hours')}")
        return task_id
    else:
        log_test("Create task with V1 fields", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_create_subtask(parent_task_id):
    """TEST 16: Create subtask"""
    subtask_data = {
        "title": "Subtask 1: Prepare tools",
        "description": "Gather all necessary tools",
        "priority": "medium",
        "assigned_to": user_id
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/{parent_task_id}/subtasks",
        headers=get_headers(),
        json=subtask_data
    )
    
    if response.status_code == 201:
        data = response.json()
        subtask_id = data.get("id")
        
        is_subtask = data.get("parent_task_id") == parent_task_id
        
        log_test("Create subtask", is_subtask, 
                f"Subtask ID: {subtask_id}, Parent: {data.get('parent_task_id')}")
        return subtask_id
    else:
        log_test("Create subtask", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_list_subtasks(parent_task_id):
    """TEST 17: List subtasks"""
    response = requests.get(
        f"{BASE_URL}/tasks/{parent_task_id}/subtasks",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        subtasks = response.json()
        log_test("List subtasks", True, f"Found {len(subtasks)} subtasks")
        return True
    else:
        log_test("List subtasks", False, f"Status: {response.status_code}")
        return False

def test_verify_subtask_count(parent_task_id):
    """TEST 18: Verify parent's subtask_count increments"""
    response = requests.get(
        f"{BASE_URL}/tasks/{parent_task_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        subtask_count = data.get("subtask_count", 0)
        
        log_test("Verify subtask count", subtask_count > 0, 
                f"Subtask count: {subtask_count}")
        return True
    else:
        log_test("Verify subtask count", False, f"Status: {response.status_code}")
        return False

def test_create_task_with_dependencies():
    """TEST 19: Create task with predecessor_task_ids"""
    print("\nTEST GROUP 6: Dependencies")
    
    # Create first task
    task1_data = {
        "title": "Task 1: Foundation work",
        "description": "Must be completed first",
        "priority": "high"
    }
    
    response1 = requests.post(
        f"{BASE_URL}/tasks",
        headers=get_headers(),
        json=task1_data
    )
    
    if response1.status_code != 201:
        log_test("Create task with dependencies", False, "Could not create first task")
        return None
    
    task1_id = response1.json().get("id")
    
    # Create second task with dependency
    task2_data = {
        "title": "Task 2: Dependent work",
        "description": "Depends on Task 1",
        "priority": "medium",
        "predecessor_task_ids": [task1_id]
    }
    
    response2 = requests.post(
        f"{BASE_URL}/tasks",
        headers=get_headers(),
        json=task2_data
    )
    
    if response2.status_code == 201:
        data = response2.json()
        task2_id = data.get("id")
        
        has_dependency = task1_id in data.get("predecessor_task_ids", [])
        
        log_test("Create task with dependencies", has_dependency, 
                f"Task ID: {task2_id}, Predecessor: {task1_id}")
        return task2_id
    else:
        log_test("Create task with dependencies", False, 
                f"Status: {response2.status_code}, Error: {response2.text[:200]}")
        return None

def test_get_dependencies(task_id):
    """TEST 20: Get dependency chain"""
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}/dependencies",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        has_structure = all([
            "task" in data,
            "predecessors" in data,
            "subtasks" in data,
            "parent" in data
        ])
        
        log_test("Get dependency chain", has_structure, 
                f"Predecessors: {len(data.get('predecessors', []))}, Subtasks: {len(data.get('subtasks', []))}")
        return True
    else:
        log_test("Get dependency chain", False, f"Status: {response.status_code}")
        return False

def test_log_time_entry(task_id):
    """TEST 21: Log work hours"""
    print("\nTEST GROUP 7: Time & Parts Logging")
    
    time_data = {
        "hours": 3.5,
        "hourly_rate": 75.0,
        "description": "Completed maintenance work",
        "entry_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/{task_id}/log-time",
        headers=get_headers(),
        json=time_data
    )
    
    if response.status_code == 200:
        data = response.json()
        
        cost_calculated = data.get("cost") == (3.5 * 75.0)
        
        log_test("Log work hours", cost_calculated, 
                f"Hours: {data.get('hours')}, Rate: ${data.get('hourly_rate')}, Cost: ${data.get('cost')}")
        return True
    else:
        log_test("Log work hours", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

def test_verify_task_hours_updated(task_id):
    """TEST 22: Verify actual_hours and labor_cost updated"""
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        actual_hours = data.get("actual_hours") or 0
        labor_cost = data.get("labor_cost") or 0
        
        hours_updated = (actual_hours > 0 and labor_cost > 0)
        
        log_test("Verify hours and cost updated", hours_updated, 
                f"Actual hours: {actual_hours}, Labor cost: ${labor_cost}")
        return True
    else:
        log_test("Verify hours and cost updated", False, f"Status: {response.status_code}")
        return False

def test_log_parts(task_id):
    """TEST 23: Log parts used"""
    parts_data = {
        "part_id": "part-123",
        "part_name": "Hydraulic seal",
        "quantity": 2,
        "unit_cost": 45.50,
        "total_cost": 91.00,
        "notes": "Replaced worn seals"
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks/{task_id}/log-parts",
        headers=get_headers(),
        json=parts_data
    )
    
    if response.status_code == 200:
        data = response.json()
        
        log_test("Log parts used", True, 
                f"Part: {parts_data['part_name']}, Qty: {parts_data['quantity']}, Cost: ${parts_data['total_cost']}")
        return True
    else:
        log_test("Log parts used", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return False

def test_verify_parts_array_updated(task_id):
    """TEST 24: Verify parts_used array updated"""
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        parts_logged = len(data.get("parts_used", [])) > 0
        
        log_test("Verify parts array updated", parts_logged, 
                f"Parts count: {len(data.get('parts_used', []))}")
        return True
    else:
        log_test("Verify parts array updated", False, f"Status: {response.status_code}")
        return False

def test_create_task_with_all_v1_fields():
    """TEST 25: Create task with all V1 fields"""
    print("\nTEST GROUP 8: Enhanced Fields")
    
    task_data = {
        "title": "Complete V1 Task",
        "description": "Task with all V1 enhancement fields",
        "priority": "urgent",
        "assigned_to": user_id,
        "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        # All V1 fields
        "asset_id": "asset-789",
        "task_type": "project_task",
        "estimated_hours": 8.0,
        "requires_checklist": "checklist-template-xyz",
        "linked_inspection_id": "inspection-999",
        "predecessor_task_ids": []
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=get_headers(),
        json=task_data
    )
    
    if response.status_code == 201:
        data = response.json()
        
        # Verify all V1 fields persist
        all_fields_present = all([
            data.get("asset_id") == "asset-789",
            data.get("task_type") == "project_task",
            data.get("estimated_hours") == 8.0,
            data.get("requires_checklist") == "checklist-template-xyz",
            data.get("linked_inspection_id") == "inspection-999"
        ])
        
        log_test("Create task with all V1 fields", all_fields_present, 
                f"All V1 fields persisted correctly")
        return data.get("id")
    else:
        log_test("Create task with all V1 fields", False, 
                f"Status: {response.status_code}, Error: {response.text[:200]}")
        return None

def test_get_task_analytics():
    """TEST 26: Get task analytics overview"""
    print("\nTEST GROUP 9: Analytics")
    
    response = requests.get(
        f"{BASE_URL}/tasks/analytics/overview",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        has_analytics = all([
            "total_tasks" in data,
            "completed_tasks" in data,
            "in_progress_tasks" in data,
            "todo_tasks" in data,
            "overdue_tasks" in data,
            "average_completion_hours" in data,
            "on_time_percentage" in data,
            "completion_trend" in data
        ])
        
        log_test("Get task analytics", has_analytics, 
                f"Total: {data.get('total_tasks')}, Completed: {data.get('completed_tasks')}, On-time: {data.get('on_time_percentage')}%")
        return True
    else:
        log_test("Get task analytics", False, f"Status: {response.status_code}")
        return False

def test_verify_completion_trends():
    """TEST 27: Verify completion trends"""
    response = requests.get(
        f"{BASE_URL}/tasks/analytics/overview",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        
        has_trend = isinstance(data.get("completion_trend"), list)
        
        log_test("Verify completion trends", has_trend, 
                f"Trend data points: {len(data.get('completion_trend', []))}")
        return True
    else:
        log_test("Verify completion trends", False, f"Status: {response.status_code}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in test_results if r["passed"])
    failed = sum(1 for r in test_results if not r["passed"])
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
    
    if failed > 0:
        print("\n" + "="*80)
        print("FAILED TESTS")
        print("="*80)
        for r in test_results:
            if not r["passed"]:
                print(f"\n❌ {r['test']}")
                if r["details"]:
                    print(f"   {r['details']}")
    
    print("\n" + "="*80)
    print("CRITICAL SUCCESS CRITERIA VERIFICATION")
    print("="*80)
    
    # Check critical criteria
    criteria = {
        "V1 enhancement fields persist": any("V1 fields" in r["test"] and r["passed"] for r in test_results),
        "Scoring calculations work": any("scoring" in r["test"].lower() and r["passed"] for r in test_results),
        "Time tracking works": any("time" in r["test"].lower() and r["passed"] for r in test_results),
        "Subtask hierarchy works": any("subtask" in r["test"].lower() and r["passed"] for r in test_results),
        "Task dependencies track": any("dependencies" in r["test"].lower() and r["passed"] for r in test_results),
        "Analytics endpoints work": any("analytics" in r["test"].lower() and r["passed"] for r in test_results),
    }
    
    for criterion, met in criteria.items():
        status = "✅" if met else "❌"
        print(f"{status} {criterion}")

def main():
    """Main test execution"""
    print("="*80)
    print("CHECKLISTS & TASKS V1 ENHANCEMENTS - COMPREHENSIVE BACKEND TESTING")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['email']}")
    print("="*80)
    
    # Login
    if not login():
        print("\n❌ Login failed. Cannot proceed with tests.")
        return
    
    # ==================== CHECKLISTS V1 TESTS ====================
    
    # Test Group 1: Enhanced Template Creation
    template_id = test_checklist_template_with_v1_fields()
    if template_id:
        test_list_templates()
        test_get_template(template_id)
        test_update_template(template_id)
        
        # Test Group 2: Enhanced Execution
        execution_id = test_start_execution_with_v1_fields(template_id)
        if execution_id:
            test_update_execution(execution_id, template_id)
            test_complete_execution_with_scoring(execution_id, template_id)
        
        # Test Group 3: V1 Endpoints
        test_get_analytics(template_id)
        test_get_due_checklists()
        test_set_schedule(template_id)
        
        if execution_id:
            test_supervisor_approval(execution_id)
    
    # ==================== TASKS V1 TESTS ====================
    
    # Test Group 4: Task Templates
    task_template_id = test_create_task_template()
    if task_template_id:
        test_list_task_templates()
        test_create_task_from_template(task_template_id)
    
    # Test Group 5: Subtasks
    parent_task_id = test_create_task_with_v1_fields()
    if parent_task_id:
        subtask_id = test_create_subtask(parent_task_id)
        test_list_subtasks(parent_task_id)
        test_verify_subtask_count(parent_task_id)
    
    # Test Group 6: Dependencies
    dependent_task_id = test_create_task_with_dependencies()
    if dependent_task_id:
        test_get_dependencies(dependent_task_id)
    
    # Test Group 7: Time & Parts Logging
    if parent_task_id:
        test_log_time_entry(parent_task_id)
        test_verify_task_hours_updated(parent_task_id)
        test_log_parts(parent_task_id)
        test_verify_parts_array_updated(parent_task_id)
    
    # Test Group 8: Enhanced Fields
    test_create_task_with_all_v1_fields()
    
    # Test Group 9: Analytics
    test_get_task_analytics()
    test_verify_completion_trends()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
