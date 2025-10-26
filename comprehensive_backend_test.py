import requests
import sys
import json
from datetime import datetime
import uuid
import io
import os

class ComprehensiveSettingsAPITester:
    """PRIORITY 1: Settings APIs Testing - Theme, Regional, Privacy, Notifications"""
    
    def __init__(self, base_url="https://rbacmaster-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_user_id = None

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

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

    def create_test_user_and_login(self):
        """Create a test user with organization and login"""
        unique_email = f"settingstest_{uuid.uuid4().hex[:8]}@testcompany.com"
        user_data = {
            "email": unique_email,
            "password": "SecurePass123!",
            "name": "Settings Test User",
            "organization_name": f"Settings Test Org {uuid.uuid4().hex[:6]}"
        }
        
        success, response = self.run_test(
            "Create Settings Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id')
            print(f"✅ Created and logged in as: {unique_email}")
            return True, response
        
        return False, response

    def test_theme_settings_workflow(self):
        """Test complete theme settings workflow"""
        print("\n🎨 Testing Theme Settings Workflow...")
        
        # 1. GET theme defaults
        success1, defaults = self.run_test(
            "GET Theme Defaults",
            "GET",
            "users/theme",
            200
        )
        
        if not success1:
            return False
        
        # Verify default structure
        expected_keys = ['theme', 'accent_color', 'font_size', 'view_density']
        if not all(key in defaults for key in expected_keys):
            self.log_test("Theme Defaults Structure", False, f"Missing keys in defaults: {expected_keys}")
            return False
        
        # 2. PUT theme settings with all 4 fields
        theme_data = {
            "theme": "dark",
            "accent_color": "#ef4444",
            "font_size": "large", 
            "view_density": "spacious"
        }
        
        success2, update_response = self.run_test(
            "PUT Theme Settings (All 4 Fields)",
            "PUT",
            "users/theme",
            200,
            data=theme_data
        )
        
        if not success2:
            return False
        
        # 3. GET theme settings to verify persistence
        success3, updated_settings = self.run_test(
            "GET Theme Settings (Verify Persistence)",
            "GET",
            "users/theme",
            200
        )
        
        if success3:
            # Verify all 4 fields were updated correctly
            verification_success = True
            for key, expected_value in theme_data.items():
                if updated_settings.get(key) != expected_value:
                    self.log_test(f"Theme {key} Verification", False, f"Expected {expected_value}, got {updated_settings.get(key)}")
                    verification_success = False
                else:
                    self.log_test(f"Theme {key} Verification", True, f"Correctly saved as {expected_value}")
            
            return verification_success
        
        return False

    def test_regional_settings_workflow(self):
        """Test complete regional settings workflow"""
        print("\n🌍 Testing Regional Settings Workflow...")
        
        # 1. GET regional defaults
        success1, defaults = self.run_test(
            "GET Regional Defaults",
            "GET",
            "users/regional",
            200
        )
        
        if not success1:
            return False
        
        # 2. PUT regional settings with all 5 fields
        regional_data = {
            "language": "es",
            "timezone": "America/New_York",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "EUR"
        }
        
        success2, update_response = self.run_test(
            "PUT Regional Settings (All 5 Fields)",
            "PUT",
            "users/regional",
            200,
            data=regional_data
        )
        
        if not success2:
            return False
        
        # 3. GET regional settings to verify persistence
        success3, updated_settings = self.run_test(
            "GET Regional Settings (Verify Persistence)",
            "GET",
            "users/regional",
            200
        )
        
        if success3:
            # Verify all 5 fields were updated correctly
            verification_success = True
            for key, expected_value in regional_data.items():
                if updated_settings.get(key) != expected_value:
                    self.log_test(f"Regional {key} Verification", False, f"Expected {expected_value}, got {updated_settings.get(key)}")
                    verification_success = False
                else:
                    self.log_test(f"Regional {key} Verification", True, f"Correctly saved as {expected_value}")
            
            return verification_success
        
        return False

    def test_privacy_settings_workflow(self):
        """Test complete privacy settings workflow"""
        print("\n🔒 Testing Privacy Settings Workflow...")
        
        # 1. GET privacy defaults
        success1, defaults = self.run_test(
            "GET Privacy Defaults",
            "GET",
            "users/privacy",
            200
        )
        
        if not success1:
            return False
        
        # 2. PUT privacy settings with all 3 fields
        privacy_data = {
            "profile_visibility": "private",
            "show_activity_status": False,
            "show_last_seen": False
        }
        
        success2, update_response = self.run_test(
            "PUT Privacy Settings (All 3 Fields)",
            "PUT",
            "users/privacy",
            200,
            data=privacy_data
        )
        
        if not success2:
            return False
        
        # 3. GET privacy settings to verify persistence
        success3, updated_settings = self.run_test(
            "GET Privacy Settings (Verify Persistence)",
            "GET",
            "users/privacy",
            200
        )
        
        if success3:
            # Verify all 3 fields were updated correctly
            verification_success = True
            for key, expected_value in privacy_data.items():
                if updated_settings.get(key) != expected_value:
                    self.log_test(f"Privacy {key} Verification", False, f"Expected {expected_value}, got {updated_settings.get(key)}")
                    verification_success = False
                else:
                    self.log_test(f"Privacy {key} Verification", True, f"Correctly saved as {expected_value}")
            
            return verification_success
        
        return False

    def test_notification_settings_workflow(self):
        """Test notification settings workflow"""
        print("\n🔔 Testing Notification Settings Workflow...")
        
        # 1. GET notification defaults
        success1, defaults = self.run_test(
            "GET Notification Defaults",
            "GET",
            "users/settings",
            200
        )
        
        if not success1:
            return False
        
        # 2. PUT notification settings
        notification_data = {
            "email_notifications": False,
            "push_notifications": True,
            "weekly_reports": False,
            "marketing_emails": True
        }
        
        success2, update_response = self.run_test(
            "PUT Notification Settings",
            "PUT",
            "users/settings",
            200,
            data=notification_data
        )
        
        if not success2:
            return False
        
        # 3. GET notification settings to verify persistence
        success3, updated_settings = self.run_test(
            "GET Notification Settings (Verify Persistence)",
            "GET",
            "users/settings",
            200
        )
        
        if success3:
            # Verify all fields were updated correctly
            verification_success = True
            for key, expected_value in notification_data.items():
                if updated_settings.get(key) != expected_value:
                    self.log_test(f"Notification {key} Verification", False, f"Expected {expected_value}, got {updated_settings.get(key)}")
                    verification_success = False
                else:
                    self.log_test(f"Notification {key} Verification", True, f"Correctly saved as {expected_value}")
            
            return verification_success
        
        return False

    def run_all_tests(self):
        """Run all settings API tests"""
        print("🚀 Starting PRIORITY 1: Settings APIs Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Create test user and login
        if not self.create_test_user_and_login():
            print("❌ User creation/login failed, stopping settings tests")
            return self.generate_report()

        # Test all settings workflows
        self.test_theme_settings_workflow()
        self.test_regional_settings_workflow()
        self.test_privacy_settings_workflow()
        self.test_notification_settings_workflow()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 SETTINGS API TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }


class ComprehensiveUserManagementTester:
    """PRIORITY 2: User Management Testing"""
    
    def __init__(self, base_url="https://rbacmaster-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_user_id = None
        self.created_users = []

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

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

    def create_test_user_and_login(self):
        """Create a test user with organization and login"""
        unique_email = f"usermgmt_{uuid.uuid4().hex[:8]}@testcompany.com"
        user_data = {
            "email": unique_email,
            "password": "SecurePass123!",
            "name": "User Management Test User",
            "organization_name": f"User Mgmt Test Org {uuid.uuid4().hex[:6]}"
        }
        
        success, response = self.run_test(
            "Create User Management Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id')
            print(f"✅ Created and logged in as: {unique_email}")
            return True, response
        
        return False, response

    def test_user_list_with_password_fields(self):
        """Test GET /api/users - verify password fields visible for Developer panel"""
        print("\n👥 Testing User List with Password Fields...")
        
        success, users = self.run_test(
            "GET Users List",
            "GET",
            "users",
            200
        )
        
        if success and isinstance(users, list) and len(users) > 0:
            # Check if users have password or password_hash fields visible
            user_with_password = False
            for user in users:
                if 'password' in user or 'password_hash' in user:
                    user_with_password = True
                    break
            
            if user_with_password:
                self.log_test("Password Fields Visibility", True, "Password fields are visible in user list")
            else:
                self.log_test("Password Fields Visibility", False, "Password fields are NOT visible in user list")
            
            return success
        
        return False

    def test_user_update_workflow(self):
        """Test PUT /api/users/{user_id} - update role and status"""
        print("\n✏️ Testing User Update Workflow...")
        
        # First get users list to find a user to update
        success, users = self.run_test(
            "GET Users for Update Test",
            "GET",
            "users",
            200
        )
        
        if not success or not users:
            return False
        
        # Find a user that's not the current user
        target_user = None
        for user in users:
            if user.get('id') != self.test_user_id:
                target_user = user
                break
        
        if not target_user:
            # Create another user to update
            invite_data = {
                "email": f"updatetest_{uuid.uuid4().hex[:8]}@example.com",
                "role": "viewer"
            }
            
            invite_success, invite_response = self.run_test(
                "Create User to Update",
                "POST",
                "users/invite",
                200,
                data=invite_data
            )
            
            if not invite_success:
                return False
            
            # For this test, we'll simulate having a user to update
            target_user_id = str(uuid.uuid4())  # Simulate user ID
        else:
            target_user_id = target_user['id']
        
        # Test updating user role and status
        update_data = {
            "role": "supervisor",
            "status": "active"
        }
        
        success, update_response = self.run_test(
            "PUT User Update (Role & Status)",
            "PUT",
            f"users/{target_user_id}",
            200,
            data=update_data
        )
        
        return success

    def test_user_delete_workflow(self):
        """Test DELETE /api/users/{user_id} - soft delete"""
        print("\n🗑️ Testing User Delete Workflow...")
        
        # Create a user to delete via invitation
        delete_test_email = f"deletetest_{uuid.uuid4().hex[:8]}@example.com"
        invite_data = {
            "email": delete_test_email,
            "role": "viewer"
        }
        
        invite_success, invite_response = self.run_test(
            "Create User for Delete Test",
            "POST",
            "users/invite",
            200,
            data=invite_data
        )
        
        if not invite_success:
            return False
        
        # Get users list to find the created user
        success, users = self.run_test(
            "GET Users Before Delete",
            "GET",
            "users",
            200
        )
        
        if not success:
            return False
        
        initial_user_count = len(users)
        
        # Find a user to delete (not the current user)
        target_user = None
        for user in users:
            if user.get('id') != self.test_user_id and user.get('email') != delete_test_email:
                target_user = user
                break
        
        if not target_user:
            self.log_test("User Delete Test", False, "No suitable user found to delete")
            return False
        
        # Test deleting the user
        success, delete_response = self.run_test(
            "DELETE User (Soft Delete)",
            "DELETE",
            f"users/{target_user['id']}",
            200
        )
        
        if success:
            # Verify user is removed from list (soft delete)
            success2, users_after = self.run_test(
                "GET Users After Delete (Verify Removal)",
                "GET",
                "users",
                200
            )
            
            if success2:
                final_user_count = len(users_after)
                if final_user_count < initial_user_count:
                    self.log_test("Soft Delete Verification", True, f"User count decreased from {initial_user_count} to {final_user_count}")
                else:
                    self.log_test("Soft Delete Verification", False, f"User count unchanged: {initial_user_count} -> {final_user_count}")
                
                return True
        
        return False

    def run_all_tests(self):
        """Run all user management tests"""
        print("🚀 Starting PRIORITY 2: User Management Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Create test user and login
        if not self.create_test_user_and_login():
            print("❌ User creation/login failed, stopping user management tests")
            return self.generate_report()

        # Test user management workflows
        self.test_user_list_with_password_fields()
        self.test_user_update_workflow()
        self.test_user_delete_workflow()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 USER MANAGEMENT TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }


if __name__ == "__main__":
    # Run FINAL COMPREHENSIVE BACKEND TESTING - ALL FIXES APPLIED
    print("🚀 Starting FINAL COMPREHENSIVE BACKEND TESTING - ALL FIXES APPLIED")
    print("🎯 Testing with MAXIMUM rigor and detail as requested")
    print("=" * 80)
    
    # PRIORITY 1: SETTINGS APIs (JUST FIXED)
    print("\n" + "="*60)
    print("🎨 PRIORITY 1: SETTINGS APIs (JUST FIXED)")
    print("="*60)
    settings_tester = ComprehensiveSettingsAPITester()
    settings_results = settings_tester.run_all_tests()
    
    # PRIORITY 2: USER MANAGEMENT
    print("\n" + "="*60)
    print("👥 PRIORITY 2: USER MANAGEMENT")
    print("="*60)
    user_mgmt_tester = ComprehensiveUserManagementTester()
    user_mgmt_results = user_mgmt_tester.run_all_tests()
    
    # Generate FINAL COMPREHENSIVE SUMMARY
    print("\n" + "=" * 80)
    print("🎯 FINAL COMPREHENSIVE BACKEND TESTING SUMMARY")
    print("🎯 TARGET: 90%+ success rate with detailed error analysis")
    print("=" * 80)
    
    all_results = [
        ("PRIORITY 1: Settings APIs", settings_results),
        ("PRIORITY 2: User Management", user_mgmt_results)
    ]
    
    total_tests = sum(result["total_tests"] for _, result in all_results)
    total_passed = sum(result["passed_tests"] for _, result in all_results)
    overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_tests - total_passed}")
    print(f"   Success Rate: {overall_success_rate:.1f}%")
    
    # Target achievement check
    target_met = "✅ TARGET MET" if overall_success_rate >= 90 else "❌ TARGET NOT MET"
    print(f"   {target_met} (Target: 90%+)")
    
    print(f"\n📋 PRIORITY BREAKDOWN:")
    for priority_name, results in all_results:
        success_rate = results["success_rate"]
        status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
        print(f"   {status} {priority_name}: {results['passed_tests']}/{results['total_tests']} ({success_rate:.1f}%)")
    
    # Detailed error analysis for failures
    print(f"\n🔍 DETAILED ERROR ANALYSIS:")
    has_failures = False
    for priority_name, results in all_results:
        failed_tests = [test for test in results["test_results"] if not test['success']]
        if failed_tests:
            has_failures = True
            print(f"\n❌ {priority_name} FAILURES:")
            for test in failed_tests:
                print(f"   • {test['test']}")
                print(f"     └─ {test['details'][:200]}...")
    
    if not has_failures:
        print("   🎉 NO FAILURES - ALL SYSTEMS OPERATIONAL!")
    
    print("\n🎉 FINAL COMPREHENSIVE BACKEND TESTING COMPLETE!")
    print("=" * 80)