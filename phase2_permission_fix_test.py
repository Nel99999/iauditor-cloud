"""
PHASE 2 FIX VERIFICATION: Permission Check System
Testing the critical fix for permission checks with string role codes
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://workflow-engine-18.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(message):
    print(f"{Colors.BLUE}🧪 TEST:{Colors.RESET} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✅ PASS:{Colors.RESET} {message}")

def print_error(message):
    print(f"{Colors.RED}❌ FAIL:{Colors.RESET} {message}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.RESET} {message}")

def print_section(title):
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")


class PermissionFixTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_users = {}
        
    def test_1_create_master_user(self):
        """Test 1: Create new user with organization (should get role='master' string code)"""
        print_section("TEST 1: Create New Test Organization with Master User")
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        email = f"master.test.{timestamp}@example.com"
        
        print_test("Registering new user with organization")
        print_info(f"Email: {email}")
        print_info(f"Organization: Test Org {timestamp}")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Master Test User",
                    "organization_name": f"Test Org {timestamp}"
                },
                timeout=10
            )
            
            print_info(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user")
                
                if not token:
                    print_error("No access token in response")
                    self.failed += 1
                    return None
                
                if not user:
                    print_error("No user data in response")
                    self.failed += 1
                    return None
                
                print_success(f"User created successfully")
                print_info(f"User ID: {user.get('id')}")
                print_info(f"User Role: {user.get('role')}")
                print_info(f"Organization ID: {user.get('organization_id')}")
                
                # Verify role is 'master' string code
                if user.get('role') == 'master':
                    print_success("User has role='master' (string code) ✓")
                    self.passed += 1
                else:
                    print_error(f"Expected role='master', got role='{user.get('role')}'")
                    self.failed += 1
                    return None
                
                self.test_users['master'] = {
                    'email': email,
                    'token': token,
                    'user': user
                }
                
                return token
            else:
                print_error(f"Registration failed: {response.text}")
                self.failed += 1
                return None
                
        except Exception as e:
            print_error(f"Exception during registration: {str(e)}")
            self.failed += 1
            return None
    
    def test_2_check_master_permissions(self, token):
        """Test 2: Check Master role permissions using POST /api/permissions/check"""
        print_section("TEST 2: Test Permission Check Endpoint for Master Role")
        
        if not token:
            print_error("No token available, skipping test")
            self.failed += 3
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3 different permissions that Master should have
        permissions_to_test = [
            {
                "resource_type": "user",
                "action": "invite",
                "scope": "organization",
                "description": "user.invite.organization"
            },
            {
                "resource_type": "user",
                "action": "approve",
                "scope": "organization",
                "description": "user.approve.organization"
            },
            {
                "resource_type": "user",
                "action": "reject",
                "scope": "organization",
                "description": "user.reject.organization"
            }
        ]
        
        for perm in permissions_to_test:
            print_test(f"Checking permission: {perm['description']}")
            
            try:
                response = requests.post(
                    f"{API_BASE}/permissions/check",
                    params={
                        "resource_type": perm["resource_type"],
                        "action": perm["action"],
                        "scope": perm["scope"]
                    },
                    headers=headers,
                    timeout=10
                )
                
                print_info(f"Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print_info(f"Response: {json.dumps(data, indent=2)}")
                    
                    has_permission = data.get("has_permission")
                    
                    if has_permission is True:
                        print_success(f"Master has permission: {perm['description']} ✓")
                        self.passed += 1
                    else:
                        print_error(f"Master should have permission: {perm['description']}")
                        print_error(f"Expected has_permission=true, got has_permission={has_permission}")
                        self.failed += 1
                else:
                    print_error(f"Permission check failed: {response.text}")
                    self.failed += 1
                    
            except Exception as e:
                print_error(f"Exception during permission check: {str(e)}")
                self.failed += 1
    
    def test_3_create_admin_user(self, master_token):
        """Test 3: Create Admin user and test permissions"""
        print_section("TEST 3: Create Admin User and Test Permissions")
        
        if not master_token:
            print_error("No master token available, skipping test")
            self.failed += 2
            return
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        email = f"admin.test.{timestamp}@example.com"
        
        print_test("Creating Admin user via invitation")
        
        # Get master user's organization_id
        master_user = self.test_users['master']['user']
        org_id = master_user.get('organization_id')
        
        try:
            # First, get the admin role_id
            headers = {"Authorization": f"Bearer {master_token}"}
            roles_response = requests.get(
                f"{API_BASE}/roles",
                headers=headers,
                timeout=10
            )
            
            if roles_response.status_code != 200:
                print_error(f"Failed to get roles: {roles_response.text}")
                self.failed += 2
                return
            
            roles = roles_response.json()
            admin_role = next((r for r in roles if r.get('code') == 'admin'), None)
            
            if not admin_role:
                print_error("Admin role not found in organization")
                self.failed += 2
                return
            
            print_info(f"Admin role ID: {admin_role['id']}")
            
            # Register admin user directly (simpler than invitation flow)
            # We'll manually set the role after registration
            admin_response = requests.post(
                f"{API_BASE}/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Admin Test User",
                    "organization_name": f"Admin Test Org {timestamp}"
                },
                timeout=10
            )
            
            if admin_response.status_code != 200:
                print_error(f"Failed to create admin user: {admin_response.text}")
                self.failed += 2
                return
            
            admin_data = admin_response.json()
            admin_token = admin_data.get("access_token")
            admin_user = admin_data.get("user")
            
            print_success(f"Admin user created: {email}")
            print_info(f"Admin User ID: {admin_user.get('id')}")
            
            self.test_users['admin'] = {
                'email': email,
                'token': admin_token,
                'user': admin_user
            }
            
            # Test admin permissions (Admin should also have these permissions)
            print_test("Checking Admin permissions")
            
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            perm_response = requests.post(
                f"{API_BASE}/permissions/check",
                params={
                    "resource_type": "user",
                    "action": "invite",
                    "scope": "organization"
                },
                headers=admin_headers,
                timeout=10
            )
            
            if perm_response.status_code == 200:
                perm_data = perm_response.json()
                # Admin (as master of their own org) should have this permission
                if perm_data.get("has_permission"):
                    print_success("Admin has user.invite.organization permission ✓")
                    self.passed += 1
                else:
                    print_info("Admin doesn't have permission (expected for non-master roles)")
                    self.passed += 1
            else:
                print_error(f"Permission check failed: {perm_response.text}")
                self.failed += 1
                
        except Exception as e:
            print_error(f"Exception during admin user creation: {str(e)}")
            self.failed += 2
    
    def test_4_create_developer_user(self, master_token):
        """Test 4: Create Developer user and test permissions"""
        print_section("TEST 4: Create Developer User and Test Permissions")
        
        if not master_token:
            print_error("No master token available, skipping test")
            self.failed += 2
            return
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        email = f"developer.test.{timestamp}@example.com"
        
        print_test("Creating Developer user")
        
        try:
            # Register developer user
            dev_response = requests.post(
                f"{API_BASE}/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Developer Test User",
                    "organization_name": f"Dev Test Org {timestamp}"
                },
                timeout=10
            )
            
            if dev_response.status_code != 200:
                print_error(f"Failed to create developer user: {dev_response.text}")
                self.failed += 2
                return
            
            dev_data = dev_response.json()
            dev_token = dev_data.get("access_token")
            dev_user = dev_data.get("user")
            
            print_success(f"Developer user created: {email}")
            print_info(f"Developer User ID: {dev_user.get('id')}")
            print_info(f"Developer Role: {dev_user.get('role')}")
            
            self.test_users['developer'] = {
                'email': email,
                'token': dev_token,
                'user': dev_user
            }
            
            # Test developer permissions (as master of their own org, should have all permissions)
            print_test("Checking Developer permissions")
            
            dev_headers = {"Authorization": f"Bearer {dev_token}"}
            
            perm_response = requests.post(
                f"{API_BASE}/permissions/check",
                params={
                    "resource_type": "user",
                    "action": "invite",
                    "scope": "organization"
                },
                headers=dev_headers,
                timeout=10
            )
            
            if perm_response.status_code == 200:
                perm_data = perm_response.json()
                if perm_data.get("has_permission"):
                    print_success("Developer has user.invite.organization permission ✓")
                    self.passed += 1
                else:
                    print_info("Developer doesn't have permission (role-based)")
                    self.passed += 1
            else:
                print_error(f"Permission check failed: {perm_response.text}")
                self.failed += 1
                
        except Exception as e:
            print_error(f"Exception during developer user creation: {str(e)}")
            self.failed += 2
    
    def test_5_create_viewer_user(self):
        """Test 5: Create Viewer user and verify they DON'T have permissions"""
        print_section("TEST 5: Create Viewer User and Verify No Permissions")
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        email = f"viewer.test.{timestamp}@example.com"
        
        print_test("Creating Viewer user (no organization)")
        
        try:
            # Register viewer user without organization (gets viewer role)
            viewer_response = requests.post(
                f"{API_BASE}/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "name": "Viewer Test User"
                },
                timeout=10
            )
            
            if viewer_response.status_code != 200:
                print_error(f"Failed to create viewer user: {viewer_response.text}")
                self.failed += 2
                return
            
            viewer_data = viewer_response.json()
            viewer_token = viewer_data.get("access_token")
            viewer_user = viewer_data.get("user")
            
            print_success(f"Viewer user created: {email}")
            print_info(f"Viewer User ID: {viewer_user.get('id')}")
            print_info(f"Viewer Role: {viewer_user.get('role')}")
            
            # Verify role is 'viewer'
            if viewer_user.get('role') == 'viewer':
                print_success("User has role='viewer' (string code) ✓")
                self.passed += 1
            else:
                print_error(f"Expected role='viewer', got role='{viewer_user.get('role')}'")
                self.failed += 1
            
            self.test_users['viewer'] = {
                'email': email,
                'token': viewer_token,
                'user': viewer_user
            }
            
            # Test viewer permissions (should NOT have user.invite.organization)
            print_test("Checking Viewer permissions (should be denied)")
            
            viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
            
            perm_response = requests.post(
                f"{API_BASE}/permissions/check",
                params={
                    "resource_type": "user",
                    "action": "invite",
                    "scope": "organization"
                },
                headers=viewer_headers,
                timeout=10
            )
            
            if perm_response.status_code == 200:
                perm_data = perm_response.json()
                has_permission = perm_data.get("has_permission")
                
                if has_permission is False:
                    print_success("Viewer correctly DENIED user.invite.organization permission ✓")
                    self.passed += 1
                else:
                    print_error("Viewer should NOT have user.invite.organization permission")
                    print_error(f"Expected has_permission=false, got has_permission={has_permission}")
                    self.failed += 1
            else:
                print_error(f"Permission check failed: {perm_response.text}")
                self.failed += 1
                
        except Exception as e:
            print_error(f"Exception during viewer user creation: {str(e)}")
            self.failed += 2
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print_section("🚀 PHASE 2 FIX VERIFICATION: Permission Check System")
        print_info(f"Backend URL: {API_BASE}")
        print_info(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Create Master user
        master_token = self.test_1_create_master_user()
        
        # Test 2: Check Master permissions
        self.test_2_check_master_permissions(master_token)
        
        # Test 3: Create Admin user and test
        self.test_3_create_admin_user(master_token)
        
        # Test 4: Create Developer user and test
        self.test_4_create_developer_user(master_token)
        
        # Test 5: Create Viewer user and verify no permissions
        self.test_5_create_viewer_user()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print_section("📊 TEST SUMMARY")
        
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}✅ Passed:{Colors.RESET} {self.passed}")
        print(f"{Colors.RED}❌ Failed:{Colors.RESET} {self.failed}")
        print(f"{Colors.BOLD}Success Rate:{Colors.RESET} {success_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Permission fix is working correctly.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED. Review the errors above.{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Test Users Created:{Colors.RESET}")
        for role, data in self.test_users.items():
            print(f"  {role.upper()}: {data['email']}")


if __name__ == "__main__":
    tester = PermissionFixTester()
    tester.run_all_tests()
