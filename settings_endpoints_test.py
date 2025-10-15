#!/usr/bin/env python3
"""
Critical Settings Endpoints Testing
Tests the reported bug fix for settings not saving due to preferences_routes not being registered.

Testing all 5 preference categories:
1. Theme Preferences (/api/users/theme)
2. Regional Preferences (/api/users/regional) 
3. Privacy Preferences (/api/users/privacy)
4. Security Preferences (/api/users/security-prefs)
5. Notification Settings (/api/users/settings)

Focus: Verify data persistence after save operations
"""

import requests
import json
import os
import uuid
from datetime import datetime

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://typescript-complete-1.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

class SettingsEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_email = f"settings.test.{uuid.uuid4().hex[:8]}@testcorp.com"
        self.test_password = "SettingsTest123!@#"
        self.access_token = None
        self.user_id = None
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
        """Setup test user for settings testing"""
        print("\n🔧 Setting up test user for settings testing...")
        
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password,
            "name": "Settings Test User",
            "organization_name": "Settings Testing Corp"
        }
        
        response = self.session.post(f"{API_URL}/auth/register", json=user_data)
        if response.status_code in [200, 201]:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            
            if self.access_token:
                self.log_result("User Registration", True, f"User created with ID: {self.user_id}")
                return True
            else:
                self.log_result("User Registration", False, "No access token received")
                return False
        else:
            self.log_result("User Setup", False, "Failed to register user", response)
            return False
    
    def test_theme_preferences(self):
        """Test Theme Preferences endpoints"""
        print("\n🎨 Testing Theme Preferences...")
        
        # 1. Get default theme preferences
        response = self.make_request("GET", "/users/theme")
        if response.status_code == 200:
            defaults = response.json()
            expected_fields = ["theme", "accent_color", "view_density", "font_size"]
            if all(field in defaults for field in expected_fields):
                self.log_result("Theme GET Default", True, f"Default theme: {defaults['theme']}, accent: {defaults['accent_color']}")
            else:
                self.log_result("Theme GET Default", False, "Missing required theme fields")
        else:
            self.log_result("Theme GET Default", False, "Failed to get theme preferences", response)
            return
        
        # 2. Update theme preferences
        new_theme_data = {
            "theme": "dark",
            "accent_color": "#ef4444",
            "view_density": "compact",
            "font_size": "large"
        }
        
        response = self.make_request("PUT", "/users/theme", json=new_theme_data)
        if response.status_code == 200:
            self.log_result("Theme PUT Update", True, "Theme preferences updated successfully")
        else:
            self.log_result("Theme PUT Update", False, "Failed to update theme preferences", response)
            return
        
        # 3. Verify persistence by getting updated preferences
        response = self.make_request("GET", "/users/theme")
        if response.status_code == 200:
            updated = response.json()
            if (updated["theme"] == "dark" and 
                updated["accent_color"] == "#ef4444" and
                updated["view_density"] == "compact" and
                updated["font_size"] == "large"):
                self.log_result("Theme Persistence", True, "Theme preferences persisted correctly")
            else:
                self.log_result("Theme Persistence", False, f"Theme not persisted: {updated}")
        else:
            self.log_result("Theme Persistence", False, "Failed to verify theme persistence", response)
    
    def test_regional_preferences(self):
        """Test Regional Preferences endpoints"""
        print("\n🌍 Testing Regional Preferences...")
        
        # 1. Get default regional preferences
        response = self.make_request("GET", "/users/regional")
        if response.status_code == 200:
            defaults = response.json()
            expected_fields = ["language", "timezone", "date_format", "time_format", "currency"]
            if all(field in defaults for field in expected_fields):
                self.log_result("Regional GET Default", True, f"Default language: {defaults['language']}, timezone: {defaults['timezone']}")
            else:
                self.log_result("Regional GET Default", False, "Missing required regional fields")
        else:
            self.log_result("Regional GET Default", False, "Failed to get regional preferences", response)
            return
        
        # 2. Update regional preferences
        new_regional_data = {
            "language": "es",
            "timezone": "America/New_York",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "EUR"
        }
        
        response = self.make_request("PUT", "/users/regional", json=new_regional_data)
        if response.status_code == 200:
            self.log_result("Regional PUT Update", True, "Regional preferences updated successfully")
        else:
            self.log_result("Regional PUT Update", False, "Failed to update regional preferences", response)
            return
        
        # 3. Verify persistence
        response = self.make_request("GET", "/users/regional")
        if response.status_code == 200:
            updated = response.json()
            if (updated["language"] == "es" and 
                updated["timezone"] == "America/New_York" and
                updated["date_format"] == "DD/MM/YYYY" and
                updated["time_format"] == "24h" and
                updated["currency"] == "EUR"):
                self.log_result("Regional Persistence", True, "Regional preferences persisted correctly")
            else:
                self.log_result("Regional Persistence", False, f"Regional not persisted: {updated}")
        else:
            self.log_result("Regional Persistence", False, "Failed to verify regional persistence", response)
    
    def test_privacy_preferences(self):
        """Test Privacy Preferences endpoints"""
        print("\n🔒 Testing Privacy Preferences...")
        
        # 1. Get default privacy preferences
        response = self.make_request("GET", "/users/privacy")
        if response.status_code == 200:
            defaults = response.json()
            expected_fields = ["profile_visibility", "show_activity_status", "show_last_seen"]
            if all(field in defaults for field in expected_fields):
                self.log_result("Privacy GET Default", True, f"Default visibility: {defaults['profile_visibility']}")
            else:
                self.log_result("Privacy GET Default", False, "Missing required privacy fields")
        else:
            self.log_result("Privacy GET Default", False, "Failed to get privacy preferences", response)
            return
        
        # 2. Update privacy preferences
        new_privacy_data = {
            "profile_visibility": "private",
            "show_activity_status": False,
            "show_last_seen": False
        }
        
        response = self.make_request("PUT", "/users/privacy", json=new_privacy_data)
        if response.status_code == 200:
            self.log_result("Privacy PUT Update", True, "Privacy preferences updated successfully")
        else:
            self.log_result("Privacy PUT Update", False, "Failed to update privacy preferences", response)
            return
        
        # 3. Verify persistence
        response = self.make_request("GET", "/users/privacy")
        if response.status_code == 200:
            updated = response.json()
            if (updated["profile_visibility"] == "private" and 
                updated["show_activity_status"] == False and
                updated["show_last_seen"] == False):
                self.log_result("Privacy Persistence", True, "Privacy preferences persisted correctly")
            else:
                self.log_result("Privacy Persistence", False, f"Privacy not persisted: {updated}")
        else:
            self.log_result("Privacy Persistence", False, "Failed to verify privacy persistence", response)
    
    def test_security_preferences(self):
        """Test Security Preferences endpoints"""
        print("\n🛡️ Testing Security Preferences...")
        
        # 1. Get default security preferences
        response = self.make_request("GET", "/users/security-prefs")
        if response.status_code == 200:
            defaults = response.json()
            expected_fields = ["two_factor_enabled", "session_timeout"]
            if all(field in defaults for field in expected_fields):
                self.log_result("Security GET Default", True, f"Default 2FA: {defaults['two_factor_enabled']}, timeout: {defaults['session_timeout']}")
            else:
                self.log_result("Security GET Default", False, "Missing required security fields")
        else:
            self.log_result("Security GET Default", False, "Failed to get security preferences", response)
            return
        
        # 2. Update security preferences
        new_security_data = {
            "two_factor_enabled": True,
            "session_timeout": 7200
        }
        
        response = self.make_request("PUT", "/users/security-prefs", json=new_security_data)
        if response.status_code == 200:
            self.log_result("Security PUT Update", True, "Security preferences updated successfully")
        else:
            self.log_result("Security PUT Update", False, "Failed to update security preferences", response)
            return
        
        # 3. Verify persistence
        response = self.make_request("GET", "/users/security-prefs")
        if response.status_code == 200:
            updated = response.json()
            if (updated["two_factor_enabled"] == True and 
                updated["session_timeout"] == 7200):
                self.log_result("Security Persistence", True, "Security preferences persisted correctly")
            else:
                self.log_result("Security Persistence", False, f"Security not persisted: {updated}")
        else:
            self.log_result("Security Persistence", False, "Failed to verify security persistence", response)
    
    def test_notification_settings(self):
        """Test Notification Settings endpoints"""
        print("\n🔔 Testing Notification Settings...")
        
        # 1. Get default notification settings
        response = self.make_request("GET", "/users/settings")
        if response.status_code == 200:
            defaults = response.json()
            expected_fields = ["email_notifications", "push_notifications", "weekly_reports", "marketing_emails"]
            if all(field in defaults for field in expected_fields):
                self.log_result("Notifications GET Default", True, f"Default email: {defaults['email_notifications']}, push: {defaults['push_notifications']}")
            else:
                self.log_result("Notifications GET Default", False, "Missing required notification fields")
        else:
            self.log_result("Notifications GET Default", False, "Failed to get notification settings", response)
            return
        
        # 2. Update notification settings
        new_notification_data = {
            "email_notifications": False,
            "push_notifications": True,
            "weekly_reports": False,
            "marketing_emails": True
        }
        
        response = self.make_request("PUT", "/users/settings", json=new_notification_data)
        if response.status_code == 200:
            self.log_result("Notifications PUT Update", True, "Notification settings updated successfully")
        else:
            self.log_result("Notifications PUT Update", False, "Failed to update notification settings", response)
            return
        
        # 3. Verify persistence
        response = self.make_request("GET", "/users/settings")
        if response.status_code == 200:
            updated = response.json()
            if (updated["email_notifications"] == False and 
                updated["push_notifications"] == True and
                updated["weekly_reports"] == False and
                updated["marketing_emails"] == True):
                self.log_result("Notifications Persistence", True, "Notification settings persisted correctly")
            else:
                self.log_result("Notifications Persistence", False, f"Notifications not persisted: {updated}")
        else:
            self.log_result("Notifications Persistence", False, "Failed to verify notification persistence", response)
    
    def test_authentication_enforcement(self):
        """Test that all endpoints require authentication"""
        print("\n🔐 Testing Authentication Enforcement...")
        
        endpoints = [
            "/users/theme",
            "/users/regional", 
            "/users/privacy",
            "/users/security-prefs",
            "/users/settings"
        ]
        
        for endpoint in endpoints:
            # Test GET without auth
            response = self.session.get(f"{API_URL}{endpoint}")
            if response.status_code == 401:
                self.log_result(f"Auth Required GET {endpoint}", True, "Properly returns 401 Unauthorized")
            else:
                self.log_result(f"Auth Required GET {endpoint}", False, f"Expected 401, got {response.status_code}")
            
            # Test PUT without auth
            response = self.session.put(f"{API_URL}{endpoint}", json={})
            if response.status_code == 401:
                self.log_result(f"Auth Required PUT {endpoint}", True, "Properly returns 401 Unauthorized")
            else:
                self.log_result(f"Auth Required PUT {endpoint}", False, f"Expected 401, got {response.status_code}")
    
    def run_all_tests(self):
        """Run all settings endpoint tests"""
        print("🚀 Starting Critical Settings Endpoints Testing")
        print("=" * 60)
        print("Testing the fix for preferences_routes registration issue")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user. Aborting tests.")
            return
        
        # Run all test suites
        try:
            self.test_theme_preferences()
            self.test_regional_preferences()
            self.test_privacy_preferences()
            self.test_security_preferences()
            self.test_notification_settings()
            self.test_authentication_enforcement()
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.results["errors"].append(f"Test execution error: {str(e)}")
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 SETTINGS ENDPOINTS TEST RESULTS")
        print("=" * 60)
        
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
        
        print("\n" + "=" * 60)
        
        if success_rate == 100:
            print("🎉 PERFECT! All settings endpoints working correctly - Bug fix successful!")
        elif success_rate >= 90:
            print("✅ EXCELLENT! Settings endpoints working with minor issues.")
        elif success_rate >= 70:
            print("⚠️ MODERATE! Some settings endpoints have issues.")
        else:
            print("❌ CRITICAL! Major issues with settings endpoints - Bug fix may not be complete.")


if __name__ == "__main__":
    tester = SettingsEndpointsTester()
    tester.run_all_tests()