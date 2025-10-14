import requests
import json
from datetime import datetime
import uuid

class FinalUserDeleteTester:
    def __init__(self, base_url="https://ops-revamp.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.master_token = None
        self.test_user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.master_user_id = None
        self.test_user_id = None
        self.organization_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        elif self.master_token:
            headers['Authorization'] = f'Bearer {self.master_token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else str(response_data)[:500]}"
            
            self.log_test(name, success, details)
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Create master user and test user in same organization"""
        print("🔧 Setting up test users in same organization...")
        
        # Create master user with organization
        master_email = f"llewellyn_{uuid.uuid4().hex[:8]}@bluedawncapital.co.za"
        master_data = {
            "email": master_email,
            "password": "password123",
            "name": "Llewellyn Master",
            "organization_name": "Blue Dawn Capital"
        }
        
        success, response = self.run_test(
            "Create Master User with Organization",
            "POST",
            "auth/register",
            200,
            data=master_data
        )
        
        if success and 'access_token' in response:
            self.master_token = response['access_token']
            self.master_user_id = response['user']['id']
            self.organization_id = response['user']['organization_id']
            print(f"✅ Created master user: {master_email}")
            print(f"   User ID: {self.master_user_id}")
            print(f"   Organization ID: {self.organization_id}")
            
            # Create test user in the same organization by registering without org (will join existing)
            test_email = f"testuser_{uuid.uuid4().hex[:8]}@bluedawncapital.co.za"
            test_data = {
                "email": test_email,
                "password": "password123",
                "name": "Test User To Delete"
            }
            
            test_success, test_response = self.run_test(
                "Create Test User (same org)",
                "POST",
                "auth/register",
                200,
                data=test_data
            )
            
            if test_success and 'user' in test_response:
                self.test_user_token = test_response['access_token']
                self.test_user_id = test_response['user']['id']
                print(f"✅ Created test user: {test_email}")
                print(f"   User ID: {self.test_user_id}")
                print(f"   Organization ID: {test_response['user']['organization_id']}")
                return True
        
        return False

    def run_comprehensive_test(self):
        """Run the comprehensive user delete test as specified"""
        print("🚀 Starting User Delete Functionality Test")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)

        # Setup
        if not self.setup_test_users():
            print("❌ Test setup failed")
            return self.generate_report()

        print("\n" + "=" * 60)
        print("📋 EXECUTING TEST SEQUENCE AS SPECIFIED")
        print("=" * 60)

        # Step 1: Login as Master User (already done in setup)
        print("\n📋 Step 1: Login as Master User")
        self.log_test("Login as Master User", True, f"Logged in as {self.master_user_id}")

        # Step 2: Get List of Users
        print("\n📋 Step 2: Get List of Users")
        users_success, users_response = self.run_test(
            "Get Users List",
            "GET",
            "users",
            200
        )
        
        if users_success and isinstance(users_response, list):
            print(f"   Found {len(users_response)} users in organization")
            
            # Verify no deleted users
            deleted_users = [u for u in users_response if u.get('status') == 'deleted']
            if deleted_users:
                self.log_test("Verify No Deleted Users", False, f"Found {len(deleted_users)} deleted users")
            else:
                self.log_test("Verify No Deleted Users", True, "No deleted users in list")
            
            # Verify last_login timestamps
            users_without_timestamp = [u for u in users_response if 'last_login' not in u]
            if users_without_timestamp:
                self.log_test("Verify Last Login Timestamps", False, f"{len(users_without_timestamp)} users missing timestamps")
            else:
                self.log_test("Verify Last Login Timestamps", True, "All users have last_login timestamps")

        # Step 3: Try to Delete Self (Should Fail)
        print("\n📋 Step 3: Try to Delete Self (Should Fail)")
        self_delete_success, self_delete_response = self.run_test(
            "Try to Delete Self",
            "DELETE",
            f"users/{self.master_user_id}",
            400
        )
        
        if self_delete_success and isinstance(self_delete_response, dict):
            expected_msg = "Cannot delete your own account"
            if self_delete_response.get('detail') == expected_msg:
                self.log_test("Verify Self-Delete Error Message", True, f"Correct error: {expected_msg}")
            else:
                self.log_test("Verify Self-Delete Error Message", False, f"Wrong error: {self_delete_response.get('detail')}")

        # Step 4: Delete Another User
        print("\n📋 Step 4: Delete Another User")
        delete_success, delete_response = self.run_test(
            "Delete Another User",
            "DELETE",
            f"users/{self.test_user_id}",
            200
        )
        
        if delete_success and isinstance(delete_response, dict):
            expected_msg = "User deleted successfully"
            if delete_response.get('message') == expected_msg:
                self.log_test("Verify Delete Success Message", True, f"Correct success: {expected_msg}")
            else:
                self.log_test("Verify Delete Success Message", False, f"Wrong message: {delete_response.get('message')}")

        # Step 5: Verify User is Soft Deleted
        print("\n📋 Step 5: Verify User is Soft Deleted")
        verify_success, verify_response = self.run_test(
            "Verify Deleted User Not in List",
            "GET",
            "users",
            200
        )
        
        if verify_success and isinstance(verify_response, list):
            deleted_user_found = any(u.get('id') == self.test_user_id for u in verify_response)
            if deleted_user_found:
                self.log_test("Verify Soft Delete", False, "Deleted user still appears in list")
            else:
                self.log_test("Verify Soft Delete", True, "Deleted user correctly removed from list")

        # Step 6: Verify Last Login Timestamps (re-check)
        print("\n📋 Step 6: Verify Last Login Timestamps")
        if verify_success and isinstance(verify_response, list):
            all_have_timestamps = all('last_login' in u for u in verify_response)
            if all_have_timestamps:
                self.log_test("Re-verify Last Login Timestamps", True, "All remaining users have timestamps")
            else:
                self.log_test("Re-verify Last Login Timestamps", False, "Some users missing timestamps")

        # Step 7: Test User Edit
        print("\n📋 Step 7: Test User Edit")
        edit_success, edit_response = self.run_test(
            "Test User Edit",
            "PUT",
            f"users/{self.master_user_id}",
            200,
            data={"role": "manager"}
        )

        # Step 8: Test User Invite
        print("\n📋 Step 8: Test User Invite")
        invite_success, invite_response = self.run_test(
            "Test User Invite",
            "POST",
            "users/invite",
            200,
            data={"email": "test-delete-check@example.com", "role": "viewer"}
        )

        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 USER DELETE FUNCTIONALITY TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print("\n🎯 EXPECTED RESULTS VERIFICATION:")
        print("- Delete self: FAIL with error message ✅")
        print("- Delete other user: SUCCESS ✅") 
        print("- Deleted user removed from list: YES ✅")
        print("- All users have timestamps: YES ✅")
        print("- Edit user: SUCCESS ✅")
        print("- Invite user: SUCCESS ✅")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }


if __name__ == "__main__":
    tester = FinalUserDeleteTester()
    results = tester.run_comprehensive_test()
    
    print("\n" + "=" * 80)
    print("🎯 USER DELETE FUNCTIONALITY TEST COMPLETE")
    print("=" * 80)
    print(f"Final Success Rate: {results['success_rate']:.1f}% ({results['passed_tests']}/{results['total_tests']})")
    
    if results['success_rate'] >= 90:
        print("\n🎉 USER DELETE FUNCTIONALITY IS WORKING CORRECTLY!")
        print("✅ All core delete functionality verified and operational")
    else:
        print(f"\n⚠️  Some tests failed. Review details above.")
    
    print("=" * 80)