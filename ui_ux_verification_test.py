#!/usr/bin/env python3
"""
Backend Testing for UI/UX Phase 1 & 2 - Verification Test
Context: Frontend CSS/React components were updated, verifying backend APIs still work
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://ops-revamp.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_health_check(self):
        """Test 1: Health Check - Verify backend is running"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Health Check", True, "Backend is running and accessible")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_authentication_apis(self):
        """Test 2: Authentication APIs - Login and JWT token verification"""
        # Try with existing test user from previous tests
        test_user = {
            "email": "testuser.222072@example.com",
            "password": "SecurePassword123!",
            "name": "UI Test User",
            "organization_name": "UI Test Organization"
        }
        
        try:
            # Try registration first
            reg_response = self.session.post(f"{BACKEND_URL}/auth/register", json=test_user)
            if reg_response.status_code in [200, 201]:
                self.log_test("User Registration", True, "Test user registered successfully")
            elif reg_response.status_code == 400:
                # User might already exist, that's okay
                self.log_test("User Registration", True, "User already exists (expected)")
            else:
                self.log_test("User Registration", False, f"Registration failed: {reg_response.status_code} - {reg_response.text}")
        except Exception as e:
            self.log_test("User Registration", False, f"Registration error: {str(e)}")
        
        # Now test login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        try:
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            if login_response.status_code == 200:
                login_result = login_response.json()
                if "access_token" in login_result:
                    self.auth_token = login_result["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Authentication Login", True, "JWT token received successfully")
                    
                    # Verify token works with protected endpoint
                    me_response = self.session.get(f"{BACKEND_URL}/auth/me")
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        self.log_test("JWT Token Verification", True, f"Protected endpoint accessible, user: {user_data.get('email')}")
                        return True
                    else:
                        self.log_test("JWT Token Verification", False, f"Protected endpoint failed: {me_response.status_code}")
                        return False
                else:
                    self.log_test("Authentication Login", False, "No access_token in response")
                    return False
            else:
                self.log_test("Authentication Login", False, f"Login failed: {login_response.status_code} - {login_response.text}")
                return False
        except Exception as e:
            self.log_test("Authentication Login", False, f"Login error: {str(e)}")
            return False
    
    def test_theme_apis(self):
        """Test 3: Theme APIs - GET and PUT /api/users/theme"""
        if not self.auth_token:
            self.log_test("Theme APIs", False, "No authentication token available")
            return False
        
        try:
            # Test GET /api/users/theme
            get_response = self.session.get(f"{BACKEND_URL}/users/theme")
            if get_response.status_code == 200:
                theme_data = get_response.json()
                self.log_test("GET Theme Preferences", True, f"Theme data retrieved: {theme_data}")
                
                # Test PUT /api/users/theme
                updated_theme = {
                    "theme": "dark",
                    "accent_color": "#3b82f6",
                    "density": "comfortable",
                    "font_size": "medium"
                }
                
                put_response = self.session.put(f"{BACKEND_URL}/users/theme", json=updated_theme)
                if put_response.status_code == 200:
                    put_result = put_response.json()
                    self.log_test("PUT Theme Preferences", True, f"Theme updated successfully: {put_result}")
                    
                    # Verify the update by getting theme again
                    verify_response = self.session.get(f"{BACKEND_URL}/users/theme")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get("theme") == "dark":
                            self.log_test("Theme Update Verification", True, "Theme update persisted correctly")
                            return True
                        else:
                            self.log_test("Theme Update Verification", False, f"Theme not updated: {verify_data}")
                            return False
                    else:
                        self.log_test("Theme Update Verification", False, f"Verification failed: {verify_response.status_code}")
                        return False
                else:
                    self.log_test("PUT Theme Preferences", False, f"Theme update failed: {put_response.status_code} - {put_response.text}")
                    return False
            else:
                self.log_test("GET Theme Preferences", False, f"Get theme failed: {get_response.status_code} - {get_response.text}")
                return False
        except Exception as e:
            self.log_test("Theme APIs", False, f"Theme API error: {str(e)}")
            return False
    
    def test_additional_endpoints(self):
        """Test 4: Additional endpoint accessibility check"""
        if not self.auth_token:
            self.log_test("Additional Endpoints", False, "No authentication token available")
            return False
        
        # Test some key endpoints to ensure they're accessible
        endpoints_to_test = [
            ("/dashboard/stats", "Dashboard Statistics"),
            ("/users", "User Management"),
            ("/roles", "Role Management"),
            ("/permissions", "Permission Management")
        ]
        
        success_count = 0
        total_count = len(endpoints_to_test)
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [200, 201]:
                    self.log_test(f"Endpoint Access - {name}", True, f"Accessible at {endpoint}")
                    success_count += 1
                else:
                    self.log_test(f"Endpoint Access - {name}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Endpoint Access - {name}", False, f"Error: {str(e)}")
        
        overall_success = success_count >= (total_count * 0.75)  # 75% success rate
        self.log_test("Overall Endpoint Accessibility", overall_success, f"{success_count}/{total_count} endpoints accessible")
        return overall_success
    
    def run_all_tests(self):
        """Run all backend verification tests"""
        print("🎯 BACKEND TESTING FOR UI/UX PHASE 1 & 2 - VERIFICATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Run tests in sequence
        health_ok = self.test_health_check()
        auth_ok = self.test_authentication_apis()
        theme_ok = self.test_theme_apis()
        endpoints_ok = self.test_additional_endpoints()
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print()
        print("=" * 70)
        print("🎯 BACKEND VERIFICATION TEST RESULTS")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   └─ {result['details']}")
        
        print()
        if success_rate >= 95:
            print("🎉 EXCELLENT: All backend APIs working correctly after frontend updates!")
        elif success_rate >= 85:
            print("✅ GOOD: Backend APIs mostly working, minor issues detected")
        else:
            print("⚠️  WARNING: Significant backend issues detected")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)