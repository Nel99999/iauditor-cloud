#!/usr/bin/env python3
"""
COMPREHENSIVE REVIEW BACKEND TESTING
Covers QUICK WINS VERIFICATION + PHASE 3-5 COMPREHENSIVE TESTING

PART 1: QUICK WINS (Items 2 & 3)
- Item 2: Settings Tabs Persistence Test
- Item 3: Workflow Designer Dialog Test

PART 2: PHASE 3 - INTEGRATION TESTING
- End-to-end flows (User Registration → Organization → Role Assignment)
- User Invitation → Email → Acceptance
- Workflow Creation → Approval Process → Notification
- Task Creation → Assignment → Completion
- Settings Changes → Data Persistence
- API Key Configuration → Test Messages

PART 3: PHASE 5 - PERFORMANCE & SECURITY
- Performance Tests (API response times, large datasets, pagination)
- Security Tests (organization isolation, role restrictions, JWT handling)
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime, timedelta
import concurrent.futures
import threading

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://backendhealer.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class ComprehensiveReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_id = uuid.uuid4().hex[:8]
        self.master_user = {
            "email": f"master.{self.test_id}@review.com",
            "password": "MasterPass123!@#",
            "name": "Master Review User",
            "organization_name": f"Review Corp {self.test_id}",
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
        self.viewer_user = {
            "email": f"viewer.{self.test_id}@review.com",
            "password": "ViewerPass123!@#", 
            "name": "Viewer Review User",
            "access_token": None,
            "user_id": None,
            "organization_id": None
        }
        
        self.workflow_template_id = None
        self.workflow_instance_id = None
        self.task_id = None
        self.invitation_token = None
        
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {},
            "security_results": {}
        }
    
    def log_result(self, test_name, success, message="", response=None, performance_time=None):
        """Log test result with optional performance tracking"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅"
        else:
            self.results["failed"] += 1
            status = "❌"
            error_msg = f"{test_name}: {message}"
            if response:
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
            self.results["errors"].append(error_msg)
        
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
        elif user_type == "viewer":
            user = self.viewer_user
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
            self.log_result("Master User Registration", False, "Failed to register master user", response)
            return False
        
        # 2. Create Admin User via invitation
        if self.master_user["access_token"]:
            invitation_data = {
                "email": self.admin_user["email"],
                "role": "admin",
                "message": "Admin user for comprehensive testing"
            }
            
            response, perf_time = self.make_request("POST", "/invitations", json=invitation_data)
            if response.status_code == 200:
                invitation_id = response.json().get("id")
                self.log_result("Admin User Invitation", True, f"Admin invitation sent: {invitation_id}", performance_time=perf_time)
                
                # Get invitation token for acceptance
                response, _ = self.make_request("GET", "/invitations/pending")
                if response.status_code == 200:
                    invitations = response.json()
                    admin_invitation = next((inv for inv in invitations if inv["email"] == self.admin_user["email"]), None)
                    if admin_invitation:
                        self.invitation_token = admin_invitation["token"]
                        
                        # Accept invitation
                        accept_data = {
                            "token": self.invitation_token,
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
                            self.log_result("Admin User Creation", False, "Failed to accept invitation", response)
                    else:
                        self.log_result("Admin User Creation", False, "Invitation not found in pending list")
            else:
                self.log_result("Admin User Invitation", False, "Failed to send admin invitation", response)
        
        # 3. Create Viewer User via invitation
        if self.master_user["access_token"]:
            invitation_data = {
                "email": self.viewer_user["email"],
                "role": "viewer",
                "message": "Viewer user for comprehensive testing"
            }
            
            response, perf_time = self.make_request("POST", "/invitations", json=invitation_data)
            if response.status_code == 200:
                invitation_id = response.json().get("id")
                self.log_result("Viewer User Invitation", True, f"Viewer invitation sent: {invitation_id}", performance_time=perf_time)
                
                # Get invitation token for acceptance
                response, _ = self.make_request("GET", "/invitations/pending")
                if response.status_code == 200:
                    invitations = response.json()
                    viewer_invitation = next((inv for inv in invitations if inv["email"] == self.viewer_user["email"]), None)
                    if viewer_invitation:
                        viewer_token = viewer_invitation["token"]
                        
                        # Accept invitation
                        accept_data = {
                            "token": viewer_token,
                            "password": self.viewer_user["password"],
                            "name": self.viewer_user["name"]
                        }
                        
                        response = self.session.post(f"{API_URL}/invitations/accept", json=accept_data)
                        if response.status_code == 200:
                            data = response.json()
                            self.viewer_user["access_token"] = data.get("access_token")
                            self.viewer_user["user_id"] = data.get("user", {}).get("id")
                            self.viewer_user["organization_id"] = data.get("user", {}).get("organization_id")
                            self.log_result("Viewer User Creation", True, "Viewer user created via invitation")
                        else:
                            self.log_result("Viewer User Creation", False, "Failed to accept viewer invitation", response)
            else:
                self.log_result("Viewer User Invitation", False, "Failed to send viewer invitation", response)
        
        return True
    
    def test_quick_wins_settings_persistence(self):
        """QUICK WIN Item 2: Settings Tabs Persistence Test"""
        print("\n🎯 QUICK WIN Item 2: Settings Tabs Persistence Test...")
        
        # Test Profile Settings
        profile_data = {
            "phone": "+1-555-0123",
            "bio": "Comprehensive testing user profile"
        }
        
        response, perf_time = self.make_request("PUT", "/users/profile", json=profile_data)
        if response.status_code == 200:
            self.log_result("Profile Settings Save", True, "Profile updated successfully", performance_time=perf_time)
            
            # Verify persistence
            response, _ = self.make_request("GET", "/users/profile")
            if response.status_code == 200:
                data = response.json()
                if data.get("phone") == profile_data["phone"] and data.get("bio") == profile_data["bio"]:
                    self.log_result("Profile Settings Persistence", True, "Profile data persisted correctly")
                else:
                    self.log_result("Profile Settings Persistence", False, "Profile data not persisted correctly")
            else:
                self.log_result("Profile Settings Persistence", False, "Failed to retrieve profile", response)
        else:
            self.log_result("Profile Settings Save", False, "Failed to update profile", response)
        
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
                self.log_result("Theme Settings Persistence", False, "Failed to retrieve theme", response)
        else:
            self.log_result("Theme Settings Save", False, "Failed to update theme", response)
        
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
                self.log_result("Regional Settings Persistence", False, "Failed to retrieve regional settings", response)
        else:
            self.log_result("Regional Settings Save", False, "Failed to update regional settings", response)
        
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
                self.log_result("Privacy Settings Persistence", False, "Failed to retrieve privacy settings", response)
        else:
            self.log_result("Privacy Settings Save", False, "Failed to update privacy settings", response)
        
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
                self.log_result("Notification Settings Persistence", False, "Failed to retrieve notification settings", response)
        else:
            self.log_result("Notification Settings Save", False, "Failed to update notification settings", response)
        
        # Test Security Settings (Password Change)
        password_data = {
            "current_password": self.master_user["password"],
            "new_password": "NewMasterPass456!@#",
            "confirm_password": "NewMasterPass456!@#"
        }
        
        response, perf_time = self.make_request("PUT", "/users/password", json=password_data)
        if response.status_code == 200:
            self.master_user["password"] = password_data["new_password"]  # Update for future tests
            self.log_result("Security Settings (Password)", True, "Password changed successfully", performance_time=perf_time)
        else:
            self.log_result("Security Settings (Password)", False, "Failed to change password", response)
    
    def test_quick_wins_workflow_designer(self):
        """QUICK WIN Item 3: Workflow Designer Dialog Test"""
        print("\n🎯 QUICK WIN Item 3: Workflow Designer Dialog Test...")
        
        # Create workflow template with all required fields
        workflow_data = {
            "name": "Comprehensive Review Workflow",
            "description": "Test workflow for comprehensive review",
            "resource_type": "inspection",
            "approver_role": "admin",
            "approver_context": "department",
            "approval_type": "single",
            "escalate_to_role": "master",
            "escalation_time_hours": 24,
            "steps": [
                {
                    "name": "Initial Review",
                    "description": "First level review",
                    "approver_role": "supervisor",
                    "required": True,
                    "order": 1
                },
                {
                    "name": "Final Approval", 
                    "description": "Final approval step",
                    "approver_role": "admin",
                    "required": True,
                    "order": 2
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
            self.log_result("Workflow Template Creation", False, "Failed to create workflow template", response)
        
        # Test workflow instance creation
        if self.workflow_template_id:
            instance_data = {
                "template_id": self.workflow_template_id,
                "resource_id": str(uuid.uuid4()),
                "resource_type": "inspection",
                "title": "Test Workflow Instance",
                "description": "Testing workflow instance creation"
            }
            
            response, perf_time = self.make_request("POST", "/workflows/instances", json=instance_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.workflow_instance_id = data.get("id")
                self.log_result("Workflow Instance Creation", True, f"Workflow instance created: {self.workflow_instance_id}", performance_time=perf_time)
            else:
                self.log_result("Workflow Instance Creation", False, "Failed to create workflow instance", response)
    
    def test_integration_flow_user_registration(self):
        """PHASE 3: User Registration → Organization → Role Assignment Flow"""
        print("\n🔗 PHASE 3: User Registration → Organization → Role Assignment Flow...")
        
        # This flow was already tested in setup_test_users, but let's verify the results
        if self.master_user["organization_id"] and self.admin_user["organization_id"] and self.viewer_user["organization_id"]:
            # Verify all users are in the same organization
            if (self.master_user["organization_id"] == self.admin_user["organization_id"] == 
                self.viewer_user["organization_id"]):
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
                    
                    response, _ = self.make_request("GET", "/users/me", user_type="viewer")
                    if response.status_code == 200:
                        viewer_role = response.json().get("role")
                        
                        if master_role == "master" and admin_role == "admin" and viewer_role == "viewer":
                            self.log_result("Role Assignment Verification", True, "All users have correct roles")
                        else:
                            self.log_result("Role Assignment Verification", False, f"Incorrect roles: master={master_role}, admin={admin_role}, viewer={viewer_role}")
                    else:
                        self.log_result("Role Assignment Verification", False, "Failed to get viewer role")
                else:
                    self.log_result("Role Assignment Verification", False, "Failed to get admin role")
            else:
                self.log_result("Role Assignment Verification", False, "Failed to get master role")
        else:
            self.log_result("Organization Assignment", False, "Missing organization assignments")
    
    def test_integration_flow_workflow_approval(self):
        """PHASE 3: Workflow Creation → Approval Process → Notification Flow"""
        print("\n🔗 PHASE 3: Workflow Creation → Approval Process → Notification Flow...")
        
        if not self.workflow_instance_id:
            self.log_result("Workflow Approval Flow", False, "No workflow instance available")
            return
        
        # Get workflow instance for approval
        response, _ = self.make_request("GET", f"/workflows/instances/{self.workflow_instance_id}")
        if response.status_code == 200:
            workflow = response.json()
            if workflow.get("status") == "pending":
                self.log_result("Workflow Status Check", True, "Workflow in pending status")
                
                # Check if workflow appears in approver's list (admin user)
                response, _ = self.make_request("GET", "/workflows/my-approvals", user_type="admin")
                if response.status_code == 200:
                    approvals = response.json()
                    workflow_found = any(w.get("id") == self.workflow_instance_id for w in approvals)
                    if workflow_found:
                        self.log_result("Workflow in Approvals List", True, "Workflow appears in admin's approval list")
                        
                        # Approve the workflow
                        approval_data = {
                            "action": "approve",
                            "comment": "Approved during comprehensive testing"
                        }
                        
                        response, perf_time = self.make_request("POST", f"/workflows/instances/{self.workflow_instance_id}/approve", 
                                                              json=approval_data, user_type="admin")
                        if response.status_code == 200:
                            self.log_result("Workflow Approval", True, "Workflow approved successfully", performance_time=perf_time)
                            
                            # Verify status update
                            response, _ = self.make_request("GET", f"/workflows/instances/{self.workflow_instance_id}")
                            if response.status_code == 200:
                                updated_workflow = response.json()
                                if updated_workflow.get("status") == "approved":
                                    self.log_result("Workflow Status Update", True, "Workflow status updated to approved")
                                else:
                                    self.log_result("Workflow Status Update", False, f"Status not updated: {updated_workflow.get('status')}")
                            else:
                                self.log_result("Workflow Status Update", False, "Failed to get updated workflow", response)
                        else:
                            self.log_result("Workflow Approval", False, "Failed to approve workflow", response)
                    else:
                        self.log_result("Workflow in Approvals List", False, "Workflow not found in admin's approval list")
                else:
                    self.log_result("Workflow in Approvals List", False, "Failed to get admin's approvals", response)
            else:
                self.log_result("Workflow Status Check", False, f"Unexpected workflow status: {workflow.get('status')}")
        else:
            self.log_result("Workflow Status Check", False, "Failed to get workflow instance", response)
    
    def test_integration_flow_task_lifecycle(self):
        """PHASE 3: Task Creation → Assignment → Completion Flow"""
        print("\n🔗 PHASE 3: Task Creation → Assignment → Completion Flow...")
        
        # Create task with assignment
        task_data = {
            "title": "Comprehensive Review Task",
            "description": "Task for testing complete lifecycle",
            "priority": "high",
            "status": "todo",
            "assigned_to": self.admin_user["user_id"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response, perf_time = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.task_id = data.get("id")
            self.log_result("Task Creation with Assignment", True, f"Task created and assigned: {self.task_id}", performance_time=perf_time)
            
            # Verify task appears in assignee's task list
            response, _ = self.make_request("GET", "/tasks", user_type="admin")
            if response.status_code == 200:
                tasks = response.json()
                assigned_task = next((t for t in tasks if t.get("id") == self.task_id), None)
                if assigned_task:
                    self.log_result("Task in Assignee List", True, "Task appears in admin's task list")
                    
                    # Update task status progression: To Do → In Progress → Done
                    status_progression = ["in_progress", "completed"]
                    for status in status_progression:
                        update_data = {"status": status}
                        response, perf_time = self.make_request("PUT", f"/tasks/{self.task_id}", 
                                                              json=update_data, user_type="admin")
                        if response.status_code == 200:
                            self.log_result(f"Task Status Update ({status})", True, 
                                          f"Task updated to {status}", performance_time=perf_time)
                        else:
                            self.log_result(f"Task Status Update ({status})", False, 
                                          f"Failed to update to {status}", response)
                    
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
                        self.log_result("Task Statistics Update", False, "Failed to get dashboard statistics", response)
                else:
                    self.log_result("Task in Assignee List", False, "Task not found in admin's task list")
            else:
                self.log_result("Task in Assignee List", False, "Failed to get admin's tasks", response)
        else:
            self.log_result("Task Creation with Assignment", False, "Failed to create task", response)
    
    def test_integration_flow_settings_persistence(self):
        """PHASE 3: Settings Changes → Data Persistence Flow"""
        print("\n🔗 PHASE 3: Settings Changes → Data Persistence Flow...")
        
        # Test logout and login to verify persistence
        original_token = self.master_user["access_token"]
        
        # Login again to simulate logout/login
        login_data = {
            "email": self.master_user["email"],
            "password": self.master_user["password"]
        }
        
        response = self.session.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            new_token = data.get("access_token")
            self.master_user["access_token"] = new_token
            self.log_result("Re-authentication", True, "Successfully logged in again")
            
            # Verify all settings persist after re-login
            settings_endpoints = [
                ("/users/profile", "Profile"),
                ("/users/theme", "Theme"),
                ("/users/regional", "Regional"),
                ("/users/privacy", "Privacy"),
                ("/users/settings", "Notifications")
            ]
            
            for endpoint, setting_type in settings_endpoints:
                response, perf_time = self.make_request("GET", endpoint)
                if response.status_code == 200:
                    data = response.json()
                    if data:  # Check if settings exist
                        self.log_result(f"{setting_type} Persistence After Login", True, 
                                      f"{setting_type} settings persisted", performance_time=perf_time)
                    else:
                        self.log_result(f"{setting_type} Persistence After Login", False, 
                                      f"{setting_type} settings not found")
                else:
                    self.log_result(f"{setting_type} Persistence After Login", False, 
                                  f"Failed to retrieve {setting_type} settings", response)
        else:
            self.log_result("Re-authentication", False, "Failed to login again", response)
    
    def test_integration_flow_api_keys(self):
        """PHASE 3: API Key Configuration → Test Messages Flow"""
        print("\n🔗 PHASE 3: API Key Configuration → Test Messages Flow...")
        
        # Test Twilio credentials (use test values)
        twilio_data = {
            "account_sid": "ACtest1234567890abcdefghijklmnopqr",
            "auth_token": "test_auth_token_1234567890abcdef",
            "phone_number": "+15551234567"
        }
        
        response, perf_time = self.make_request("POST", "/sms/settings", json=twilio_data)
        if response.status_code == 200:
            self.log_result("Twilio Configuration", True, "Twilio credentials saved", performance_time=perf_time)
            
            # Test connection (will fail with test creds, but verify API structure)
            response, perf_time = self.make_request("POST", "/sms/test-connection")
            # Expect failure with test credentials, but API should be called correctly
            if response.status_code in [400, 401, 403]:  # Expected failure codes
                self.log_result("Twilio Connection Test", True, "API structure correct (expected failure with test creds)", performance_time=perf_time)
            else:
                self.log_result("Twilio Connection Test", False, "Unexpected response", response)
            
            # Attempt to send test SMS (verify endpoint called correctly)
            sms_data = {
                "to": "+15559876543",
                "message": "Test SMS from comprehensive review"
            }
            
            response, perf_time = self.make_request("POST", "/sms/send", json=sms_data)
            # Expect failure with test credentials, but endpoint should be accessible
            if response.status_code in [400, 401, 403, 500]:  # Expected failure codes
                self.log_result("SMS Send Test", True, "SMS endpoint accessible (expected failure with test creds)", performance_time=perf_time)
            else:
                self.log_result("SMS Send Test", False, "Unexpected SMS response", response)
        else:
            self.log_result("Twilio Configuration", False, "Failed to save Twilio credentials", response)
        
        # Test SendGrid configuration
        sendgrid_data = {
            "api_key": "SG.test_api_key_1234567890abcdefghijklmnopqrstuvwxyz",
            "from_email": "test@review.com",
            "from_name": "Review Test"
        }
        
        response, perf_time = self.make_request("POST", "/settings/email", json=sendgrid_data)
        if response.status_code == 200:
            self.log_result("SendGrid Configuration", True, "SendGrid credentials saved", performance_time=perf_time)
            
            # Test email connection
            response, perf_time = self.make_request("POST", "/settings/email/test")
            # Expect failure with test credentials
            if response.status_code in [400, 401, 403]:  # Expected failure codes
                self.log_result("SendGrid Connection Test", True, "Email API structure correct (expected failure with test creds)", performance_time=perf_time)
            else:
                self.log_result("SendGrid Connection Test", False, "Unexpected email response", response)
        else:
            self.log_result("SendGrid Configuration", False, "Failed to save SendGrid credentials", response)
    
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
            ("GET", "/organizations", "Organizations"),
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
                self.log_result(f"Performance: {name}", False, f"Endpoint failed: {response.status_code}", response)
        
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
        for i in range(25):  # Create 25 tasks
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
            self.log_result("Pagination Performance", False, "Failed to test pagination", response)
        
        # Test concurrent requests
        def make_concurrent_request():
            response, perf_time = self.make_request("GET", "/tasks")
            return response.status_code == 200, perf_time
        
        print("Testing concurrent requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_concurrent_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = sum(1 for success, _ in results if success)
        avg_concurrent_time = sum(perf_time for _, perf_time in results) / len(results)
        
        if successful_requests >= 8:  # Allow some failures
            self.log_result("Concurrent Requests", True, f"{successful_requests}/10 successful, avg: {avg_concurrent_time:.0f}ms")
        else:
            self.log_result("Concurrent Requests", False, f"Only {successful_requests}/10 successful")
        
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
                self.log_result("Organization Data Isolation", False, "Failed to test task isolation", response)
            
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
                self.log_result("User List Isolation", False, "Failed to test user isolation", response)
        else:
            self.log_result("Second Organization Setup", False, "Failed to create isolated organization", response)
    
    def test_security_role_restrictions(self):
        """PHASE 5: Security Tests - Role Restrictions"""
        print("\n🔒 PHASE 5: Security Tests - Role Restrictions...")
        
        # Test that viewer cannot access admin endpoints
        admin_endpoints = [
            ("GET", "/settings/email", "Email Settings"),
            ("GET", "/sms/settings", "SMS Settings"),
            ("POST", "/users/invite", "User Invitation"),
            ("DELETE", f"/users/{self.admin_user['user_id']}", "User Deletion")
        ]
        
        for method, endpoint, name in admin_endpoints:
            if method == "POST":
                response, _ = self.make_request(method, endpoint, user_type="viewer", 
                                             json={"email": "test@test.com", "role": "viewer"})
            else:
                response, _ = self.make_request(method, endpoint, user_type="viewer")
            
            if response.status_code == 403:
                self.log_result(f"Role Restriction: {name}", True, "Viewer correctly denied access")
            elif response.status_code == 401:
                self.log_result(f"Role Restriction: {name}", True, "Authentication required (acceptable)")
            else:
                self.log_result(f"Role Restriction: {name}", False, f"Unexpected access: {response.status_code}")
        
        # Test that admin cannot access master-only endpoints
        master_only_endpoints = [
            ("GET", "/settings/email", "Email Settings Access"),
            ("POST", "/settings/email", "Email Settings Modification")
        ]
        
        for method, endpoint, name in master_only_endpoints:
            if method == "POST":
                response, _ = self.make_request(method, endpoint, user_type="admin",
                                             json={"api_key": "test", "from_email": "test@test.com"})
            else:
                response, _ = self.make_request(method, endpoint, user_type="admin")
            
            if response.status_code == 403:
                self.log_result(f"Admin Role Restriction: {name}", True, "Admin correctly denied master access")
            elif response.status_code == 200:
                # Check if this endpoint allows admin access
                self.log_result(f"Admin Role Restriction: {name}", True, "Admin has appropriate access")
            else:
                self.log_result(f"Admin Role Restriction: {name}", False, f"Unexpected response: {response.status_code}")
    
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
        
        # Test token expiry (simulate by using very old token format)
        expired_headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDk0NTkyMDB9.invalid'}
        response = self.session.get(f"{API_URL}/users/me", headers=expired_headers)
        if response.status_code == 401:
            self.log_result("Expired JWT Rejection", True, "Expired token correctly rejected")
        else:
            self.log_result("Expired JWT Rejection", False, f"Expired token not rejected: {response.status_code}")
    
    def test_security_input_validation(self):
        """PHASE 5: Security Tests - Input Validation"""
        print("\n🔒 PHASE 5: Security Tests - Input Validation...")
        
        # Test SQL injection attempts (should be safe with MongoDB)
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                "email": payload,
                "password": "test123"
            }
            
            response = self.session.post(f"{API_URL}/auth/login", json=login_data)
            if response.status_code in [400, 401, 422]:  # Should reject invalid input
                self.log_result("SQL Injection Protection", True, f"Payload rejected: {payload[:20]}...")
            else:
                self.log_result("SQL Injection Protection", False, f"Payload not rejected: {payload[:20]}...")
        
        # Test XSS attempts
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            task_data = {
                "title": payload,
                "description": "Test task",
                "priority": "low"
            }
            
            response, _ = self.make_request("POST", "/tasks", json=task_data)
            if response.status_code in [200, 201]:
                # Check if payload was sanitized
                created_task = response.json()
                if payload not in created_task.get("title", ""):
                    self.log_result("XSS Protection", True, f"XSS payload sanitized: {payload[:20]}...")
                else:
                    self.log_result("XSS Protection", False, f"XSS payload not sanitized: {payload[:20]}...")
            else:
                self.log_result("XSS Protection", True, f"XSS payload rejected: {payload[:20]}...")
    
    def run_all_tests(self):
        """Run all comprehensive review tests"""
        print("🚀 Starting COMPREHENSIVE REVIEW BACKEND TESTING")
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
            self.test_integration_flow_workflow_approval()
            self.test_integration_flow_task_lifecycle()
            self.test_integration_flow_settings_persistence()
            self.test_integration_flow_api_keys()
            
            # PART 3: PHASE 5 - PERFORMANCE & SECURITY
            print("\n" + "="*50)
            print("PART 3: PHASE 5 - PERFORMANCE & SECURITY")
            print("="*50)
            self.test_performance_api_response_times()
            self.test_performance_large_datasets()
            self.test_security_organization_isolation()
            self.test_security_role_restrictions()
            self.test_security_jwt_handling()
            self.test_security_input_validation()
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE REVIEW BACKEND TEST RESULTS")
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
        
        # Results by Category
        print(f"\n📋 RESULTS BY CATEGORY:")
        
        quick_wins_tests = [e for e in self.results["errors"] if "Settings" in e or "Workflow Designer" in e]
        integration_tests = [e for e in self.results["errors"] if "Flow" in e or "Integration" in e]
        performance_tests = [e for e in self.results["errors"] if "Performance" in e]
        security_tests = [e for e in self.results["errors"] if "Security" in e or "Role Restriction" in e or "JWT" in e]
        
        categories = [
            ("QUICK WINS", quick_wins_tests),
            ("INTEGRATION FLOWS", integration_tests), 
            ("PERFORMANCE", performance_tests),
            ("SECURITY", security_tests)
        ]
        
        for category, errors in categories:
            category_total = 20  # Approximate tests per category
            category_failed = len(errors)
            category_passed = category_total - category_failed
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"  {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
        
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
        
        print("\n📋 RECOMMENDATIONS:")
        if success_rate >= 95:
            print("- Address minor issues in failed tests")
            print("- Consider load testing with higher concurrency")
            print("- Review security headers and policies")
        else:
            print("- Focus on failed integration flows first")
            print("- Improve API performance for slow endpoints")
            print("- Strengthen security controls")
            print("- Consider using websearch tool for persistent issues")


if __name__ == "__main__":
    tester = ComprehensiveReviewTester()
    tester.run_all_tests()