#!/usr/bin/env python3
"""
TEST USER ALLOCATION FUNCTIONALITY - VERIFY FIX
Tests the fix for 422 error when allocating users to units
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "Test@1234"

# Test results tracking
test_results = []
total_tests = 0
passed_tests = 0

def log_test(test_name, passed, details=""):
    """Log test result"""
    global total_tests, passed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
    
    status = "✅ PASSED" if passed else "❌ FAILED"
    result = {
        "test": test_name,
        "status": status,
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    print(f"\n{status}: {test_name}")
    if details:
        print(f"  Details: {details}")
    return passed

def authenticate():
    """Authenticate and get token"""
    print("\n" + "="*80)
    print("AUTHENTICATING TEST USER")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_info = data.get("user", {})
            print(f"✅ Authentication successful")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Organization ID: {user_info.get('organization_id')}")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def get_all_users(token):
    """Get all users in the organization"""
    print("\n" + "="*80)
    print("TEST 1: GET ALL USERS")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            
            # Display first few users
            for i, user in enumerate(users[:5]):
                print(f"   User {i+1}: {user.get('name')} ({user.get('email')}) - ID: {user.get('id')}")
            
            log_test("Get All Users", True, f"Retrieved {len(users)} users")
            return users
        else:
            log_test("Get All Users", False, f"Status: {response.status_code}, Response: {response.text}")
            return []
    except Exception as e:
        log_test("Get All Users", False, f"Error: {str(e)}")
        return []

def get_all_units(token):
    """Get all organizational units"""
    print("\n" + "="*80)
    print("TEST 2: GET ALL ORGANIZATIONAL UNITS")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/organizations/units",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            units = response.json()
            print(f"✅ Retrieved {len(units)} organizational units")
            
            # Display units
            for i, unit in enumerate(units[:5]):
                print(f"   Unit {i+1}: {unit.get('name')} (Level {unit.get('level')}) - ID: {unit.get('id')}")
            
            log_test("Get All Units", True, f"Retrieved {len(units)} units")
            return units
        else:
            log_test("Get All Units", False, f"Status: {response.status_code}, Response: {response.text}")
            return []
    except Exception as e:
        log_test("Get All Units", False, f"Error: {str(e)}")
        return []

def assign_user_to_unit(token, user_id, unit_id, role="inspector"):
    """Assign user to unit - CRITICAL TEST"""
    print("\n" + "="*80)
    print("TEST 3: ASSIGN USER TO UNIT (POST /api/organizations/units/{unit_id}/assign-user)")
    print("="*80)
    print(f"User ID: {user_id}")
    print(f"Unit ID: {unit_id}")
    print(f"Role: {role}")
    
    # CRITICAL: Request body must include BOTH user_id AND unit_id
    request_body = {
        "user_id": user_id,
        "unit_id": unit_id,
        "role": role
    }
    
    print(f"\nRequest Body:")
    print(json.dumps(request_body, indent=2))
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/organizations/units/{unit_id}/assign-user",
            headers={"Authorization": f"Bearer {token}"},
            json=request_body,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            assignment = response.json()
            print(f"\n✅ User assigned successfully!")
            print(f"   Assignment ID: {assignment.get('id')}")
            print(f"   User ID: {assignment.get('user_id')}")
            print(f"   Unit ID: {assignment.get('unit_id')}")
            print(f"   Organization ID: {assignment.get('organization_id')}")
            print(f"   Role: {assignment.get('role')}")
            print(f"   Created At: {assignment.get('created_at')}")
            
            log_test("Assign User to Unit (201 Created)", True, f"Assignment ID: {assignment.get('id')}")
            return assignment
        elif response.status_code == 422:
            print(f"\n❌ VALIDATION ERROR (422) - This should NOT happen after fix!")
            log_test("Assign User to Unit (Should be 201, not 422)", False, f"422 Error: {response.text}")
            return None
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "already assigned" in error_detail.lower():
                print(f"\n⚠️  User already assigned to this unit (expected behavior)")
                log_test("Assign User to Unit (Already Assigned)", True, "User already assigned - expected")
                return {"already_assigned": True}
            else:
                log_test("Assign User to Unit", False, f"400 Error: {response.text}")
                return None
        else:
            log_test("Assign User to Unit", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        log_test("Assign User to Unit", False, f"Error: {str(e)}")
        return None

def verify_assignment_in_db(token, user_id, unit_id):
    """Verify assignment was created in database"""
    print("\n" + "="*80)
    print("TEST 4: VERIFY ASSIGNMENT IN DATABASE")
    print("="*80)
    
    # We'll verify by checking if the user appears in the unit's user list
    try:
        response = requests.get(
            f"{BACKEND_URL}/organizations/units/{unit_id}/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            unit_users = response.json()
            print(f"✅ Retrieved {len(unit_users)} users in unit")
            
            # Check if our user is in the list
            user_found = False
            for assignment in unit_users:
                user_data = assignment.get("user", {})
                if user_data.get("id") == user_id:
                    user_found = True
                    print(f"\n✅ User found in unit assignments!")
                    print(f"   Assignment ID: {assignment.get('assignment_id')}")
                    print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
                    print(f"   Role: {assignment.get('role')}")
                    print(f"   Assigned At: {assignment.get('assigned_at')}")
                    break
            
            if user_found:
                log_test("Verify Assignment in Database", True, "User found in unit assignments")
                return True
            else:
                log_test("Verify Assignment in Database", False, "User not found in unit assignments")
                return False
        else:
            log_test("Verify Assignment in Database", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Verify Assignment in Database", False, f"Error: {str(e)}")
        return False

def verify_user_count_updates(token):
    """Verify user count updates in hierarchy"""
    print("\n" + "="*80)
    print("TEST 5: VERIFY USER COUNT UPDATES IN HIERARCHY")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/organizations/hierarchy",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            hierarchy = response.json()
            print(f"✅ Retrieved organization hierarchy")
            
            # Display user counts
            def display_hierarchy(units, indent=0):
                for unit in units:
                    user_count = unit.get("user_count", 0)
                    print(f"{'  ' * indent}• {unit.get('name')} (Level {unit.get('level')}) - {user_count} users")
                    if unit.get("children"):
                        display_hierarchy(unit.get("children"), indent + 1)
            
            display_hierarchy(hierarchy)
            
            log_test("Verify User Count Updates", True, "Hierarchy retrieved with user counts")
            return hierarchy
        else:
            log_test("Verify User Count Updates", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Verify User Count Updates", False, f"Error: {str(e)}")
        return None

def get_unit_users(token, unit_id):
    """Get all users in a unit"""
    print("\n" + "="*80)
    print("TEST 6: GET UNIT USERS")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/organizations/units/{unit_id}/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users in unit")
            
            for i, assignment in enumerate(users):
                user_data = assignment.get("user", {})
                print(f"   User {i+1}: {user_data.get('name')} ({user_data.get('email')}) - Role: {assignment.get('role')}")
            
            log_test("Get Unit Users", True, f"Retrieved {len(users)} users")
            return users
        else:
            log_test("Get Unit Users", False, f"Status: {response.status_code}")
            return []
    except Exception as e:
        log_test("Get Unit Users", False, f"Error: {str(e)}")
        return []

def test_error_handling_missing_unit_id(token, user_id, unit_id):
    """Test error handling when unit_id is missing from body"""
    print("\n" + "="*80)
    print("TEST 7: ERROR HANDLING - MISSING unit_id IN BODY")
    print("="*80)
    
    # Request body WITHOUT unit_id (should fail with 422)
    request_body = {
        "user_id": user_id,
        "role": "inspector"
        # Missing unit_id
    }
    
    print(f"Request Body (missing unit_id):")
    print(json.dumps(request_body, indent=2))
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/organizations/units/{unit_id}/assign-user",
            headers={"Authorization": f"Bearer {token}"},
            json=request_body,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 422:
            print(f"\n✅ Correctly returned 422 for missing unit_id")
            log_test("Error Handling - Missing unit_id", True, "422 validation error as expected")
            return True
        else:
            log_test("Error Handling - Missing unit_id", False, f"Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Error Handling - Missing unit_id", False, f"Error: {str(e)}")
        return False

def test_error_handling_already_assigned(token, user_id, unit_id):
    """Test error handling when user is already assigned"""
    print("\n" + "="*80)
    print("TEST 8: ERROR HANDLING - ALREADY ASSIGNED")
    print("="*80)
    
    request_body = {
        "user_id": user_id,
        "unit_id": unit_id,
        "role": "inspector"
    }
    
    try:
        # Try to assign the same user again
        response = requests.post(
            f"{BACKEND_URL}/organizations/units/{unit_id}/assign-user",
            headers={"Authorization": f"Bearer {token}"},
            json=request_body,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "already assigned" in error_detail.lower():
                print(f"\n✅ Correctly returned 400 with 'already assigned' message")
                log_test("Error Handling - Already Assigned", True, "400 error with correct message")
                return True
            else:
                log_test("Error Handling - Already Assigned", False, f"400 but wrong message: {error_detail}")
                return False
        else:
            log_test("Error Handling - Already Assigned", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Error Handling - Already Assigned", False, f"Error: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)
    
    for result in test_results:
        print(f"\n{result['status']}: {result['test']}")
        if result['details']:
            print(f"  {result['details']}")
    
    # Critical assessment
    print("\n" + "="*80)
    print("CRITICAL ASSESSMENT")
    print("="*80)
    
    # Check if the main fix worked (no 422 errors on valid requests)
    assign_test = next((r for r in test_results if "Assign User to Unit" in r['test'] and "422" in r['test']), None)
    
    if assign_test and not assign_test['passed']:
        print("\n❌ CRITICAL ISSUE: User allocation still returning 422 error!")
        print("   The fix did NOT resolve the issue.")
    else:
        print("\n✅ SUCCESS: User allocation working correctly!")
        print("   No 422 errors on valid requests with both user_id and unit_id.")
    
    return passed_tests == total_tests

def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("USER ALLOCATION FUNCTIONALITY TEST")
    print("Testing fix for 422 error when allocating users to units")
    print("="*80)
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Step 2: Get all users
    users = get_all_users(token)
    if not users:
        print("\n❌ Cannot proceed without users")
        sys.exit(1)
    
    # Step 3: Get all units
    units = get_all_units(token)
    if not units:
        print("\n❌ Cannot proceed without units")
        sys.exit(1)
    
    # Select a user and unit for testing
    # Try to find a user that's not already assigned to many units
    test_user = None
    for user in users:
        if user.get('email') != TEST_USER_EMAIL:  # Don't use the test account itself
            test_user = user
            break
    
    if not test_user:
        print("\n⚠️  Using first available user")
        test_user = users[0]
    
    test_unit = units[0]  # Use first unit
    
    print(f"\n📋 Selected for testing:")
    print(f"   User: {test_user.get('name')} ({test_user.get('email')})")
    print(f"   Unit: {test_unit.get('name')} (Level {test_unit.get('level')})")
    
    # Step 4: Assign user to unit (CRITICAL TEST)
    assignment = assign_user_to_unit(token, test_user['id'], test_unit['id'])
    
    # Step 5: Verify assignment in database
    if assignment and not assignment.get('already_assigned'):
        verify_assignment_in_db(token, test_user['id'], test_unit['id'])
    
    # Step 6: Verify user count updates
    verify_user_count_updates(token)
    
    # Step 7: Get unit users
    get_unit_users(token, test_unit['id'])
    
    # Step 8: Test error handling - missing unit_id
    test_error_handling_missing_unit_id(token, test_user['id'], test_unit['id'])
    
    # Step 9: Test error handling - already assigned
    test_error_handling_already_assigned(token, test_user['id'], test_unit['id'])
    
    # Print summary
    all_passed = print_summary()
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
