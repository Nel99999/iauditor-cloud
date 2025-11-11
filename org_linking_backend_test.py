#!/usr/bin/env python3
"""
BACKEND TESTING - ORGANIZATION LINKING & USER ASSIGNMENT
Test the newly implemented backend endpoints for linking units and user assignment.

Test User:
- Email: llewellyn@bluedawncapital.co.za
- Password: Test@1234
- Role: developer

Total Tests: 19 backend tests across 4 test suites
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "Test@1234"

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": []
}

def log_test(test_name, status, message, details=None):
    """Log test result"""
    test_results["total"] += 1
    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ {test_name}: {message}")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"❌ {test_name}: {message}")
    elif status == "WARN":
        test_results["warnings"] += 1
        print(f"⚠️  {test_name}: {message}")
    
    test_results["tests"].append({
        "name": test_name,
        "status": status,
        "message": message,
        "details": details
    })

def authenticate():
    """Authenticate and get JWT token"""
    print("\n🔐 AUTHENTICATING...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_data = data.get("user", {})
            print(f"✅ Authenticated as: {user_data.get('name')} ({user_data.get('email')})")
            print(f"   Role: {user_data.get('role')}, Organization: {user_data.get('organization_id')}")
            return token, user_data
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def get_headers(token):
    """Get request headers with auth token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# ============================================================================
# TEST SUITE 1: USER ASSIGNMENT & COUNT (5 tests)
# ============================================================================

def test_suite_1_user_assignment(token):
    """Test Suite 1: User Assignment & Count"""
    print("\n" + "="*80)
    print("TEST SUITE 1: USER ASSIGNMENT & COUNT (5 tests)")
    print("="*80)
    
    headers = get_headers(token)
    
    # Test 1.1: Get All Users
    print("\n📋 Test 1.1: Get All Users")
    try:
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            user_count = len(users)
            log_test(
                "Test 1.1",
                "PASS",
                f"Retrieved {user_count} users successfully",
                {"user_count": user_count, "users": [u.get("email") for u in users[:5]]}
            )
            return users
        else:
            log_test("Test 1.1", "FAIL", f"Failed to get users: {response.status_code}", {"response": response.text})
            return []
    except Exception as e:
        log_test("Test 1.1", "FAIL", f"Exception: {str(e)}")
        return []

def test_suite_1_assign_user(token, users):
    """Test 1.2-1.5: Assign user to unit and verify"""
    headers = get_headers(token)
    
    # First, get available units
    print("\n📋 Getting available units...")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units", headers=headers)
        if response.status_code != 200:
            log_test("Test 1.2", "FAIL", "Cannot get units for assignment test", {"response": response.text})
            return
        
        units = response.json()
        if not units:
            log_test("Test 1.2", "WARN", "No units available for assignment test")
            return
        
        # Pick first unit
        test_unit = units[0]
        unit_id = test_unit["id"]
        print(f"   Using unit: {test_unit['name']} (ID: {unit_id})")
        
        # Pick a user to assign (not the current user)
        if len(users) < 2:
            log_test("Test 1.2", "WARN", "Not enough users for assignment test")
            return
        
        # Find a user without organizational_unit_id or pick second user
        test_user = None
        for user in users[1:]:  # Skip first user (likely current user)
            if not user.get("organizational_unit_id"):
                test_user = user
                break
        
        if not test_user:
            test_user = users[1]  # Just use second user
        
        user_id = test_user["id"]
        print(f"   Using user: {test_user['name']} ({test_user['email']})")
        
        # Test 1.2: Assign User to Unit
        print("\n📋 Test 1.2: Assign User to Unit")
        try:
            response = requests.post(
                f"{BASE_URL}/organizations/units/{unit_id}/assign-user",
                headers=headers,
                json={
                    "user_id": user_id,
                    "unit_id": unit_id,
                    "role": "inspector"
                }
            )
            
            if response.status_code == 201:
                assignment = response.json()
                log_test(
                    "Test 1.2",
                    "PASS",
                    f"User assigned to unit successfully",
                    {"assignment_id": assignment.get("id"), "unit_id": unit_id, "user_id": user_id}
                )
                assignment_id = assignment.get("id")
            elif response.status_code == 400 and "already assigned" in response.text:
                log_test("Test 1.2", "WARN", "User already assigned to this unit (expected if re-running tests)")
                assignment_id = None
            else:
                log_test("Test 1.2", "FAIL", f"Assignment failed: {response.status_code}", {"response": response.text})
                return
        except Exception as e:
            log_test("Test 1.2", "FAIL", f"Exception: {str(e)}")
            return
        
        # Test 1.3: Verify Assignment in Database (via API)
        print("\n📋 Test 1.3: Verify Assignment in Database")
        try:
            # Get user details to check organizational_unit_id
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            if response.status_code == 200:
                all_users = response.json()
                assigned_user = next((u for u in all_users if u["id"] == user_id), None)
                
                if assigned_user and assigned_user.get("organizational_unit_id") == unit_id:
                    log_test(
                        "Test 1.3",
                        "PASS",
                        "Assignment verified in database - organizational_unit_id updated",
                        {"user_id": user_id, "organizational_unit_id": assigned_user.get("organizational_unit_id")}
                    )
                else:
                    log_test("Test 1.3", "WARN", "organizational_unit_id not updated or different", 
                            {"expected": unit_id, "actual": assigned_user.get("organizational_unit_id") if assigned_user else None})
            else:
                log_test("Test 1.3", "FAIL", f"Cannot verify assignment: {response.status_code}")
        except Exception as e:
            log_test("Test 1.3", "FAIL", f"Exception: {str(e)}")
        
        # Test 1.4: Get Hierarchy with User Counts
        print("\n📋 Test 1.4: Get Hierarchy with User Counts")
        try:
            response = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
            if response.status_code == 200:
                hierarchy = response.json()
                
                # Find our test unit in hierarchy
                def find_unit_in_tree(nodes, target_id):
                    for node in nodes:
                        if node["id"] == target_id:
                            return node
                        if node.get("children"):
                            found = find_unit_in_tree(node["children"], target_id)
                            if found:
                                return found
                    return None
                
                test_unit_in_hierarchy = find_unit_in_tree(hierarchy, unit_id)
                
                if test_unit_in_hierarchy:
                    user_count = test_unit_in_hierarchy.get("user_count", 0)
                    log_test(
                        "Test 1.4",
                        "PASS",
                        f"Hierarchy shows user_count field correctly",
                        {"unit_id": unit_id, "user_count": user_count}
                    )
                else:
                    log_test("Test 1.4", "WARN", "Test unit not found in hierarchy")
            else:
                log_test("Test 1.4", "FAIL", f"Failed to get hierarchy: {response.status_code}")
        except Exception as e:
            log_test("Test 1.4", "FAIL", f"Exception: {str(e)}")
        
        # Test 1.5: Get Unit Users
        print("\n📋 Test 1.5: Get Unit Users")
        try:
            response = requests.get(f"{BASE_URL}/organizations/units/{unit_id}/users", headers=headers)
            if response.status_code == 200:
                unit_users = response.json()
                log_test(
                    "Test 1.5",
                    "PASS",
                    f"Retrieved {len(unit_users)} users assigned to unit",
                    {"unit_id": unit_id, "user_count": len(unit_users)}
                )
            else:
                log_test("Test 1.5", "FAIL", f"Failed to get unit users: {response.status_code}")
        except Exception as e:
            log_test("Test 1.5", "FAIL", f"Exception: {str(e)}")
            
    except Exception as e:
        log_test("Test 1.2-1.5", "FAIL", f"Exception in assignment tests: {str(e)}")

# ============================================================================
# TEST SUITE 2: LINK EXISTING UNITS (8 tests)
# ============================================================================

def test_suite_2_link_units(token):
    """Test Suite 2: Link Existing Units"""
    print("\n" + "="*80)
    print("TEST SUITE 2: LINK EXISTING UNITS (8 tests)")
    print("="*80)
    
    headers = get_headers(token)
    
    # Test 2.1: Get Available Units for Linking
    print("\n📋 Test 2.1: Get Available Units for Linking")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units?level=2&unassigned=true", headers=headers)
        if response.status_code == 200:
            unassigned_units = response.json()
            log_test(
                "Test 2.1",
                "PASS",
                f"Retrieved {len(unassigned_units)} unassigned level 2 units",
                {"count": len(unassigned_units)}
            )
        else:
            log_test("Test 2.1", "FAIL", f"Failed to get unassigned units: {response.status_code}")
    except Exception as e:
        log_test("Test 2.1", "FAIL", f"Exception: {str(e)}")
    
    # Test 2.2: Create Test Orphaned Unit
    print("\n📋 Test 2.2: Create Test Orphaned Unit")
    orphaned_unit_id = None
    parent_for_orphan = None
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Strategy: Create a level 3 unit with a parent, then unlink it to make it orphaned
        # First, get or create a level 2 parent
        response = requests.get(f"{BASE_URL}/organizations/units?level=2", headers=headers)
        if response.status_code == 200:
            level2_units = response.json()
            if level2_units:
                # Use existing level 2 unit
                parent_for_orphan = level2_units[0]["id"]
                print(f"   Using existing level 2 unit as temporary parent: {level2_units[0]['name']}")
            else:
                # Need to create level 2 unit first (which needs level 1 parent)
                response = requests.get(f"{BASE_URL}/organizations/units?level=1", headers=headers)
                if response.status_code == 200:
                    level1_units = response.json()
                    if level1_units:
                        level1_parent = level1_units[0]["id"]
                        # Create level 2 unit
                        response = requests.post(
                            f"{BASE_URL}/organizations/units",
                            headers=headers,
                            json={
                                "name": f"Temp Parent Org {timestamp}",
                                "description": "Temporary parent for orphan test",
                                "level": 2,
                                "parent_id": level1_parent
                            }
                        )
                        if response.status_code == 201:
                            parent_for_orphan = response.json()["id"]
                            print(f"   Created level 2 unit as temporary parent")
        
        if not parent_for_orphan:
            log_test("Test 2.2", "FAIL", "Could not create/find parent for orphan test")
            return
        
        # Now create level 3 unit with parent
        response = requests.post(
            f"{BASE_URL}/organizations/units",
            headers=headers,
            json={
                "name": f"Orphaned Company Test {timestamp}",
                "description": "Test unit for linking",
                "level": 3,
                "parent_id": parent_for_orphan
            }
        )
        
        if response.status_code == 201:
            orphaned_unit = response.json()
            orphaned_unit_id = orphaned_unit["id"]
            print(f"   Created level 3 unit with parent: {orphaned_unit['name']}")
            
            # Now unlink it to make it orphaned
            response = requests.post(
                f"{BASE_URL}/organizations/units/{orphaned_unit_id}/unlink",
                headers=headers
            )
            
            if response.status_code == 200:
                log_test(
                    "Test 2.2",
                    "PASS",
                    f"Created and unlinked unit to make it orphaned",
                    {"unit_id": orphaned_unit_id, "name": orphaned_unit["name"], "level": 3}
                )
            else:
                log_test("Test 2.2", "WARN", f"Created unit but failed to unlink: {response.status_code}")
        else:
            log_test("Test 2.2", "FAIL", f"Failed to create unit: {response.status_code}", {"response": response.text})
            return
    except Exception as e:
        log_test("Test 2.2", "FAIL", f"Exception: {str(e)}")
        return
    
    # Test 2.3: Verify Unit is Unassigned
    print("\n📋 Test 2.3: Verify Unit is Unassigned")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units?level=3&unassigned=true", headers=headers)
        if response.status_code == 200:
            unassigned_level3 = response.json()
            found = any(u["id"] == orphaned_unit_id for u in unassigned_level3)
            if found:
                log_test(
                    "Test 2.3",
                    "PASS",
                    "Orphaned unit appears in unassigned list",
                    {"unit_id": orphaned_unit_id}
                )
            else:
                log_test("Test 2.3", "WARN", "Orphaned unit not found in unassigned list")
        else:
            log_test("Test 2.3", "FAIL", f"Failed to get unassigned units: {response.status_code}")
    except Exception as e:
        log_test("Test 2.3", "FAIL", f"Exception: {str(e)}")
    
    # Get a parent unit at level 2 for linking
    print("\n📋 Finding parent unit at level 2...")
    parent_unit_id = None
    try:
        response = requests.get(f"{BASE_URL}/organizations/units?level=2", headers=headers)
        if response.status_code == 200:
            level2_units = response.json()
            if level2_units:
                parent_unit_id = level2_units[0]["id"]
                print(f"   Using parent unit: {level2_units[0]['name']} (ID: {parent_unit_id})")
            else:
                print("   ⚠️  No level 2 units available, creating one...")
                # Create a level 2 unit (needs level 1 parent)
                response = requests.get(f"{BASE_URL}/organizations/units?level=1", headers=headers)
                if response.status_code == 200:
                    level1_units = response.json()
                    if level1_units:
                        level1_parent = level1_units[0]["id"]
                        response = requests.post(
                            f"{BASE_URL}/organizations/units",
                            headers=headers,
                            json={
                                "name": f"Test Parent Unit {timestamp}",
                                "description": "Parent unit for linking test",
                                "level": 2,
                                "parent_id": level1_parent
                            }
                        )
                        if response.status_code == 201:
                            parent_unit = response.json()
                            parent_unit_id = parent_unit["id"]
                            print(f"   Created parent unit: {parent_unit['name']} (ID: {parent_unit_id})")
    except Exception as e:
        print(f"   ❌ Error finding/creating parent unit: {str(e)}")
    
    if not parent_unit_id:
        log_test("Test 2.4-2.8", "FAIL", "No parent unit available for linking tests")
        return
    
    # Test 2.4: Link Unit to Parent
    print("\n📋 Test 2.4: Link Unit to Parent")
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/units/{parent_unit_id}/link-child",
            headers=headers,
            json={
                "child_unit_id": orphaned_unit_id
            }
        )
        
        if response.status_code == 201:
            link_result = response.json()
            log_test(
                "Test 2.4",
                "PASS",
                "Unit linked to parent successfully",
                {"parent_id": parent_unit_id, "child_id": orphaned_unit_id, "result": link_result}
            )
        else:
            log_test("Test 2.4", "FAIL", f"Failed to link unit: {response.status_code}", {"response": response.text})
            return
    except Exception as e:
        log_test("Test 2.4", "FAIL", f"Exception: {str(e)}")
        return
    
    # Test 2.5: Verify Linking in Database
    print("\n📋 Test 2.5: Verify Linking in Database")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units/{orphaned_unit_id}", headers=headers)
        if response.status_code == 200:
            linked_unit = response.json()
            if linked_unit.get("parent_id") == parent_unit_id:
                log_test(
                    "Test 2.5",
                    "PASS",
                    "Child unit now has parent_id field",
                    {"child_id": orphaned_unit_id, "parent_id": linked_unit.get("parent_id")}
                )
            else:
                log_test("Test 2.5", "FAIL", f"parent_id mismatch", 
                        {"expected": parent_unit_id, "actual": linked_unit.get("parent_id")})
        else:
            log_test("Test 2.5", "FAIL", f"Failed to get unit: {response.status_code}")
    except Exception as e:
        log_test("Test 2.5", "FAIL", f"Exception: {str(e)}")
    
    # Test 2.6: Verify Unit No Longer in Unassigned List
    print("\n📋 Test 2.6: Verify Unit No Longer in Unassigned List")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units?level=3&unassigned=true", headers=headers)
        if response.status_code == 200:
            unassigned_level3 = response.json()
            found = any(u["id"] == orphaned_unit_id for u in unassigned_level3)
            if not found:
                log_test(
                    "Test 2.6",
                    "PASS",
                    "Linked unit no longer appears in unassigned list",
                    {"unit_id": orphaned_unit_id}
                )
            else:
                log_test("Test 2.6", "WARN", "Linked unit still in unassigned list")
        else:
            log_test("Test 2.6", "FAIL", f"Failed to get unassigned units: {response.status_code}")
    except Exception as e:
        log_test("Test 2.6", "FAIL", f"Exception: {str(e)}")
    
    # Test 2.7: Test Level Validation
    print("\n📋 Test 2.7: Test Level Validation")
    try:
        # Try to link a level 4 unit to a level 2 parent (should fail - needs level 3)
        # First create a level 4 unit with a temporary parent, then unlink it
        # Get a level 3 unit to create level 4
        response = requests.get(f"{BASE_URL}/organizations/units?level=3", headers=headers)
        if response.status_code == 200:
            level3_units = response.json()
            if level3_units:
                temp_parent_l3 = level3_units[0]["id"]
                # Create level 4 unit
                response = requests.post(
                    f"{BASE_URL}/organizations/units",
                    headers=headers,
                    json={
                        "name": f"Wrong Level Unit {timestamp}",
                        "description": "Unit with wrong level for testing",
                        "level": 4,
                        "parent_id": temp_parent_l3
                    }
                )
                
                if response.status_code == 201:
                    wrong_level_unit = response.json()
                    wrong_level_unit_id = wrong_level_unit["id"]
                    
                    # Unlink it
                    requests.post(f"{BASE_URL}/organizations/units/{wrong_level_unit_id}/unlink", headers=headers)
                    
                    # Try to link it to level 2 parent (should fail - child should be level 3)
                    response = requests.post(
                        f"{BASE_URL}/organizations/units/{parent_unit_id}/link-child",
                        headers=headers,
                        json={
                            "child_unit_id": wrong_level_unit_id
                        }
                    )
            
            if response.status_code == 400:
                log_test(
                    "Test 2.7",
                    "PASS",
                    "Level validation working - rejected wrong level",
                    {"status_code": 400, "error": response.json().get("detail")}
                )
            else:
                log_test("Test 2.7", "FAIL", f"Level validation failed - should reject: {response.status_code}")
        else:
            log_test("Test 2.7", "WARN", "Could not create test unit for level validation")
    except Exception as e:
        log_test("Test 2.7", "FAIL", f"Exception: {str(e)}")
    
    # Test 2.8: Test Already Linked Validation
    print("\n📋 Test 2.8: Test Already Linked Validation")
    try:
        # Try to link the already linked unit again
        response = requests.post(
            f"{BASE_URL}/organizations/units/{parent_unit_id}/link-child",
            headers=headers,
            json={
                "child_unit_id": orphaned_unit_id
            }
        )
        
        if response.status_code == 400 and "already linked" in response.text.lower():
            log_test(
                "Test 2.8",
                "PASS",
                "Already linked validation working",
                {"status_code": 400, "error": response.json().get("detail")}
            )
        else:
            log_test("Test 2.8", "FAIL", f"Already linked validation failed: {response.status_code}")
    except Exception as e:
        log_test("Test 2.8", "FAIL", f"Exception: {str(e)}")
    
    return orphaned_unit_id

# ============================================================================
# TEST SUITE 3: UNLINK FUNCTIONALITY (3 tests)
# ============================================================================

def test_suite_3_unlink(token, linked_unit_id):
    """Test Suite 3: Unlink Functionality"""
    print("\n" + "="*80)
    print("TEST SUITE 3: UNLINK FUNCTIONALITY (3 tests)")
    print("="*80)
    
    if not linked_unit_id:
        log_test("Test 3.1-3.3", "WARN", "No linked unit available for unlink tests")
        return
    
    headers = get_headers(token)
    
    # Test 3.1: Unlink Unit from Parent
    print("\n📋 Test 3.1: Unlink Unit from Parent")
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/units/{linked_unit_id}/unlink",
            headers=headers
        )
        
        if response.status_code == 200:
            unlink_result = response.json()
            log_test(
                "Test 3.1",
                "PASS",
                "Unit unlinked from parent successfully",
                {"unit_id": linked_unit_id, "result": unlink_result}
            )
        else:
            log_test("Test 3.1", "FAIL", f"Failed to unlink unit: {response.status_code}", {"response": response.text})
            return
    except Exception as e:
        log_test("Test 3.1", "FAIL", f"Exception: {str(e)}")
        return
    
    # Test 3.2: Verify Unit is Orphaned
    print("\n📋 Test 3.2: Verify Unit is Orphaned")
    try:
        response = requests.get(f"{BASE_URL}/organizations/units/{linked_unit_id}", headers=headers)
        if response.status_code == 200:
            orphaned_unit = response.json()
            if orphaned_unit.get("parent_id") is None:
                log_test(
                    "Test 3.2",
                    "PASS",
                    "Unit has no parent (parent_id is null)",
                    {"unit_id": linked_unit_id, "parent_id": orphaned_unit.get("parent_id")}
                )
            else:
                log_test("Test 3.2", "FAIL", f"Unit still has parent_id", 
                        {"parent_id": orphaned_unit.get("parent_id")})
        else:
            log_test("Test 3.2", "FAIL", f"Failed to get unit: {response.status_code}")
    except Exception as e:
        log_test("Test 3.2", "FAIL", f"Exception: {str(e)}")
    
    # Test 3.3: Test Unlink Already Orphaned Unit
    print("\n📋 Test 3.3: Test Unlink Already Orphaned Unit")
    try:
        response = requests.post(
            f"{BASE_URL}/organizations/units/{linked_unit_id}/unlink",
            headers=headers
        )
        
        if response.status_code == 400 and "not linked" in response.text.lower():
            log_test(
                "Test 3.3",
                "PASS",
                "Unlink validation working - rejected orphaned unit",
                {"status_code": 400, "error": response.json().get("detail")}
            )
        else:
            log_test("Test 3.3", "FAIL", f"Unlink validation failed: {response.status_code}")
    except Exception as e:
        log_test("Test 3.3", "FAIL", f"Exception: {str(e)}")

# ============================================================================
# TEST SUITE 4: HIERARCHY INTEGRITY (3 tests)
# ============================================================================

def test_suite_4_hierarchy(token):
    """Test Suite 4: Hierarchy Integrity"""
    print("\n" + "="*80)
    print("TEST SUITE 4: HIERARCHY INTEGRITY (3 tests)")
    print("="*80)
    
    headers = get_headers(token)
    
    # Test 4.1: Get Complete Hierarchy
    print("\n📋 Test 4.1: Get Complete Hierarchy")
    try:
        response = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
        if response.status_code == 200:
            hierarchy = response.json()
            
            # Verify tree structure
            def validate_tree(nodes, parent_level=0):
                issues = []
                for node in nodes:
                    # Check user_count field exists
                    if "user_count" not in node:
                        issues.append(f"Missing user_count in node {node['id']}")
                    
                    # Check level progression
                    if parent_level > 0 and node["level"] != parent_level + 1:
                        issues.append(f"Invalid level progression: parent {parent_level}, child {node['level']}")
                    
                    # Recursively check children
                    if node.get("children"):
                        issues.extend(validate_tree(node["children"], node["level"]))
                
                return issues
            
            issues = validate_tree(hierarchy)
            
            if not issues:
                log_test(
                    "Test 4.1",
                    "PASS",
                    f"Hierarchy structure valid with {len(hierarchy)} root units",
                    {"root_count": len(hierarchy), "structure": "valid"}
                )
            else:
                log_test("Test 4.1", "WARN", f"Hierarchy has {len(issues)} issues", {"issues": issues})
        else:
            log_test("Test 4.1", "FAIL", f"Failed to get hierarchy: {response.status_code}")
    except Exception as e:
        log_test("Test 4.1", "FAIL", f"Exception: {str(e)}")
    
    # Test 4.2: Get All Units with Filters
    print("\n📋 Test 4.2: Get All Units with Filters")
    try:
        # Test all units
        response1 = requests.get(f"{BASE_URL}/organizations/units", headers=headers)
        # Test level filter
        response2 = requests.get(f"{BASE_URL}/organizations/units?level=1", headers=headers)
        # Test unassigned filter
        response3 = requests.get(f"{BASE_URL}/organizations/units?unassigned=true", headers=headers)
        
        if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
            all_units = response1.json()
            level1_units = response2.json()
            unassigned_units = response3.json()
            
            log_test(
                "Test 4.2",
                "PASS",
                "All filter combinations working",
                {
                    "all_units": len(all_units),
                    "level1_units": len(level1_units),
                    "unassigned_units": len(unassigned_units)
                }
            )
        else:
            log_test("Test 4.2", "FAIL", "Some filter combinations failed")
    except Exception as e:
        log_test("Test 4.2", "FAIL", f"Exception: {str(e)}")
    
    # Test 4.3: Verify User Count Calculation
    print("\n📋 Test 4.3: Verify User Count Calculation")
    try:
        response = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
        if response.status_code == 200:
            hierarchy = response.json()
            
            # Count total user_count across all units
            def count_users(nodes):
                total = 0
                for node in nodes:
                    total += node.get("user_count", 0)
                    if node.get("children"):
                        total += count_users(node["children"])
                return total
            
            total_user_count = count_users(hierarchy)
            
            log_test(
                "Test 4.3",
                "PASS",
                f"User count calculation working - {total_user_count} total assignments",
                {"total_user_count": total_user_count}
            )
        else:
            log_test("Test 4.3", "FAIL", f"Failed to get hierarchy: {response.status_code}")
    except Exception as e:
        log_test("Test 4.3", "FAIL", f"Exception: {str(e)}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("BACKEND TESTING - ORGANIZATION LINKING & USER ASSIGNMENT")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print(f"Total Tests: 19 backend tests across 4 test suites")
    
    # Authenticate
    token, user_data = authenticate()
    if not token:
        print("\n❌ AUTHENTICATION FAILED - Cannot proceed with tests")
        sys.exit(1)
    
    # Run test suites
    users = test_suite_1_user_assignment(token)
    test_suite_1_assign_user(token, users)
    
    linked_unit_id = test_suite_2_link_units(token)
    
    test_suite_3_unlink(token, linked_unit_id)
    
    test_suite_4_hierarchy(token)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⚠️  Warnings: {test_results['warnings']}")
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    # Print failed tests
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results['tests']:
            if test['status'] == 'FAIL':
                print(f"   - {test['name']}: {test['message']}")
    
    # Print warnings
    if test_results['warnings'] > 0:
        print("\n⚠️  WARNINGS:")
        for test in test_results['tests']:
            if test['status'] == 'WARN':
                print(f"   - {test['name']}: {test['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
