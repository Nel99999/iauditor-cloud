#!/usr/bin/env python3
"""
COMPREHENSIVE SAVE FUNCTIONALITY TEST
Tests ALL data saving operations across the entire platform
"""

import requests
import json
import uuid
import os
from datetime import datetime

# Get backend URL
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=')[1].strip()
            break

API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveSaveTest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.org_id = None
        self.session = requests.Session()
        self.results = {"total": 0, "passed": 0, "failed": 0, "tests": []}
        
    def log(self, category, operation, success, details="", response=None):
        self.results["total"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅ PASS"
        else:
            self.results["failed"] += 1
            status = "❌ FAIL"
            if response and hasattr(response, 'text'):
                details += f" | Error: {response.text[:200]}"
        
        test = f"{status} | {category} | {operation}"
        if details:
            test += f" | {details}"
        print(test)
        self.results["tests"].append({"category": category, "operation": operation, "success": success, "details": details})
    
    def setup_user(self):
        """Setup test user"""
        print("\n" + "="*80)
        print("SETTING UP TEST USER")
        print("="*80)
        
        user_data = {
            "email": f"comprehensive.test.{uuid.uuid4().hex[:8]}@testcorp.com",
            "password": "ComprehensiveTest123!@#",
            "name": "Comprehensive Test User",
            "organization_name": f"Test Corp {uuid.uuid4().hex[:6]}"
        }
        
        response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.org_id = data.get("user", {}).get("organization_id")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.log("Setup", "User Registration", True, f"User ID: {self.user_id}")
            return True
        else:
            self.log("Setup", "User Registration", False, f"Status: {response.status_code}")
            return False
    
    def test_user_profile_updates(self):
        """Test user profile update operations"""
        print("\n" + "="*80)
        print("TESTING USER PROFILE UPDATES")
        print("="*80)
        
        # Update profile
        profile_data = {"name": "Updated Name", "phone": "+1234567890", "bio": "Test bio"}
        response = self.session.put(f"{API_BASE}/users/profile", json=profile_data)
        self.log("User Profile", "Update Profile", response.status_code == 200, f"Status: {response.status_code}")
        
        # Get profile to verify
        response = self.session.get(f"{API_BASE}/users/me")
        if response.status_code == 200:
            data = response.json()
            verified = data.get("name") == "Updated Name" and data.get("phone") == "+1234567890"
            self.log("User Profile", "Verify Persistence", verified, "Data persists correctly" if verified else "Data not persisted")
        else:
            self.log("User Profile", "Verify Persistence", False, f"Status: {response.status_code}")
    
    def test_password_change(self):
        """Test password change"""
        print("\n" + "="*80)
        print("TESTING PASSWORD CHANGE")
        print("="*80)
        
        pwd_data = {"current_password": "ComprehensiveTest123!@#", "new_password": "NewPassword123!@#"}
        response = self.session.put(f"{API_BASE}/users/password", json=pwd_data)
        self.log("Password", "Change Password", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_all_preferences(self):
        """Test all 5 preference categories"""
        print("\n" + "="*80)
        print("TESTING ALL PREFERENCE CATEGORIES")
        print("="*80)
        
        # Theme preferences
        theme_data = {"theme": "dark", "accent_color": "#ef4444", "view_density": "compact", "font_size": "large"}
        response = self.session.put(f"{API_BASE}/users/theme", json=theme_data)
        self.log("Preferences", "Theme Save", response.status_code == 200, f"Status: {response.status_code}")
        
        response = self.session.get(f"{API_BASE}/users/theme")
        if response.status_code == 200:
            data = response.json()
            verified = data.get("theme") == "dark"
            self.log("Preferences", "Theme Persist", verified, "Theme persists" if verified else "Theme not persisted")
        
        # Regional preferences
        regional_data = {"language": "es", "timezone": "America/New_York", "date_format": "DD/MM/YYYY"}
        response = self.session.put(f"{API_BASE}/users/regional", json=regional_data)
        self.log("Preferences", "Regional Save", response.status_code == 200, f"Status: {response.status_code}")
        
        # Privacy preferences
        privacy_data = {"profile_visibility": "private", "show_activity_status": False}
        response = self.session.put(f"{API_BASE}/users/privacy", json=privacy_data)
        self.log("Preferences", "Privacy Save", response.status_code == 200, f"Status: {response.status_code}")
        
        # Security preferences
        security_data = {"two_factor_enabled": True, "session_timeout": 7200}
        response = self.session.put(f"{API_BASE}/users/security-prefs", json=security_data)
        self.log("Preferences", "Security Save", response.status_code == 200, f"Status: {response.status_code}")
        
        # Notification settings
        notif_data = {"email_notifications": False, "push_notifications": True, "weekly_reports": False}
        response = self.session.put(f"{API_BASE}/users/settings", json=notif_data)
        self.log("Preferences", "Notifications Save", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_organization_crud(self):
        """Test organization unit CRUD operations"""
        print("\n" + "="*80)
        print("TESTING ORGANIZATION CRUD")
        print("="*80)
        
        # Create org unit (root units must be level 1)
        org_data = {"name": "Test Department", "level": 1, "parent_id": None}
        response = self.session.post(f"{API_BASE}/organizations/units", json=org_data)
        unit_id = None
        if response.status_code in [200, 201]:
            unit_id = response.json().get("id")
            self.log("Organization", "Create Unit", True, f"Unit ID: {unit_id}")
        else:
            self.log("Organization", "Create Unit", False, f"Status: {response.status_code}", response=response)
        
        # Update org unit if created
        if unit_id:
            update_data = {"name": "Updated Department"}
            response = self.session.put(f"{API_BASE}/organizations/units/{unit_id}", json=update_data)
            self.log("Organization", "Update Unit", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_task_crud(self):
        """Test task CRUD operations"""
        print("\n" + "="*80)
        print("TESTING TASK CRUD")
        print("="*80)
        
        # Create task
        task_data = {
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "status": "todo"
        }
        response = self.session.post(f"{API_BASE}/tasks", json=task_data)
        task_id = None
        if response.status_code in [200, 201]:
            task_id = response.json().get("id")
            self.log("Tasks", "Create Task", True, f"Task ID: {task_id}")
        else:
            self.log("Tasks", "Create Task", False, f"Status: {response.status_code}")
        
        # Update task if created
        if task_id:
            update_data = {"title": "Updated Task", "status": "in_progress"}
            response = self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data)
            self.log("Tasks", "Update Task", response.status_code == 200, f"Status: {response.status_code}")
            
            # Add comment
            comment_data = {"text": "Test comment"}
            response = self.session.post(f"{API_BASE}/tasks/{task_id}/comments", json=comment_data)
            self.log("Tasks", "Add Comment", response.status_code in [200, 201], f"Status: {response.status_code}")
    
    def test_inspection_crud(self):
        """Test inspection template CRUD"""
        print("\n" + "="*80)
        print("TESTING INSPECTION CRUD")
        print("="*80)
        
        # Create inspection template
        template_data = {
            "name": "Test Inspection",
            "description": "Test description",
            "questions": [
                {"question_text": "Test question?", "question_type": "yes_no", "required": True}
            ]
        }
        response = self.session.post(f"{API_BASE}/inspections/templates", json=template_data)
        template_id = None
        if response.status_code in [200, 201]:
            template_id = response.json().get("id")
            self.log("Inspections", "Create Template", True, f"Template ID: {template_id}")
        else:
            self.log("Inspections", "Create Template", False, f"Status: {response.status_code}")
        
        # Update template if created
        if template_id:
            update_data = {"name": "Updated Inspection"}
            response = self.session.put(f"{API_BASE}/inspections/templates/{template_id}", json=update_data)
            self.log("Inspections", "Update Template", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_checklist_crud(self):
        """Test checklist template CRUD"""
        print("\n" + "="*80)
        print("TESTING CHECKLIST CRUD")
        print("="*80)
        
        # Create checklist template
        template_data = {
            "name": "Test Checklist",
            "description": "Test description",
            "items": [
                {"text": "Test item 1", "required": True}
            ]
        }
        response = self.session.post(f"{API_BASE}/checklists/templates", json=template_data)
        template_id = None
        if response.status_code in [200, 201]:
            template_id = response.json().get("id")
            self.log("Checklists", "Create Template", True, f"Template ID: {template_id}")
        else:
            self.log("Checklists", "Create Template", False, f"Status: {response.status_code}")
        
        # Update template if created
        if template_id:
            update_data = {"name": "Updated Checklist"}
            response = self.session.put(f"{API_BASE}/checklists/templates/{template_id}", json=update_data)
            self.log("Checklists", "Update Template", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_role_crud(self):
        """Test custom role CRUD"""
        print("\n" + "="*80)
        print("TESTING ROLE CRUD")
        print("="*80)
        
        # Create custom role
        role_data = {
            "name": "Test Role",
            "code": "test_role",
            "level": 5,
            "color": "#3b82f6",
            "description": "Test role description"
        }
        response = self.session.post(f"{API_BASE}/roles", json=role_data)
        role_id = None
        if response.status_code in [200, 201]:
            role_id = response.json().get("id")
            self.log("Roles", "Create Custom Role", True, f"Role ID: {role_id}")
        else:
            self.log("Roles", "Create Custom Role", False, f"Status: {response.status_code}")
        
        # Update role if created (requires all fields)
        if role_id:
            update_data = {
                "name": "Updated Role",
                "code": "test_role",
                "level": 5,
                "color": "#10b981",
                "description": "Updated description"
            }
            response = self.session.put(f"{API_BASE}/roles/{role_id}", json=update_data)
            self.log("Roles", "Update Role", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_workflow_crud(self):
        """Test workflow template CRUD"""
        print("\n" + "="*80)
        print("TESTING WORKFLOW CRUD")
        print("="*80)
        
        # Create workflow template
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test description",
            "resource_type": "task",
            "steps": [
                {
                    "step_number": 1,
                    "step_name": "Approval Step",
                    "approver_role": "supervisor",
                    "approval_type": "any_one",
                    "timeout_hours": 24
                }
            ]
        }
        response = self.session.post(f"{API_BASE}/workflows/templates", json=workflow_data)
        workflow_id = None
        if response.status_code in [200, 201]:
            workflow_id = response.json().get("id")
            self.log("Workflows", "Create Template", True, f"Workflow ID: {workflow_id}")
        else:
            self.log("Workflows", "Create Template", False, f"Status: {response.status_code}")
        
        # Update workflow if created
        if workflow_id:
            update_data = {"name": "Updated Workflow"}
            response = self.session.put(f"{API_BASE}/workflows/templates/{workflow_id}", json=update_data)
            self.log("Workflows", "Update Template", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_user_invitation(self):
        """Test user invitation"""
        print("\n" + "="*80)
        print("TESTING USER INVITATION")
        print("="*80)
        
        invite_data = {
            "email": f"invited.{uuid.uuid4().hex[:6]}@test.com",
            "role": "viewer"
        }
        response = self.session.post(f"{API_BASE}/users/invite", json=invite_data)
        self.log("User Management", "Send Invitation", response.status_code in [200, 201], f"Status: {response.status_code}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SAVE TEST SUMMARY")
        print("="*80)
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.results["tests"]:
                if not test["success"]:
                    print(f"  - {test['category']} | {test['operation']} | {test['details']}")
        
        print("\n" + "="*80)
        
        if success_rate >= 95:
            print("✅ EXCELLENT: All critical save operations working!")
        elif success_rate >= 85:
            print("⚠️  GOOD: Most save operations working, minor issues found")
        else:
            print("❌ CRITICAL: Multiple save operations failing")
        
        print("="*80 + "\n")
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        if not self.setup_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        self.test_user_profile_updates()
        self.test_password_change()
        self.test_all_preferences()
        self.test_organization_crud()
        self.test_task_crud()
        self.test_inspection_crud()
        self.test_checklist_crud()
        self.test_role_crud()
        self.test_workflow_crud()
        self.test_user_invitation()
        
        self.print_summary()

if __name__ == "__main__":
    tester = ComprehensiveSaveTest()
    tester.run_all_tests()
