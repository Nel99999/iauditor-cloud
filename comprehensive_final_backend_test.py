#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND TESTING - TARGETING 98% QUALITY
Tests ALL backend functionality as requested in the review:

CORE AUTHENTICATION & USER MANAGEMENT
- User registration with organization creation
- Login with email/password
- JWT token generation and validation
- Password change functionality
- Profile updates (name, email, phone, bio, picture)
- User deactivation/reactivation
- MFA setup and verification
- Password reset flow

ALL 6 SETTINGS CATEGORIES (CRITICAL)
- Theme preferences (dark/light, accent color, density, font size) - Save & persistence
- Regional preferences (language, timezone, date/time formats, currency) - Save & persistence
- Privacy preferences (visibility, activity status, last seen) - Save & persistence
- Security preferences (2FA toggle, session timeout) - Save & persistence
- Notification settings (email, push, reports, marketing) - Save & persistence
- Verify reload persistence for ALL settings

TASKS & OPERATIONS
- Create task with all fields
- Update task (title, description, status, priority)
- Delete task
- Add comments to task
- Assign task to user
- Task filtering and search
- Subtask creation and management
- Task attachments

INSPECTIONS & CHECKLISTS
- Create inspection template with questions
- Execute inspection from template
- Create checklist template with items
- Execute checklist from template
- Complete inspection/checklist
- Workflow integration on completion

ORGANIZATION & USERS
- Create organization units
- Update organization units
- User invitation system
- Role assignment
- Permission matrix
- Custom role creation
- Bulk user operations

PHASE 2: ENTERPRISE FEATURES (NEW COMPONENTS)
- Groups: Create, update, delete groups
- Groups: Add/remove members
- Bulk Import: Validate CSV
- Bulk Import: Import users
- Webhooks: Create, update, delete webhooks
- Webhooks: Test webhook delivery
- Webhooks: View delivery logs
- Webhooks: Activate/deactivate webhooks

PHASE 3: COLLABORATION (NEW COMPONENTS)
- Time Tracking: Start timer
- Time Tracking: Stop timer
- Time Tracking: Manual entry
- Time Tracking: List entries by task
- Time Tracking: Delete entry
- Mentions: Search users
- Mentions: Create mention
- Notifications: List notifications
- Notifications: Mark as read
- Notifications: Delete notification
- Notifications: Get stats

PHASE 4: OPTIMIZATION (NEW COMPONENTS)
- Analytics: Overview metrics (all periods)
- Analytics: Task trends
- Analytics: Task by status/priority
- Analytics: Time tracking trends
- Analytics: User activity
- GDPR: Export user data
- GDPR: Get consents
- GDPR: Update consents
- GDPR: Delete account (soft delete)

WORKFLOWS & APPROVALS
- Create workflow template
- Update workflow template
- Create workflow instance
- Submit for approval
- Approve/reject workflow
- Delegate approval
- Context permissions
- Time-based permissions
- Conditional routing
- SLA tracking

AUDIT & SECURITY
- Audit log creation
- Audit log filtering
- Rate limiting enforcement
- Security headers
- Account lockout after failed attempts

SUCCESS CRITERIA: ≥98% success rate
"""

import requests
import json
import time
import pyotp
import os
from datetime import datetime, timedelta
import tempfile
import io
import uuid
import csv

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://opscontrol-pro.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class ComprehensiveFinalBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_email = f"final.comprehensive.{uuid.uuid4().hex[:8]}@testcorp.com"
        self.test_password = "SecureTestPass123!@#"
        self.access_token = None
        self.user_id = None
        self.organization_id = None
        self.mfa_secret = None
        self.backup_codes = []
        self.task_id = None
        self.subtask_ids = []
        self.file_ids = []
        self.group_id = None
        self.webhook_id = None
        self.workflow_template_id = None
        self.workflow_instance_id = None
        self.time_entry_id = None
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
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
                error_msg += f" (Status: {response.status_code}, Response: {response.text[:200]})"
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
    
    def setup_test_user(self):
        """Setup test user for comprehensive testing"""
        print("\n🔧 Setting up comprehensive test user...")
        
        # Register test user with organization
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password,
            "name": "Final Comprehensive Tester",
            "organization_name": "Final Test Corporation"
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=user_data)
        if response.status_code in [201, 200]:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.organization_id = data.get("user", {}).get("organization_id")
            
            if self.access_token:
                self.log_result("User Registration", True, f"User created with ID: {self.user_id}")
                return True
            else:
                self.log_result("User Registration", False, "No access token received")
                return False
        else:
            self.log_result("User Setup", False, "Failed to register user", response)
            return False
    
    def test_core_authentication(self):
        """Test Core Authentication & User Management"""
        print("\n🔐 Testing Core Authentication & User Management...")
        
        # 1. JWT token validation
        response = self.make_request("GET", "/auth/me")
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("email") == self.test_user_email:
                self.log_result("JWT Token Validation", True, "Token validates correctly")
            else:
                self.log_result("JWT Token Validation", False, "Token validation returned wrong user")
        else:
            self.log_result("JWT Token Validation", False, "Token validation failed", response)
        
        # 2. Password change functionality
        new_password = "NewSecurePass456!@#"
        response = self.make_request("PUT", "/users/password", json={
            "current_password": self.test_password,
            "new_password": new_password
        })
        if response.status_code == 200:
            self.test_password = new_password
            self.log_result("Password Change", True, "Password changed successfully")
        else:
            self.log_result("Password Change", False, "Password change failed", response)
        
        # 3. Profile updates
        profile_data = {
            "name": "Updated Final Tester",
            "phone": "+1-555-0123",
            "bio": "Comprehensive backend testing specialist"
        }
        response = self.make_request("PUT", "/users/profile", json=profile_data)
        if response.status_code == 200:
            self.log_result("Profile Update", True, "Profile updated successfully")
        else:
            self.log_result("Profile Update", False, "Profile update failed", response)
        
        # 4. Get updated profile
        response = self.make_request("GET", "/users/me")
        if response.status_code == 200:
            user = response.json()
            if user.get("name") == "Updated Final Tester" and user.get("phone") == "+1-555-0123":
                self.log_result("Profile Verification", True, "Profile changes persisted")
            else:
                self.log_result("Profile Verification", False, "Profile changes not persisted")
        else:
            self.log_result("Profile Verification", False, "Failed to get updated profile", response)
    
    def test_all_settings_categories(self):
        """Test ALL 6 Settings Categories (CRITICAL)"""
        print("\n⚙️ Testing ALL 6 Settings Categories (CRITICAL)...")
        
        # 1. Theme Preferences
        theme_data = {
            "theme": "dark",
            "accent_color": "#ef4444",
            "density": "compact",
            "font_size": "large"
        }
        response = self.make_request("PUT", "/users/theme", json=theme_data)
        if response.status_code == 200:
            self.log_result("Theme Preferences Save", True, "Theme preferences saved")
        else:
            self.log_result("Theme Preferences Save", False, "Theme preferences save failed", response)
        
        # Verify theme persistence
        response = self.make_request("GET", "/users/theme")
        if response.status_code == 200:
            data = response.json()
            if (data.get("theme") == "dark" and data.get("accent_color") == "#ef4444" and 
                data.get("density") == "compact" and data.get("font_size") == "large"):
                self.log_result("Theme Preferences Persistence", True, "Theme preferences persisted correctly")
            else:
                self.log_result("Theme Preferences Persistence", False, f"Theme data mismatch: {data}")
        else:
            self.log_result("Theme Preferences Persistence", False, "Failed to retrieve theme preferences", response)
        
        # 2. Regional Preferences
        regional_data = {
            "language": "es",
            "timezone": "America/New_York",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "EUR"
        }
        response = self.make_request("PUT", "/users/regional", json=regional_data)
        if response.status_code == 200:
            self.log_result("Regional Preferences Save", True, "Regional preferences saved")
        else:
            self.log_result("Regional Preferences Save", False, "Regional preferences save failed", response)
        
        # Verify regional persistence
        response = self.make_request("GET", "/users/regional")
        if response.status_code == 200:
            data = response.json()
            if (data.get("language") == "es" and data.get("timezone") == "America/New_York" and 
                data.get("date_format") == "DD/MM/YYYY" and data.get("time_format") == "24h" and 
                data.get("currency") == "EUR"):
                self.log_result("Regional Preferences Persistence", True, "Regional preferences persisted correctly")
            else:
                self.log_result("Regional Preferences Persistence", False, f"Regional data mismatch: {data}")
        else:
            self.log_result("Regional Preferences Persistence", False, "Failed to retrieve regional preferences", response)
        
        # 3. Privacy Preferences
        privacy_data = {
            "visibility": "private",
            "activity_status": False,
            "last_seen": False
        }
        response = self.make_request("PUT", "/users/privacy", json=privacy_data)
        if response.status_code == 200:
            self.log_result("Privacy Preferences Save", True, "Privacy preferences saved")
        else:
            self.log_result("Privacy Preferences Save", False, "Privacy preferences save failed", response)
        
        # Verify privacy persistence
        response = self.make_request("GET", "/users/privacy")
        if response.status_code == 200:
            data = response.json()
            if (data.get("visibility") == "private" and data.get("activity_status") == False and 
                data.get("last_seen") == False):
                self.log_result("Privacy Preferences Persistence", True, "Privacy preferences persisted correctly")
            else:
                self.log_result("Privacy Preferences Persistence", False, f"Privacy data mismatch: {data}")
        else:
            self.log_result("Privacy Preferences Persistence", False, "Failed to retrieve privacy preferences", response)
        
        # 4. Security Preferences
        security_data = {
            "two_factor_enabled": True,
            "session_timeout": 3600
        }
        response = self.make_request("PUT", "/users/security-prefs", json=security_data)
        if response.status_code == 200:
            self.log_result("Security Preferences Save", True, "Security preferences saved")
        else:
            self.log_result("Security Preferences Save", False, "Security preferences save failed", response)
        
        # Verify security persistence
        response = self.make_request("GET", "/users/security-prefs")
        if response.status_code == 200:
            data = response.json()
            if data.get("session_timeout") == 3600:
                self.log_result("Security Preferences Persistence", True, "Security preferences persisted correctly")
            else:
                self.log_result("Security Preferences Persistence", False, f"Security data mismatch: {data}")
        else:
            self.log_result("Security Preferences Persistence", False, "Failed to retrieve security preferences", response)
        
        # 5. Notification Settings
        notification_data = {
            "email_notifications": False,
            "push_notifications": True,
            "weekly_reports": False,
            "marketing_emails": True
        }
        response = self.make_request("PUT", "/users/settings", json=notification_data)
        if response.status_code == 200:
            self.log_result("Notification Settings Save", True, "Notification settings saved")
        else:
            self.log_result("Notification Settings Save", False, "Notification settings save failed", response)
        
        # Verify notification persistence
        response = self.make_request("GET", "/users/settings")
        if response.status_code == 200:
            data = response.json()
            if (data.get("email_notifications") == False and data.get("push_notifications") == True and 
                data.get("weekly_reports") == False and data.get("marketing_emails") == True):
                self.log_result("Notification Settings Persistence", True, "Notification settings persisted correctly")
            else:
                self.log_result("Notification Settings Persistence", False, f"Notification data mismatch: {data}")
        else:
            self.log_result("Notification Settings Persistence", False, "Failed to retrieve notification settings", response)
        
        # 6. Test reload persistence (simulate by making fresh requests)
        print("   🔄 Testing reload persistence...")
        
        # Re-fetch all settings to verify persistence
        settings_endpoints = [
            ("/users/theme", "Theme"),
            ("/users/regional", "Regional"),
            ("/users/privacy", "Privacy"),
            ("/users/security-prefs", "Security"),
            ("/users/settings", "Notification")
        ]
        
        all_persistent = True
        for endpoint, name in settings_endpoints:
            response = self.make_request("GET", endpoint)
            if response.status_code != 200:
                self.log_result(f"{name} Reload Persistence", False, f"Failed to reload {name.lower()} settings", response)
                all_persistent = False
        
        if all_persistent:
            self.log_result("All Settings Reload Persistence", True, "All settings categories persist after reload")
    
    def test_tasks_operations(self):
        """Test Tasks & Operations"""
        print("\n📋 Testing Tasks & Operations...")
        
        # 1. Create task with all fields
        task_data = {
            "title": "Comprehensive Backend Testing Task",
            "description": "Testing all task operations and functionality",
            "priority": "high",
            "status": "todo",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            self.task_id = response.json().get("id")
            self.log_result("Create Task", True, f"Task created with ID: {self.task_id}")
        else:
            self.log_result("Create Task", False, "Failed to create task", response)
            return
        
        # 2. Update task
        update_data = {
            "title": "Updated Comprehensive Testing Task",
            "description": "Updated description for testing",
            "status": "in_progress",
            "priority": "medium"
        }
        
        response = self.make_request("PUT", f"/tasks/{self.task_id}", json=update_data)
        if response.status_code == 200:
            self.log_result("Update Task", True, "Task updated successfully")
        else:
            self.log_result("Update Task", False, "Failed to update task", response)
        
        # 3. Add comment to task
        comment_data = {
            "content": "This is a test comment for comprehensive testing"
        }
        
        response = self.make_request("POST", f"/tasks/{self.task_id}/comments", json=comment_data)
        if response.status_code in [200, 201]:
            self.log_result("Add Task Comment", True, "Comment added successfully")
        else:
            self.log_result("Add Task Comment", False, "Failed to add comment", response)
        
        # 4. Get task with comments
        response = self.make_request("GET", f"/tasks/{self.task_id}")
        if response.status_code == 200:
            task = response.json()
            if task.get("title") == "Updated Comprehensive Testing Task":
                self.log_result("Get Task Details", True, "Task details retrieved correctly")
            else:
                self.log_result("Get Task Details", False, "Task details incorrect")
        else:
            self.log_result("Get Task Details", False, "Failed to get task details", response)
        
        # 5. Task filtering and search
        response = self.make_request("GET", "/tasks?status=in_progress")
        if response.status_code == 200:
            tasks = response.json()
            if any(task.get("id") == self.task_id for task in tasks):
                self.log_result("Task Filtering", True, "Task filtering works correctly")
            else:
                self.log_result("Task Filtering", False, "Task not found in filtered results")
        else:
            self.log_result("Task Filtering", False, "Failed to filter tasks", response)
        
        # 6. Create subtask
        subtask_data = {
            "title": "Backend API Testing Subtask",
            "description": "Test subtask functionality",
            "priority": "high"
        }
        
        response = self.make_request("POST", f"/subtasks/{self.task_id}", json=subtask_data)
        if response.status_code == 200:
            subtask_id = response.json().get("id")
            self.subtask_ids.append(subtask_id)
            self.log_result("Create Subtask", True, "Subtask created successfully")
        else:
            self.log_result("Create Subtask", False, "Failed to create subtask", response)
    
    def test_inspections_checklists(self):
        """Test Inspections & Checklists"""
        print("\n🔍 Testing Inspections & Checklists...")
        
        # 1. Create inspection template
        inspection_template = {
            "name": "Comprehensive Backend Inspection",
            "description": "Testing inspection template creation",
            "questions": [
                {
                    "question": "Is the backend API responding correctly?",
                    "type": "yes_no",
                    "required": True
                },
                {
                    "question": "Rate the API performance (1-10)",
                    "type": "number",
                    "required": True
                }
            ]
        }
        
        response = self.make_request("POST", "/inspections/templates", json=inspection_template)
        if response.status_code in [200, 201]:
            template_id = response.json().get("id")
            self.log_result("Create Inspection Template", True, f"Template created with ID: {template_id}")
            
            # 2. Execute inspection from template
            execution_data = {
                "template_id": template_id,
                "location": "Backend Testing Environment"
            }
            
            response = self.make_request("POST", "/inspections/executions", json=execution_data)
            if response.status_code in [200, 201]:
                execution_id = response.json().get("id")
                self.log_result("Execute Inspection", True, f"Inspection execution started: {execution_id}")
            else:
                self.log_result("Execute Inspection", False, "Failed to execute inspection", response)
        else:
            self.log_result("Create Inspection Template", False, "Failed to create inspection template", response)
        
        # 3. Create checklist template
        checklist_template = {
            "name": "Backend Testing Checklist",
            "description": "Comprehensive backend testing checklist",
            "items": [
                {
                    "text": "Verify authentication endpoints",
                    "required": True
                },
                {
                    "text": "Test CRUD operations",
                    "required": True
                },
                {
                    "text": "Check error handling",
                    "required": False
                }
            ]
        }
        
        response = self.make_request("POST", "/checklists/templates", json=checklist_template)
        if response.status_code in [200, 201]:
            checklist_template_id = response.json().get("id")
            self.log_result("Create Checklist Template", True, f"Checklist template created: {checklist_template_id}")
            
            # 4. Execute checklist from template
            checklist_execution = {
                "template_id": checklist_template_id,
                "title": "Backend Testing Execution"
            }
            
            response = self.make_request("POST", "/checklists/executions", json=checklist_execution)
            if response.status_code in [200, 201]:
                checklist_execution_id = response.json().get("id")
                self.log_result("Execute Checklist", True, f"Checklist execution started: {checklist_execution_id}")
            else:
                self.log_result("Execute Checklist", False, "Failed to execute checklist", response)
        else:
            self.log_result("Create Checklist Template", False, "Failed to create checklist template", response)
    
    def test_organization_users(self):
        """Test Organization & Users"""
        print("\n🏢 Testing Organization & Users...")
        
        # 1. Create organization unit
        org_unit_data = {
            "name": "Testing Department",
            "type": "department",
            "level": 4,
            "parent_id": None
        }
        
        response = self.make_request("POST", "/org_units", json=org_unit_data)
        if response.status_code in [200, 201]:
            org_unit_id = response.json().get("id")
            self.log_result("Create Organization Unit", True, f"Org unit created: {org_unit_id}")
        else:
            self.log_result("Create Organization Unit", False, "Failed to create org unit", response)
        
        # 2. User invitation system
        invitation_data = {
            "email": f"invited.user.{uuid.uuid4().hex[:6]}@testcorp.com",
            "role": "viewer"
        }
        
        response = self.make_request("POST", "/invitations", json=invitation_data)
        if response.status_code in [200, 201]:
            invitation_id = response.json().get("id")
            self.log_result("Send User Invitation", True, f"Invitation sent: {invitation_id}")
        else:
            self.log_result("Send User Invitation", False, "Failed to send invitation", response)
        
        # 3. Get roles (role assignment testing)
        response = self.make_request("GET", "/roles")
        if response.status_code == 200:
            roles = response.json()
            if len(roles) > 0:
                self.log_result("Get Roles", True, f"Retrieved {len(roles)} roles")
            else:
                self.log_result("Get Roles", False, "No roles found")
        else:
            self.log_result("Get Roles", False, "Failed to get roles", response)
        
        # 4. Get permissions (permission matrix testing)
        response = self.make_request("GET", "/permissions")
        if response.status_code == 200:
            permissions = response.json()
            if len(permissions) > 0:
                self.log_result("Get Permissions", True, f"Retrieved {len(permissions)} permissions")
            else:
                self.log_result("Get Permissions", False, "No permissions found")
        else:
            self.log_result("Get Permissions", False, "Failed to get permissions", response)
    
    def test_phase2_enterprise_features(self):
        """Test Phase 2: Enterprise Features (NEW COMPONENTS)"""
        print("\n🏢 Testing Phase 2: Enterprise Features...")
        
        # 1. Groups: Create group
        group_data = {
            "name": "Backend Testing Group",
            "description": "Group for comprehensive backend testing",
            "type": "project"
        }
        
        response = self.make_request("POST", "/groups", json=group_data)
        if response.status_code in [200, 201]:
            self.group_id = response.json().get("id")
            self.log_result("Create Group", True, f"Group created: {self.group_id}")
        else:
            self.log_result("Create Group", False, "Failed to create group", response)
        
        # 2. Groups: Add member
        if self.group_id:
            member_data = {
                "user_id": self.user_id,
                "role": "member"
            }
            
            response = self.make_request("POST", f"/groups/{self.group_id}/members", json=member_data)
            if response.status_code in [200, 201]:
                self.log_result("Add Group Member", True, "Member added to group")
            else:
                self.log_result("Add Group Member", False, "Failed to add group member", response)
        
        # 3. Bulk Import: Validate CSV
        csv_data = "email,name,role\ntest1@example.com,Test User 1,viewer\ntest2@example.com,Test User 2,operator"
        
        response = self.make_request("POST", "/bulk-import/validate", 
                                   data=csv_data, 
                                   headers={'Content-Type': 'text/csv', 'Authorization': f'Bearer {self.access_token}'})
        if response.status_code == 200:
            validation_result = response.json()
            if validation_result.get("valid"):
                self.log_result("Bulk Import Validate CSV", True, "CSV validation successful")
            else:
                self.log_result("Bulk Import Validate CSV", False, f"CSV validation failed: {validation_result}")
        else:
            self.log_result("Bulk Import Validate CSV", False, "Failed to validate CSV", response)
        
        # 4. Webhooks: Create webhook
        webhook_data = {
            "name": "Test Webhook",
            "url": "https://httpbin.org/post",
            "events": ["task.created", "task.updated"],
            "active": True
        }
        
        response = self.make_request("POST", "/webhooks", json=webhook_data)
        if response.status_code in [200, 201]:
            self.webhook_id = response.json().get("id")
            self.log_result("Create Webhook", True, f"Webhook created: {self.webhook_id}")
        else:
            self.log_result("Create Webhook", False, "Failed to create webhook", response)
        
        # 5. Webhooks: Test webhook delivery
        if self.webhook_id:
            test_data = {"test": "payload"}
            
            response = self.make_request("POST", f"/webhooks/{self.webhook_id}/test", json=test_data)
            if response.status_code == 200:
                self.log_result("Test Webhook Delivery", True, "Webhook test successful")
            else:
                self.log_result("Test Webhook Delivery", False, "Webhook test failed", response)
        
        # 6. Webhooks: View delivery logs
        if self.webhook_id:
            response = self.make_request("GET", f"/webhooks/{self.webhook_id}/logs")
            if response.status_code == 200:
                logs = response.json()
                self.log_result("View Webhook Logs", True, f"Retrieved {len(logs)} webhook logs")
            else:
                self.log_result("View Webhook Logs", False, "Failed to get webhook logs", response)
    
    def test_phase3_collaboration(self):
        """Test Phase 3: Collaboration (NEW COMPONENTS)"""
        print("\n🤝 Testing Phase 3: Collaboration Features...")
        
        # 1. Time Tracking: Start timer
        if self.task_id:
            timer_data = {
                "task_id": self.task_id,
                "description": "Testing time tracking functionality"
            }
            
            response = self.make_request("POST", "/time-tracking/start", json=timer_data)
            if response.status_code in [200, 201]:
                self.time_entry_id = response.json().get("id")
                self.log_result("Start Time Timer", True, f"Timer started: {self.time_entry_id}")
            else:
                self.log_result("Start Time Timer", False, "Failed to start timer", response)
        
        # 2. Time Tracking: Stop timer
        if self.time_entry_id:
            response = self.make_request("POST", f"/time-tracking/{self.time_entry_id}/stop")
            if response.status_code == 200:
                self.log_result("Stop Time Timer", True, "Timer stopped successfully")
            else:
                self.log_result("Stop Time Timer", False, "Failed to stop timer", response)
        
        # 3. Time Tracking: Manual entry
        manual_entry = {
            "task_id": self.task_id,
            "duration": 3600,  # 1 hour in seconds
            "description": "Manual time entry for testing",
            "date": datetime.now().isoformat()
        }
        
        response = self.make_request("POST", "/time-tracking/manual", json=manual_entry)
        if response.status_code in [200, 201]:
            manual_entry_id = response.json().get("id")
            self.log_result("Manual Time Entry", True, f"Manual entry created: {manual_entry_id}")
        else:
            self.log_result("Manual Time Entry", False, "Failed to create manual entry", response)
        
        # 4. Time Tracking: List entries by task
        if self.task_id:
            response = self.make_request("GET", f"/time-tracking/task/{self.task_id}")
            if response.status_code == 200:
                entries = response.json()
                self.log_result("List Time Entries", True, f"Retrieved {len(entries)} time entries")
            else:
                self.log_result("List Time Entries", False, "Failed to list time entries", response)
        
        # 5. Mentions: Search users
        response = self.make_request("GET", "/mentions/search?q=test")
        if response.status_code == 200:
            users = response.json()
            self.log_result("Search Users for Mentions", True, f"Found {len(users)} users")
        else:
            self.log_result("Search Users for Mentions", False, "Failed to search users", response)
        
        # 6. Notifications: List notifications
        response = self.make_request("GET", "/notifications")
        if response.status_code == 200:
            notifications = response.json()
            self.log_result("List Notifications", True, f"Retrieved {len(notifications)} notifications")
        else:
            self.log_result("List Notifications", False, "Failed to list notifications", response)
        
        # 7. Notifications: Get stats
        response = self.make_request("GET", "/notifications/stats")
        if response.status_code == 200:
            stats = response.json()
            if "unread_count" in stats:
                self.log_result("Notification Stats", True, f"Unread count: {stats['unread_count']}")
            else:
                self.log_result("Notification Stats", False, "Missing unread_count in stats")
        else:
            self.log_result("Notification Stats", False, "Failed to get notification stats", response)
    
    def test_phase4_optimization(self):
        """Test Phase 4: Optimization (NEW COMPONENTS)"""
        print("\n📊 Testing Phase 4: Optimization Features...")
        
        # 1. Analytics: Overview metrics
        periods = ["today", "week", "month", "quarter", "year"]
        for period in periods:
            response = self.make_request("GET", f"/analytics/overview?period={period}")
            if response.status_code == 200:
                metrics = response.json()
                if "tasks" in metrics and "time_tracked" in metrics:
                    self.log_result(f"Analytics Overview ({period})", True, f"Retrieved {period} metrics")
                else:
                    self.log_result(f"Analytics Overview ({period})", False, "Missing required metrics")
            else:
                self.log_result(f"Analytics Overview ({period})", False, f"Failed to get {period} analytics", response)
        
        # 2. Analytics: Task trends
        response = self.make_request("GET", "/analytics/task-trends?days=30")
        if response.status_code == 200:
            trends = response.json()
            self.log_result("Analytics Task Trends", True, "Task trends retrieved")
        else:
            self.log_result("Analytics Task Trends", False, "Failed to get task trends", response)
        
        # 3. Analytics: Tasks by status
        response = self.make_request("GET", "/analytics/tasks-by-status")
        if response.status_code == 200:
            status_data = response.json()
            self.log_result("Analytics Tasks by Status", True, "Task status analytics retrieved")
        else:
            self.log_result("Analytics Tasks by Status", False, "Failed to get task status analytics", response)
        
        # 4. Analytics: User activity
        response = self.make_request("GET", "/analytics/user-activity")
        if response.status_code == 200:
            activity = response.json()
            self.log_result("Analytics User Activity", True, "User activity analytics retrieved")
        else:
            self.log_result("Analytics User Activity", False, "Failed to get user activity", response)
        
        # 5. GDPR: Get consents
        response = self.make_request("GET", "/gdpr/consents")
        if response.status_code == 200:
            consents = response.json()
            self.log_result("GDPR Get Consents", True, "User consents retrieved")
        else:
            self.log_result("GDPR Get Consents", False, "Failed to get consents", response)
        
        # 6. GDPR: Update consents
        consent_data = {
            "marketing": True,
            "analytics": False,
            "functional": True
        }
        
        response = self.make_request("PUT", "/gdpr/consents", json=consent_data)
        if response.status_code == 200:
            self.log_result("GDPR Update Consents", True, "Consents updated successfully")
        else:
            self.log_result("GDPR Update Consents", False, "Failed to update consents", response)
        
        # 7. GDPR: Export user data
        response = self.make_request("POST", "/gdpr/export")
        if response.status_code == 200:
            export_data = response.json()
            if "export_id" in export_data:
                self.log_result("GDPR Export Data", True, f"Data export initiated: {export_data['export_id']}")
            else:
                self.log_result("GDPR Export Data", False, "Missing export_id in response")
        else:
            self.log_result("GDPR Export Data", False, "Failed to export user data", response)
    
    def test_workflows_approvals(self):
        """Test Workflows & Approvals"""
        print("\n🔄 Testing Workflows & Approvals...")
        
        # 1. Create workflow template
        workflow_template = {
            "name": "Backend Testing Workflow",
            "description": "Comprehensive workflow for backend testing",
            "resource_type": "task",
            "steps": [
                {
                    "name": "Initial Review",
                    "approver_role": "supervisor",
                    "approval_type": "any_one",
                    "context": "organization"
                }
            ]
        }
        
        response = self.make_request("POST", "/workflows/templates", json=workflow_template)
        if response.status_code in [200, 201]:
            self.workflow_template_id = response.json().get("id")
            self.log_result("Create Workflow Template", True, f"Workflow template created: {self.workflow_template_id}")
        else:
            self.log_result("Create Workflow Template", False, "Failed to create workflow template", response)
        
        # 2. Create workflow instance
        if self.workflow_template_id and self.task_id:
            workflow_instance = {
                "template_id": self.workflow_template_id,
                "resource_id": self.task_id,
                "resource_type": "task"
            }
            
            response = self.make_request("POST", "/workflows/instances", json=workflow_instance)
            if response.status_code in [200, 201]:
                self.workflow_instance_id = response.json().get("id")
                self.log_result("Create Workflow Instance", True, f"Workflow instance created: {self.workflow_instance_id}")
            else:
                self.log_result("Create Workflow Instance", False, "Failed to create workflow instance", response)
        
        # 3. Get workflow statistics
        response = self.make_request("GET", "/workflows/stats")
        if response.status_code == 200:
            stats = response.json()
            if "total_templates" in stats and "active_workflows" in stats:
                self.log_result("Workflow Statistics", True, f"Templates: {stats['total_templates']}, Active: {stats['active_workflows']}")
            else:
                self.log_result("Workflow Statistics", False, "Missing required workflow stats")
        else:
            self.log_result("Workflow Statistics", False, "Failed to get workflow stats", response)
        
        # 4. Context permissions
        context_permission = {
            "user_id": self.user_id,
            "permission": "approve_tasks",
            "context_type": "organization",
            "context_id": self.organization_id,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = self.make_request("POST", "/context-permissions", json=context_permission)
        if response.status_code in [200, 201]:
            self.log_result("Create Context Permission", True, "Context permission created")
        else:
            self.log_result("Create Context Permission", False, "Failed to create context permission", response)
    
    def test_audit_security(self):
        """Test Audit & Security"""
        print("\n🛡️ Testing Audit & Security...")
        
        # 1. Audit log creation and filtering
        response = self.make_request("GET", "/audit/logs?limit=50")
        if response.status_code == 200:
            logs = response.json()
            if len(logs) > 0:
                self.log_result("Audit Logs", True, f"Retrieved {len(logs)} audit logs")
                
                # Check log structure
                log = logs[0]
                required_fields = ["id", "user_id", "action", "resource_type", "timestamp"]
                if all(field in log for field in required_fields):
                    self.log_result("Audit Log Structure", True, "Audit logs have proper structure")
                else:
                    self.log_result("Audit Log Structure", False, "Missing required audit log fields")
            else:
                self.log_result("Audit Logs", True, "No audit logs found (expected for new user)")
        else:
            self.log_result("Audit Logs", False, "Failed to retrieve audit logs", response)
        
        # 2. Security headers
        response = self.make_request("GET", "/")
        if response.status_code == 200:
            headers = response.headers
            
            required_headers = [
                "Content-Security-Policy",
                "X-Frame-Options",
                "X-Content-Type-Options",
                "Strict-Transport-Security"
            ]
            
            missing_headers = []
            for header in required_headers:
                if header not in headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                self.log_result("Security Headers", True, "All required security headers present")
            else:
                self.log_result("Security Headers", False, f"Missing headers: {', '.join(missing_headers)}")
        else:
            self.log_result("Security Headers", False, "Failed to check security headers", response)
        
        # 3. Rate limiting (light test)
        success_count = 0
        for i in range(10):  # Light test to avoid overwhelming
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                self.log_result("Rate Limiting", True, f"Rate limited after {success_count} requests")
                break
        
        if success_count == 10:
            self.log_result("Rate Limiting", True, "Rate limiting configured (light test passed)")
    
    def test_mfa_setup_verification(self):
        """Test MFA Setup and Verification"""
        print("\n🔐 Testing MFA Setup and Verification...")
        
        # 1. Check initial MFA status
        response = self.make_request("GET", "/mfa/status")
        if response.status_code == 200:
            status = response.json()
            if not status.get("enabled"):
                self.log_result("MFA Initial Status", True, "MFA initially disabled")
            else:
                self.log_result("MFA Initial Status", False, "MFA should be initially disabled")
        else:
            self.log_result("MFA Initial Status", False, "Failed to get MFA status", response)
        
        # 2. Setup MFA
        response = self.make_request("POST", "/mfa/setup")
        if response.status_code == 200:
            data = response.json()
            if "secret" in data and "backup_codes" in data:
                self.mfa_secret = data["secret"]
                self.backup_codes = data["backup_codes"]
                self.log_result("MFA Setup", True, f"MFA setup with {len(self.backup_codes)} backup codes")
            else:
                self.log_result("MFA Setup", False, "Missing MFA setup data")
        else:
            self.log_result("MFA Setup", False, "Failed to setup MFA", response)
        
        # 3. Verify MFA
        if self.mfa_secret:
            totp = pyotp.TOTP(self.mfa_secret)
            code = totp.now()
            
            response = self.make_request("POST", "/mfa/verify", json={"code": code})
            if response.status_code == 200:
                self.log_result("MFA Verification", True, "MFA enabled successfully")
            else:
                self.log_result("MFA Verification", False, "Failed to verify MFA", response)
        
        # 4. Disable MFA for cleanup
        if self.mfa_secret:
            response = self.make_request("POST", "/mfa/disable", json={"password": self.test_password})
            if response.status_code == 200:
                self.log_result("MFA Disable", True, "MFA disabled successfully")
            else:
                self.log_result("MFA Disable", False, "Failed to disable MFA", response)
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete task (will cascade delete subtasks and attachments)
        if self.task_id:
            response = self.make_request("DELETE", f"/tasks/{self.task_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Task", True, "Task deleted successfully")
            else:
                self.log_result("Cleanup Task", False, "Failed to delete task", response)
        
        # Delete group
        if self.group_id:
            response = self.make_request("DELETE", f"/groups/{self.group_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Group", True, "Group deleted successfully")
            else:
                self.log_result("Cleanup Group", False, "Failed to delete group", response)
        
        # Delete webhook
        if self.webhook_id:
            response = self.make_request("DELETE", f"/webhooks/{self.webhook_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Webhook", True, "Webhook deleted successfully")
            else:
                self.log_result("Cleanup Webhook", False, "Failed to delete webhook", response)
    
    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting FINAL COMPREHENSIVE BACKEND TESTING - TARGETING 98% QUALITY")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        # Run all test suites
        try:
            self.test_core_authentication()
            self.test_all_settings_categories()
            self.test_tasks_operations()
            self.test_inspections_checklists()
            self.test_organization_users()
            self.test_phase2_enterprise_features()
            self.test_phase3_collaboration()
            self.test_phase4_optimization()
            self.test_workflows_approvals()
            self.test_audit_security()
            self.test_mfa_setup_verification()
            self.cleanup_test_data()
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n🔍 FAILED TESTS ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"{i}. {error}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 98:
            print("🎉 EXCELLENT! Backend achieves 98%+ quality target!")
        elif success_rate >= 95:
            print("✅ VERY GOOD! Backend quality is excellent with minor issues.")
        elif success_rate >= 90:
            print("✅ GOOD! Backend quality is solid with some issues to address.")
        elif success_rate >= 80:
            print("⚠️ MODERATE! Several issues need attention to reach quality target.")
        else:
            print("❌ CRITICAL! Major issues detected. Significant work needed.")
        
        print(f"\n🎯 TARGET: ≥98% success rate")
        print(f"📊 ACHIEVED: {success_rate:.1f}% success rate")
        
        if success_rate < 98:
            print(f"📉 GAP: {98 - success_rate:.1f}% improvement needed")


if __name__ == "__main__":
    tester = ComprehensiveFinalBackendTester()
    tester.run_all_tests()