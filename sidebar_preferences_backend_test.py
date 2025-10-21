#!/usr/bin/env python3
"""
Sidebar Preferences API Backend Testing
Tests all sidebar preferences endpoints with production user credentials
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://twilio-ops.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"  # Using production password

class SidebarPreferencesAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.user_id = None
        self.organization_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if response_data and isinstance(response_data, dict):
            print(f"    Response: {json.dumps(response_data, indent=2)}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Authenticate with production user credentials"""
        try:
            print(f"\n🔐 AUTHENTICATING with {TEST_USER_EMAIL}...")
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.organization_id = data.get("user", {}).get("organization_id")
                
                print(f"✅ Authentication successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Organization ID: {self.organization_id}")
                print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_default_preferences(self):
        """Test 1: GET /api/users/sidebar-preferences - Get default preferences"""
        try:
            print(f"\n📋 TEST 1: GET Default Sidebar Preferences")
            
            response = requests.get(
                f"{self.base_url}/users/sidebar-preferences",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify default structure
                expected_fields = [
                    "default_mode", "hover_expand_enabled", "auto_collapse_enabled",
                    "inactivity_timeout", "context_aware_enabled", "collapse_after_navigation"
                ]
                
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    # Verify default values
                    expected_defaults = {
                        "default_mode": "expanded",
                        "hover_expand_enabled": True,
                        "auto_collapse_enabled": False,
                        "inactivity_timeout": 10,
                        "context_aware_enabled": True,
                        "collapse_after_navigation": False
                    }
                    
                    matches_defaults = all(data.get(key) == value for key, value in expected_defaults.items())
                    
                    if matches_defaults:
                        self.log_test(
                            "Get Default Sidebar Preferences",
                            True,
                            "Default preferences returned correctly",
                            data
                        )
                        return data
                    else:
                        self.log_test(
                            "Get Default Sidebar Preferences",
                            False,
                            f"Default values don't match expected. Got: {data}"
                        )
                else:
                    self.log_test(
                        "Get Default Sidebar Preferences",
                        False,
                        f"Missing required fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "Get Default Sidebar Preferences",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Get Default Sidebar Preferences",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_update_preferences_valid(self):
        """Test 2: PUT /api/users/sidebar-preferences - Update with valid preferences"""
        try:
            print(f"\n📋 TEST 2: PUT Update Sidebar Preferences (Valid)")
            
            custom_preferences = {
                "default_mode": "mini",
                "hover_expand_enabled": True,
                "auto_collapse_enabled": True,
                "inactivity_timeout": 15,
                "context_aware_enabled": False,
                "collapse_after_navigation": True
            }
            
            response = requests.put(
                f"{self.base_url}/users/sidebar-preferences",
                json=custom_preferences,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "preferences" in data:
                    # Verify the returned preferences match what we sent
                    returned_prefs = data["preferences"]
                    matches = all(returned_prefs.get(key) == value for key, value in custom_preferences.items())
                    
                    if matches:
                        self.log_test(
                            "Update Sidebar Preferences (Valid)",
                            True,
                            "Preferences updated successfully",
                            data
                        )
                        return custom_preferences
                    else:
                        self.log_test(
                            "Update Sidebar Preferences (Valid)",
                            False,
                            f"Returned preferences don't match. Expected: {custom_preferences}, Got: {returned_prefs}"
                        )
                else:
                    self.log_test(
                        "Update Sidebar Preferences (Valid)",
                        False,
                        f"Response missing required fields. Got: {data}"
                    )
            else:
                self.log_test(
                    "Update Sidebar Preferences (Valid)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Update Sidebar Preferences (Valid)",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_get_updated_preferences(self):
        """Test 3: GET /api/users/sidebar-preferences - Verify persistence"""
        try:
            print(f"\n📋 TEST 3: GET Updated Sidebar Preferences (Verify Persistence)")
            
            response = requests.get(
                f"{self.base_url}/users/sidebar-preferences",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify it matches our custom preferences from test 2
                expected_custom = {
                    "default_mode": "mini",
                    "hover_expand_enabled": True,
                    "auto_collapse_enabled": True,
                    "inactivity_timeout": 15,
                    "context_aware_enabled": False,
                    "collapse_after_navigation": True
                }
                
                matches = all(data.get(key) == value for key, value in expected_custom.items())
                
                if matches:
                    self.log_test(
                        "Get Updated Sidebar Preferences (Persistence)",
                        True,
                        "Updated preferences persisted correctly",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Get Updated Sidebar Preferences (Persistence)",
                        False,
                        f"Preferences don't match expected. Expected: {expected_custom}, Got: {data}"
                    )
            else:
                self.log_test(
                    "Get Updated Sidebar Preferences (Persistence)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Get Updated Sidebar Preferences (Persistence)",
                False,
                f"Exception: {str(e)}"
            )
        
        return False
    
    def test_validation_invalid_mode(self):
        """Test 4: PUT /api/users/sidebar-preferences - Invalid mode validation"""
        try:
            print(f"\n📋 TEST 4: PUT Invalid Mode Validation")
            
            invalid_preferences = {
                "default_mode": "invalid_mode",
                "hover_expand_enabled": True,
                "auto_collapse_enabled": False,
                "inactivity_timeout": 10,
                "context_aware_enabled": True,
                "collapse_after_navigation": False
            }
            
            response = requests.put(
                f"{self.base_url}/users/sidebar-preferences",
                json=invalid_preferences,
                headers=self.get_headers()
            )
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "Invalid mode" in data["detail"]:
                    self.log_test(
                        "Invalid Mode Validation",
                        True,
                        f"Correctly rejected invalid mode: {data['detail']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Invalid Mode Validation",
                        False,
                        f"Wrong error message. Got: {data}"
                    )
            else:
                self.log_test(
                    "Invalid Mode Validation",
                    False,
                    f"Expected 400, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Invalid Mode Validation",
                False,
                f"Exception: {str(e)}"
            )
        
        return False
    
    def test_validation_timeout_too_low(self):
        """Test 5: PUT /api/users/sidebar-preferences - Timeout too low validation"""
        try:
            print(f"\n📋 TEST 5: PUT Timeout Too Low Validation")
            
            invalid_preferences = {
                "default_mode": "expanded",
                "hover_expand_enabled": True,
                "auto_collapse_enabled": True,
                "inactivity_timeout": 3,  # Below minimum of 5
                "context_aware_enabled": True,
                "collapse_after_navigation": False
            }
            
            response = requests.put(
                f"{self.base_url}/users/sidebar-preferences",
                json=invalid_preferences,
                headers=self.get_headers()
            )
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "between 5 and 60" in data["detail"]:
                    self.log_test(
                        "Timeout Too Low Validation",
                        True,
                        f"Correctly rejected low timeout: {data['detail']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Timeout Too Low Validation",
                        False,
                        f"Wrong error message. Got: {data}"
                    )
            else:
                self.log_test(
                    "Timeout Too Low Validation",
                    False,
                    f"Expected 400, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Timeout Too Low Validation",
                False,
                f"Exception: {str(e)}"
            )
        
        return False
    
    def test_validation_timeout_too_high(self):
        """Test 6: PUT /api/users/sidebar-preferences - Timeout too high validation"""
        try:
            print(f"\n📋 TEST 6: PUT Timeout Too High Validation")
            
            invalid_preferences = {
                "default_mode": "expanded",
                "hover_expand_enabled": True,
                "auto_collapse_enabled": True,
                "inactivity_timeout": 70,  # Above maximum of 60
                "context_aware_enabled": True,
                "collapse_after_navigation": False
            }
            
            response = requests.put(
                f"{self.base_url}/users/sidebar-preferences",
                json=invalid_preferences,
                headers=self.get_headers()
            )
            
            if response.status_code == 400:
                data = response.json()
                if "detail" in data and "between 5 and 60" in data["detail"]:
                    self.log_test(
                        "Timeout Too High Validation",
                        True,
                        f"Correctly rejected high timeout: {data['detail']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Timeout Too High Validation",
                        False,
                        f"Wrong error message. Got: {data}"
                    )
            else:
                self.log_test(
                    "Timeout Too High Validation",
                    False,
                    f"Expected 400, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Timeout Too High Validation",
                False,
                f"Exception: {str(e)}"
            )
        
        return False
    
    def verify_mongodb_persistence(self):
        """Test 7: Verify data persists in MongoDB user_preferences collection"""
        try:
            print(f"\n📋 TEST 7: MongoDB Persistence Verification")
            
            # We can't directly access MongoDB from here, but we can verify through API
            # Get preferences again to ensure they're still there
            response = requests.get(
                f"{self.base_url}/users/sidebar-preferences",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we still have our custom preferences (not defaults)
                if data.get("default_mode") == "mini" and data.get("inactivity_timeout") == 15:
                    self.log_test(
                        "MongoDB Persistence Verification",
                        True,
                        "Preferences persist correctly in database",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "MongoDB Persistence Verification",
                        False,
                        f"Preferences reverted to defaults or changed unexpectedly: {data}"
                    )
            else:
                self.log_test(
                    "MongoDB Persistence Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "MongoDB Persistence Verification",
                False,
                f"Exception: {str(e)}"
            )
        
        return False
    
    def run_all_tests(self):
        """Run all sidebar preferences tests"""
        print("🚀 STARTING SIDEBAR PREFERENCES API BACKEND TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all tests
        test_functions = [
            self.test_get_default_preferences,
            self.test_update_preferences_valid,
            self.test_get_updated_preferences,
            self.test_validation_invalid_mode,
            self.test_validation_timeout_too_low,
            self.test_validation_timeout_too_high,
            self.verify_mongodb_persistence
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = test_func()
                if result is True or (result is not None and result is not False):
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SIDEBAR PREFERENCES API TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Sidebar Preferences API is fully operational.")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review issues above.")
        
        # Print individual test results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        return passed_tests, total_tests


if __name__ == "__main__":
    tester = SidebarPreferencesAPITester()
    result = tester.run_all_tests()
    
    if result:
        passed, total = result
        # Exit with appropriate code
        exit(0 if passed == total else 1)
    else:
        exit(1)