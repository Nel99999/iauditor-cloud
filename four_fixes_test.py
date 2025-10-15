#!/usr/bin/env python3
"""
Backend Testing for 4 Specific Fixes
=====================================

This test verifies the 4 backend issues that were just implemented:
1. Privacy Settings Persistence
2. Workflow Validation Fields  
3. Role Assignment (Master vs Admin)
4. Pagination Limits

Test Requirements:
- Create test users and login
- Test privacy settings persistence across logout/login
- Test workflow validation for required fields
- Test role assignment for organization creators
- Test pagination limits enforcement
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://opsplatform-v2.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_users = []
        self.test_data = {}
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def register_user(self, email, name, password, organization_name=None):
        """Register a new user"""
        data = {
            "email": email,
            "name": name,
            "password": password
        }
        if organization_name:
            data["organization_name"] = organization_name
            
        response = self.session.post(f"{BACKEND_URL}/auth/register", json=data)
        if response.status_code in [200, 201]:
            result = response.json()
            self.log(f"✅ User registered: {email} (Role: {result.get('user', {}).get('role', 'unknown')})")
            return result
        else:
            self.log(f"❌ Registration failed for {email}: {response.status_code} - {response.text}", "ERROR")
            return None
            
    def login_user(self, email, password):
        """Login user and return token"""
        data = {"email": email, "password": password}
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=data)
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            user = result.get("user", {})
            self.log(f"✅ Login successful: {email} (Role: {user.get('role', 'unknown')})")
            return token, user
        else:
            self.log(f"❌ Login failed for {email}: {response.status_code} - {response.text}", "ERROR")
            return None, None
            
    def set_auth_header(self, token):
        """Set authorization header"""
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            self.session.headers.pop("Authorization", None)
            
    def test_privacy_settings_persistence(self):
        """
        Fix 1: Privacy Settings Persistence
        1. Create test user and login
        2. Update privacy settings (profile_visibility, show_activity_status, show_last_seen)
        3. Verify PUT /api/users/privacy returns updated values
        4. GET /api/users/privacy to confirm persistence
        5. Logout and login again
        6. GET /api/users/privacy again to verify still persisted
        """
        self.log("🔒 Testing Privacy Settings Persistence...")
        
        # Step 1: Create test user and login
        test_email = f"privacy_test_{int(time.time())}@example.com"
        user_data = self.register_user(test_email, "Privacy Test User", "password123", "Privacy Test Org")
        if not user_data:
            return False
            
        token = user_data.get("access_token")
        self.set_auth_header(token)
        
        # Step 2: Update privacy settings
        privacy_data = {
            "profile_visibility": "private",
            "show_activity_status": False,
            "show_last_seen": False
        }
        
        response = self.session.put(f"{BACKEND_URL}/users/privacy", json=privacy_data)
        if response.status_code != 200:
            self.log(f"❌ Privacy update failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        # Step 3: Verify PUT response contains updated values
        put_result = response.json()
        if (put_result.get("profile_visibility") != "private" or 
            put_result.get("show_activity_status") != False or 
            put_result.get("show_last_seen") != False):
            self.log(f"❌ PUT response doesn't match expected values: {put_result}", "ERROR")
            return False
            
        self.log("✅ Privacy settings PUT response correct")
        
        # Step 4: GET privacy settings to confirm persistence
        response = self.session.get(f"{BACKEND_URL}/users/privacy")
        if response.status_code != 200:
            self.log(f"❌ Privacy GET failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        get_result = response.json()
        if (get_result.get("profile_visibility") != "private" or 
            get_result.get("show_activity_status") != False or 
            get_result.get("show_last_seen") != False):
            self.log(f"❌ GET response doesn't match expected values: {get_result}", "ERROR")
            return False
            
        self.log("✅ Privacy settings GET response correct")
        
        # Step 5: Logout and login again
        self.set_auth_header(None)  # Clear auth
        token, user = self.login_user(test_email, "password123")
        if not token:
            return False
        self.set_auth_header(token)
        
        # Step 6: Verify privacy settings still persisted
        response = self.session.get(f"{BACKEND_URL}/users/privacy")
        if response.status_code != 200:
            self.log(f"❌ Privacy GET after re-login failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        final_result = response.json()
        if (final_result.get("profile_visibility") != "private" or 
            final_result.get("show_activity_status") != False or 
            final_result.get("show_last_seen") != False):
            self.log(f"❌ Privacy settings not persisted after re-login: {final_result}", "ERROR")
            return False
            
        self.log("✅ Privacy settings persisted correctly after logout/login")
        return True
        
    def test_workflow_validation_fields(self):
        """
        Fix 2: Workflow Validation Fields
        1. Try to create workflow with empty approver_role - should fail with validation error
        2. Try to create workflow with empty approver_context - should fail with validation error
        3. Try to create workflow with empty approval_type - should fail with validation error
        4. Create workflow with valid values - should succeed and return all fields properly
        """
        self.log("⚙️ Testing Workflow Validation Fields...")
        
        # Create test user for workflow testing
        test_email = f"workflow_test_{int(time.time())}@example.com"
        user_data = self.register_user(test_email, "Workflow Test User", "password123", "Workflow Test Org")
        if not user_data:
            return False
            
        token = user_data.get("access_token")
        self.set_auth_header(token)
        
        # Test 1: Empty approver_role should fail
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test workflow validation",
            "resource_type": "task",
            "steps": [
                {
                    "step_number": 1,
                    "name": "Approval Step",
                    "approver_role": "",  # Empty - should fail
                    "approver_context": "manager",
                    "approval_type": "single",
                    "escalate_after_hours": 24
                }
            ]
        }
        
        response = self.session.post(f"{BACKEND_URL}/workflows/templates", json=workflow_data)
        if response.status_code == 201:
            self.log(f"❌ Workflow creation should have failed with empty approver_role. Response: {response.text}", "ERROR")
            return False
        elif response.status_code in [400, 422]:
            self.log("✅ Empty approver_role correctly rejected")
        else:
            self.log(f"❌ Unexpected response for empty approver_role: {response.status_code} - {response.text}", "ERROR")
            return False
        
        # Test 2: Empty approver_context should fail
        workflow_data["steps"][0]["approver_role"] = "manager"
        workflow_data["steps"][0]["approver_context"] = ""  # Empty - should fail
        
        response = self.session.post(f"{BACKEND_URL}/workflows/templates", json=workflow_data)
        if response.status_code == 201:
            self.log(f"❌ Workflow creation should have failed with empty approver_context. Response: {response.text}", "ERROR")
            return False
        elif response.status_code in [400, 422]:
            self.log("✅ Empty approver_context correctly rejected")
        else:
            self.log(f"❌ Unexpected response for empty approver_context: {response.status_code} - {response.text}", "ERROR")
            return False
        
        # Test 3: Empty approval_type should fail
        workflow_data["steps"][0]["approver_context"] = "department"
        workflow_data["steps"][0]["approval_type"] = ""  # Empty - should fail
        
        response = self.session.post(f"{BACKEND_URL}/workflows/templates", json=workflow_data)
        if response.status_code == 201:
            self.log(f"❌ Workflow creation should have failed with empty approval_type. Response: {response.text}", "ERROR")
            return False
        elif response.status_code in [400, 422]:
            self.log("✅ Empty approval_type correctly rejected")
        else:
            self.log(f"❌ Unexpected response for empty approval_type: {response.status_code} - {response.text}", "ERROR")
            return False
        
        # Test 4: Valid workflow should succeed
        workflow_data["steps"][0]["approval_type"] = "single"
        
        response = self.session.post(f"{BACKEND_URL}/workflows/templates", json=workflow_data)
        if response.status_code != 201:
            self.log(f"❌ Valid workflow creation failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        result = response.json()
        step = result.get("steps", [{}])[0]
        
        # Verify all fields are returned properly
        if (not step.get("approver_role") or 
            not step.get("approver_context") or 
            not step.get("approval_type")):
            self.log(f"❌ Workflow fields not returned properly: {step}", "ERROR")
            return False
            
        self.log("✅ Valid workflow created successfully with all fields")
        return True
        
    def test_role_assignment_master_vs_admin(self):
        """
        Fix 3: Role Assignment (Master vs Admin)
        1. Register NEW user with organization creation
        2. Verify user gets "master" role (not "admin")
        3. Check GET /api/auth/me or GET /api/users/me
        4. Confirm role field shows "master"
        """
        self.log("👑 Testing Role Assignment (Master vs Admin)...")
        
        # Step 1: Register NEW user with organization creation
        test_email = f"master_test_{int(time.time())}@example.com"
        user_data = self.register_user(test_email, "Master Test User", "password123", "Master Test Organization")
        if not user_data:
            return False
            
        # Step 2: Verify user gets "master" role from registration response
        user = user_data.get("user", {})
        role_from_register = user.get("role")
        
        if role_from_register != "master":
            self.log(f"❌ Registration should return 'master' role, got: {role_from_register}", "ERROR")
            return False
        self.log("✅ Registration correctly returns 'master' role")
        
        # Step 3: Check GET /api/auth/me
        token = user_data.get("access_token")
        self.set_auth_header(token)
        
        response = self.session.get(f"{BACKEND_URL}/auth/me")
        if response.status_code != 200:
            self.log(f"❌ GET /auth/me failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        auth_me_result = response.json()
        role_from_auth_me = auth_me_result.get("role")
        
        if role_from_auth_me != "master":
            self.log(f"❌ GET /auth/me should return 'master' role, got: {role_from_auth_me}", "ERROR")
            return False
        self.log("✅ GET /auth/me correctly returns 'master' role")
        
        # Step 4: Check GET /api/users/me
        response = self.session.get(f"{BACKEND_URL}/users/me")
        if response.status_code != 200:
            self.log(f"❌ GET /users/me failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
        users_me_result = response.json()
        role_from_users_me = users_me_result.get("role")
        
        if role_from_users_me != "master":
            self.log(f"❌ GET /users/me should return 'master' role, got: {role_from_users_me}", "ERROR")
            return False
        self.log("✅ GET /users/me correctly returns 'master' role")
        
        return True
        
    def test_pagination_limits(self):
        """
        Fix 4: Pagination Limits
        1. Create 20+ test tasks
        2. GET /api/tasks?limit=10 - should return exactly 10 tasks
        3. GET /api/tasks?limit=5&skip=5 - should return tasks 6-10
        4. GET /api/tasks?limit=200 - should enforce max limit of 100
        5. Verify pagination working correctly
        """
        self.log("📄 Testing Pagination Limits...")
        
        # Create test user for pagination testing
        test_email = f"pagination_test_{int(time.time())}@example.com"
        user_data = self.register_user(test_email, "Pagination Test User", "password123", "Pagination Test Org")
        if not user_data:
            return False
            
        token = user_data.get("access_token")
        self.set_auth_header(token)
        
        # Step 1: Create 25 test tasks
        self.log("Creating 25 test tasks...")
        created_tasks = []
        for i in range(25):
            task_data = {
                "title": f"Test Task {i+1}",
                "description": f"Description for test task {i+1}",
                "status": "todo",
                "priority": "medium"
            }
            
            response = self.session.post(f"{BACKEND_URL}/tasks", json=task_data)
            if response.status_code == 201:
                created_tasks.append(response.json())
            else:
                self.log(f"❌ Failed to create task {i+1}: {response.status_code}", "ERROR")
                return False
                
        self.log(f"✅ Created {len(created_tasks)} test tasks")
        
        # Step 2: GET /api/tasks?limit=10 - should return exactly 10 tasks
        response = self.session.get(f"{BACKEND_URL}/tasks?limit=10")
        if response.status_code != 200:
            self.log(f"❌ GET tasks with limit=10 failed: {response.status_code}", "ERROR")
            return False
            
        tasks_limit_10 = response.json()
        if len(tasks_limit_10) != 10:
            self.log(f"❌ Expected 10 tasks, got {len(tasks_limit_10)}", "ERROR")
            return False
        self.log("✅ limit=10 correctly returns 10 tasks")
        
        # Step 3: GET /api/tasks?limit=5&skip=5 - should return tasks 6-10
        response = self.session.get(f"{BACKEND_URL}/tasks?limit=5&skip=5")
        if response.status_code != 200:
            self.log(f"❌ GET tasks with limit=5&skip=5 failed: {response.status_code}", "ERROR")
            return False
            
        tasks_skip_5 = response.json()
        if len(tasks_skip_5) != 5:
            self.log(f"❌ Expected 5 tasks with skip=5, got {len(tasks_skip_5)}", "ERROR")
            return False
        self.log("✅ limit=5&skip=5 correctly returns 5 tasks")
        
        # Step 4: GET /api/tasks?limit=200 - should enforce max limit of 100
        response = self.session.get(f"{BACKEND_URL}/tasks?limit=200")
        if response.status_code != 200:
            self.log(f"❌ GET tasks with limit=200 failed: {response.status_code}", "ERROR")
            return False
            
        tasks_limit_200 = response.json()
        if len(tasks_limit_200) > 100:
            self.log(f"❌ limit=200 should be capped at 100, got {len(tasks_limit_200)}", "ERROR")
            return False
        self.log(f"✅ limit=200 correctly capped at {len(tasks_limit_200)} tasks (max 100)")
        
        # Step 5: Verify pagination consistency
        # Get first 10 and next 10, should be different sets
        response1 = self.session.get(f"{BACKEND_URL}/tasks?limit=10&skip=0")
        response2 = self.session.get(f"{BACKEND_URL}/tasks?limit=10&skip=10")
        
        if response1.status_code != 200 or response2.status_code != 200:
            self.log("❌ Pagination consistency test failed", "ERROR")
            return False
            
        tasks1 = response1.json()
        tasks2 = response2.json()
        
        # Check that task IDs are different (no overlap)
        ids1 = {task["id"] for task in tasks1}
        ids2 = {task["id"] for task in tasks2}
        
        if ids1.intersection(ids2):
            self.log("❌ Pagination overlap detected - same tasks in different pages", "ERROR")
            return False
        self.log("✅ Pagination consistency verified - no overlap between pages")
        
        return True
        
    def run_all_tests(self):
        """Run all 4 fix verification tests"""
        self.log("🚀 Starting Backend Fix Verification Tests...")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Privacy Settings Persistence
        try:
            results["privacy_settings"] = self.test_privacy_settings_persistence()
        except Exception as e:
            self.log(f"❌ Privacy settings test failed with exception: {str(e)}", "ERROR")
            results["privacy_settings"] = False
            
        # Test 2: Workflow Validation Fields
        try:
            results["workflow_validation"] = self.test_workflow_validation_fields()
        except Exception as e:
            self.log(f"❌ Workflow validation test failed with exception: {str(e)}", "ERROR")
            results["workflow_validation"] = False
            
        # Test 3: Role Assignment (Master vs Admin)
        try:
            results["role_assignment"] = self.test_role_assignment_master_vs_admin()
        except Exception as e:
            self.log(f"❌ Role assignment test failed with exception: {str(e)}", "ERROR")
            results["role_assignment"] = False
            
        # Test 4: Pagination Limits
        try:
            results["pagination_limits"] = self.test_pagination_limits()
        except Exception as e:
            self.log(f"❌ Pagination limits test failed with exception: {str(e)}", "ERROR")
            results["pagination_limits"] = False
            
        # Summary
        self.log("=" * 60)
        self.log("🎯 TEST RESULTS SUMMARY:")
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"  {test_name.replace('_', ' ').title()}: {status}")
            
        success_rate = (passed / total) * 100
        self.log(f"\n🏆 SUCCESS RATE: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        if success_rate == 100:
            self.log("🎉 ALL FIXES VERIFIED WORKING!")
        elif success_rate >= 75:
            self.log("⚠️  Most fixes working, minor issues remain")
        else:
            self.log("🚨 CRITICAL ISSUES - Multiple fixes not working")
            
        return results

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed