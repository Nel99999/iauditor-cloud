"""
COMPREHENSIVE PHASES 3-6 FINAL VALIDATION
Testing complete approval and invitation system with ALL bug fixes applied
"""
import requests
import json
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://auth-workflow-hub.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, passed, details=""):
        self.total += 1
        if passed:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        self.results.append(result)
        print(result)
    
    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        for result in self.results:
            print(result)
        print("="*80)
        print(f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/self.total*100):.1f}%")
        print("="*80)


def test_organization_creation_auto_approval():
    """Test 1: Organization Creation & Auto-Approval"""
    print("\n" + "="*80)
    print("TEST 1: ORGANIZATION CREATION & AUTO-APPROVAL")
    print("="*80)
    
    results = TestResults()
    
    # Create unique test user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"orgcreator.{timestamp}@example.com"
    test_org_name = f"TestOrg_{timestamp}"
    
    # Register with organization_name
    print(f"\n1.1 Registering user with organization_name: {test_org_name}")
    register_data = {
        "email": test_email,
        "name": "Org Creator",
        "password": "SecurePass123!",
        "organization_name": test_org_name
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            # Verify auto-approval
            approval_status = user.get("approval_status")
            is_active = user.get("is_active")
            role = user.get("role")
            
            results.add_result(
                "Registration successful",
                True,
                f"User created with email {test_email}"
            )
            
            results.add_result(
                "Auto-approved as Master",
                approval_status == "approved" and role == "master",
                f"approval_status={approval_status}, role={role}"
            )
            
            results.add_result(
                "User is active",
                is_active == True,
                f"is_active={is_active}"
            )
            
            results.add_result(
                "Access token received",
                token is not None and len(token) > 0,
                f"Token length: {len(token) if token else 0}"
            )
            
            # Test login immediately
            print(f"\n1.2 Testing immediate login for org creator")
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": test_email, "password": "SecurePass123!"}
            )
            
            results.add_result(
                "Org creator can login immediately",
                login_response.status_code == 200,
                f"Status: {login_response.status_code}"
            )
            
            return results, token, user
            
        else:
            results.add_result(
                "Registration failed",
                False,
                f"Status {response.status_code}: {response.text}"
            )
            return results, None, None
            
    except Exception as e:
        results.add_result("Registration exception", False, str(e))
        return results, None, None


def test_login_approval_checks(db_access_token):
    """Test 2: Login Approval Checks"""
    print("\n" + "="*80)
    print("TEST 2: LOGIN APPROVAL CHECKS")
    print("="*80)
    
    results = TestResults()
    
    # We need to manually create pending/rejected users via DB
    # Since we can't directly manipulate DB, we'll test the login behavior
    # by attempting to login with non-existent users (which should fail differently)
    
    print("\n2.1 Testing login with non-existent user (should get 401)")
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": "nonexistent@example.com", "password": "test123"}
        )
        
        results.add_result(
            "Non-existent user gets 401",
            response.status_code == 401,
            f"Status: {response.status_code}, Message: {response.json().get('detail', '')}"
        )
    except Exception as e:
        results.add_result("Login test exception", False, str(e))
    
    # Note: We cannot fully test pending/rejected users without DB manipulation
    # This would require creating users directly in MongoDB with those statuses
    print("\n⚠️  Note: Full pending/rejected user testing requires direct DB access")
    print("    The auth_routes.py code shows proper 403 handling for:")
    print("    - approval_status='pending' → 403 'pending admin approval'")
    print("    - approval_status='rejected' → 403 'not approved'")
    
    return results


def test_pending_approvals_endpoint(master_token, org_id):
    """Test 3: Pending Approvals Endpoint"""
    print("\n" + "="*80)
    print("TEST 3: PENDING APPROVALS ENDPOINT")
    print("="*80)
    
    results = TestResults()
    
    print("\n3.1 Master calls GET /api/users/pending-approvals")
    try:
        headers = {"Authorization": f"Bearer {master_token}"}
        response = requests.get(f"{BACKEND_URL}/users/pending-approvals", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            pending_users = response.json()
            results.add_result(
                "Pending approvals endpoint accessible",
                True,
                f"Found {len(pending_users)} pending users"
            )
            
            # Should be empty since org_name is required (no self-registrations)
            results.add_result(
                "No pending self-registrations",
                len(pending_users) == 0,
                "All registrations with org_name are auto-approved"
            )
        elif response.status_code == 403:
            results.add_result(
                "Permission check working",
                False,
                f"Master should have access: {response.json().get('detail', '')}"
            )
        else:
            results.add_result(
                "Unexpected response",
                False,
                f"Status {response.status_code}: {response.text}"
            )
            
    except Exception as e:
        results.add_result("Pending approvals test exception", False, str(e))
    
    return results


def test_approval_endpoints(master_token):
    """Test 4: Approval Endpoints"""
    print("\n" + "="*80)
    print("TEST 4: APPROVAL ENDPOINTS")
    print("="*80)
    
    results = TestResults()
    
    # Test approve endpoint with non-existent user
    print("\n4.1 Testing approve endpoint with invalid user_id")
    try:
        headers = {"Authorization": f"Bearer {master_token}"}
        response = requests.post(
            f"{BACKEND_URL}/users/invalid-user-id/approve",
            headers=headers,
            json={"approval_notes": "Test approval"}
        )
        
        results.add_result(
            "Approve endpoint accessible",
            response.status_code in [404, 403],
            f"Status: {response.status_code}"
        )
    except Exception as e:
        results.add_result("Approve endpoint test exception", False, str(e))
    
    # Test reject endpoint with non-existent user
    print("\n4.2 Testing reject endpoint with invalid user_id")
    try:
        headers = {"Authorization": f"Bearer {master_token}"}
        response = requests.post(
            f"{BACKEND_URL}/users/invalid-user-id/reject",
            headers=headers,
            json={"approval_notes": "Test rejection"}
        )
        
        results.add_result(
            "Reject endpoint accessible",
            response.status_code in [404, 403],
            f"Status: {response.status_code}"
        )
    except Exception as e:
        results.add_result("Reject endpoint test exception", False, str(e))
    
    print("\n⚠️  Note: Full approval/rejection testing requires pending users")
    print("    Since all registrations with org_name are auto-approved,")
    print("    we cannot create pending users to test approval workflow")
    
    return results


def test_invitation_system():
    """Test 5: Invitation System"""
    print("\n" + "="*80)
    print("TEST 5: INVITATION SYSTEM")
    print("="*80)
    
    results = TestResults()
    
    # First create a Master user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    master_email = f"inviter.{timestamp}@example.com"
    master_org = f"InviteOrg_{timestamp}"
    
    print(f"\n5.1 Creating Master user: {master_email}")
    register_data = {
        "email": master_email,
        "name": "Master Inviter",
        "password": "SecurePass123!",
        "organization_name": master_org
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            results.add_result("Master user creation failed", False, response.text)
            return results
        
        master_token = response.json().get("access_token")
        master_user = response.json().get("user", {})
        org_id = master_user.get("organization_id")
        
        results.add_result("Master user created", True, f"Org: {master_org}")
        
        # Get roles to find a role to invite
        print(f"\n5.2 Getting roles for invitation")
        headers = {"Authorization": f"Bearer {master_token}"}
        roles_response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
        
        if roles_response.status_code == 200:
            roles = roles_response.json()
            # Find viewer role
            viewer_role = next((r for r in roles if r.get("code") == "viewer"), None)
            
            if viewer_role:
                role_id = viewer_role.get("id")
                results.add_result("Found viewer role", True, f"Role ID: {role_id}")
                
                # Send invitation
                print(f"\n5.3 Sending invitation")
                invite_email = f"invited.{timestamp}@example.com"
                invite_data = {
                    "email": invite_email,
                    "role_id": role_id,
                    "scope_type": "organization",
                    "scope_id": org_id
                }
                
                invite_response = requests.post(
                    f"{BACKEND_URL}/invitations",
                    headers=headers,
                    json=invite_data
                )
                
                if invite_response.status_code == 201:
                    invitation = invite_response.json().get("invitation", {})
                    token = invitation.get("token")
                    
                    results.add_result(
                        "Invitation sent successfully",
                        True,
                        f"Token: {token[:20]}..."
                    )
                    
                    # Validate token
                    print(f"\n5.4 Validating invitation token")
                    validate_response = requests.get(
                        f"{BACKEND_URL}/invitations/token/{token}"
                    )
                    
                    results.add_result(
                        "Invitation token valid",
                        validate_response.status_code == 200,
                        f"Status: {validate_response.status_code}"
                    )
                    
                    # Accept invitation
                    print(f"\n5.5 Accepting invitation")
                    accept_data = {
                        "token": token,
                        "name": "Invited User",
                        "password": "InvitedPass123!"
                    }
                    
                    accept_response = requests.post(
                        f"{BACKEND_URL}/invitations/accept",
                        json=accept_data
                    )
                    
                    if accept_response.status_code == 200:
                        accept_data = accept_response.json()
                        invited_user = accept_data.get("user", {})
                        invited_token = accept_data.get("access_token")
                        
                        results.add_result(
                            "Invitation accepted",
                            True,
                            f"User created: {invited_user.get('email')}"
                        )
                        
                        # Verify invited user properties
                        approval_status = invited_user.get("approval_status")
                        is_invited = invited_user.get("invited")
                        user_role = invited_user.get("role")
                        
                        results.add_result(
                            "Invited user auto-approved",
                            approval_status == "approved",
                            f"approval_status={approval_status}"
                        )
                        
                        results.add_result(
                            "Invited flag set",
                            is_invited == True,
                            f"invited={is_invited}"
                        )
                        
                        results.add_result(
                            "Role stored as CODE",
                            user_role == "viewer",
                            f"role={user_role}"
                        )
                        
                        # Test immediate login
                        print(f"\n5.6 Testing immediate login for invited user")
                        login_response = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"email": invite_email, "password": "InvitedPass123!"}
                        )
                        
                        results.add_result(
                            "Invited user can login immediately",
                            login_response.status_code == 200,
                            f"Status: {login_response.status_code}"
                        )
                        
                    else:
                        results.add_result(
                            "Invitation acceptance failed",
                            False,
                            f"Status {accept_response.status_code}: {accept_response.text}"
                        )
                else:
                    results.add_result(
                        "Invitation sending failed",
                        False,
                        f"Status {invite_response.status_code}: {invite_response.text}"
                    )
            else:
                results.add_result("Viewer role not found", False, "Cannot test invitation")
        else:
            results.add_result("Failed to get roles", False, f"Status: {roles_response.status_code}")
            
    except Exception as e:
        results.add_result("Invitation system test exception", False, str(e))
    
    return results


def test_invitation_permissions():
    """Test 6: Invitation Permissions"""
    print("\n" + "="*80)
    print("TEST 6: INVITATION PERMISSIONS")
    print("="*80)
    
    results = TestResults()
    
    # Create Master user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    master_email = f"master.{timestamp}@example.com"
    master_org = f"PermOrg_{timestamp}"
    
    print(f"\n6.1 Creating Master user")
    register_data = {
        "email": master_email,
        "name": "Master User",
        "password": "SecurePass123!",
        "organization_name": master_org
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            results.add_result("Master creation failed", False, response.text)
            return results
        
        master_token = response.json().get("access_token")
        master_user = response.json().get("user", {})
        org_id = master_user.get("organization_id")
        
        # Get roles
        headers = {"Authorization": f"Bearer {master_token}"}
        roles_response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
        
        if roles_response.status_code != 200:
            results.add_result("Failed to get roles", False, f"Status: {roles_response.status_code}")
            return results
        
        roles = roles_response.json()
        viewer_role = next((r for r in roles if r.get("code") == "viewer"), None)
        admin_role = next((r for r in roles if r.get("code") == "admin"), None)
        
        if not viewer_role or not admin_role:
            results.add_result("Required roles not found", False, "Need viewer and admin roles")
            return results
        
        # Create Viewer via invitation
        print(f"\n6.2 Creating Viewer user via invitation")
        viewer_email = f"viewer.{timestamp}@example.com"
        invite_data = {
            "email": viewer_email,
            "role_id": viewer_role.get("id"),
            "scope_type": "organization",
            "scope_id": org_id
        }
        
        invite_response = requests.post(
            f"{BACKEND_URL}/invitations",
            headers=headers,
            json=invite_data
        )
        
        if invite_response.status_code == 201:
            token = invite_response.json().get("invitation", {}).get("token")
            
            # Accept as viewer
            accept_response = requests.post(
                f"{BACKEND_URL}/invitations/accept",
                json={
                    "token": token,
                    "name": "Viewer User",
                    "password": "ViewerPass123!"
                }
            )
            
            if accept_response.status_code == 200:
                viewer_token = accept_response.json().get("access_token")
                results.add_result("Viewer user created", True, viewer_email)
                
                # Viewer tries to invite someone
                print(f"\n6.3 Viewer tries to invite someone (should fail)")
                viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
                viewer_invite_data = {
                    "email": f"test.{timestamp}@example.com",
                    "role_id": viewer_role.get("id"),
                    "scope_type": "organization",
                    "scope_id": org_id
                }
                
                viewer_invite_response = requests.post(
                    f"{BACKEND_URL}/invitations",
                    headers=viewer_headers,
                    json=viewer_invite_data
                )
                
                results.add_result(
                    "Viewer cannot invite (permission check)",
                    viewer_invite_response.status_code == 403,
                    f"Status: {viewer_invite_response.status_code}, Message: {viewer_invite_response.json().get('detail', '')}"
                )
            else:
                results.add_result("Viewer acceptance failed", False, accept_response.text)
        else:
            results.add_result("Viewer invitation failed", False, invite_response.text)
        
        # Create Admin via invitation
        print(f"\n6.4 Creating Admin user via invitation")
        admin_email = f"admin.{timestamp}@example.com"
        admin_invite_data = {
            "email": admin_email,
            "role_id": admin_role.get("id"),
            "scope_type": "organization",
            "scope_id": org_id
        }
        
        admin_invite_response = requests.post(
            f"{BACKEND_URL}/invitations",
            headers=headers,
            json=admin_invite_data
        )
        
        if admin_invite_response.status_code == 201:
            admin_token_inv = admin_invite_response.json().get("invitation", {}).get("token")
            
            # Accept as admin
            admin_accept_response = requests.post(
                f"{BACKEND_URL}/invitations/accept",
                json={
                    "token": admin_token_inv,
                    "name": "Admin User",
                    "password": "AdminPass123!"
                }
            )
            
            if admin_accept_response.status_code == 200:
                admin_token = admin_accept_response.json().get("access_token")
                results.add_result("Admin user created", True, admin_email)
                
                # Admin invites Viewer (should succeed)
                print(f"\n6.5 Admin invites Viewer (should succeed)")
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                admin_viewer_invite = {
                    "email": f"adminviewer.{timestamp}@example.com",
                    "role_id": viewer_role.get("id"),
                    "scope_type": "organization",
                    "scope_id": org_id
                }
                
                admin_viewer_response = requests.post(
                    f"{BACKEND_URL}/invitations",
                    headers=admin_headers,
                    json=admin_viewer_invite
                )
                
                results.add_result(
                    "Admin can invite Viewer",
                    admin_viewer_response.status_code == 201,
                    f"Status: {admin_viewer_response.status_code}"
                )
                
                # Admin tries to invite Master (should fail - hierarchy violation)
                print(f"\n6.6 Admin tries to invite Master (should fail)")
                master_role = next((r for r in roles if r.get("code") == "master"), None)
                if master_role:
                    admin_master_invite = {
                        "email": f"adminmaster.{timestamp}@example.com",
                        "role_id": master_role.get("id"),
                        "scope_type": "organization",
                        "scope_id": org_id
                    }
                    
                    admin_master_response = requests.post(
                        f"{BACKEND_URL}/invitations",
                        headers=admin_headers,
                        json=admin_master_invite
                    )
                    
                    results.add_result(
                        "Admin cannot invite Master (hierarchy check)",
                        admin_master_response.status_code == 403,
                        f"Status: {admin_master_response.status_code}"
                    )
                else:
                    results.add_result("Master role not found", False, "Cannot test hierarchy")
            else:
                results.add_result("Admin acceptance failed", False, admin_accept_response.text)
        else:
            results.add_result("Admin invitation failed", False, admin_invite_response.text)
            
    except Exception as e:
        results.add_result("Invitation permissions test exception", False, str(e))
    
    return results


def test_role_hierarchy_new_org():
    """Test 7: Role Hierarchy in New Organizations"""
    print("\n" + "="*80)
    print("TEST 7: ROLE HIERARCHY IN NEW ORGANIZATIONS")
    print("="*80)
    
    results = TestResults()
    
    # Create new organization
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"neworgrole.{timestamp}@example.com"
    test_org = f"NewRoleOrg_{timestamp}"
    
    print(f"\n7.1 Creating new organization: {test_org}")
    register_data = {
        "email": test_email,
        "name": "New Org Admin",
        "password": "SecurePass123!",
        "organization_name": test_org
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            results.add_result("New org creation failed", False, response.text)
            return results
        
        token = response.json().get("access_token")
        user = response.json().get("user", {})
        org_id = user.get("organization_id")
        
        results.add_result("New organization created", True, f"Org ID: {org_id}")
        
        # Check roles are initialized
        print(f"\n7.2 Checking roles initialized for new org")
        headers = {"Authorization": f"Bearer {token}"}
        roles_response = requests.get(f"{BACKEND_URL}/roles", headers=headers)
        
        if roles_response.status_code == 200:
            roles = roles_response.json()
            org_roles = [r for r in roles if r.get("organization_id") == org_id]
            
            results.add_result(
                "Roles initialized for new org",
                len(org_roles) > 0,
                f"Found {len(org_roles)} roles"
            )
            
            # Check Admin role has user.invite permission
            admin_role = next((r for r in org_roles if r.get("code") == "admin"), None)
            if admin_role:
                admin_role_id = admin_role.get("id")
                results.add_result("Admin role found", True, f"Role ID: {admin_role_id}")
                
                # Get permissions for admin role
                print(f"\n7.3 Checking Admin role permissions")
                perms_response = requests.get(
                    f"{BACKEND_URL}/permissions/roles/{admin_role_id}",
                    headers=headers
                )
                
                if perms_response.status_code == 200:
                    permissions = perms_response.json()
                    
                    # Check for user.invite permission
                    invite_perm = next(
                        (p for p in permissions if 
                         p.get("resource_type") == "user" and 
                         p.get("action") == "invite"),
                        None
                    )
                    
                    results.add_result(
                        "Admin has user.invite permission",
                        invite_perm is not None,
                        f"Found: {invite_perm is not None}"
                    )
                    
                    # Check for approval permissions
                    approve_perm = next(
                        (p for p in permissions if 
                         p.get("resource_type") == "user" and 
                         p.get("action") == "approve"),
                        None
                    )
                    
                    reject_perm = next(
                        (p for p in permissions if 
                         p.get("resource_type") == "user" and 
                         p.get("action") == "reject"),
                        None
                    )
                    
                    results.add_result(
                        "Admin has user.approve permission",
                        approve_perm is not None,
                        f"Found: {approve_perm is not None}"
                    )
                    
                    results.add_result(
                        "Admin has user.reject permission",
                        reject_perm is not None,
                        f"Found: {reject_perm is not None}"
                    )
                else:
                    results.add_result(
                        "Failed to get admin permissions",
                        False,
                        f"Status: {perms_response.status_code}"
                    )
            else:
                results.add_result("Admin role not found", False, "Cannot check permissions")
        else:
            results.add_result(
                "Failed to get roles",
                False,
                f"Status: {roles_response.status_code}"
            )
            
    except Exception as e:
        results.add_result("Role hierarchy test exception", False, str(e))
    
    return results


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE PHASES 3-6 FINAL VALIDATION")
    print("Testing complete approval and invitation system")
    print("="*80)
    
    all_results = []
    
    # Test 1: Organization Creation & Auto-Approval
    test1_results, master_token, master_user = test_organization_creation_auto_approval()
    all_results.append(("Test 1: Organization Creation & Auto-Approval", test1_results))
    
    # Test 2: Login Approval Checks
    if master_token:
        test2_results = test_login_approval_checks(master_token)
        all_results.append(("Test 2: Login Approval Checks", test2_results))
    
    # Test 3: Pending Approvals Endpoint
    if master_token and master_user:
        org_id = master_user.get("organization_id")
        test3_results = test_pending_approvals_endpoint(master_token, org_id)
        all_results.append(("Test 3: Pending Approvals Endpoint", test3_results))
    
    # Test 4: Approval Endpoints
    if master_token:
        test4_results = test_approval_endpoints(master_token)
        all_results.append(("Test 4: Approval Endpoints", test4_results))
    
    # Test 5: Invitation System
    test5_results = test_invitation_system()
    all_results.append(("Test 5: Invitation System", test5_results))
    
    # Test 6: Invitation Permissions
    test6_results = test_invitation_permissions()
    all_results.append(("Test 6: Invitation Permissions", test6_results))
    
    # Test 7: Role Hierarchy in New Organizations
    test7_results = test_role_hierarchy_new_org()
    all_results.append(("Test 7: Role Hierarchy in New Organizations", test7_results))
    
    # Print final summary
    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE SUMMARY")
    print("="*80)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for test_name, results in all_results:
        print(f"\n{test_name}:")
        print(f"  Passed: {results.passed}/{results.total}")
        total_tests += results.total
        total_passed += results.passed
        total_failed += results.failed
    
    print("\n" + "="*80)
    print(f"OVERALL RESULTS")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    print("="*80)
    
    # Detailed results
    print("\n" + "="*80)
    print("DETAILED TEST RESULTS")
    print("="*80)
    for test_name, results in all_results:
        print(f"\n{test_name}:")
        for result in results.results:
            print(f"  {result}")


if __name__ == "__main__":
    main()
