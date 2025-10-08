import requests
import sys
import json
from datetime import datetime
import uuid
import io
import os

class AuthAPITester:
    def __init__(self, base_url="https://deploy-prep-check.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else response_data}"
            
            self.log_test(name, success, details)
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_user_registration_without_org(self):
        """Test user registration without organization"""
        test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        test_data = {
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "User Registration (without org)",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True, test_email
        return False, test_email

    def test_user_registration_with_org(self):
        """Test user registration with organization creation"""
        test_email = f"org_owner_{uuid.uuid4().hex[:8]}@company.com"
        test_data = {
            "email": test_email,
            "password": "TestPass123!",
            "name": "Org Owner",
            "organization_name": f"Test Company {uuid.uuid4().hex[:6]}"
        }
        
        success, response = self.run_test(
            "User Registration (with org)",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        return success, test_email

    def test_duplicate_registration(self, email):
        """Test registration with existing email"""
        test_data = {
            "email": email,
            "password": "TestPass123!",
            "name": "Duplicate User"
        }
        
        success, response = self.run_test(
            "Duplicate Email Registration",
            "POST",
            "auth/register",
            400,
            data=test_data
        )
        
        return success

    def test_login_valid_credentials(self, email):
        """Test login with valid credentials"""
        login_data = {
            "email": email,
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Login (valid credentials)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_login_invalid_password(self, email):
        """Test login with wrong password"""
        login_data = {
            "email": email,
            "password": "WrongPassword123!"
        }
        
        success, response = self.run_test(
            "Login (invalid password)",
            "POST",
            "auth/login",
            401,
            data=login_data
        )
        
        return success

    def test_login_nonexistent_email(self):
        """Test login with non-existent email"""
        login_data = {
            "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "Login (non-existent email)",
            "POST",
            "auth/login",
            401,
            data=login_data
        )
        
        return success

    def test_get_current_user_authenticated(self):
        """Test /me endpoint with valid token"""
        success, response = self.run_test(
            "Get Current User (authenticated)",
            "GET",
            "auth/me",
            200
        )
        
        return success

    def test_get_current_user_unauthenticated(self):
        """Test /me endpoint without token"""
        old_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Get Current User (unauthenticated)",
            "GET",
            "auth/me",
            401
        )
        
        self.token = old_token
        return success

    def test_get_current_user_invalid_token(self):
        """Test /me endpoint with invalid token"""
        old_token = self.token
        self.token = "invalid_token_12345"
        
        success, response = self.run_test(
            "Get Current User (invalid token)",
            "GET",
            "auth/me",
            401
        )
        
        self.token = old_token
        return success

    def test_logout(self):
        """Test logout endpoint"""
        success, response = self.run_test(
            "Logout",
            "POST",
            "auth/logout",
            200
        )
        
        return success

    def test_password_validation(self):
        """Test password validation (minimum 6 characters)"""
        test_email = f"short_pass_{uuid.uuid4().hex[:8]}@example.com"
        test_data = {
            "email": test_email,
            "password": "123",  # Too short
            "name": "Short Pass User"
        }
        
        success, response = self.run_test(
            "Password Validation (too short)",
            "POST",
            "auth/register",
            422,  # Validation error
            data=test_data
        )
        
        return success

    def test_email_format_validation(self):
        """Test email format validation"""
        test_data = {
            "email": "invalid-email-format",
            "password": "TestPass123!",
            "name": "Invalid Email User"
        }
        
        success, response = self.run_test(
            "Email Format Validation",
            "POST",
            "auth/register",
            422,  # Validation error
            data=test_data
        )
        
        return success

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Test user registration without organization
        reg_success, test_email = self.test_user_registration_without_org()
        
        if not reg_success:
            print("❌ Registration failed, stopping tests")
            return self.generate_report()

        # Test duplicate registration
        self.test_duplicate_registration(test_email)

        # Test user registration with organization
        self.test_user_registration_with_org()

        # Test login scenarios
        self.test_login_valid_credentials(test_email)
        self.test_login_invalid_password(test_email)
        self.test_login_nonexistent_email()

        # Test protected endpoints
        self.test_get_current_user_authenticated()
        self.test_get_current_user_unauthenticated()
        self.test_get_current_user_invalid_token()

        # Test logout
        self.test_logout()

        # Test validation
        self.test_password_validation()
        self.test_email_format_validation()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }

class OrganizationAPITester:
    def __init__(self, base_url="https://deploy-prep-check.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_units = []  # Track created units for cleanup

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else response_data}"
            
            self.log_test(name, success, details)
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def login_test_user(self):
        """Login with test user that has organization"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login Test User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_organization_units(self):
        """Test getting all organization units"""
        success, response = self.run_test(
            "Get Organization Units",
            "GET",
            "organizations/units",
            200
        )
        return success, response

    def test_get_organization_hierarchy(self):
        """Test getting organization hierarchy"""
        success, response = self.run_test(
            "Get Organization Hierarchy",
            "GET",
            "organizations/hierarchy",
            200
        )
        return success, response

    def test_create_root_unit(self):
        """Test creating a root organization unit (Company level)"""
        unit_data = {
            "name": f"Test Company {uuid.uuid4().hex[:6]}",
            "description": "Test company for hierarchy testing",
            "level": 1,
            "parent_id": None
        }
        
        success, response = self.run_test(
            "Create Root Unit (Company)",
            "POST",
            "organizations/units",
            201,
            data=unit_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_units.append(response['id'])
            return success, response
        return success, response

    def test_create_child_unit(self, parent_id, parent_level):
        """Test creating a child unit"""
        level_names = {1: "Company", 2: "Region", 3: "Location", 4: "Department", 5: "Team"}
        child_level = parent_level + 1
        
        unit_data = {
            "name": f"Test {level_names[child_level]} {uuid.uuid4().hex[:6]}",
            "description": f"Test {level_names[child_level].lower()} under parent",
            "level": child_level,
            "parent_id": parent_id
        }
        
        success, response = self.run_test(
            f"Create Child Unit ({level_names[child_level]})",
            "POST",
            "organizations/units",
            201,
            data=unit_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_units.append(response['id'])
            return success, response
        return success, response

    def test_level_validation_invalid(self, parent_id, parent_level):
        """Test level validation - should fail with wrong level"""
        unit_data = {
            "name": f"Invalid Level Unit {uuid.uuid4().hex[:6]}",
            "description": "This should fail level validation",
            "level": parent_level + 2,  # Skip a level - should fail
            "parent_id": parent_id
        }
        
        success, response = self.run_test(
            "Level Validation (Invalid - Skip Level)",
            "POST",
            "organizations/units",
            400,
            data=unit_data
        )
        
        return success

    def test_root_level_validation(self):
        """Test that root units must be level 1"""
        unit_data = {
            "name": f"Invalid Root Unit {uuid.uuid4().hex[:6]}",
            "description": "Root unit with wrong level",
            "level": 2,  # Should be 1 for root
            "parent_id": None
        }
        
        success, response = self.run_test(
            "Root Level Validation (Must be Level 1)",
            "POST",
            "organizations/units",
            400,
            data=unit_data
        )
        
        return success

    def test_update_organization_unit(self, unit_id):
        """Test updating an organization unit"""
        update_data = {
            "name": f"Updated Unit Name {uuid.uuid4().hex[:6]}",
            "description": "Updated description for testing"
        }
        
        success, response = self.run_test(
            "Update Organization Unit",
            "PUT",
            f"organizations/units/{unit_id}",
            200,
            data=update_data
        )
        
        return success, response

    def test_get_unit_users(self, unit_id):
        """Test getting users assigned to a unit"""
        success, response = self.run_test(
            "Get Unit Users",
            "GET",
            f"organizations/units/{unit_id}/users",
            200
        )
        
        return success, response

    def test_create_user_invitation(self, unit_id):
        """Test creating a user invitation"""
        invitation_data = {
            "email": f"invited_user_{uuid.uuid4().hex[:8]}@example.com",
            "unit_id": unit_id,
            "role": "viewer"
        }
        
        success, response = self.run_test(
            "Create User Invitation",
            "POST",
            "organizations/invitations",
            201,
            data=invitation_data
        )
        
        return success, response

    def test_get_invitations(self):
        """Test getting pending invitations"""
        success, response = self.run_test(
            "Get Pending Invitations",
            "GET",
            "organizations/invitations",
            200
        )
        
        return success, response

    def test_delete_unit_with_children(self, parent_id):
        """Test that units with children cannot be deleted"""
        success, response = self.run_test(
            "Delete Unit with Children (Should Fail)",
            "DELETE",
            f"organizations/units/{parent_id}",
            400
        )
        
        return success

    def test_delete_organization_unit(self, unit_id):
        """Test deleting an organization unit (soft delete)"""
        success, response = self.run_test(
            "Delete Organization Unit",
            "DELETE",
            f"organizations/units/{unit_id}",
            200
        )
        
        return success, response

    def run_all_tests(self):
        """Run all organization tests"""
        print("🚀 Starting Organization API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Login first
        if not self.login_test_user():
            print("❌ Login failed, stopping organization tests")
            return self.generate_report()

        # Test basic endpoints
        self.test_get_organization_units()
        self.test_get_organization_hierarchy()

        # Test creating root unit
        root_success, root_unit = self.test_create_root_unit()
        if not root_success or not isinstance(root_unit, dict) or 'id' not in root_unit:
            print("❌ Root unit creation failed, stopping hierarchy tests")
            return self.generate_report()

        root_id = root_unit['id']
        
        # Test level validation
        self.test_root_level_validation()
        self.test_level_validation_invalid(root_id, 1)

        # Create child units for each level
        current_parent_id = root_id
        current_level = 1
        
        for level in range(2, 6):  # Levels 2-5
            child_success, child_unit = self.test_create_child_unit(current_parent_id, current_level)
            if child_success and isinstance(child_unit, dict) and 'id' in child_unit:
                current_parent_id = child_unit['id']
                current_level = level
            else:
                break

        # Test update functionality
        if self.created_units:
            self.test_update_organization_unit(self.created_units[0])

        # Test user management
        if self.created_units:
            self.test_get_unit_users(self.created_units[0])
            self.test_create_user_invitation(self.created_units[0])
            self.test_get_invitations()

        # Test deletion constraints
        if len(self.created_units) >= 2:
            # Try to delete parent with children (should fail)
            self.test_delete_unit_with_children(self.created_units[0])
            
            # Delete child units first (should succeed)
            for unit_id in reversed(self.created_units[1:]):  # Delete children first
                self.test_delete_organization_unit(unit_id)
            
            # Finally delete root unit
            self.test_delete_organization_unit(self.created_units[0])

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 ORGANIZATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }

def main():
    print("🧪 COMPREHENSIVE API TESTING")
    print("=" * 80)
    
    # Test Authentication System
    print("\n📋 PHASE 1: Authentication System Testing")
    auth_tester = AuthAPITester()
    auth_report = auth_tester.run_all_tests()
    
    # Test Organization System
    print("\n🏢 PHASE 2: Organization System Testing")
    org_tester = OrganizationAPITester()
    org_report = org_tester.run_all_tests()
    
    # Combined results
    total_tests = auth_report["total_tests"] + org_report["total_tests"]
    total_passed = auth_report["passed_tests"] + org_report["passed_tests"]
    total_failed = auth_report["failed_tests"] + org_report["failed_tests"]
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL TEST SUMMARY")
    print("=" * 80)
    print(f"Authentication Tests: {auth_report['passed_tests']}/{auth_report['total_tests']} ({auth_report['success_rate']:.1f}%)")
    print(f"Organization Tests: {org_report['passed_tests']}/{org_report['total_tests']} ({org_report['success_rate']:.1f}%)")
    print(f"Overall: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.1f}%)")
    
    # Return appropriate exit code
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())