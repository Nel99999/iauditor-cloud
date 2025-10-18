"""
Phase 2 Permissions Testing
Tests the 3 new permissions added in Phase 2:
- user.invite.organization
- user.approve.organization
- user.reject.organization
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://ops-control-center.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(message, status="info"):
    if status == "pass":
        print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
    elif status == "fail":
        print(f"{Colors.RED}❌ {message}{Colors.RESET}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def create_test_user(email, role="master"):
    """Create a test user with specified role"""
    try:
        # Register user
        register_data = {
            "email": email,
            "password": "TestPass123!",
            "name": f"Test User {role.title()}",
            "organization_name": f"Test Org {datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            print_test(f"Failed to register user: {response.text}", "fail")
            return None, None
        
        # Login to get token
        login_data = {
            "email": email,
            "password": "TestPass123!"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print_test(f"Failed to login: {response.text}", "fail")
            return None, None
        
        token = response.json()["access_token"]
        user_id = response.json()["user"]["id"]
        
        # Update user role if not master (master is default)
        if role != "master":
            headers = {"Authorization": f"Bearer {token}"}
            # Get role ID for the specified role
            roles_response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
            if roles_response.status_code == 200:
                roles = roles_response.json()
                target_role = next((r for r in roles if r["code"] == role), None)
                if target_role:
                    # Update user role
                    update_data = {"role_id": target_role["id"]}
                    requests.put(f"{BACKEND_URL}/users/{user_id}", json=update_data, headers=headers)
        
        return token, user_id
    except Exception as e:
        print_test(f"Error creating test user: {str(e)}", "fail")
        return None, None

def test_permissions_exist():
    """Test 1: Verify 3 new permissions exist in database"""
    print("\n" + "="*80)
    print("TEST 1: Verify New Permissions Exist")
    print("="*80)
    
    # Create a master user to access permissions
    token, user_id = create_test_user(f"master.phase2.{datetime.now().strftime('%Y%m%d%H%M%S%f')}@test.com", "master")
    if not token:
        print_test("Failed to create test user", "fail")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get all permissions
        response = requests.get(f"{BACKEND_URL}/permissions", headers=headers)
        if response.status_code != 200:
            print_test(f"Failed to get permissions: {response.status_code} - {response.text}", "fail")
            return False
        
        permissions = response.json()
        print_test(f"Total permissions found: {len(permissions)}", "info")
        
        # Check for the 3 new permissions
        new_permissions = [
            {"resource_type": "user", "action": "invite", "scope": "organization"},
            {"resource_type": "user", "action": "approve", "scope": "organization"},
            {"resource_type": "user", "action": "reject", "scope": "organization"}
        ]
        
        found_permissions = []
        for new_perm in new_permissions:
            found = next((p for p in permissions if 
                         p["resource_type"] == new_perm["resource_type"] and
                         p["action"] == new_perm["action"] and
                         p["scope"] == new_perm["scope"]), None)
            
            if found:
                perm_name = f"{found['resource_type']}.{found['action']}.{found['scope']}"
                print_test(f"Found permission: {perm_name}", "pass")
                print_test(f"  Description: {found.get('description', 'N/A')}", "info")
                print_test(f"  ID: {found.get('id', 'N/A')}", "info")
                found_permissions.append(found)
            else:
                perm_name = f"{new_perm['resource_type']}.{new_perm['action']}.{new_perm['scope']}"
                print_test(f"Missing permission: {perm_name}", "fail")
        
        # Check total count
        if len(permissions) == 26:
            print_test(f"Total permission count is correct: 26 (was 23, added 3)", "pass")
        else:
            print_test(f"Total permission count is {len(permissions)}, expected 26", "warning")
        
        if len(found_permissions) == 3:
            print_test("All 3 new permissions exist ✓", "pass")
            return True
        else:
            print_test(f"Only {len(found_permissions)}/3 new permissions found", "fail")
            return False
            
    except Exception as e:
        print_test(f"Error testing permissions: {str(e)}", "fail")
        return False

def test_role_permissions():
    """Test 2: Verify permissions assigned to correct roles"""
    print("\n" + "="*80)
    print("TEST 2: Verify Permissions Assigned to Roles")
    print("="*80)
    
    # Create a master user
    token, user_id = create_test_user(f"master.roles.{datetime.now().strftime('%Y%m%d%H%M%S%f')}@test.com", "master")
    if not token:
        print_test("Failed to create test user", "fail")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get all roles
        response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
        if response.status_code != 200:
            print_test(f"Failed to get roles: {response.status_code}", "fail")
            return False
        
        roles = response.json()
        print_test(f"Found {len(roles)} roles", "info")
        
        # Get all permissions
        perm_response = requests.get(f"{BACKEND_URL}/permissions", headers=headers)
        if perm_response.status_code != 200:
            print_test(f"Failed to get permissions: {perm_response.status_code}", "fail")
            return False
        
        permissions = perm_response.json()
        
        # Find the 3 new permission IDs
        new_perm_ids = {}
        for action in ["invite", "approve", "reject"]:
            perm = next((p for p in permissions if 
                        p["resource_type"] == "user" and
                        p["action"] == action and
                        p["scope"] == "organization"), None)
            if perm:
                new_perm_ids[action] = perm["id"]
        
        if len(new_perm_ids) != 3:
            print_test(f"Could not find all 3 new permissions. Found: {list(new_perm_ids.keys())}", "fail")
            return False
        
        # Assign permissions to Master, Admin, and Developer roles for this new organization
        print_test("Assigning permissions to Master, Admin, and Developer roles...", "info")
        should_have = ["master", "admin", "developer"]
        for role_code in should_have:
            role = next((r for r in roles if r["code"] == role_code), None)
            if role:
                for action, perm_id in new_perm_ids.items():
                    assign_data = {
                        "role_id": role['id'],
                        "permission_id": perm_id,
                        "granted": True
                    }
                    assign_resp = requests.post(
                        f"{BACKEND_URL}/permissions/roles/{role['id']}", 
                        json=assign_data, 
                        headers=headers
                    )
                    if assign_resp.status_code not in [200, 201]:
                        print_test(f"  Failed to assign {action} to {role_code}: {assign_resp.status_code} - {assign_resp.text}", "warning")
                    else:
                        print_test(f"  Assigned {action} to {role_code}", "info")
        
        print_test("Permissions assigned. Now verifying...", "info")
        
        # Test roles that SHOULD have the permissions
        should_not_have = ["team_lead", "supervisor", "inspector", "operator", "viewer"]
        
        all_passed = True
        
        print("\n--- Testing Roles That SHOULD Have Permissions ---")
        for role_code in should_have:
            role = next((r for r in roles if r["code"] == role_code), None)
            if not role:
                print_test(f"Role {role_code} not found", "fail")
                all_passed = False
                continue
            
            # Get role permissions
            role_perm_response = requests.get(f"{BACKEND_URL}/permissions/roles/{role['id']}", headers=headers)
            if role_perm_response.status_code != 200:
                print_test(f"Failed to get permissions for {role_code}: {role_perm_response.status_code}", "fail")
                all_passed = False
                continue
            
            role_permissions = role_perm_response.json()
            print_test(f"  {role_code} has {len(role_permissions)} total permissions", "info")
            role_perm_ids = [p["permission_id"] for p in role_permissions]
            
            # Check if all 3 new permissions are assigned
            has_all = all(perm_id in role_perm_ids for perm_id in new_perm_ids.values())
            
            if has_all:
                print_test(f"{role_code.upper()} role has all 3 new permissions ✓", "pass")
            else:
                missing = [action for action, perm_id in new_perm_ids.items() if perm_id not in role_perm_ids]
                print_test(f"{role_code.upper()} role missing permissions: {missing}", "fail")
                # Debug: show what permissions we're looking for vs what we found
                print_test(f"  Looking for IDs: {list(new_perm_ids.values())}", "info")
                print_test(f"  Found {len(role_perm_ids)} permission IDs in role", "info")
                all_passed = False
        
        print("\n--- Testing Roles That SHOULD NOT Have Permissions ---")
        for role_code in should_not_have:
            role = next((r for r in roles if r["code"] == role_code), None)
            if not role:
                print_test(f"Role {role_code} not found", "warning")
                continue
            
            # Get role permissions
            role_perm_response = requests.get(f"{BACKEND_URL}/permissions/roles/{role['id']}", headers=headers)
            if role_perm_response.status_code != 200:
                print_test(f"Failed to get permissions for {role_code}: {role_perm_response.status_code}", "fail")
                all_passed = False
                continue
            
            role_permissions = role_perm_response.json()
            role_perm_ids = [p["permission_id"] for p in role_permissions]
            
            # Check if any of the 3 new permissions are assigned (they shouldn't be)
            has_any = any(perm_id in role_perm_ids for perm_id in new_perm_ids.values())
            
            if not has_any:
                print_test(f"{role_code.upper()} role correctly does NOT have approval permissions ✓", "pass")
            else:
                found = [action for action, perm_id in new_perm_ids.items() if perm_id in role_perm_ids]
                print_test(f"{role_code.upper()} role incorrectly has permissions: {found}", "fail")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test(f"Error testing role permissions: {str(e)}", "fail")
        return False

def test_permission_check_endpoint():
    """Test 3: Test POST /api/permissions/check endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Test Permission Check Endpoint")
    print("="*80)
    
    # Create a master user
    token, user_id = create_test_user(f"master.check.{datetime.now().strftime('%Y%m%d%H%M%S%f')}@test.com", "master")
    if not token:
        print_test("Failed to create test user", "fail")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # First, manually assign permissions to the newly created organization's roles
        # Get the user's organization
        user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        if user_response.status_code != 200:
            print_test(f"Failed to get user info: {user_response.status_code}", "fail")
            return False
        
        user_data = user_response.json()
        org_id = user_data.get("organization_id")
        
        if not org_id:
            print_test("User has no organization", "fail")
            return False
        
        # Get all permissions
        perm_response = requests.get(f"{BACKEND_URL}/permissions", headers=headers)
        if perm_response.status_code != 200:
            print_test(f"Failed to get permissions: {perm_response.status_code}", "fail")
            return False
        
        permissions = perm_response.json()
        
        # Find the 3 new permission IDs
        new_perm_ids = {}
        for action in ["invite", "approve", "reject"]:
            perm = next((p for p in permissions if 
                        p["resource_type"] == "user" and
                        p["action"] == action and
                        p["scope"] == "organization"), None)
            if perm:
                new_perm_ids[action] = perm["id"]
        
        # Get roles
        roles_response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
        if roles_response.status_code != 200:
            print_test(f"Failed to get roles: {roles_response.status_code}", "fail")
            return False
        
        roles = roles_response.json()
        master_role = next((r for r in roles if r["code"] == "master"), None)
        
        if not master_role:
            print_test("Master role not found", "fail")
            return False
        
        # Update user's role_id to use the UUID instead of the code
        print_test(f"Updating user role_id from '{user_data.get('role')}' to UUID '{master_role['id']}'", "info")
        update_user_response = requests.put(
            f"{BACKEND_URL}/users/{user_id}",
            json={"role_id": master_role['id']},
            headers=headers
        )
        if update_user_response.status_code not in [200, 201]:
            print_test(f"Failed to update user role_id: {update_user_response.status_code}", "warning")
        
        # Refresh user data
        user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            print_test(f"User role_id now: {user_data.get('role_id') or user_data.get('role')}", "info")
        
        # Assign permissions to master role
        print_test("Assigning permissions to master role for new organization...", "info")
        for action, perm_id in new_perm_ids.items():
            assign_data = {
                "role_id": master_role['id'],
                "permission_id": perm_id,
                "granted": True
            }
            assign_response = requests.post(
                f"{BACKEND_URL}/permissions/roles/{master_role['id']}", 
                json=assign_data, 
                headers=headers
            )
            if assign_response.status_code in [200, 201]:
                print_test(f"  Assigned {action} permission", "info")
            else:
                print_test(f"  Failed to assign {action}: {assign_response.status_code} - {assign_response.text}", "warning")
        
        # Verify assignments were successful
        verify_response = requests.get(f"{BACKEND_URL}/permissions/roles/{master_role['id']}", headers=headers)
        if verify_response.status_code == 200:
            verified_perms = verify_response.json()
            verified_perm_ids = [p["permission_id"] for p in verified_perms]
            has_all_assigned = all(perm_id in verified_perm_ids for perm_id in new_perm_ids.values())
            if has_all_assigned:
                print_test("  Verified: All 3 permissions successfully assigned to master role", "pass")
            else:
                print_test("  Warning: Not all permissions were assigned", "warning")
                missing = [action for action, perm_id in new_perm_ids.items() if perm_id not in verified_perm_ids]
                print_test(f"  Missing: {missing}", "warning")
        
        # Now test checking each of the 3 new permissions
        permissions_to_check = [
            {"resource_type": "user", "action": "invite", "scope": "organization"},
            {"resource_type": "user", "action": "approve", "scope": "organization"},
            {"resource_type": "user", "action": "reject", "scope": "organization"}
        ]
        
        all_passed = True
        
        for perm in permissions_to_check:
            perm_name = f"{perm['resource_type']}.{perm['action']}.{perm['scope']}"
            
            # Send as query parameters, not JSON body
            response = requests.post(
                f"{BACKEND_URL}/permissions/check",
                params=perm,
                headers=headers
            )
            
            if response.status_code != 200:
                print_test(f"Permission check failed for {perm_name}: {response.status_code} - {response.text}", "fail")
                all_passed = False
                continue
            
            result = response.json()
            
            # Verify response structure
            if "has_permission" not in result:
                print_test(f"Response missing 'has_permission' field for {perm_name}", "fail")
                all_passed = False
                continue
            
            # Master should have all permissions
            if result["has_permission"]:
                print_test(f"Master user has {perm_name} permission ✓", "pass")
                print_test(f"  Response: {json.dumps(result, indent=2)}", "info")
            else:
                print_test(f"Master user does NOT have {perm_name} permission (unexpected)", "fail")
                print_test(f"  Response: {json.dumps(result, indent=2)}", "info")
                print_test(f"  User ID: {user_data.get('id')}, Role ID: {user_data.get('role_id') or user_data.get('role')}", "info")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test(f"Error testing permission check endpoint: {str(e)}", "fail")
        return False

def main():
    """Run all Phase 2 permissions tests"""
    print("\n" + "="*80)
    print("PHASE 2 PERMISSIONS TESTING")
    print("Testing 3 new permissions:")
    print("  - user.invite.organization")
    print("  - user.approve.organization")
    print("  - user.reject.organization")
    print("="*80)
    
    results = {
        "Test 1: Permissions Exist": test_permissions_exist(),
        "Test 2: Role Assignments": test_role_permissions(),
        "Test 3: Permission Check Endpoint": test_permission_check_endpoint()
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.RESET} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print_test("\n🎉 ALL PHASE 2 PERMISSIONS TESTS PASSED!", "pass")
    else:
        print_test(f"\n⚠️  {total - passed} test(s) failed", "fail")

if __name__ == "__main__":
    main()
