#!/usr/bin/env python3
"""
TARGETED BACKEND TESTING - FOCUSING ON CRITICAL ISSUES
Based on the comprehensive test results, this focuses on:
1. Settings persistence with correct field names
2. Available endpoints only
3. Critical functionality verification
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ts-conversion.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class TargetedBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_email = f"targeted.test.{uuid.uuid4().hex[:8]}@testcorp.com"
        self.test_password = "SecureTestPass123!@#"
        self.access_token = None
        self.user_id = None
        self.organization_id = None
        self.task_id = None
        self.group_id = None
        self.webhook_id = None
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
        """Setup test user"""
        print("\n🔧 Setting up targeted test user...")
        
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password,
            "name": "Targeted Test User",
            "organization_name": "Targeted Test Corp"
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
    
    def test_settings_with_correct_fields(self):
        """Test Settings with Correct Field Names"""
        print("\n⚙️ Testing Settings with Correct Field Names...")
        
        # 1. Theme Preferences (using correct field names from preferences_routes.py)
        theme_data = {
            "theme": "dark",
            "accent_color": "#ef4444",
            "view_density": "compact",  # This is the correct field name
            "font_size": "large"
        }
        response = self.make_request("PUT", "/users/theme", json=theme_data)
        if response.status_code == 200:
            self.log_result("Theme Preferences Save", True, "Theme preferences saved")
        else:
            self.log_result("Theme Preferences Save", False, "Theme preferences save failed", response)
        
        # Verify theme persistence with correct field names
        response = self.make_request("GET", "/users/theme")
        if response.status_code == 200:
            data = response.json()
            if (data.get("theme") == "dark" and data.get("accent_color") == "#ef4444" and 
                data.get("view_density") == "compact" and data.get("font_size") == "large"):
                self.log_result("Theme Preferences Persistence", True, "Theme preferences persisted correctly")
            else:
                self.log_result("Theme Preferences Persistence", False, f"Theme data mismatch: {data}")
        else:
            self.log_result("Theme Preferences Persistence", False, "Failed to retrieve theme preferences", response)
        
        # 2. Privacy Preferences (using correct field names)
        privacy_data = {
            "profile_visibility": "private",
            "show_activity_status": False,
            "show_last_seen": False
        }
        response = self.make_request("PUT", "/users/privacy", json=privacy_data)
        if response.status_code == 200:
            self.log_result("Privacy Preferences Save", True, "Privacy preferences saved")
        else:
            self.log_result("Privacy Preferences Save", False, "Privacy preferences save failed", response)
        
        # Verify privacy persistence with correct field names
        response = self.make_request("GET", "/users/privacy")
        if response.status_code == 200:
            data = response.json()
            if (data.get("profile_visibility") == "private" and data.get("show_activity_status") == False and 
                data.get("show_last_seen") == False):
                self.log_result("Privacy Preferences Persistence", True, "Privacy preferences persisted correctly")
            else:
                self.log_result("Privacy Preferences Persistence", False, f"Privacy data mismatch: {data}")
        else:
            self.log_result("Privacy Preferences Persistence", False, "Failed to retrieve privacy preferences", response)
        
        # 3. Regional Preferences
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
            
            # Verify persistence
            response = self.make_request("GET", "/users/regional")
            if response.status_code == 200:
                data = response.json()
                if (data.get("language") == "es" and data.get("timezone") == "America/New_York"):
                    self.log_result("Regional Preferences Persistence", True, "Regional preferences persisted correctly")
                else:
                    self.log_result("Regional Preferences Persistence", False, f"Regional data mismatch: {data}")
            else:
                self.log_result("Regional Preferences Persistence", False, "Failed to retrieve regional preferences", response)
        else:
            self.log_result("Regional Preferences Save", False, "Regional preferences save failed", response)
        
        # 4. Security Preferences
        security_data = {
            "two_factor_enabled": True,
            "session_timeout": 3600
        }
        response = self.make_request("PUT", "/users/security-prefs", json=security_data)
        if response.status_code == 200:
            self.log_result("Security Preferences Save", True, "Security preferences saved")
            
            # Verify persistence
            response = self.make_request("GET", "/users/security-prefs")
            if response.status_code == 200:
                data = response.json()
                if data.get("session_timeout") == 3600:
                    self.log_result("Security Preferences Persistence", True, "Security preferences persisted correctly")
                else:
                    self.log_result("Security Preferences Persistence", False, f"Security data mismatch: {data}")
            else:
                self.log_result("Security Preferences Persistence", False, "Failed to retrieve security preferences", response)
        else:
            self.log_result("Security Preferences Save", False, "Security preferences save failed", response)
        
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
            
            # Verify persistence
            response = self.make_request("GET", "/users/settings")
            if response.status_code == 200:
                data = response.json()
                if (data.get("email_notifications") == False and data.get("push_notifications") == True):
                    self.log_result("Notification Settings Persistence", True, "Notification settings persisted correctly")
                else:
                    self.log_result("Notification Settings Persistence", False, f"Notification data mismatch: {data}")
            else:
                self.log_result("Notification Settings Persistence", False, "Failed to retrieve notification settings", response)
        else:
            self.log_result("Notification Settings Save", False, "Notification settings save failed", response)
    
    def test_core_functionality(self):
        """Test Core Functionality that Works"""
        print("\n🔧 Testing Core Functionality...")
        
        # 1. Authentication
        response = self.make_request("GET", "/auth/me")
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("email") == self.test_user_email:
                self.log_result("Authentication Verification", True, "JWT token validates correctly")
            else:
                self.log_result("Authentication Verification", False, "Token validation returned wrong user")
        else:
            self.log_result("Authentication Verification", False, "Token validation failed", response)
        
        # 2. Task Creation
        task_data = {
            "title": "Targeted Test Task",
            "description": "Testing core task functionality",
            "priority": "high",
            "status": "todo"
        }
        
        response = self.make_request("POST", "/tasks", json=task_data)
        if response.status_code in [200, 201]:
            self.task_id = response.json().get("id")
            self.log_result("Task Creation", True, f"Task created with ID: {self.task_id}")
        else:
            self.log_result("Task Creation", False, "Failed to create task", response)
        
        # 3. Task Update
        if self.task_id:
            update_data = {
                "title": "Updated Targeted Test Task",
                "status": "in_progress"
            }
            
            response = self.make_request("PUT", f"/tasks/{self.task_id}", json=update_data)
            if response.status_code == 200:
                self.log_result("Task Update", True, "Task updated successfully")
            else:
                self.log_result("Task Update", False, "Failed to update task", response)
        
        # 4. Roles and Permissions
        response = self.make_request("GET", "/roles")
        if response.status_code == 200:
            roles = response.json()
            if len(roles) >= 10:
                self.log_result("Roles System", True, f"Retrieved {len(roles)} roles")
            else:
                self.log_result("Roles System", False, f"Expected at least 10 roles, got {len(roles)}")
        else:
            self.log_result("Roles System", False, "Failed to get roles", response)
        
        response = self.make_request("GET", "/permissions")
        if response.status_code == 200:
            permissions = response.json()
            if len(permissions) >= 20:
                self.log_result("Permissions System", True, f"Retrieved {len(permissions)} permissions")
            else:
                self.log_result("Permissions System", False, f"Expected at least 20 permissions, got {len(permissions)}")
        else:
            self.log_result("Permissions System", False, "Failed to get permissions", response)
    
    def test_working_new_features(self):
        """Test New Features that are Working"""
        print("\n🆕 Testing Working New Features...")
        
        # 1. Groups
        group_data = {
            "name": "Targeted Test Group",
            "description": "Group for targeted testing",
            "type": "project"
        }
        
        response = self.make_request("POST", "/groups", json=group_data)
        if response.status_code in [200, 201]:
            self.group_id = response.json().get("id")
            self.log_result("Group Creation", True, f"Group created: {self.group_id}")
        else:
            self.log_result("Group Creation", False, "Failed to create group", response)
        
        # 2. Webhooks
        webhook_data = {
            "name": "Targeted Test Webhook",
            "url": "https://httpbin.org/post",
            "events": ["task.created", "task.updated"],
            "active": True
        }
        
        response = self.make_request("POST", "/webhooks", json=webhook_data)
        if response.status_code in [200, 201]:
            self.webhook_id = response.json().get("id")
            self.log_result("Webhook Creation", True, f"Webhook created: {self.webhook_id}")
            
            # Test webhook
            test_data = {"test": "payload"}
            response = self.make_request("POST", f"/webhooks/{self.webhook_id}/test", json=test_data)
            if response.status_code == 200:
                self.log_result("Webhook Test", True, "Webhook test successful")
            else:
                self.log_result("Webhook Test", False, "Webhook test failed", response)
        else:
            self.log_result("Webhook Creation", False, "Failed to create webhook", response)
        
        # 3. Notifications
        response = self.make_request("GET", "/notifications")
        if response.status_code == 200:
            notifications = response.json()
            self.log_result("Notifications List", True, f"Retrieved {len(notifications)} notifications")
        else:
            self.log_result("Notifications List", False, "Failed to list notifications", response)
        
        # 4. Analytics (partial)
        response = self.make_request("GET", "/analytics/user-activity")
        if response.status_code == 200:
            activity = response.json()
            self.log_result("Analytics User Activity", True, "User activity analytics retrieved")
        else:
            self.log_result("Analytics User Activity", False, "Failed to get user activity", response)
        
        # 5. Dashboard Stats
        response = self.make_request("GET", "/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            if "users" in stats and "tasks" in stats:
                self.log_result("Dashboard Statistics", True, "Dashboard stats retrieved successfully")
            else:
                self.log_result("Dashboard Statistics", False, "Missing required dashboard stats")
        else:
            self.log_result("Dashboard Statistics", False, "Failed to get dashboard stats", response)
    
    def test_audit_and_security(self):
        """Test Audit and Security Features"""
        print("\n🛡️ Testing Audit and Security...")
        
        # 1. Audit Logs
        response = self.make_request("GET", "/audit/logs?limit=20")
        if response.status_code == 200:
            logs = response.json()
            self.log_result("Audit Logs", True, f"Retrieved {len(logs)} audit logs")
            
            if logs:
                log = logs[0]
                required_fields = ["id", "user_id", "action", "resource_type", "timestamp"]
                if all(field in log for field in required_fields):
                    self.log_result("Audit Log Structure", True, "Audit logs have proper structure")
                else:
                    self.log_result("Audit Log Structure", False, "Missing required audit log fields")
        else:
            self.log_result("Audit Logs", False, "Failed to retrieve audit logs", response)
        
        # 2. Security Headers
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
    
    def identify_missing_endpoints(self):
        """Identify Missing or Non-Working Endpoints"""
        print("\n🔍 Identifying Missing/Non-Working Endpoints...")
        
        missing_endpoints = [
            ("/api/org_units", "Organization Units"),
            ("/api/time-tracking/start", "Time Tracking"),
            ("/api/mentions/search", "Mentions"),
            ("/api/analytics/task-trends", "Analytics Task Trends"),
            ("/api/analytics/tasks-by-status", "Analytics Tasks by Status"),
            ("/api/gdpr/consents", "GDPR Consents"),
            ("/api/bulk-import/validate", "Bulk Import"),
            ("/api/webhooks/{id}/logs", "Webhook Logs")
        ]
        
        for endpoint, name in missing_endpoints:
            # Test if endpoint exists
            test_endpoint = endpoint.replace("{id}", "test-id")
            response = self.make_request("GET", test_endpoint)
            
            if response.status_code == 404:
                self.log_result(f"Missing Endpoint: {name}", False, f"Endpoint {endpoint} returns 404")
            elif response.status_code in [401, 403]:
                self.log_result(f"Endpoint Exists: {name}", True, f"Endpoint {endpoint} exists (auth required)")
            else:
                self.log_result(f"Endpoint Available: {name}", True, f"Endpoint {endpoint} available")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.task_id:
            response = self.make_request("DELETE", f"/tasks/{self.task_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Task", True, "Task deleted successfully")
            else:
                self.log_result("Cleanup Task", False, "Failed to delete task", response)
        
        if self.group_id:
            response = self.make_request("DELETE", f"/groups/{self.group_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Group", True, "Group deleted successfully")
            else:
                self.log_result("Cleanup Group", False, "Failed to delete group", response)
        
        if self.webhook_id:
            response = self.make_request("DELETE", f"/webhooks/{self.webhook_id}")
            if response.status_code == 200:
                self.log_result("Cleanup Webhook", True, "Webhook deleted successfully")
            else:
                self.log_result("Cleanup Webhook", False, "Failed to delete webhook", response)
    
    def run_targeted_tests(self):
        """Run targeted backend tests"""
        print("🎯 Starting TARGETED BACKEND TESTING - FOCUSING ON CRITICAL ISSUES")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        # Run targeted test suites
        try:
            self.test_settings_with_correct_fields()
            self.test_core_functionality()
            self.test_working_new_features()
            self.test_audit_and_security()
            self.identify_missing_endpoints()
            self.cleanup_test_data()
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print targeted test results summary"""
        print("\n" + "=" * 70)
        print("📊 TARGETED BACKEND TEST RESULTS")
        print("=" * 70)
        
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
        
        print("\n" + "=" * 70)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Core backend functionality is working well.")
        elif success_rate >= 80:
            print("✅ GOOD! Most core features working with some issues.")
        elif success_rate >= 70:
            print("⚠️ MODERATE! Several issues need attention.")
        else:
            print("❌ CRITICAL! Major issues detected in core functionality.")


if __name__ == "__main__":
    tester = TargetedBackendTester()
    tester.run_targeted_tests()