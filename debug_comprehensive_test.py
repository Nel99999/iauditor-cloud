#!/usr/bin/env python3
"""
Debug Comprehensive Test - Identify and fix issues
"""

import requests
import json
import os
import uuid

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://auth-workflow-hub.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class DebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_id = uuid.uuid4().hex[:8]
        self.master_user = {
            "email": f"debug.{self.test_id}@test.com",
            "password": "DebugPass123!@#",
            "name": "Debug User",
            "organization_name": f"Debug Corp {self.test_id}",
            "access_token": None,
            "user_id": None,
            "organization_id": None
        }
        self.admin_role_id = None
        self.viewer_role_id = None
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test result"""
        if success:
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")
            if response:
                print(f"   Status: {response.status_code}, Response: {response.text[:500]}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make authenticated request"""
        if self.master_user["access_token"] and 'headers' not in kwargs:
            kwargs['headers'] = {'Authorization': f'Bearer {self.master_user["access_token"]}'}
        elif self.master_user["access_token"] and 'headers' in kwargs:
            kwargs['headers']['Authorization'] = f'Bearer {self.master_user["access_token"]}'
        
        url = f"{API_URL}{endpoint}"
        return self.session.request(method, url, **kwargs)
    
    def setup_user(self):
        """Setup test user"""
        print("\n🔧 Setting up debug user...")
        
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
            self.log_result("User Registration", True, f"User created: {self.master_user['user_id']}")
            return True
        else:
            self.log_result("User Registration", False, "Failed to register user", response)
            return False
    
    def debug_roles(self):
        """Debug role system"""
        print("\n🔍 Debugging Roles...")
        
        response = self.make_request("GET", "/roles")
        if response.status_code == 200:
            roles = response.json()
            self.log_result("Get Roles", True, f"Found {len(roles)} roles")
            
            # Find admin and viewer role IDs
            for role in roles:
                if role.get("code") == "admin":
                    self.admin_role_id = role.get("id")
                    print(f"   Admin role ID: {self.admin_role_id}")
                elif role.get("code") == "viewer":
                    self.viewer_role_id = role.get("id")
                    print(f"   Viewer role ID: {self.viewer_role_id}")
        else:
            self.log_result("Get Roles", False, "Failed to get roles", response)
    
    def debug_invitations(self):
        """Debug invitation system"""
        print("\n🔍 Debugging Invitations...")
        
        if not self.admin_role_id:
            self.log_result("Invitation Test", False, "No admin role ID available")
            return
        
        invitation_data = {
            "email": f"invited.{self.test_id}@test.com",
            "role_id": self.admin_role_id
        }
        
        response = self.make_request("POST", "/invitations", json=invitation_data)
        if response.status_code in [200, 201]:
            self.log_result("Create Invitation", True, "Invitation created successfully")
            
            # Test get pending invitations
            response = self.make_request("GET", "/invitations/pending")
            if response.status_code == 200:
                invitations = response.json()
                self.log_result("Get Pending Invitations", True, f"Found {len(invitations)} pending invitations")
            else:
                self.log_result("Get Pending Invitations", False, "Failed to get pending invitations", response)
        else:
            self.log_result("Create Invitation", False, "Failed to create invitation", response)
    
    def debug_profile_endpoints(self):
        """Debug profile endpoints"""
        print("\n🔍 Debugging Profile Endpoints...")
        
        # Test profile endpoint
        response = self.make_request("GET", "/users/profile")
        print(f"Profile endpoint status: {response.status_code}")
        if response.status_code == 200:
            self.log_result("Get Profile", True, "Profile endpoint working")
        else:
            self.log_result("Get Profile", False, f"Profile endpoint failed - {response.status_code}: {response.text[:200]}")
        
        # Test users/me endpoint
        response = self.make_request("GET", "/users/me")
        if response.status_code == 200:
            self.log_result("Get Users/Me", True, "Users/me endpoint working")
        else:
            self.log_result("Get Users/Me", False, "Users/me endpoint failed", response)
    
    def debug_workflow_endpoints(self):
        """Debug workflow endpoints"""
        print("\n🔍 Debugging Workflow Endpoints...")
        
        # Test workflow templates endpoint
        response = self.make_request("GET", "/workflows/templates")
        if response.status_code == 200:
            self.log_result("Get Workflow Templates", True, "Workflow templates endpoint working")
        else:
            self.log_result("Get Workflow Templates", False, "Workflow templates endpoint failed", response)
        
        # Test creating workflow template
        workflow_data = {
            "name": "Debug Workflow",
            "description": "Test workflow",
            "resource_type": "inspection",
            "approver_role": "admin",
            "approver_context": "department",
            "approval_type": "single",
            "escalate_to_role": "master",
            "escalation_time_hours": 24,
            "steps": [
                {
                    "name": "Review",
                    "description": "Review step",
                    "approver_role": "admin",
                    "required": True,
                    "order": 1
                }
            ]
        }
        
        response = self.make_request("POST", "/workflows/templates", json=workflow_data)
        print(f"Workflow creation status: {response.status_code}")
        print(f"Workflow creation response: {response.text[:300]}")
        if response.status_code in [200, 201]:
            self.log_result("Create Workflow Template", True, "Workflow template created")
        else:
            self.log_result("Create Workflow Template", False, f"Failed to create workflow template - {response.status_code}: {response.text[:200]}")
    
    def debug_settings_endpoints(self):
        """Debug settings endpoints"""
        print("\n🔍 Debugging Settings Endpoints...")
        
        # Test various settings endpoints
        settings_endpoints = [
            ("/users/theme", "Theme Settings"),
            ("/users/regional", "Regional Settings"),
            ("/users/privacy", "Privacy Settings"),
            ("/users/settings", "Notification Settings")
        ]
        
        for endpoint, name in settings_endpoints:
            # Test GET
            response = self.make_request("GET", endpoint)
            if response.status_code == 200:
                self.log_result(f"GET {name}", True, f"{name} GET working")
            else:
                self.log_result(f"GET {name}", False, f"{name} GET failed", response)
    
    def debug_organizations_endpoint(self):
        """Debug organizations endpoint"""
        print("\n🔍 Debugging Organizations Endpoint...")
        
        response = self.make_request("GET", "/organizations")
        if response.status_code == 200:
            self.log_result("Get Organizations", True, "Organizations endpoint working")
        else:
            self.log_result("Get Organizations", False, "Organizations endpoint failed", response)
        
        # Try alternative endpoint
        response = self.make_request("GET", "/org_units")
        if response.status_code == 200:
            self.log_result("Get Org Units", True, "Org units endpoint working")
        else:
            self.log_result("Get Org Units", False, "Org units endpoint failed", response)
    
    def debug_api_keys_endpoints(self):
        """Debug API keys endpoints"""
        print("\n🔍 Debugging API Keys Endpoints...")
        
        # Test SMS settings
        response = self.make_request("GET", "/sms/settings")
        if response.status_code == 200:
            self.log_result("Get SMS Settings", True, "SMS settings endpoint working")
        else:
            self.log_result("Get SMS Settings", False, "SMS settings endpoint failed", response)
        
        # Test email settings
        response = self.make_request("GET", "/settings/email")
        if response.status_code == 200:
            self.log_result("Get Email Settings", True, "Email settings endpoint working")
        else:
            self.log_result("Get Email Settings", False, "Email settings endpoint failed", response)
    
    def run_debug_tests(self):
        """Run all debug tests"""
        print("🚀 Starting Debug Tests")
        print("=" * 50)
        
        if not self.setup_user():
            return
        
        self.debug_roles()
        self.debug_invitations()
        self.debug_profile_endpoints()
        self.debug_workflow_endpoints()
        self.debug_settings_endpoints()
        self.debug_organizations_endpoint()
        self.debug_api_keys_endpoints()
        
        print("\n" + "=" * 50)
        print("🔍 Debug Tests Complete")


if __name__ == "__main__":
    tester = DebugTester()
    tester.run_debug_tests()