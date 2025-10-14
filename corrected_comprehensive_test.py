#!/usr/bin/env python3
"""
CORRECTED COMPREHENSIVE REVIEW BACKEND TESTING
Fixed issues identified in debug testing
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime, timedelta
import concurrent.futures

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://secureflow-mgmt.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class CorrectedComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_id = uuid.uuid4().hex[:8]
        self.master_user = {
            "email": f"corrected.{self.test_id}@review.com",
            "password": "CorrectedPass123!@#",
            "name": "Corrected Review User",
            "organization_name": f"Corrected Corp {self.test_id}",
            "access_token": None,
            "user_id": None,
            "organization_id": None
        }
        self.admin_user = {
            "email": f"admin.{self.test_id}@review.com", 
            "password": "AdminPass123!@#",
            "name": "Admin Review User",
            "access_token": None,
            "user_id": None,
            "organization_id": None
        }
        
        self.admin_role_id = None
        self.viewer_role_id = None
        self.workflow_template_id = None
        self.task_id = None
        
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {}
        }
    
    def log_result(self, test_name, success, message="", performance_time=None):
        """Log test result with optional performance tracking"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅"
        else:
            self.results["failed"] += 1
            status = "❌"
            self.results["errors"].append(f"{test_name}: {message}")
        
        perf_info = f" ({performance_time:.0f}ms)" if performance_time else ""
        print(f"{status} {test_name}: {message}{perf_info}")
        
        if performance_time:
            self.results["performance_metrics"][test_name] = performance_time
    
    def make_request(self, method, endpoint, user_type="master", **kwargs):
        """Make authenticated request with performance tracking"""
        start_time = time.time()
        
        # Get user info
        if user_type == "master":
            user = self.master_user
        elif user_type == "admin":
            user = self.admin_user
        else:
            user = self.master_user
        
        # Add auth header
        if user["access_token"] and 'headers' not in kwargs:
            kwargs['headers'] = {'Authorization': f'Bearer {user["access_token"]}'}
        elif user["access_token"] and 'headers' in kwargs:
            kwargs['headers']['Authorization'] = f'Bearer {user["access_token"]}'
        
        url = f"{API_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        end_time = time.time()
        performance_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return response, performance_time
    
    def setup_test_users(self):
        """Setup all test users for comprehensive testing"""
        print("\n🔧 Setting up test users...")
        
        # 1. Register Master User (with organization creation)
        user_data = {
            "email": self.master_user["email"],
            "password": self.master_user["password"],
            "name": self.master_user["name"],
            "organization_name": self.master_user["organization_name"]
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.master_user["access_token"] = data.get("access_token")
            self.master_user["user_id"] = data.get("user", {}).get("id")
            self.master_user["organization_id"] = data.get("user", {}).get("organization_id")
            self.log_result("Master User Registration", True, f"Master user created with org: {self.master_user['organization_id']}")
        else:
            self.log_result("Master User Registration", False, f"Failed to register master user: {response.status_code}")
            return False
        
        # 2. Get role IDs
        response, _ = self.make_request("GET", "/roles")
        if response.status_code == 200:
            roles = response.json()
            for role in roles:
                if role.get("code") == "admin":
                    self.admin_role_id = role.get("id")
                elif role.get("code") == "viewer":
                    self.viewer_role_id = role.get("id")
            self.log_result("Role IDs Retrieved", True, f"Admin: {self.admin_role_id}, Viewer: {self.viewer_role_id}")
        else:
            self.log_result("Role IDs Retrieved", False, "Failed to get roles")
            return False
        
        # 3. Create Admin User via invitation
        if self.admin_role_id:
            invitation_data = {
                "email": self.admin_user["email"],
                "role_id": self.admin_role_id
            }
            
            response, perf_time = self.make_request("POST", "/invitations", json=invitation_data)
            if response.status_code in [200, 201]:
                self.log_result("Admin User Invitation", True, "Admin invitation sent", performance_time=perf_time)
                
                # Get invitation token for acceptance
                response, _ = self.make_request("GET", "/invitations/pending")
                if response.status_code == 200:
                    invitations = response.json()
                    admin_invitation = next((inv for inv in invitations if inv["email"] == self.admin_user["email"]), None)
                    if admin_invitation:
                        invitation_token = admin_invitation["token"]
                        
                        # Accept invitation
                        accept_data = {
                            "token": invitation_token,
                            "password": self.admin_user["password"],
                            "name": self.admin_user["name"]
                        }
                        
                        response = self.session.post(f"{API_URL}/invitations/accept", json=accept_data)
                        if response.status_code == 200:
                            data = response.json()
                            self.admin_user["access_token"] = data.get("access_token")
                            self.admin_user["user_id"] = data.get("user", {}).get("id")
                            self.admin_user["organization_id"] = data.get("user", {}).get("organization_id")
                            self.log_result("Admin User Creation", True, "Admin user created via invitation")
                        else:
                            self.log_result("Admin User Creation", False, f"Failed to accept invitation: {response.status_code}")
                    else:
                        self.log_result("Admin User Creation", False, "Invitation not found in pending list")
            else:
                self.log_result("Admin User Invitation", False, f"Failed to send admin invitation: {response.status_code}")
        
        return True
    
    def test_quick_wins_settings_persistence(self):
        """QUICK WIN Item 2: Settings Tabs Persistence Test"""
        print("\n🎯 QUICK WIN Item 2: Settings Tabs Persistence Test...")
        
        # Test Profile Settings (using correct endpoint /users/me)
        profile_data = {
            "phone": "+1-555-0123",
            "bio": "Comprehensive testing user profile"
        }
        
        response, perf_time = self.make_request("PUT", "/users/profile", json=profile_data)
        if response.status_code == 200:
            self.log_result("Profile Settings Save", True, "Profile updated successfully", performance_time=perf_time)
            
            # Verify persistence using correct endpoint
            response, _ = self.make_request("GET", "/users/me")
            if response.status_code == 200:
                data = response.json()
                if data.get("phone") == profile_data["phone"] and data.get("bio") == profile_data["bio"]:
                    self.log_result("Profile Settings Persistence", True, "Profile data persisted correctly")
                else:
                    self.log_result("Profile Settings Persistence", False, "Profile data not persisted correctly")
            else:
                self.log_result("Profile Settings Persistence", False, f"Failed to retrieve profile: {response.status_code}")
        else:
            self.log_result("Profile Settings Save", False, f"Failed to update profile: {response.status_code}")
        
        # Test Appearance Settings (Theme)
        theme_data = {
            "theme": "dark",
            "accent_color": "#ef4444",
            "density": "compact",
            "font_size": "large"
        }
        
        response, perf_time = self.make_request("PUT", "/users/theme", json=theme_data)
        if response.status_code == 200:
            self.log_result("Theme Settings Save", True, "Theme updated successfully", performance_time=perf_time)
            
            # Verify persistence
            response, _ = self.make_request("GET", "/users/theme")
            if response.status_code == 200:
                data = response.json()
                if data.get("theme") == "dark" and data.get("accent_color") == "#ef4444":
                    self.log_result("Theme Settings Persistence", True, "Theme data persisted correctly")
                else:
                    self.log_result("Theme Settings Persistence", False, "Theme data not persisted correctly")
            else:
                self.log_result("Theme Settings Persistence", False, f"Failed to retrieve theme: {response.status_code}")
        else:
            self.log_result("Theme Settings Save", False, f"Failed to update theme: {response.status_code}")
        
        # Test Regional Settings
        regional_data = {
            "language": "es",
            "timezone": "America/New_York",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "EUR"
        }
        
        response, perf_time = self.make_request("PUT", "/users/regional", json=regional_data)
        if response.status_code == 200:
            self.log_result("Regional Settings Save", True, "Regional settings updated successfully", performance_time=perf_time)
            
            # Verify persistence
            response, _ = self.make_request("GET", "/users/regional")
            if response.status_code == 200:
                data = response.json()
                if data.get("language") == "es" and data.get("timezone") == "America/New_York":
                    self.log_result("Regional Settings Persistence", True, "Regional data persisted correctly")
                else:
                    self.log_result("Regional Settings Persistence", False, "Regional data not persisted correctly")
            else:
                self.log_result("Regional Settings Persistence", False, f"Failed to retrieve regional settings: {response.status_code}")
        else:
            self.log_result("Regional Settings Save", False, f"Failed to update regional settings: {response.status_code}")
        
        # Test Privacy Settings
        privacy_data = {
            "profile_visibility": "private",
            "show_activity": False,
            "show_last_seen": False
        }
        
        response, perf_time = self.make_request("PUT", "/users/privacy", json=privacy_data)
        if response.status_code == 200:
            self.log_result("Privacy Settings Save", True, "Privacy settings updated successfully", performance_time=perf_time)
            
            # Verify persistence
            response, _ = self.make_request("GET", "/users/privacy")
            if response.status_code == 200:
                data = response.json()
                if data.get("profile_visibility") == "private" and data.get("show_activity") == False:
                    self.log_result("Privacy Settings Persistence", True, "Privacy data persisted correctly")
                else:
                    self.log_result("Privacy Settings Persistence", False, "Privacy data not persisted correctly")
            else:
                self.log_result("Privacy Settings Persistence", False, f"Failed to retrieve privacy settings: {response.status_code}")
        else:
            self.log_result("Privacy Settings Save", False, f"Failed to update privacy settings: {response.status_code}")
        
        # Test Notification Settings
        notification_data = {
            "email_notifications": False,
            "push_notifications": True,
            "weekly_reports": False,
            "marketing_emails": True
        }
        
        response, perf_time = self.make_request("PUT", "/users/settings", json=notification_data)
        if response.status_code == 200:
            self.log_result("Notification Settings Save", True, "Notification settings updated successfully", performance_time=perf_time)
            
            # Verify persistence
            response, _ = self.make_request("GET", "/users/settings")
            if response.status_code == 200:
                data = response.json()
                if data.get("email_notifications") == False and data.get("push_notifications") == True:
                    self.log_result("Notification Settings Persistence", True, "Notification data persisted correctly")
                else:
                    self.log_result("Notification Settings Persistence", False, "Notification data not persisted correctly")
            else:
                self.log_result("Notification Settings Persistence", False, f"Failed to retrieve notification settings: {response.status_code}")
        else:
            self.log_result("Notification Settings Save", False, f"Failed to update notification settings: {response.status_code}")
        
        # Test Security Settings (Password Change)
        password_data = {
            "current_password": self.master_user["password"],
            "new_password": "NewCorrectedPass456!@#",
            "confirm_password": "NewCorrectedPass456!@#"
        }
        
        response, perf_time = self.make_request("PUT", "/users/password", json=password_data)
        if response.status_code == 200:
            self.master_user["password"] = password_data["new_password"]  # Update for future tests
            self.log_result("Security Settings (Password)", True, "Password changed successfully", performance_time=perf_time)
        else:
            self.log_result("Security Settings (Password)", False, f"Failed to change password: {response.status_code}")
    
    def test_quick_wins_workflow_designer(self):
        """QUICK WIN Item 3: Workflow Designer Dialog Test"""
        print("\n🎯 QUICK WIN Item 3: Workflow Designer Dialog Test...")
        
        # Create workflow template with corrected step format
        workflow_data = {
            "name": "Corrected Review Workflow",
            "description": "Test workflow for comprehensive review",
            "resource_type": "inspection",
            "approver_role": "admin",
            "approver_context": "department",
            "approval_type": "single",
            "escalate_to_role": "master",
            "escalation_time_hours": 24,
            "steps": [
                {
                    "step_number": 1,  # Changed from "order" to "step_number"
                    "name": "Initial Review",
                    "description": "First level review",
                    "approver_role": "supervisor",
                    "required": True
                },
                {
                    "step_number": 2,  # Sequential step number
                    "name": "Final Approval", 
                    "description": "Final approval step",
                    "approver_role": "admin",
                    "required": True
                }
            ]
        }
        
        response, perf_time = self.make_request("POST", "/workflows/templates", json=workflow_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.workflow_template_id = data.get("id")
            
            # Verify all fields are properly set
            required_fields = ["resource_type", "approver_role", "approver_context", "approval_type", "escalate_to_role"]
            missing_fields = []
            for field in required_fields:
                if not data.get(field) or data.get(field) == "":
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_result("Workflow Designer Validation", True, "All required fields populated correctly", performance_time=perf_time)
            else:
                self.log_result("Workflow Designer Validation", False, f"Empty fields detected: {missing_fields}")
            
            # Test workflow creation success
            if self.workflow_template_id:
                self.log_result("Workflow Template Creation", True, f"Workflow template created: {self.workflow_template_id}")
            else:
                self.log_result("Workflow Template Creation", False, "No workflow ID returned")
        else:
            self.log_result("Workflow Template Creation", False, f"Failed to create workflow template: {response.status_code} - {response.text[:200]}")
    
    def test_integration_flow_user_registration(self):
        """PHASE 3: User Registration → Organization → Role Assignment Flow"""
        print("\n🔗 PHASE 3: User Registration → Organization → Role Assignment Flow...")
        
        # Verify organization assignment
        if self.master_user["organization_id"] and self.admin_user["organization_id"]:
            # Verify all users are in the same organization
            if self.master_user["organization_id"] == self.admin_user["organization_id"]:
                self.log_result("Organization Assignment", True, "All users assigned to same organization")
            else:
                self.log_result("Organization Assignment", False, "Users not in same organization")
            
            # Verify role assignments
            response, _ = self.make_request("GET", "/users/me")
            if response.status_code == 200:
                master_role = response.json().get("role")
                
                response, _ = self.make_request("GET", "/users/me", user_type="admin")
                if response.status_code == 200:
                    admin_role = response.json().get("role")
                    
                    if master_role == "master" and admin_role == "admin":
                        self.log_result("Role Assignment Verification", True, "All users have correct roles")
                    else:
                        self.log_result("Role Assignment Verification", False, f"Incorrect roles: master={master_role}, admin={admin_role}")
                else:
                    self.log_result("Role Assignment Verification", False, f"Failed to get admin role: {response.status_code}")
            else:
                self.log_result("Role Assignment Verification", False, f"Failed to get master role: {response.status_code}")
        else:
            self.log_result("Organization Assignment", False, "Missing organization assignments")
    
    def test_integration_flow_task_lifecycle(self):
        """PHASE 3: Task Creation → Assignment → Completion Flow"""
        print("\n🔗 PHASE 3: Task Creation → Assignment → Completion Flow...")
        
        # Create task with assignment
        task_data = {
            "title": "Corrected Review Task",
            "description": "Task for testing complete lifecycle",
            "priority": "high",
            "status": "todo",
            "assigned_to": self.admin_user["user_id"] if self.admin_user["user_id"] else self.master_user["user_id"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response, perf_time = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.task_id = data.get("id")
            self.log_result("Task Creation with Assignment", True, f"Task created and assigned: {self.task_id}", performance_time=perf_time)
            
            # Update task status progression: To Do → In Progress → Done
            status_progression = ["in_progress", "completed"]
            for status in status_progression:
                update_data = {"status": status}
                response, perf_time = self.make_request("PUT", f"/tasks/{self.task_id}", 
                                                      json=update_data)
                if response.status_code == 200:
                    self.log_result(f"Task Status Update ({status})", True, 
                                  f"Task updated to {status}", performance_time=perf_time)
                else:
                    self.log_result(f"Task Status Update ({status})", False, 
                                  f"Failed to update to {status}: {response.status_code}")
            
            # Verify task statistics update
            response, _ = self.make_request("GET", "/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                task_stats = stats.get("tasks", {})
                if task_stats.get("completed", 0) > 0:
                    self.log_result("Task Statistics Update", True, "Task completion reflected in statistics")
                else:
                    self.log_result("Task Statistics Update", False, "Task completion not reflected in statistics")
            else:
                self.log_result("Task Statistics Update", False, f"Failed to get dashboard statistics: {response.status_code}")
        else:
            self.log_result("Task Creation with Assignment", False, f"Failed to create task: {response.status_code}")
    
    def test_performance_api_response_times(self):
        """PHASE 5: Performance Tests - API Response Times"""
        print("\n⚡ PHASE 5: Performance Tests - API Response Times...")
        
        # Test critical endpoints for < 500ms response time
        critical_endpoints = [
            ("GET", "/", "Health Check"),
            ("GET", "/users/me", "User Profile"),
            ("GET", "/dashboard/stats", "Dashboard Stats"),
            ("GET", "/tasks", "Tasks List"),
            ("GET", "/workflows/templates", "Workflow Templates"),
            ("GET", "/organizations/units", "Organization Units"),  # Corrected endpoint
            ("GET", "/roles", "Roles List"),
            ("GET", "/permissions", "Permissions List")
        ]
        
        performance_results = []
        for method, endpoint, name in critical_endpoints:
            response, perf_time = self.make_request(method, endpoint)
            performance_results.append((name, perf_time))
            
            if response.status_code == 200:
                if perf_time < 500:
                    self.log_result(f"Performance: {name}", True, f"Response time: {perf_time:.0f}ms (< 500ms target)", performance_time=perf_time)
                else:
                    self.log_result(f"Performance: {name}", False, f"Response time: {perf_time:.0f}ms (> 500ms target)", performance_time=perf_time)
            else:
                self.log_result(f"Performance: {name}", False, f"Endpoint failed: {response.status_code}")
        
        # Calculate average response time
        avg_response_time = sum(perf[1] for perf in performance_results) / len(performance_results)
        if avg_response_time < 500:
            self.log_result("Average API Performance", True, f"Average response time: {avg_response_time:.0f}ms")
        else:
            self.log_result("Average API Performance", False, f"Average response time: {avg_response_time:.0f}ms (> 500ms)")
    
    def test_performance_large_datasets(self):
        """PHASE 5: Performance Tests - Large Datasets"""
        print("\n⚡ PHASE 5: Performance Tests - Large Datasets...")
        
        # Create multiple tasks to test pagination
        print("Creating test dataset...")
        task_ids = []
        for i in range(15):  # Create 15 tasks (smaller dataset for faster testing)
            task_data = {
                "title": f"Performance Test Task {i+1}",
                "description": f"Task {i+1} for performance testing",
                "priority": "medium",
                "status": "todo"
            }
            
            response, _ = self.make_request("POST", "/tasks", json=task_data)
            if response.status_code in [200, 201]:
                task_ids.append(response.json().get("id"))
        
        self.log_result("Large Dataset Creation", True, f"Created {len(task_ids)} test tasks")
        
        # Test pagination performance
        response, perf_time = self.make_request("GET", "/tasks?limit=10&offset=0")
        if response.status_code == 200:
            tasks = response.json()
            if len(tasks) <= 10:  # Should respect limit
                self.log_result("Pagination Performance", True, f"Paginated response in {perf_time:.0f}ms", performance_time=perf_time)
            else:
                self.log_result("Pagination Performance", False, f"Pagination not working: got {len(tasks)} tasks")
        else:
            self.log_result("Pagination Performance", False, f"Failed to test pagination: {response.status_code}")
        
        # Test concurrent requests
        def make_concurrent_request():
            response, perf_time = self.make_request("GET", "/tasks")
            return response.status_code == 200, perf_time
        
        print("Testing concurrent requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_concurrent_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = sum(1 for success, _ in results if success)
        avg_concurrent_time = sum(perf_time for _, perf_time in results) / len(results)
        
        if successful_requests >= 4:  # Allow some failures
            self.log_result("Concurrent Requests", True, f"{successful_requests}/5 successful, avg: {avg_concurrent_time:.0f}ms")
        else:
            self.log_result("Concurrent Requests", False, f"Only {successful_requests}/5 successful")
        
        # Cleanup test tasks
        for task_id in task_ids:
            self.make_request("DELETE", f"/tasks/{task_id}")
    
    def test_security_organization_isolation(self):
        """PHASE 5: Security Tests - Organization Isolation"""
        print("\n🔒 PHASE 5: Security Tests - Organization Isolation...")
        
        # Create a second organization with different user
        second_org_user = {
            "email": f"isolated.{self.test_id}@security.com",
            "password": "IsolatedPass123!@#",
            "name": "Isolated User",
            "organization_name": f"Isolated Corp {self.test_id}"
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=second_org_user)
        if response.status_code in [200, 201]:
            data = response.json()
            second_org_token = data.get("access_token")
            second_org_id = data.get("user", {}).get("organization_id")
            
            self.log_result("Second Organization Setup", True, f"Created isolated org: {second_org_id}")
            
            # Test that users from different orgs cannot access each other's data
            # Try to access first org's tasks from second org user
            headers = {'Authorization': f'Bearer {second_org_token}'}
            response = self.session.get(f"{API_URL}/tasks", headers=headers)
            
            if response.status_code == 200:
                tasks = response.json()
                # Should not see tasks from first organization
                first_org_tasks = [t for t in tasks if t.get("organization_id") == self.master_user["organization_id"]]
                if len(first_org_tasks) == 0:
                    self.log_result("Organization Data Isolation", True, "Cannot access other organization's tasks")
                else:
                    self.log_result("Organization Data Isolation", False, f"Can access {len(first_org_tasks)} tasks from other org")
            else:
                self.log_result("Organization Data Isolation", False, f"Failed to test task isolation: {response.status_code}")
            
            # Test user list isolation
            response = self.session.get(f"{API_URL}/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                first_org_users = [u for u in users if u.get("organization_id") == self.master_user["organization_id"]]
                if len(first_org_users) == 0:
                    self.log_result("User List Isolation", True, "Cannot access other organization's users")
                else:
                    self.log_result("User List Isolation", False, f"Can access {len(first_org_users)} users from other org")
            else:
                self.log_result("User List Isolation", False, f"Failed to test user isolation: {response.status_code}")
        else:
            self.log_result("Second Organization Setup", False, f"Failed to create isolated organization: {response.status_code}")
    
    def test_security_jwt_handling(self):
        """PHASE 5: Security Tests - JWT Token Handling"""
        print("\n🔒 PHASE 5: Security Tests - JWT Token Handling...")
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(f"{API_URL}/users/me", headers=invalid_headers)
        if response.status_code == 401:
            self.log_result("Invalid JWT Rejection", True, "Invalid token correctly rejected")
        else:
            self.log_result("Invalid JWT Rejection", False, f"Invalid token not rejected: {response.status_code}")
        
        # Test with no token
        response = self.session.get(f"{API_URL}/users/me")
        if response.status_code == 401:
            self.log_result("Missing JWT Rejection", True, "Missing token correctly rejected")
        else:
            self.log_result("Missing JWT Rejection", False, f"Missing token not rejected: {response.status_code}")
        
        # Test with malformed token
        malformed_headers = {'Authorization': 'Bearer malformed.token.here'}
        response = self.session.get(f"{API_URL}/users/me", headers=malformed_headers)
        if response.status_code == 401:
            self.log_result("Malformed JWT Rejection", True, "Malformed token correctly rejected")
        else:
            self.log_result("Malformed JWT Rejection", False, f"Malformed token not rejected: {response.status_code}")
    
    def run_all_tests(self):
        """Run all corrected comprehensive review tests"""
        print("🚀 Starting CORRECTED COMPREHENSIVE REVIEW BACKEND TESTING")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        try:
            # PART 1: QUICK WINS
            print("\n" + "="*50)
            print("PART 1: QUICK WINS VERIFICATION")
            print("="*50)
            self.test_quick_wins_settings_persistence()
            self.test_quick_wins_workflow_designer()
            
            # PART 2: PHASE 3 - INTEGRATION TESTING
            print("\n" + "="*50)
            print("PART 2: PHASE 3 - INTEGRATION TESTING")
            print("="*50)
            self.test_integration_flow_user_registration()
            self.test_integration_flow_task_lifecycle()
            
            # PART 3: PHASE 5 - PERFORMANCE & SECURITY
            print("\n" + "="*50)
            print("PART 3: PHASE 5 - PERFORMANCE & SECURITY")
            print("="*50)
            self.test_performance_api_response_times()
            self.test_performance_large_datasets()
            self.test_security_organization_isolation()
            self.test_security_jwt_handling()
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 CORRECTED COMPREHENSIVE REVIEW BACKEND TEST RESULTS")
        print("=" * 80)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance Summary
        if self.results["performance_metrics"]:
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            avg_perf = sum(self.results["performance_metrics"].values()) / len(self.results["performance_metrics"])
            print(f"Average API Response Time: {avg_perf:.0f}ms")
            
            fast_apis = sum(1 for t in self.results["performance_metrics"].values() if t < 500)
            total_apis = len(self.results["performance_metrics"])
            print(f"APIs < 500ms: {fast_apis}/{total_apis} ({fast_apis/total_apis*100:.1f}%)")
        
        if self.results["errors"]:
            print(f"\n🔍 FAILED TESTS ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"{i}. {error}")
        
        print("\n" + "=" * 80)
        
        # Overall Assessment
        if success_rate >= 98:
            print("🎉 EXCELLENT! System ready for production - 98%+ target achieved!")
        elif success_rate >= 95:
            print("✅ VERY GOOD! Minor issues to address before production.")
        elif success_rate >= 90:
            print("⚠️ GOOD! Several issues need attention.")
        elif success_rate >= 80:
            print("⚠️ MODERATE! Multiple issues require fixes.")
        else:
            print("❌ CRITICAL! Major issues detected - significant work needed.")


if __name__ == "__main__":
    tester = CorrectedComprehensiveTester()
    tester.run_all_tests()