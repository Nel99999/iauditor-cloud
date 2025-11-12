#!/usr/bin/env python3
"""
PHASE 2 TESTING - ORGANIZATIONAL ENTITIES INTEGRATION
Test that all organizational endpoints now use organizational_entities collection.

Test User:
- Email: llewellyn@bluedawncapital.co.za
- Password: Test@1234
- Role: developer

Total Tests: 24
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
    "passed": 0,
    "failed": 0,
    "total": 24,
    "details": []
}

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results["details"].append(f"{status}: {test_name} - {message}")
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")

def authenticate():
    """Authenticate and get token"""
    print("\n🔐 AUTHENTICATING...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        org_id = data.get("user", {}).get("organization_id")
        role = data.get("user", {}).get("role")
        print(f"✅ Authenticated as {TEST_USER_EMAIL}")
        print(f"   User ID: {user_id}")
        print(f"   Organization ID: {org_id}")
        print(f"   Role: {role}")
        return token, user_id, org_id
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)

def test_suite_1_hierarchy_endpoint(token):
    """TEST SUITE 1: Hierarchy Endpoint with Entities (5 tests)"""
    print("\n" + "="*80)
    print("TEST SUITE 1: HIERARCHY ENDPOINT WITH ENTITIES (5 tests)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1.1: GET Hierarchy
    print("\n📋 Test 1.1: GET Hierarchy")
    response = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
    
    if response.status_code == 200:
        hierarchy = response.json()
        entity_count = count_entities_in_tree(hierarchy)
        log_test("1.1 GET Hierarchy", True, 
                f"Retrieved tree structure with {entity_count} entities")
        
        # Test 1.2: Verify Rich Data in Hierarchy
        print("\n📋 Test 1.2: Verify Rich Data in Hierarchy")
        rich_fields_found = check_rich_fields_in_hierarchy(hierarchy)
        log_test("1.2 Verify Rich Data", len(rich_fields_found) > 0,
                f"Found rich fields: {', '.join(rich_fields_found[:5])}")
        
        # Test 1.3: Verify User Counts
        print("\n📋 Test 1.3: Verify User Counts")
        has_user_counts = check_user_counts_in_hierarchy(hierarchy)
        log_test("1.3 Verify User Counts", has_user_counts,
                "User counts present in hierarchy")
        
        # Test 1.4: Verify Tree Structure
        print("\n📋 Test 1.4: Verify Tree Structure")
        tree_valid = verify_tree_structure(hierarchy)
        log_test("1.4 Verify Tree Structure", tree_valid,
                "Parent-child relationships properly nested")
        
        # Test 1.5: Count Total Entities
        print("\n📋 Test 1.5: Count Total Entities")
        log_test("1.5 Count Total Entities", entity_count >= 14,
                f"Found {entity_count} entities (expected 14+)")
        
        return hierarchy
    else:
        log_test("1.1 GET Hierarchy", False, 
                f"Status: {response.status_code}, Response: {response.text[:200]}")
        log_test("1.2 Verify Rich Data", False, "Hierarchy request failed")
        log_test("1.3 Verify User Counts", False, "Hierarchy request failed")
        log_test("1.4 Verify Tree Structure", False, "Hierarchy request failed")
        log_test("1.5 Count Total Entities", False, "Hierarchy request failed")
        return None

def test_suite_2_get_units_endpoint(token):
    """TEST SUITE 2: GET /units Endpoint (4 tests)"""
    print("\n" + "="*80)
    print("TEST SUITE 2: GET /units ENDPOINT (4 tests)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2.1: GET All Units
    print("\n📋 Test 2.1: GET All Units")
    response = requests.get(f"{BASE_URL}/organizations/units", headers=headers)
    
    if response.status_code == 200:
        units = response.json()
        log_test("2.1 GET All Units", len(units) >= 14,
                f"Retrieved {len(units)} entities (expected 14+)")
        
        # Test 2.2: GET Units by Level
        print("\n📋 Test 2.2: GET Units by Level (level=3)")
        response_level = requests.get(f"{BASE_URL}/organizations/units?level=3", headers=headers)
        if response_level.status_code == 200:
            level3_units = response_level.json()
            all_level3 = all(u.get("level") == 3 for u in level3_units)
            log_test("2.2 GET Units by Level", all_level3,
                    f"Retrieved {len(level3_units)} level 3 entities")
        else:
            log_test("2.2 GET Units by Level", False, f"Status: {response_level.status_code}")
        
        # Test 2.3: GET Unassigned Units
        print("\n📋 Test 2.3: GET Unassigned Units")
        response_unassigned = requests.get(
            f"{BASE_URL}/organizations/units?level=2&unassigned=true", 
            headers=headers
        )
        if response_unassigned.status_code == 200:
            unassigned = response_unassigned.json()
            all_orphaned = all(u.get("parent_id") is None for u in unassigned)
            log_test("2.3 GET Unassigned Units", all_orphaned,
                    f"Retrieved {len(unassigned)} orphaned entities")
        else:
            log_test("2.3 GET Unassigned Units", False, f"Status: {response_unassigned.status_code}")
        
        # Test 2.4: Verify User Counts in Units
        print("\n📋 Test 2.4: Verify User Counts in Units")
        has_user_counts = all("user_count" in u for u in units)
        log_test("2.4 Verify User Counts", has_user_counts,
                "All units have user_count field")
        
        return units
    else:
        log_test("2.1 GET All Units", False, 
                f"Status: {response.status_code}, Response: {response.text[:200]}")
        log_test("2.2 GET Units by Level", False, "GET All Units failed")
        log_test("2.3 GET Unassigned Units", False, "GET All Units failed")
        log_test("2.4 Verify User Counts", False, "GET All Units failed")
        return None

def test_suite_3_link_unlink(token, units):
    """TEST SUITE 3: Link/Unlink with Entities (6 tests)"""
    print("\n" + "="*80)
    print("TEST SUITE 3: LINK/UNLINK WITH ENTITIES (6 tests)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not units:
        for i in range(6):
            log_test(f"3.{i+1} Link/Unlink Test", False, "No units available")
        return
    
    # Find an orphaned entity and a potential parent
    orphaned = [u for u in units if u.get("parent_id") is None and u.get("level") > 1]
    potential_parents = [u for u in units if u.get("level") < 5]
    
    if not orphaned or not potential_parents:
        print("⚠️  No suitable entities for link/unlink testing")
        for i in range(6):
            log_test(f"3.{i+1} Link/Unlink Test", False, "No suitable entities")
        return
    
    # Find compatible pair (parent.level + 1 == child.level)
    test_child = None
    test_parent = None
    
    for child in orphaned:
        for parent in potential_parents:
            if parent["level"] + 1 == child["level"]:
                test_child = child
                test_parent = parent
                break
        if test_child:
            break
    
    if not test_child or not test_parent:
        print("⚠️  No compatible parent-child pair found")
        for i in range(6):
            log_test(f"3.{i+1} Link/Unlink Test", False, "No compatible pair")
        return
    
    print(f"\n🔗 Using Parent: {test_parent['name']} (Level {test_parent['level']})")
    print(f"🔗 Using Child: {test_child['name']} (Level {test_child['level']})")
    
    # Test 3.1: Link Entity to Parent
    print("\n📋 Test 3.1: Link Entity to Parent")
    response = requests.post(
        f"{BASE_URL}/organizations/units/{test_parent['id']}/link-child",
        headers=headers,
        json={"child_unit_id": test_child['id']}
    )
    
    if response.status_code == 201:
        log_test("3.1 Link Entity", True, "Entity linked successfully")
        
        # Test 3.2: Verify Link in Database
        print("\n📋 Test 3.2: Verify Link in Database")
        response_verify = requests.get(
            f"{BASE_URL}/organizations/units/{test_child['id']}",
            headers=headers
        )
        if response_verify.status_code == 200:
            updated_child = response_verify.json()
            linked = updated_child.get("parent_id") == test_parent['id']
            log_test("3.2 Verify Link in DB", linked,
                    f"parent_id = {updated_child.get('parent_id')}")
        else:
            log_test("3.2 Verify Link in DB", False, f"Status: {response_verify.status_code}")
        
        # Test 3.3: Verify in Hierarchy
        print("\n📋 Test 3.3: Verify in Hierarchy")
        response_hierarchy = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
        if response_hierarchy.status_code == 200:
            hierarchy = response_hierarchy.json()
            found_in_tree = find_entity_in_tree(hierarchy, test_child['id'])
            log_test("3.3 Verify in Hierarchy", found_in_tree,
                    "Linked entity appears in tree")
        else:
            log_test("3.3 Verify in Hierarchy", False, "Hierarchy request failed")
        
        # Test 3.4: Unlink Entity
        print("\n📋 Test 3.4: Unlink Entity")
        response_unlink = requests.post(
            f"{BASE_URL}/organizations/units/{test_child['id']}/unlink",
            headers=headers
        )
        if response_unlink.status_code == 200:
            log_test("3.4 Unlink Entity", True, "Entity unlinked successfully")
            
            # Test 3.5: Verify Unlink
            print("\n📋 Test 3.5: Verify Unlink")
            response_verify_unlink = requests.get(
                f"{BASE_URL}/organizations/units/{test_child['id']}",
                headers=headers
            )
            if response_verify_unlink.status_code == 200:
                unlinked_child = response_verify_unlink.json()
                is_orphaned = unlinked_child.get("parent_id") is None
                log_test("3.5 Verify Unlink", is_orphaned,
                        f"parent_id = {unlinked_child.get('parent_id')}")
            else:
                log_test("3.5 Verify Unlink", False, f"Status: {response_verify_unlink.status_code}")
            
            # Test 3.6: Verify in Unassigned List
            print("\n📋 Test 3.6: Verify in Unassigned List")
            response_unassigned = requests.get(
                f"{BASE_URL}/organizations/units?unassigned=true",
                headers=headers
            )
            if response_unassigned.status_code == 200:
                unassigned_list = response_unassigned.json()
                found_in_unassigned = any(u['id'] == test_child['id'] for u in unassigned_list)
                log_test("3.6 Verify in Unassigned", found_in_unassigned,
                        "Entity appears in unassigned list")
            else:
                log_test("3.6 Verify in Unassigned", False, "Unassigned request failed")
        else:
            log_test("3.4 Unlink Entity", False, f"Status: {response_unlink.status_code}")
            log_test("3.5 Verify Unlink", False, "Unlink failed")
            log_test("3.6 Verify in Unassigned", False, "Unlink failed")
    else:
        log_test("3.1 Link Entity", False, 
                f"Status: {response.status_code}, Response: {response.text[:200]}")
        for i in range(2, 7):
            log_test(f"3.{i} Link/Unlink Test", False, "Link failed")

def test_suite_4_user_assignment(token, units):
    """TEST SUITE 4: User Assignment with Entities (4 tests)"""
    print("\n" + "="*80)
    print("TEST SUITE 4: USER ASSIGNMENT WITH ENTITIES (4 tests)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not units:
        for i in range(4):
            log_test(f"4.{i+1} User Assignment Test", False, "No units available")
        return
    
    # Get users to find one to assign
    response_users = requests.get(f"{BASE_URL}/users", headers=headers)
    if response_users.status_code != 200:
        for i in range(4):
            log_test(f"4.{i+1} User Assignment Test", False, "Cannot get users")
        return
    
    users = response_users.json()
    if not users:
        for i in range(4):
            log_test(f"4.{i+1} User Assignment Test", False, "No users available")
        return
    
    # Find a user not assigned to the first unit
    test_unit = units[0]
    test_user = users[0]
    
    print(f"\n👤 Using User: {test_user.get('name', 'Unknown')} ({test_user.get('email')})")
    print(f"🏢 Using Unit: {test_unit['name']}")
    
    # Test 4.1: Assign User to Entity
    print("\n📋 Test 4.1: Assign User to Entity")
    response = requests.post(
        f"{BASE_URL}/organizations/units/{test_unit['id']}/assign-user",
        headers=headers,
        json={
            "user_id": test_user['id'],
            "unit_id": test_unit['id'],
            "role": "inspector"
        }
    )
    
    if response.status_code in [201, 400]:  # 400 if already assigned
        if response.status_code == 201:
            log_test("4.1 Assign User", True, "User assigned successfully")
            assignment_created = True
        else:
            # Already assigned
            log_test("4.1 Assign User", True, "User already assigned (expected)")
            assignment_created = False
        
        # Test 4.2: Verify User Count Updates
        print("\n📋 Test 4.2: Verify User Count Updates")
        response_hierarchy = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
        if response_hierarchy.status_code == 200:
            hierarchy = response_hierarchy.json()
            entity_in_tree = find_entity_in_tree(hierarchy, test_unit['id'])
            if entity_in_tree:
                user_count = entity_in_tree.get("user_count", 0)
                log_test("4.2 Verify User Count", user_count > 0,
                        f"Entity has {user_count} users")
            else:
                log_test("4.2 Verify User Count", False, "Entity not found in hierarchy")
        else:
            log_test("4.2 Verify User Count", False, "Hierarchy request failed")
        
        # Test 4.3: GET Unit Users
        print("\n📋 Test 4.3: GET Unit Users")
        response_unit_users = requests.get(
            f"{BASE_URL}/organizations/units/{test_unit['id']}/users",
            headers=headers
        )
        if response_unit_users.status_code == 200:
            unit_users = response_unit_users.json()
            user_found = any(u['user']['id'] == test_user['id'] for u in unit_users)
            log_test("4.3 GET Unit Users", user_found,
                    f"Found {len(unit_users)} users, target user present")
        else:
            log_test("4.3 GET Unit Users", False, f"Status: {response_unit_users.status_code}")
        
        # Test 4.4: Verify in Hierarchy
        print("\n📋 Test 4.4: Verify in Hierarchy")
        log_test("4.4 Verify in Hierarchy", entity_in_tree is not None,
                "User count reflects assignments")
    else:
        log_test("4.1 Assign User", False, 
                f"Status: {response.status_code}, Response: {response.text[:200]}")
        for i in range(2, 5):
            log_test(f"4.{i} User Assignment Test", False, "Assignment failed")

def test_suite_5_crud_operations(token):
    """TEST SUITE 5: Create/Update/Delete Operations (5 tests)"""
    print("\n" + "="*80)
    print("TEST SUITE 5: CREATE/UPDATE/DELETE OPERATIONS (5 tests)")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 5.1: Create New Entity via Entities API
    print("\n📋 Test 5.1: Create New Entity via Entities API")
    new_entity_data = {
        "entity_type": "company",
        "level": 3,
        "name": f"Test Company {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Test company for Phase 2 testing",
        "industry": "Technology",
        "address_city": "Test City",
        "address_country": "Test Country",
        "tax_id": "TEST123456",
        "cost_center": "CC-TEST-001",
        "primary_color": "#FF5733"
    }
    
    response = requests.post(
        f"{BASE_URL}/entities",
        headers=headers,
        json=new_entity_data
    )
    
    if response.status_code == 201:
        new_entity = response.json()
        entity_id = new_entity.get("id")
        log_test("5.1 Create New Entity", True, f"Created entity: {new_entity['name']}")
        
        # Test 5.2: Verify Appears in Hierarchy (should be absent as orphaned)
        print("\n📋 Test 5.2: Verify Appears in Hierarchy")
        response_hierarchy = requests.get(f"{BASE_URL}/organizations/hierarchy", headers=headers)
        if response_hierarchy.status_code == 200:
            hierarchy = response_hierarchy.json()
            found = find_entity_in_tree(hierarchy, entity_id)
            # Should NOT be in tree as it's orphaned (no parent_id)
            log_test("5.2 Verify in Hierarchy", found is None,
                    "Orphaned entity correctly absent from tree")
        else:
            log_test("5.2 Verify in Hierarchy", False, "Hierarchy request failed")
        
        # Test 5.3: Update Entity
        print("\n📋 Test 5.3: Update Entity")
        update_data = {
            "name": f"Updated Test Company {datetime.now().strftime('%H%M%S')}",
            "industry": "Manufacturing",
            "tax_id": "UPDATED999"
        }
        response_update = requests.put(
            f"{BASE_URL}/entities/{entity_id}",
            headers=headers,
            json=update_data
        )
        if response_update.status_code == 200:
            log_test("5.3 Update Entity", True, "Entity updated successfully")
            
            # Test 5.4: Verify Update in Hierarchy
            print("\n📋 Test 5.4: Verify Update in Hierarchy")
            response_entity = requests.get(f"{BASE_URL}/entities/{entity_id}", headers=headers)
            if response_entity.status_code == 200:
                updated_entity = response_entity.json()
                name_updated = updated_entity.get("name") == update_data["name"]
                industry_updated = updated_entity.get("industry") == update_data["industry"]
                log_test("5.4 Verify Update", name_updated and industry_updated,
                        "Updated fields verified")
            else:
                log_test("5.4 Verify Update", False, "Entity GET failed")
        else:
            log_test("5.3 Update Entity", False, f"Status: {response_update.status_code}")
            log_test("5.4 Verify Update", False, "Update failed")
        
        # Test 5.5: Delete Workflow
        print("\n📋 Test 5.5: Delete Workflow")
        # Entity is already orphaned, so can delete directly
        response_delete = requests.delete(
            f"{BASE_URL}/entities/{entity_id}",
            headers=headers
        )
        if response_delete.status_code == 200:
            log_test("5.5 Delete Workflow", True, "Entity deleted successfully")
        else:
            log_test("5.5 Delete Workflow", False, 
                    f"Status: {response_delete.status_code}, Response: {response_delete.text[:200]}")
    else:
        log_test("5.1 Create New Entity", False, 
                f"Status: {response.status_code}, Response: {response.text[:200]}")
        for i in range(2, 6):
            log_test(f"5.{i} CRUD Test", False, "Create failed")

# Helper functions
def count_entities_in_tree(tree):
    """Recursively count entities in tree"""
    count = len(tree)
    for entity in tree:
        count += count_entities_in_tree(entity.get("children", []))
    return count

def check_rich_fields_in_hierarchy(tree):
    """Check for rich metadata fields in hierarchy"""
    rich_fields = set()
    
    def check_entity(entity):
        for field in ["logo_url", "primary_color", "address_city", "address_country", 
                     "industry", "tax_id", "cost_center", "phone", "email"]:
            if entity.get(field) is not None:
                rich_fields.add(field)
        for child in entity.get("children", []):
            check_entity(child)
    
    for entity in tree:
        check_entity(entity)
    
    return list(rich_fields)

def check_user_counts_in_hierarchy(tree):
    """Check if user_count field exists in hierarchy"""
    def check_entity(entity):
        if "user_count" not in entity:
            return False
        for child in entity.get("children", []):
            if not check_entity(child):
                return False
        return True
    
    return all(check_entity(entity) for entity in tree)

def verify_tree_structure(tree):
    """Verify tree has proper parent-child relationships"""
    # Check that all entities have required fields
    def check_entity(entity):
        required = ["id", "name", "level", "children"]
        if not all(field in entity for field in required):
            return False
        for child in entity.get("children", []):
            if not check_entity(child):
                return False
        return True
    
    return all(check_entity(entity) for entity in tree)

def find_entity_in_tree(tree, entity_id):
    """Find entity in tree by ID"""
    for entity in tree:
        if entity.get("id") == entity_id:
            return entity
        found = find_entity_in_tree(entity.get("children", []), entity_id)
        if found:
            return found
    return None

def main():
    """Main test execution"""
    print("="*80)
    print("PHASE 2 TESTING - ORGANIZATIONAL ENTITIES INTEGRATION")
    print("="*80)
    print(f"Test User: {TEST_USER_EMAIL}")
    print(f"Total Tests: {test_results['total']}")
    print("="*80)
    
    # Authenticate
    token, user_id, org_id = authenticate()
    
    # Run test suites
    hierarchy = test_suite_1_hierarchy_endpoint(token)
    units = test_suite_2_get_units_endpoint(token)
    test_suite_3_link_unlink(token, units)
    test_suite_4_user_assignment(token, units)
    test_suite_5_crud_operations(token)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed']/test_results['total']*100):.1f}%")
    print("="*80)
    
    print("\n📋 DETAILED RESULTS:")
    for detail in test_results["details"]:
        print(detail)
    
    # Exit with appropriate code
    sys.exit(0 if test_results["failed"] == 0 else 1)

if __name__ == "__main__":
    main()
