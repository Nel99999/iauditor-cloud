#!/usr/bin/env python3
"""
V1 Platform Complete Testing - Work Orders, Inventory, Projects, Incidents Modules
Comprehensive backend API testing for 4 modules with 37 endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"

# Global variables
auth_token = None
test_asset_id = None
test_wo_id = None
test_inventory_item_id = None
test_project_id = None
test_incident_id = None

# Test results tracking
test_results = {
    "work_orders": {"passed": 0, "failed": 0, "tests": []},
    "inventory": {"passed": 0, "failed": 0, "tests": []},
    "projects": {"passed": 0, "failed": 0, "tests": []},
    "incidents": {"passed": 0, "failed": 0, "tests": []}
}


def log_test(module, test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")
    
    test_results[module]["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results[module]["passed"] += 1
    else:
        test_results[module]["failed"] += 1


def authenticate():
    """Authenticate and get token"""
    global auth_token
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            print(f"✅ Authentication successful")
            print(f"   User: {data.get('user', {}).get('name')}")
            print(f"   Role: {data.get('user', {}).get('role')}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False


def get_headers():
    """Get request headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


def get_test_asset():
    """Get or create a test asset for work orders"""
    global test_asset_id
    print("\n" + "="*80)
    print("SETUP: Getting Test Asset")
    print("="*80)
    
    try:
        # Try to get existing assets
        response = requests.get(
            f"{BASE_URL}/assets",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            assets = response.json()
            if assets and len(assets) > 0:
                test_asset_id = assets[0]["id"]
                print(f"✅ Using existing asset: {assets[0].get('name')} (ID: {test_asset_id})")
                return True
        
        # Create new asset if none exist
        asset_data = {
            "asset_tag": f"TEST-ASSET-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": "Test Equipment for WO Testing",
            "asset_type": "equipment",
            "status": "operational",
            "criticality": "medium"
        }
        
        response = requests.post(
            f"{BASE_URL}/assets",
            headers=get_headers(),
            json=asset_data
        )
        
        if response.status_code == 201:
            data = response.json()
            test_asset_id = data["id"]
            print(f"✅ Created test asset: {data.get('name')} (ID: {test_asset_id})")
            return True
        else:
            print(f"⚠️ Could not create test asset: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error getting test asset: {str(e)}")
        return False


# ============================================================================
# MODULE 1: WORK ORDERS (12 ENDPOINTS)
# ============================================================================

def test_work_orders():
    """Test Work Orders module"""
    global test_wo_id
    
    print("\n" + "="*80)
    print("MODULE 1: WORK ORDERS (12 ENDPOINTS)")
    print("="*80)
    
    # TEST GROUP 1: Basic CRUD
    print("\n--- TEST GROUP 1: Basic CRUD ---")
    
    # Test 1.1: Create Work Order
    try:
        wo_data = {
            "title": f"Test Work Order {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Comprehensive testing of work order creation",
            "work_type": "corrective",
            "priority": "high",
            "asset_id": test_asset_id,
            "estimated_hours": 4.0,
            "causes_downtime": False
        }
        
        response = requests.post(
            f"{BASE_URL}/work-orders",
            headers=get_headers(),
            json=wo_data
        )
        
        if response.status_code == 201:
            data = response.json()
            test_wo_id = data["id"]
            log_test("work_orders", "Test 1.1: Create Work Order", True, 
                    f"WO Number: {data.get('wo_number')}, Status: {data.get('status')}")
        else:
            log_test("work_orders", "Test 1.1: Create Work Order", False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}")
    except Exception as e:
        log_test("work_orders", "Test 1.1: Create Work Order", False, f"Error: {str(e)}")
    
    # Test 1.2: List Work Orders
    try:
        response = requests.get(
            f"{BASE_URL}/work-orders",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("work_orders", "Test 1.2: List Work Orders", True, 
                    f"Found {len(data)} work orders")
        else:
            log_test("work_orders", "Test 1.2: List Work Orders", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("work_orders", "Test 1.2: List Work Orders", False, f"Error: {str(e)}")
    
    # Test 1.3: Get Work Order Details
    if test_wo_id:
        try:
            response = requests.get(
                f"{BASE_URL}/work-orders/{test_wo_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 1.3: Get Work Order Details", True, 
                        f"Title: {data.get('title')}, Priority: {data.get('priority')}")
            else:
                log_test("work_orders", "Test 1.3: Get Work Order Details", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 1.3: Get Work Order Details", False, f"Error: {str(e)}")
    
    # Test 1.4: Update Work Order
    if test_wo_id:
        try:
            update_data = {
                "description": "Updated description for comprehensive testing"
            }
            
            response = requests.put(
                f"{BASE_URL}/work-orders/{test_wo_id}",
                headers=get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 1.4: Update Work Order", True, 
                        f"Description updated successfully")
            else:
                log_test("work_orders", "Test 1.4: Update Work Order", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 1.4: Update Work Order", False, f"Error: {str(e)}")
    
    # Test 1.5: Change Status to In Progress
    if test_wo_id:
        try:
            response = requests.put(
                f"{BASE_URL}/work-orders/{test_wo_id}/status",
                headers=get_headers(),
                json={"status": "in_progress"}
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 1.5: Change Status to In Progress", True, 
                        f"Status: {data.get('status')}, Actual Start: {data.get('actual_start')}")
            else:
                log_test("work_orders", "Test 1.5: Change Status to In Progress", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 1.5: Change Status to In Progress", False, f"Error: {str(e)}")
    
    # TEST GROUP 2: Labor & Parts
    print("\n--- TEST GROUP 2: Labor & Parts ---")
    
    # Test 2.1: Add Labor Hours
    if test_wo_id:
        try:
            labor_data = {
                "hours": 2.0,
                "hourly_rate": 50.0
            }
            
            response = requests.post(
                f"{BASE_URL}/work-orders/{test_wo_id}/add-labor",
                headers=get_headers(),
                json=labor_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 2.1: Add Labor Hours", True, 
                        f"Labor Cost: ${data.get('labor_cost')}, Actual Hours: {data.get('actual_hours')}")
            else:
                log_test("work_orders", "Test 2.1: Add Labor Hours", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 2.1: Add Labor Hours", False, f"Error: {str(e)}")
    
    # Test 2.2: Add Parts
    if test_wo_id:
        try:
            parts_data = {
                "cost": 100.0
            }
            
            response = requests.post(
                f"{BASE_URL}/work-orders/{test_wo_id}/add-parts",
                headers=get_headers(),
                json=parts_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 2.2: Add Parts", True, 
                        f"Parts Cost: ${data.get('parts_cost')}, Total Cost: ${data.get('total_cost')}")
            else:
                log_test("work_orders", "Test 2.2: Add Parts", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 2.2: Add Parts", False, f"Error: {str(e)}")
    
    # Test 2.3: Verify Cost Calculations
    if test_wo_id:
        try:
            response = requests.get(
                f"{BASE_URL}/work-orders/{test_wo_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                labor_cost = data.get('labor_cost', 0)
                parts_cost = data.get('parts_cost', 0)
                total_cost = data.get('total_cost', 0)
                
                expected_total = labor_cost + parts_cost
                if abs(total_cost - expected_total) < 0.01:
                    log_test("work_orders", "Test 2.3: Verify Cost Calculations", True, 
                            f"Labor: ${labor_cost}, Parts: ${parts_cost}, Total: ${total_cost}")
                else:
                    log_test("work_orders", "Test 2.3: Verify Cost Calculations", False, 
                            f"Cost mismatch: Expected ${expected_total}, Got ${total_cost}")
            else:
                log_test("work_orders", "Test 2.3: Verify Cost Calculations", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 2.3: Verify Cost Calculations", False, f"Error: {str(e)}")
    
    # TEST GROUP 3: Additional Endpoints
    print("\n--- TEST GROUP 3: Additional Endpoints ---")
    
    # Test 3.1: Get Timeline
    if test_wo_id:
        try:
            response = requests.get(
                f"{BASE_URL}/work-orders/{test_wo_id}/timeline",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("work_orders", "Test 3.1: Get Timeline", True, 
                        f"Timeline entries: {len(data.get('timeline', []))}")
            else:
                log_test("work_orders", "Test 3.1: Get Timeline", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("work_orders", "Test 3.1: Get Timeline", False, f"Error: {str(e)}")
    
    # Test 3.2: Get Stats Overview
    try:
        response = requests.get(
            f"{BASE_URL}/work-orders/stats/overview",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("work_orders", "Test 3.2: Get Stats Overview", True, 
                    f"Total WOs: {data.get('total_work_orders')}, Backlog: {data.get('backlog_count')}")
        else:
            log_test("work_orders", "Test 3.2: Get Stats Overview", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("work_orders", "Test 3.2: Get Stats Overview", False, f"Error: {str(e)}")
    
    # Test 3.3: Get Backlog
    try:
        response = requests.get(
            f"{BASE_URL}/work-orders/backlog",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("work_orders", "Test 3.3: Get Backlog", True, 
                    f"Backlog items: {len(data)}")
        else:
            log_test("work_orders", "Test 3.3: Get Backlog", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("work_orders", "Test 3.3: Get Backlog", False, f"Error: {str(e)}")
    
    # Test 3.4: Assign Work Order
    if test_wo_id:
        try:
            # Get current user ID from token
            response = requests.get(
                f"{BASE_URL}/users/me",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("id")
                
                assign_response = requests.post(
                    f"{BASE_URL}/work-orders/{test_wo_id}/assign",
                    headers=get_headers(),
                    json={"assigned_to": user_id}
                )
                
                if assign_response.status_code == 200:
                    data = assign_response.json()
                    log_test("work_orders", "Test 3.4: Assign Work Order", True, 
                            f"Assigned to: {data.get('assigned_to_name')}")
                else:
                    log_test("work_orders", "Test 3.4: Assign Work Order", False, 
                            f"Status: {assign_response.status_code}")
            else:
                log_test("work_orders", "Test 3.4: Assign Work Order", False, 
                        f"Could not get user ID")
        except Exception as e:
            log_test("work_orders", "Test 3.4: Assign Work Order", False, f"Error: {str(e)}")


# ============================================================================
# MODULE 2: INVENTORY (8 ENDPOINTS)
# ============================================================================

def test_inventory():
    """Test Inventory module"""
    global test_inventory_item_id
    
    print("\n" + "="*80)
    print("MODULE 2: INVENTORY (8 ENDPOINTS)")
    print("="*80)
    
    # TEST GROUP 4: Inventory CRUD
    print("\n--- TEST GROUP 4: Inventory CRUD ---")
    
    # Test 4.1: Create Inventory Item
    try:
        item_data = {
            "part_number": f"PART-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Test inventory item for comprehensive testing",
            "category": "spare_parts",
            "unit_of_measure": "EA",
            "quantity_on_hand": 50,
            "reorder_point": 10,
            "reorder_quantity": 25,
            "unit_cost": 15.50
        }
        
        response = requests.post(
            f"{BASE_URL}/inventory/items",
            headers=get_headers(),
            json=item_data
        )
        
        if response.status_code == 201:
            data = response.json()
            test_inventory_item_id = data["id"]
            log_test("inventory", "Test 4.1: Create Inventory Item", True, 
                    f"Part: {data.get('part_number')}, Qty: {data.get('quantity_on_hand')}")
        else:
            log_test("inventory", "Test 4.1: Create Inventory Item", False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}")
    except Exception as e:
        log_test("inventory", "Test 4.1: Create Inventory Item", False, f"Error: {str(e)}")
    
    # Test 4.2: List Inventory Items
    try:
        response = requests.get(
            f"{BASE_URL}/inventory/items",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("inventory", "Test 4.2: List Inventory Items", True, 
                    f"Found {len(data)} items")
        else:
            log_test("inventory", "Test 4.2: List Inventory Items", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("inventory", "Test 4.2: List Inventory Items", False, f"Error: {str(e)}")
    
    # Test 4.3: Get Item Details
    if test_inventory_item_id:
        try:
            response = requests.get(
                f"{BASE_URL}/inventory/items/{test_inventory_item_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("inventory", "Test 4.3: Get Item Details", True, 
                        f"Part: {data.get('part_number')}, Value: ${data.get('total_value')}")
            else:
                log_test("inventory", "Test 4.3: Get Item Details", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("inventory", "Test 4.3: Get Item Details", False, f"Error: {str(e)}")
    
    # Test 4.4: Update Item
    if test_inventory_item_id:
        try:
            update_data = {
                "description": "Updated description for testing"
            }
            
            response = requests.put(
                f"{BASE_URL}/inventory/items/{test_inventory_item_id}",
                headers=get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("inventory", "Test 4.4: Update Item", True, 
                        f"Description updated successfully")
            else:
                log_test("inventory", "Test 4.4: Update Item", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("inventory", "Test 4.4: Update Item", False, f"Error: {str(e)}")
    
    # TEST GROUP 5: Stock Management
    print("\n--- TEST GROUP 5: Stock Management ---")
    
    # Test 5.1: Adjust Stock (+10)
    if test_inventory_item_id:
        try:
            response = requests.post(
                f"{BASE_URL}/inventory/items/{test_inventory_item_id}/adjust",
                headers=get_headers(),
                json={"adjustment": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("inventory", "Test 5.1: Adjust Stock (+10)", True, 
                        f"New Qty: {data.get('quantity_on_hand')}, Available: {data.get('quantity_available')}")
            else:
                log_test("inventory", "Test 5.1: Adjust Stock (+10)", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("inventory", "Test 5.1: Adjust Stock (+10)", False, f"Error: {str(e)}")
    
    # Test 5.2: Reserve Stock (NOT IMPLEMENTED)
    log_test("inventory", "Test 5.2: Reserve Stock", False, 
            "⚠️ ENDPOINT NOT IMPLEMENTED: POST /inventory/items/{id}/reserve")
    
    # Test 5.3: Get Reorder Items
    try:
        response = requests.get(
            f"{BASE_URL}/inventory/items/reorder",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("inventory", "Test 5.3: Get Reorder Items", True, 
                    f"Items below reorder point: {len(data)}")
        else:
            log_test("inventory", "Test 5.3: Get Reorder Items", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("inventory", "Test 5.3: Get Reorder Items", False, f"Error: {str(e)}")
    
    # Test 5.4: Get Stats
    try:
        response = requests.get(
            f"{BASE_URL}/inventory/stats",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("inventory", "Test 5.4: Get Stats", True, 
                    f"Total Items: {data.get('total_items')}, Total Value: ${data.get('total_value')}")
        else:
            log_test("inventory", "Test 5.4: Get Stats", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("inventory", "Test 5.4: Get Stats", False, f"Error: {str(e)}")


# ============================================================================
# MODULE 3: PROJECTS (11 ENDPOINTS)
# ============================================================================

def test_projects():
    """Test Projects module"""
    global test_project_id
    
    print("\n" + "="*80)
    print("MODULE 3: PROJECTS (11 ENDPOINTS)")
    print("="*80)
    
    # TEST GROUP 6: Projects CRUD
    print("\n--- TEST GROUP 6: Projects CRUD ---")
    
    # Test 6.1: Create Project
    try:
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Comprehensive testing of project management",
            "project_type": "improvement",
            "priority": "high",
            "planned_start": datetime.now().isoformat(),
            "planned_end": (datetime.now() + timedelta(days=90)).isoformat(),
            "budget": 50000.00
        }
        
        response = requests.post(
            f"{BASE_URL}/projects",
            headers=get_headers(),
            json=project_data
        )
        
        if response.status_code == 201:
            data = response.json()
            test_project_id = data["id"]
            log_test("projects", "Test 6.1: Create Project", True, 
                    f"Code: {data.get('project_code')}, Budget: ${data.get('budget')}")
        else:
            log_test("projects", "Test 6.1: Create Project", False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}")
    except Exception as e:
        log_test("projects", "Test 6.1: Create Project", False, f"Error: {str(e)}")
    
    # Test 6.2: List Projects
    try:
        response = requests.get(
            f"{BASE_URL}/projects",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("projects", "Test 6.2: List Projects", True, 
                    f"Found {len(data)} projects")
        else:
            log_test("projects", "Test 6.2: List Projects", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("projects", "Test 6.2: List Projects", False, f"Error: {str(e)}")
    
    # Test 6.3: Get Project Details
    if test_project_id:
        try:
            response = requests.get(
                f"{BASE_URL}/projects/{test_project_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 6.3: Get Project Details", True, 
                        f"Name: {data.get('name')}, Status: {data.get('status')}")
            else:
                log_test("projects", "Test 6.3: Get Project Details", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 6.3: Get Project Details", False, f"Error: {str(e)}")
    
    # Test 6.4: Update Project
    if test_project_id:
        try:
            update_data = {
                "description": "Updated project description for testing"
            }
            
            response = requests.put(
                f"{BASE_URL}/projects/{test_project_id}",
                headers=get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 6.4: Update Project", True, 
                        f"Description updated successfully")
            else:
                log_test("projects", "Test 6.4: Update Project", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 6.4: Update Project", False, f"Error: {str(e)}")
    
    # TEST GROUP 7: Milestones & Tasks
    print("\n--- TEST GROUP 7: Milestones & Tasks ---")
    
    # Test 7.1: Create Milestone
    if test_project_id:
        try:
            milestone_data = {
                "name": "Phase 1 Completion",
                "description": "Complete initial phase",
                "due_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/projects/{test_project_id}/milestones",
                headers=get_headers(),
                json=milestone_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 7.1: Create Milestone", True, 
                        f"Milestone: {data.get('name')}, Order: {data.get('order')}")
            else:
                log_test("projects", "Test 7.1: Create Milestone", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 7.1: Create Milestone", False, f"Error: {str(e)}")
    
    # Test 7.2: List Milestones
    if test_project_id:
        try:
            response = requests.get(
                f"{BASE_URL}/projects/{test_project_id}/milestones",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 7.2: List Milestones", True, 
                        f"Found {len(data)} milestones")
            else:
                log_test("projects", "Test 7.2: List Milestones", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 7.2: List Milestones", False, f"Error: {str(e)}")
    
    # Test 7.3: Create Project Task
    if test_project_id:
        try:
            task_data = {
                "title": "Test Project Task",
                "description": "Task for project testing",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/projects/{test_project_id}/tasks",
                headers=get_headers(),
                json=task_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 7.3: Create Project Task", True, 
                        f"Task: {data.get('title')}, Type: {data.get('task_type')}")
            else:
                log_test("projects", "Test 7.3: Create Project Task", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 7.3: Create Project Task", False, f"Error: {str(e)}")
    
    # Test 7.4: List Project Tasks
    if test_project_id:
        try:
            response = requests.get(
                f"{BASE_URL}/projects/{test_project_id}/tasks",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("projects", "Test 7.4: List Project Tasks", True, 
                        f"Found {len(data)} tasks")
            else:
                log_test("projects", "Test 7.4: List Project Tasks", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("projects", "Test 7.4: List Project Tasks", False, f"Error: {str(e)}")
    
    # TEST GROUP 8: Analytics
    print("\n--- TEST GROUP 8: Analytics ---")
    
    # Test 8.1: Get Stats Overview
    try:
        response = requests.get(
            f"{BASE_URL}/projects/stats/overview",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("projects", "Test 8.1: Get Stats Overview", True, 
                    f"Total Projects: {data.get('total_projects')}, Budget: ${data.get('total_budget')}")
        else:
            log_test("projects", "Test 8.1: Get Stats Overview", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("projects", "Test 8.1: Get Stats Overview", False, f"Error: {str(e)}")
    
    # Test 8.2: Get Dashboard
    try:
        response = requests.get(
            f"{BASE_URL}/projects/dashboard",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("projects", "Test 8.2: Get Dashboard", True, 
                    f"Active: {data.get('active')}, Completed: {data.get('completed')}")
        else:
            log_test("projects", "Test 8.2: Get Dashboard", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("projects", "Test 8.2: Get Dashboard", False, f"Error: {str(e)}")
    
    # Test 8.3: Update Status (NOT IMPLEMENTED)
    log_test("projects", "Test 8.3: Update Status", False, 
            "⚠️ ENDPOINT NOT IMPLEMENTED: PUT /projects/{id}/status")


# ============================================================================
# MODULE 4: INCIDENTS (6 ENDPOINTS)
# ============================================================================

def test_incidents():
    """Test Incidents module"""
    global test_incident_id
    
    print("\n" + "="*80)
    print("MODULE 4: INCIDENTS (6 ENDPOINTS)")
    print("="*80)
    
    # TEST GROUP 9: Incidents
    print("\n--- TEST GROUP 9: Incidents ---")
    
    # Test 9.1: Report Incident
    try:
        incident_data = {
            "incident_type": "safety",
            "severity": "high",
            "occurred_at": datetime.now().isoformat(),
            "location": "Production Floor A",
            "description": "Test incident for comprehensive testing"
        }
        
        response = requests.post(
            f"{BASE_URL}/incidents",
            headers=get_headers(),
            json=incident_data
        )
        
        if response.status_code == 201:
            data = response.json()
            test_incident_id = data["id"]
            log_test("incidents", "Test 9.1: Report Incident", True, 
                    f"Number: {data.get('incident_number')}, Severity: {data.get('severity')}")
        else:
            log_test("incidents", "Test 9.1: Report Incident", False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}")
    except Exception as e:
        log_test("incidents", "Test 9.1: Report Incident", False, f"Error: {str(e)}")
    
    # Test 9.2: List Incidents
    try:
        response = requests.get(
            f"{BASE_URL}/incidents",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("incidents", "Test 9.2: List Incidents", True, 
                    f"Found {len(data)} incidents")
        else:
            log_test("incidents", "Test 9.2: List Incidents", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("incidents", "Test 9.2: List Incidents", False, f"Error: {str(e)}")
    
    # Test 9.3: Get Incident Details
    if test_incident_id:
        try:
            response = requests.get(
                f"{BASE_URL}/incidents/{test_incident_id}",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("incidents", "Test 9.3: Get Incident Details", True, 
                        f"Type: {data.get('incident_type')}, Location: {data.get('location')}")
            else:
                log_test("incidents", "Test 9.3: Get Incident Details", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("incidents", "Test 9.3: Get Incident Details", False, f"Error: {str(e)}")
    
    # Test 9.4: Start Investigation (NOT IMPLEMENTED)
    log_test("incidents", "Test 9.4: Start Investigation", False, 
            "⚠️ ENDPOINT NOT IMPLEMENTED: POST /incidents/{id}/investigate")
    
    # Test 9.5: Create Corrective Action
    if test_incident_id:
        try:
            action_data = {
                "description": "Implement safety protocol improvements"
            }
            
            response = requests.post(
                f"{BASE_URL}/incidents/{test_incident_id}/corrective-action",
                headers=get_headers(),
                json=action_data
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test("incidents", "Test 9.5: Create Corrective Action", True, 
                        f"CAPA Task: {data.get('title')}, Priority: {data.get('priority')}")
            else:
                log_test("incidents", "Test 9.5: Create Corrective Action", False, 
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("incidents", "Test 9.5: Create Corrective Action", False, f"Error: {str(e)}")
    
    # Test 9.6: Get Stats
    try:
        response = requests.get(
            f"{BASE_URL}/incidents/stats",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("incidents", "Test 9.6: Get Stats", True, 
                    f"Total: {data.get('total_incidents')}, This Month: {data.get('this_month')}")
        else:
            log_test("incidents", "Test 9.6: Get Stats", False, 
                    f"Status: {response.status_code}")
    except Exception as e:
        log_test("incidents", "Test 9.6: Get Stats", False, f"Error: {str(e)}")


# ============================================================================
# SUMMARY REPORT
# ============================================================================

def print_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    for module, results in test_results.items():
        passed = results["passed"]
        failed = results["failed"]
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        total_passed += passed
        total_failed += failed
        
        status_icon = "✅" if failed == 0 else "⚠️" if success_rate >= 80 else "❌"
        
        print(f"\n{status_icon} {module.upper().replace('_', ' ')}")
        print(f"   Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if failed > 0:
            print(f"   Failed Tests:")
            for test in results["tests"]:
                if not test["passed"]:
                    print(f"      - {test['name']}")
                    if test["details"]:
                        print(f"        {test['details']}")
    
    print("\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    
    total_tests = total_passed + total_failed
    overall_success = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {overall_success:.1f}%")
    
    # Missing endpoints summary
    print("\n" + "="*80)
    print("MISSING ENDPOINTS")
    print("="*80)
    print("❌ POST /api/inventory/items/{id}/reserve - Reserve stock functionality")
    print("❌ PUT /api/projects/{id}/status - Update project status")
    print("❌ POST /api/incidents/{id}/investigate - Start incident investigation")
    
    # Production readiness assessment
    print("\n" + "="*80)
    print("PRODUCTION READINESS ASSESSMENT")
    print("="*80)
    
    if overall_success >= 90:
        print("✅ EXCELLENT - System is production-ready")
    elif overall_success >= 80:
        print("⚠️ GOOD - Minor issues need attention")
    elif overall_success >= 70:
        print("⚠️ FAIR - Several issues need fixing")
    else:
        print("❌ POOR - Major issues need resolution")
    
    print("\nKey Findings:")
    print(f"- Work Orders: {test_results['work_orders']['passed']}/{test_results['work_orders']['passed'] + test_results['work_orders']['failed']} endpoints working")
    print(f"- Inventory: {test_results['inventory']['passed']}/{test_results['inventory']['passed'] + test_results['inventory']['failed']} endpoints working (1 missing)")
    print(f"- Projects: {test_results['projects']['passed']}/{test_results['projects']['passed'] + test_results['projects']['failed']} endpoints working (1 missing)")
    print(f"- Incidents: {test_results['incidents']['passed']}/{test_results['incidents']['passed'] + test_results['incidents']['failed']} endpoints working (1 missing)")
    
    return overall_success >= 80


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main test execution"""
    print("="*80)
    print("V1 PLATFORM COMPLETE TESTING")
    print("Work Orders, Inventory, Projects, Incidents Modules")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Authenticate
    if not authenticate():
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    # Get test asset
    get_test_asset()
    
    # Run all module tests
    test_work_orders()
    test_inventory()
    test_projects()
    test_incidents()
    
    # Print summary
    success = print_summary()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
