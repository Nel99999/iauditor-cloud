#!/usr/bin/env python3
"""
Quick Health Check - Backend API Verification After UI/UX Migration
Tests the 4 key areas requested: Health Check, Authentication, Dashboard Stats, User Management
"""

import requests
import json
import sys
from datetime import datetime

# Use the production URL from frontend/.env
BASE_URL = "https://ts-conversion.preview.emergentagent.com/api"

class BackendHealthChecker:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'status': status
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
    
    def test_health_check(self):
        """Test 1: Verify /api endpoint is accessible"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Health Check (/api)", True, f"Response: {data}")
                    return True
                else:
                    self.log_test("Health Check (/api)", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Check (/api)", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check (/api)", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test 2: Test login with existing user or register new test user"""
        # First try to register a new test user
        test_email = f"healthcheck.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        test_password = "HealthCheck123!"
        
        # Try registration first
        register_data = {
            "email": test_email,
            "password": test_password,
            "name": "Health Check User",
            "organization_name": "Health Check Org"
        }
        
        try:
            # Register new user
            response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                register_result = response.json()
                if "access_token" in register_result:
                    self.token = register_result["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_test("User Registration & Login", True, f"Created user and obtained token: {test_email}")
                    return True
                else:
                    self.log_test("User Registration", False, f"No access_token in registration response: {register_result}")
                    return False
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_dashboard_stats(self):
        """Test 3: GET /api/dashboard/stats to ensure dashboard data loads"""
        if not self.token:
            self.log_test("Dashboard Stats", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                data = response.json()
                # Check for expected structure
                expected_keys = ['users', 'inspections', 'tasks', 'checklists', 'organization']
                missing_keys = [key for key in expected_keys if key not in data]
                
                if not missing_keys:
                    self.log_test("Dashboard Stats", True, f"All expected data sections present: {list(data.keys())}")
                    return True
                else:
                    self.log_test("Dashboard Stats", False, f"Missing keys: {missing_keys}, Got: {list(data.keys())}")
                    return False
            else:
                self.log_test("Dashboard Stats", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Exception: {str(e)}")
            return False
    
    def test_user_management(self):
        """Test 4: GET /api/users to ensure user list loads"""
        if not self.token:
            self.log_test("User Management", False, "No authentication token available")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/users")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    user_count = len(data)
                    self.log_test("User Management", True, f"User list loaded successfully, {user_count} users found")
                    return True
                else:
                    self.log_test("User Management", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("User Management", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Management", False, f"Exception: {str(e)}")
            return False
    
    def run_health_check(self):
        """Run all health check tests"""
        print("🎯 BACKEND HEALTH CHECK - POST UI/UX MIGRATION")
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_health_check,
            self.test_authentication,
            self.test_dashboard_stats,
            self.test_user_management
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"HEALTH CHECK SUMMARY: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Backend is healthy after UI/UX migration!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Backend may have issues after UI/UX migration")
            failed_tests = [result for result in self.test_results if not result['success']]
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

if __name__ == "__main__":
    checker = BackendHealthChecker()
    success = checker.run_health_check()
    sys.exit(0 if success else 1)