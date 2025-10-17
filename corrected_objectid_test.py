#!/usr/bin/env python3
"""
Corrected Comprehensive Backend Testing for v2.0 Operational Management Platform
Focus on MongoDB ObjectId Serialization with Correct API Models

CRITICAL FIXES TO VERIFY:
1. MongoDB ObjectId Serialization - Verify no ObjectId appears in any API response
2. Self-Delegation Logic - Verify delegation validation  
3. Complete Backend Coverage - Test all major endpoints with correct field names
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime, timedelta
import tempfile

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://userperm-hub.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class CorrectedObjectIdTester:
    def __init__(self):
        self.session = requests.Session()
        # Use unique test data for each run
        unique_id = uuid.uuid4().hex[:8]
        self.test_user_email = f"corrected.test.{unique_id}@serialization.com"
        self.test_user2_email = f"corrected.test2.{unique_id}@serialization.com"
        self.test_password = "CorrectedTest123!@#"
        self.access_token = None
        self.user_id = None
        self.user2_id = None
        self.organization_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # Store created resources for cleanup
        self.created_resources = {
            "workflow_instances": [],
            "delegations": [],
            "time_entries": [],
            "checklist_templates": [],
            "checklist_executions": [],
            "tasks": [],
            "users": []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.results["failed"] += 1
            error_msg = f"❌ {test_name}: {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:300]})"
            print(error_msg)
            self.results["errors"].append(error_msg)
    
    def make_request(self, method, endpoint, **kwargs):
        """Make authenticated request"""
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {'Authorization': f'Bearer {self.access_token}'}
        elif self.access_token and 'headers' in kwargs:
            kwargs['headers']['Authorization'] = f'Bearer {self.access_token}'
        
        url = f"{API_URL}{endpoint}"
        return self.session.request(method, url, **kwargs)
    
    def check_objectid_in_response(self, response_data, test_name):
        """Check if response contains any ObjectId references"""
        response_str = json.dumps(response_data) if isinstance(response_data, (dict, list)) else str(response_data)
        
        # Check for ObjectId patterns
        objectid_indicators = [
            '"_id"',
            'ObjectId(',
            'bson.objectid',
            '$oid'
        ]
        
        for indicator in objectid_indicators:
            if indicator in response_str:
                self.log_result(f"{test_name} - ObjectId Check", False, f"Found ObjectId indicator: {indicator}")
                return False
        
        self.log_result(f"{test_name} - ObjectId Check", True, "No ObjectId found in response")
        return True
    
    def setup_test_users(self):
        """Setup test users for authentication and delegation testing"""
        print("\n🔧 Setting up test users...")
        
        # Register first test user
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password,
            "name": "Corrected Test User 1",
            "organization_name": "Corrected Testing Corp"
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.organization_id = data.get("user", {}).get("organization_id")
            
            if self.access_token and self.user_id:
                self.log_result("User 1 Registration", True, f"User created with ID: {self.user_id}")
                self.created_resources["users"].append(self.user_id)
                
                # Check for ObjectId in registration response
                self.check_objectid_in_response(data, "User Registration")
            else:
                self.log_result("User 1 Registration", False, "Missing access token or user ID")
                return False
        else:
            self.log_result("User 1 Registration", False, "Failed to register user", response)
            return False
        
        # Register second test user for delegation testing
        user_data2 = {
            "email": self.test_user2_email,
            "password": self.test_password,
            "name": "Corrected Test User 2"
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=user_data2)
        if response.status_code in [200, 201]:
            data = response.json()
            self.user2_id = data.get("user", {}).get("id")
            if self.user2_id:
                self.log_result("User 2 Registration", True, f"Second user created with ID: {self.user2_id}")
                self.created_resources["users"].append(self.user2_id)
                
                # Check for ObjectId in registration response
                self.check_objectid_in_response(data, "User 2 Registration")
            else:
                self.log_result("User 2 Registration", False, "Missing user ID for second user")
        else:
            self.log_result("User 2 Registration", False, "Failed to register second user", response)
        
        return True
    
    def test_workflow_instance_creation(self):
        """Test workflow instance creation for ObjectId serialization"""
        print("\n🔄 Testing Workflow Instance Creation...")
        
        # First create a workflow template with correct field names
        template_data = {
            "name": "Corrected ObjectId Test Workflow",
            "description": "Testing ObjectId serialization in workflow instances",
            "resource_type": "inspection",
            "steps": [  # Correct field name is 'steps', not 'approval_steps'
                {
                    "step_number": 1,
                    "name": "Initial Approval",
                    "approver_role": "supervisor",
                    "approver_context": "organization",
                    "approval_type": "any",
                    "timeout_hours": 24,
                    "required_permissions": []
                }
            ]
        }
        
        response = self.make_request("POST", "/workflows/templates", json=template_data)
        if response.status_code in [200, 201]:
            template = response.json()
            template_id = template.get("id")
            
            if template_id:
                self.log_result("Workflow Template Creation", True, f"Template created with ID: {template_id}")
                
                # Check for ObjectId in template response
                self.check_objectid_in_response(template, "Workflow Template Creation")
                
                # Now create workflow instance
                instance_data = {
                    "template_id": template_id,
                    "resource_id": str(uuid.uuid4()),
                    "resource_type": "inspection",
                    "resource_name": "ObjectId Test Instance"
                }
                
                response = self.make_request("POST", "/workflows/instances", json=instance_data)
                if response.status_code in [200, 201]:
                    instance = response.json()
                    instance_id = instance.get("id")
                    
                    if instance_id:
                        self.log_result("Workflow Instance Creation", True, f"Instance created with ID: {instance_id}")
                        self.created_resources["workflow_instances"].append(instance_id)
                        
                        # CRITICAL: Check for ObjectId in instance response
                        self.check_objectid_in_response(instance, "Workflow Instance Creation")
                    else:
                        self.log_result("Workflow Instance Creation", False, "Missing instance ID")
                else:
                    self.log_result("Workflow Instance Creation", False, "Failed to create workflow instance", response)
            else:
                self.log_result("Workflow Template Creation", False, "Missing template ID")
        else:
            self.log_result("Workflow Template Creation", False, "Failed to create workflow template", response)
    
    def test_delegation_creation(self):
        """Test delegation creation and self-delegation validation"""
        print("\n👥 Testing Delegation Creation and Validation...")
        
        if not self.user2_id:
            self.log_result("Delegation Test Setup", False, "Second user not available for delegation testing")
            return
        
        # Test 1: Valid delegation to another user with correct field names
        delegation_data = {
            "delegate_id": self.user2_id,  # Correct field name
            "workflow_types": ["inspection", "task"],
            "resource_types": ["inspection", "task"],
            "valid_from": datetime.now().isoformat(),  # Correct field name
            "valid_until": (datetime.now() + timedelta(days=7)).isoformat(),  # Correct field name
            "reason": "Testing delegation functionality"
        }
        
        response = self.make_request("POST", "/context-permissions/delegations", json=delegation_data)
        if response.status_code in [200, 201]:
            delegation = response.json()
            delegation_id = delegation.get("id")
            
            if delegation_id:
                self.log_result("Valid Delegation Creation", True, f"Delegation created with ID: {delegation_id}")
                self.created_resources["delegations"].append(delegation_id)
                
                # CRITICAL: Check for ObjectId in delegation response
                self.check_objectid_in_response(delegation, "Delegation Creation")
            else:
                self.log_result("Valid Delegation Creation", False, "Missing delegation ID")
        else:
            self.log_result("Valid Delegation Creation", False, "Failed to create delegation", response)
        
        # Test 2: Self-delegation validation (should fail)
        self_delegation_data = {
            "delegate_id": self.user_id,  # Same as current user
            "workflow_types": ["task"],
            "resource_types": ["task"],
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=7)).isoformat(),
            "reason": "Testing self-delegation prevention"
        }
        
        response = self.make_request("POST", "/context-permissions/delegations", json=self_delegation_data)
        if response.status_code in [400, 422]:
            self.log_result("Self-Delegation Prevention", True, "Self-delegation correctly rejected")
        else:
            self.log_result("Self-Delegation Prevention", False, "Self-delegation should be rejected", response)
    
    def test_time_entry_creation(self):
        """Test time entry creation for ObjectId serialization"""
        print("\n⏰ Testing Time Entry Creation...")
        
        # First create a task to track time against
        task_data = {
            "title": "Time Tracking Test Task",
            "description": "Task for time tracking testing",
            "priority": "medium",
            "status": "in_progress"
        }
        
        response = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            task = response.json()
            task_id = task.get("id")
            
            if task_id:
                self.log_result("Task Creation for Time Tracking", True, f"Task created with ID: {task_id}")
                self.created_resources["tasks"].append(task_id)
                
                # Now create time entry
                time_entry_data = {
                    "task_id": task_id,  # Use actual task ID
                    "description": "ObjectId serialization testing",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                    "duration_minutes": 120,
                    "category": "development"
                }
                
                response = self.make_request("POST", "/time-tracking/entries", json=time_entry_data)
                if response.status_code in [200, 201]:
                    entry = response.json()
                    entry_id = entry.get("id")
                    
                    if entry_id:
                        self.log_result("Time Entry Creation", True, f"Time entry created with ID: {entry_id}")
                        self.created_resources["time_entries"].append(entry_id)
                        
                        # CRITICAL: Check for ObjectId in time entry response
                        self.check_objectid_in_response(entry, "Time Entry Creation")
                    else:
                        self.log_result("Time Entry Creation", False, "Missing time entry ID")
                else:
                    self.log_result("Time Entry Creation", False, "Failed to create time entry", response)
            else:
                self.log_result("Task Creation for Time Tracking", False, "Missing task ID")
        else:
            self.log_result("Task Creation for Time Tracking", False, "Failed to create task for time tracking", response)
    
    def test_checklist_template_creation(self):
        """Test checklist template creation for ObjectId serialization"""
        print("\n📋 Testing Checklist Template Creation...")
        
        template_data = {
            "name": "Corrected ObjectId Test Checklist",
            "description": "Testing ObjectId serialization in checklist templates",
            "category": "testing",
            "items": [
                {
                    "text": "Check ObjectId serialization",  # Correct field name is 'text', not 'title'
                    "required": True,
                    "order": 1
                },
                {
                    "text": "Validate JSON response",
                    "required": True,
                    "order": 2
                }
            ]
        }
        
        response = self.make_request("POST", "/checklists/templates", json=template_data)
        if response.status_code in [200, 201]:
            template = response.json()
            template_id = template.get("id")
            
            if template_id:
                self.log_result("Checklist Template Creation", True, f"Template created with ID: {template_id}")
                self.created_resources["checklist_templates"].append(template_id)
                
                # CRITICAL: Check for ObjectId in template response
                self.check_objectid_in_response(template, "Checklist Template Creation")
                
                # Test checklist execution start
                self.test_checklist_execution_start(template_id)
            else:
                self.log_result("Checklist Template Creation", False, "Missing template ID")
        else:
            self.log_result("Checklist Template Creation", False, "Failed to create checklist template", response)
    
    def test_checklist_execution_start(self, template_id):
        """Test checklist execution start for ObjectId serialization"""
        print("\n▶️ Testing Checklist Execution Start...")
        
        execution_data = {
            "template_id": template_id,
            "title": "Corrected ObjectId Test Execution",
            "assigned_to": self.user_id
        }
        
        response = self.make_request("POST", "/checklists/executions", json=execution_data)
        if response.status_code in [200, 201]:
            execution = response.json()
            execution_id = execution.get("id")
            
            if execution_id:
                self.log_result("Checklist Execution Start", True, f"Execution started with ID: {execution_id}")
                self.created_resources["checklist_executions"].append(execution_id)
                
                # CRITICAL: Check for ObjectId in execution response
                self.check_objectid_in_response(execution, "Checklist Execution Start")
            else:
                self.log_result("Checklist Execution Start", False, "Missing execution ID")
        else:
            self.log_result("Checklist Execution Start", False, "Failed to start checklist execution", response)
    
    def test_authentication_system(self):
        """Test authentication system endpoints"""
        print("\n🔐 Testing Authentication System...")
        
        # Test /api/auth/me endpoint
        response = self.make_request("GET", "/auth/me")
        if response.status_code == 200:
            user_data = response.json()
            self.log_result("Auth Me Endpoint", True, "User profile retrieved successfully")
            
            # Check for ObjectId in user profile response
            self.check_objectid_in_response(user_data, "Auth Me Endpoint")
        else:
            self.log_result("Auth Me Endpoint", False, "Failed to get user profile", response)
        
        # Test login endpoint with existing user
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        response = self.session.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            self.log_result("Login Endpoint", True, "Login successful")
            
            # Check for ObjectId in login response
            self.check_objectid_in_response(login_response, "Login Endpoint")
        else:
            self.log_result("Login Endpoint", False, "Login failed", response)
    
    def test_user_management_system(self):
        """Test user management system endpoints"""
        print("\n👤 Testing User Management System...")
        
        # Test GET /api/users
        response = self.make_request("GET", "/users")
        if response.status_code == 200:
            users = response.json()
            self.log_result("Users List", True, f"Retrieved {len(users)} users")
            
            # Check for ObjectId in users response
            self.check_objectid_in_response(users, "Users List")
        else:
            self.log_result("Users List", False, "Failed to get users", response)
        
        # Test user profile update
        profile_data = {
            "name": "Updated Corrected Test User",
            "phone": "+1234567890",
            "bio": "Testing ObjectId serialization fixes"
        }
        
        response = self.make_request("PUT", "/users/profile", json=profile_data)
        if response.status_code == 200:
            profile = response.json()
            self.log_result("User Profile Update", True, "Profile updated successfully")
            
            # Check for ObjectId in profile response
            self.check_objectid_in_response(profile, "User Profile Update")
        else:
            self.log_result("User Profile Update", False, "Failed to update profile", response)
    
    def test_task_management(self):
        """Test task management endpoints"""
        print("\n📝 Testing Task Management...")
        
        # Create a test task
        task_data = {
            "title": "Corrected ObjectId Serialization Test Task",
            "description": "Testing ObjectId fixes in task creation",
            "priority": "high",
            "status": "todo",
            "assigned_to": self.user_id
        }
        
        response = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            task = response.json()
            task_id = task.get("id")
            
            if task_id:
                self.log_result("Task Creation", True, f"Task created with ID: {task_id}")
                self.created_resources["tasks"].append(task_id)
                
                # CRITICAL: Check for ObjectId in task response
                self.check_objectid_in_response(task, "Task Creation")
                
                # Test task retrieval
                response = self.make_request("GET", f"/tasks/{task_id}")
                if response.status_code == 200:
                    task_details = response.json()
                    self.log_result("Task Retrieval", True, "Task retrieved successfully")
                    
                    # Check for ObjectId in task details response
                    self.check_objectid_in_response(task_details, "Task Retrieval")
                else:
                    self.log_result("Task Retrieval", False, "Failed to retrieve task", response)
            else:
                self.log_result("Task Creation", False, "Missing task ID")
        else:
            self.log_result("Task Creation", False, "Failed to create task", response)
    
    def test_rbac_system(self):
        """Test RBAC (Roles, Permissions) system endpoints"""
        print("\n🛡️ Testing RBAC System...")
        
        # Test permissions endpoint
        response = self.make_request("GET", "/permissions")
        if response.status_code == 200:
            permissions = response.json()
            self.log_result("Permissions List", True, f"Retrieved {len(permissions)} permissions")
            
            # Check for ObjectId in permissions response
            self.check_objectid_in_response(permissions, "Permissions List")
        else:
            self.log_result("Permissions List", False, "Failed to get permissions", response)
        
        # Test roles endpoint
        response = self.make_request("GET", "/roles")
        if response.status_code == 200:
            roles = response.json()
            self.log_result("Roles List", True, f"Retrieved {len(roles)} roles")
            
            # Check for ObjectId in roles response
            self.check_objectid_in_response(roles, "Roles List")
        else:
            self.log_result("Roles List", False, "Failed to get roles", response)
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics endpoint"""
        print("\n📊 Testing Dashboard Statistics...")
        
        response = self.make_request("GET", "/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            self.log_result("Dashboard Statistics", True, "Dashboard stats retrieved")
            
            # Check for ObjectId in dashboard stats response
            self.check_objectid_in_response(stats, "Dashboard Statistics")
        else:
            self.log_result("Dashboard Statistics", False, "Failed to get dashboard stats", response)
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Clean up tasks
        for task_id in self.created_resources["tasks"]:
            try:
                self.make_request("DELETE", f"/tasks/{task_id}")
            except:
                pass
        
        # Clean up workflow instances
        for instance_id in self.created_resources["workflow_instances"]:
            try:
                self.make_request("POST", f"/workflows/instances/{instance_id}/cancel")
            except:
                pass
        
        # Clean up delegations
        for delegation_id in self.created_resources["delegations"]:
            try:
                self.make_request("DELETE", f"/context-permissions/delegations/{delegation_id}")
            except:
                pass
        
        print("✅ Cleanup completed")
    
    def run_all_tests(self):
        """Run all corrected ObjectId serialization and backend coverage tests"""
        print("🚀 Starting CORRECTED Comprehensive Backend Testing for v2.0 Operational Management Platform")
        print("🎯 Focus: MongoDB ObjectId Serialization with Correct API Models")
        print("=" * 90)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run all test suites
        try:
            # CRITICAL ObjectId serialization tests with correct models
            self.test_workflow_instance_creation()
            self.test_delegation_creation()
            self.test_time_entry_creation()
            self.test_checklist_template_creation()
            
            # Complete backend coverage tests
            self.test_authentication_system()
            self.test_user_management_system()
            self.test_task_management()
            self.test_rbac_system()
            self.test_dashboard_statistics()
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        finally:
            # Always cleanup
            self.cleanup_resources()
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 90)
        print("📊 CORRECTED COMPREHENSIVE BACKEND TEST RESULTS - v2.0 OPERATIONAL MANAGEMENT PLATFORM")
        print("=" * 90)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Categorize results
        objectid_tests = [error for error in self.results["errors"] if "ObjectId Check" in error]
        delegation_tests = [error for error in self.results["errors"] if "Delegation" in error]
        other_tests = [error for error in self.results["errors"] if "ObjectId Check" not in error and "Delegation" not in error]
        
        if objectid_tests:
            print(f"\n🔴 CRITICAL: ObjectId Serialization Issues ({len(objectid_tests)}):")
            for error in objectid_tests:
                print(f"  • {error}")
        
        if delegation_tests:
            print(f"\n🟡 Delegation Logic Issues ({len(delegation_tests)}):")
            for error in delegation_tests:
                print(f"  • {error}")
        
        if other_tests:
            print(f"\n🔍 Other Backend Issues ({len(other_tests)}):")
            for error in other_tests:
                print(f"  • {error}")
        
        print("\n" + "=" * 90)
        
        # Success criteria evaluation
        objectid_success = len(objectid_tests) == 0
        delegation_success = len(delegation_tests) == 0
        overall_success = success_rate >= 95
        
        print("🎯 SUCCESS CRITERIA EVALUATION:")
        print(f"✅ Zero ObjectId Serialization Errors: {'PASS' if objectid_success else 'FAIL'}")
        print(f"✅ Delegation Validation Working: {'PASS' if delegation_success else 'FAIL'}")
        print(f"✅ 95%+ Backend Success Rate: {'PASS' if overall_success else 'FAIL'}")
        
        if objectid_success and delegation_success and overall_success:
            print("\n🎉 SUCCESS! All critical fixes verified. Backend ready for production.")
        elif objectid_success and delegation_success:
            print("\n✅ GOOD! Critical ObjectId and delegation fixes working. Minor issues to address.")
        elif objectid_success:
            print("\n⚠️ PARTIAL! ObjectId fixes working but delegation or other issues need attention.")
        else:
            print("\n❌ CRITICAL! ObjectId serialization issues detected. Immediate fix required.")


if __name__ == "__main__":
    tester = CorrectedObjectIdTester()
    tester.run_all_tests()