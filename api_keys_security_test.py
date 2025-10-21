#!/usr/bin/env python3
"""
API Keys Access Control Security Test
Tests that ONLY Master and Developer roles can access API settings endpoints.
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://twilio-ops.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class APIKeysSecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.master_token = None
        self.admin_token = None
        self.master_user_id = None
        self.admin_user_id = None
        self.organization_id = None
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def register_user(self, email, name, role_type="master"):
        """Register a new user"""
        try:
            # For master user, create with organization
            if role_type == "master":
                payload = {
                    "email": email,
                    "password": "SecurePass123!",
                    "name": name,
                    "create_organization": True,
                    "organization_name": "Security Test Corp"
                }
            else:
                # For admin user, create separate organization (since we can't easily add to existing org)
                payload = {
                    "email": email,
                    "password": "SecurePass123!",
                    "name": name,
                    "create_organization": True,
                    "organization_name": "Admin Test Corp"
                }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user", {}).get("id")
                org_id = data.get("user", {}).get("organization_id")
                token = data.get("access_token")
                
                # Update role after registration (registration always creates "admin" for org creators)
                if token and user_id:
                    if role_type == "master":
                        self.update_user_role(user_id, "master", token)
                    elif role_type == "admin":
                        # Keep as admin (already set by registration)
                        pass
                
                return token, user_id, org_id
            else:
                print(f"Registration failed for {email}: {response.status_code} - {response.text}")
                return None, None, None
                
        except Exception as e:
            print(f"Registration error for {email}: {str(e)}")
            return None, None, None
    
    def update_user_role(self, user_id, role, token):
        """Update user role"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"role": role}
            
            response = self.session.put(f"{API_BASE}/users/{user_id}", json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Updated user role to {role}")
                return True
            else:
                print(f"Failed to update user role: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error updating user role: {str(e)}")
            return False
    
    def debug_user_info(self, token, user_type):
        """Debug user information"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{API_BASE}/users/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"🔍 {user_type} user info:")
                print(f"    Role: {user_data.get('role')}")
                print(f"    Organization ID: {user_data.get('organization_id')}")
                print(f"    User ID: {user_data.get('id')}")
                return user_data
            else:
                print(f"❌ Failed to get {user_type} user info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting {user_type} user info: {str(e)}")
            return None
        """Update user role"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"role": role}
            
            response = self.session.put(f"{API_BASE}/users/{user_id}", json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Updated user role to {role}")
                return True
            else:
                print(f"Failed to update user role: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error updating user role: {str(e)}")
            return False
    
    def test_endpoint_access(self, endpoint, method="GET", token=None, expected_status=200, payload=None):
        """Test endpoint access with given token"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            if method == "GET":
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
            elif method == "POST":
                response = self.session.post(f"{API_BASE}{endpoint}", json=payload or {}, headers=headers)
            
            return response.status_code, response.json() if response.content else {}
            
        except Exception as e:
            print(f"Error testing {endpoint}: {str(e)}")
            return 500, {"error": str(e)}
    
    def run_setup(self):
        """Setup test users"""
        print("🔧 Setting up test users...")
        
        # Register Master user (auto-assigned when creating organization)
        master_email = f"master.security.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.master_token, self.master_user_id, self.organization_id = self.register_user(
            master_email, "Master Security User", "master"
        )
        
        if not self.master_token:
            print("❌ Failed to create Master user")
            return False
        
        print(f"✅ Master user created: {master_email}")
        
        # Debug master user info
        master_info = self.debug_user_info(self.master_token, "Master")
        
        # Register Admin user (create separate org, then update role to admin)
        admin_email = f"admin.security.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.admin_token, self.admin_user_id, _ = self.register_user(
            admin_email, "Admin Security User", "admin"
        )
        
        if not self.admin_token:
            print("❌ Failed to create Admin user")
            return False
        
        print(f"✅ Admin user created: {admin_email}")
        
        # Debug admin user info
        admin_info = self.debug_user_info(self.admin_token, "Admin")
        
        return True
    
    def test_master_role_access(self):
        """Test Group 1: Master Role Access (Should PASS)"""
        print("\n📋 Test Group 1: Master Role Access (Should PASS)")
        
        # Test 1: GET /api/settings/email
        status, response = self.test_endpoint_access("/settings/email", "GET", self.master_token, 200)
        passed = status == 200
        self.log_test("Master GET /api/settings/email", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 2: GET /api/sms/settings
        status, response = self.test_endpoint_access("/sms/settings", "GET", self.master_token, 200)
        passed = status == 200
        self.log_test("Master GET /api/sms/settings", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 3: POST /api/settings/email with test key
        test_payload = {"sendgrid_api_key": "SG.test_key_1234567890_abcdefg"}
        status, response = self.test_endpoint_access("/settings/email", "POST", self.master_token, 200, test_payload)
        passed = status == 200
        self.log_test("Master POST /api/settings/email", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 4: POST /api/sms/settings with test credentials
        test_payload = {
            "account_sid": "ACtest1234567890abcdefghijklmn",
            "auth_token": "test_auth_token_123",
            "phone_number": "+1234567890",
            "whatsapp_number": "+1234567890"
        }
        status, response = self.test_endpoint_access("/sms/settings", "POST", self.master_token, 200, test_payload)
        passed = status == 200
        self.log_test("Master POST /api/sms/settings", passed, 
                     f"Status: {status}, Response: {response}")
    
    def test_admin_role_access(self):
        """Test Group 2: Admin Role Access (Should FAIL with 403)"""
        print("\n📋 Test Group 2: Admin Role Access (Should FAIL with 403)")
        
        # Test 5: GET /api/settings/email
        status, response = self.test_endpoint_access("/settings/email", "GET", self.admin_token, 403)
        passed = status == 403 and "Only Master and Developer roles can access email settings" in str(response)
        self.log_test("Admin GET /api/settings/email (should fail)", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 6: GET /api/sms/settings
        status, response = self.test_endpoint_access("/sms/settings", "GET", self.admin_token, 403)
        passed = status == 403 and "Only Master and Developer roles can access Twilio settings" in str(response)
        self.log_test("Admin GET /api/sms/settings (should fail)", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 7: POST /api/settings/email
        test_payload = {"sendgrid_api_key": "SG.test_key_should_fail"}
        status, response = self.test_endpoint_access("/settings/email", "POST", self.admin_token, 403, test_payload)
        passed = status == 403
        self.log_test("Admin POST /api/settings/email (should fail)", passed, 
                     f"Status: {status}, Response: {response}")
        
        # Test 8: POST /api/sms/settings
        test_payload = {
            "account_sid": "ACtest_should_fail",
            "auth_token": "test_auth_token_fail",
            "phone_number": "+1234567890"
        }
        status, response = self.test_endpoint_access("/sms/settings", "POST", self.admin_token, 403, test_payload)
        passed = status == 403
        self.log_test("Admin POST /api/sms/settings (should fail)", passed, 
                     f"Status: {status}, Response: {response}")
    
    def test_data_masking(self):
        """Test Group 3: Data Masking Verification"""
        print("\n📋 Test Group 3: Data Masking Verification")
        
        # Test 9: Verify SendGrid key masking
        status, response = self.test_endpoint_access("/settings/email", "GET", self.master_token, 200)
        if status == 200:
            api_key = response.get("sendgrid_api_key", "")
            # Should be masked as "SG.test_...defg" (first 8 chars + ... + last 4 chars)
            expected_pattern = api_key.startswith("SG.test_") and api_key.endswith("defg") and "..." in api_key
            passed = expected_pattern
            self.log_test("SendGrid key masking", passed, 
                         f"Masked key: {api_key}, Expected pattern: SG.test_...defg")
        else:
            self.log_test("SendGrid key masking", False, f"Failed to get settings: {status}")
        
        # Test 10: Verify Twilio Account SID masking
        status, response = self.test_endpoint_access("/sms/settings", "GET", self.master_token, 200)
        if status == 200:
            account_sid = response.get("account_sid", "")
            # Should be masked as "ACtest1234...klmn"
            expected_pattern = account_sid.startswith("ACtest1234") and account_sid.endswith("klmn") and "..." in account_sid
            passed = expected_pattern
            self.log_test("Twilio Account SID masking", passed, 
                         f"Masked SID: {account_sid}, Expected pattern: ACtest1234...klmn")
        else:
            self.log_test("Twilio Account SID masking", False, f"Failed to get settings: {status}")
        
        # Test 11: Verify auth tokens are never returned
        status, response = self.test_endpoint_access("/sms/settings", "GET", self.master_token, 200)
        if status == 200:
            has_auth_token = "auth_token" in response or "twilio_auth_token" in response
            passed = not has_auth_token
            self.log_test("Auth tokens not returned in GET", passed, 
                         f"Auth token present: {has_auth_token}, Response keys: {list(response.keys())}")
        else:
            self.log_test("Auth tokens not returned in GET", False, f"Failed to get settings: {status}")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔐 API Keys Access Control Security Testing")
        print("=" * 60)
        
        # Setup
        if not self.run_setup():
            print("❌ Setup failed, cannot continue with tests")
            return
        
        # Run test groups
        self.test_master_role_access()
        self.test_admin_role_access()
        self.test_data_masking()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 SUCCESS CRITERIA CHECK:")
        
        # Check success criteria
        master_access_tests = [r for r in self.test_results if "Master" in r["test"] and "should fail" not in r["test"]]
        master_success = all(r["passed"] for r in master_access_tests)
        print(f"✅ Master role has full access: {'YES' if master_success else 'NO'}")
        
        admin_denied_tests = [r for r in self.test_results if "Admin" in r["test"] and "should fail" in r["test"]]
        admin_denied = all(r["passed"] for r in admin_denied_tests)
        print(f"✅ Admin role denied with 403: {'YES' if admin_denied else 'NO'}")
        
        masking_tests = [r for r in self.test_results if "masking" in r["test"] or "not returned" in r["test"]]
        masking_success = all(r["passed"] for r in masking_tests)
        print(f"✅ Sensitive data properly masked: {'YES' if masking_success else 'NO'}")
        
        error_message_tests = [r for r in self.test_results if "should fail" in r["test"] and "Only Master and Developer roles" in r["details"]]
        error_messages = len(error_message_tests) >= 2  # At least 2 tests should have proper error messages
        print(f"✅ Proper error messages: {'YES' if error_messages else 'NO'}")
        
        overall_success = master_success and admin_denied and masking_success and error_messages
        print(f"\n🏆 OVERALL SECURITY TEST: {'✅ PASSED' if overall_success else '❌ FAILED'}")


if __name__ == "__main__":
    tester = APIKeysSecurityTester()
    tester.run_all_tests()