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

class ChecklistAPITester:
    def __init__(self, base_url="https://deploy-prep-check.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_templates = []
        self.created_executions = []

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
        """Login with test user"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login Test User for Checklists",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_checklist_templates(self):
        """Test getting all checklist templates"""
        success, response = self.run_test(
            "Get Checklist Templates",
            "GET",
            "checklists/templates",
            200
        )
        return success, response

    def test_create_checklist_template(self):
        """Test creating a new checklist template"""
        template_data = {
            "name": f"Test Opening Checklist {uuid.uuid4().hex[:6]}",
            "description": "Daily opening checklist for testing",
            "category": "opening",
            "frequency": "daily",
            "scheduled_time": "08:00",
            "items": [
                {"text": "Check all lights are working", "required": True, "order": 0},
                {"text": "Verify security system is armed", "required": True, "order": 1},
                {"text": "Count cash register", "required": True, "order": 2},
                {"text": "Check temperature settings", "required": False, "order": 3}
            ]
        }
        
        success, response = self.run_test(
            "Create Checklist Template",
            "POST",
            "checklists/templates",
            201,
            data=template_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_templates.append(response['id'])
            return success, response
        return success, response

    def test_get_checklist_template(self, template_id):
        """Test getting a specific checklist template"""
        success, response = self.run_test(
            "Get Specific Checklist Template",
            "GET",
            f"checklists/templates/{template_id}",
            200
        )
        return success, response

    def test_update_checklist_template(self, template_id):
        """Test updating a checklist template"""
        update_data = {
            "name": f"Updated Test Checklist {uuid.uuid4().hex[:6]}",
            "description": "Updated description for testing",
            "items": [
                {"text": "Updated item 1", "required": True, "order": 0},
                {"text": "New item 2", "required": True, "order": 1}
            ]
        }
        
        success, response = self.run_test(
            "Update Checklist Template",
            "PUT",
            f"checklists/templates/{template_id}",
            200,
            data=update_data
        )
        return success, response

    def test_delete_checklist_template(self, template_id):
        """Test deleting a checklist template"""
        success, response = self.run_test(
            "Delete Checklist Template",
            "DELETE",
            f"checklists/templates/{template_id}",
            200
        )
        return success, response

    def test_start_checklist_execution(self, template_id):
        """Test starting a checklist execution"""
        success, response = self.run_test(
            "Start Checklist Execution",
            "POST",
            f"checklists/executions?template_id={template_id}",
            201
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_executions.append(response['id'])
            return success, response
        return success, response

    def test_get_checklist_executions(self):
        """Test getting all checklist executions"""
        success, response = self.run_test(
            "Get Checklist Executions",
            "GET",
            "checklists/executions",
            200
        )
        return success, response

    def test_get_todays_checklists(self):
        """Test getting today's checklists"""
        success, response = self.run_test(
            "Get Today's Checklists",
            "GET",
            "checklists/executions/today",
            200
        )
        return success, response

    def test_get_checklist_execution(self, execution_id):
        """Test getting a specific checklist execution"""
        success, response = self.run_test(
            "Get Specific Checklist Execution",
            "GET",
            f"checklists/executions/{execution_id}",
            200
        )
        return success, response

    def test_update_checklist_execution(self, execution_id, template_items):
        """Test updating a checklist execution"""
        # Create items with some completed
        items = []
        for i, item in enumerate(template_items):
            items.append({
                "item_id": item["id"],
                "completed": i % 2 == 0,  # Alternate completion
                "notes": f"Test note for item {i}",
                "completed_at": datetime.now().isoformat() if i % 2 == 0 else None
            })
        
        update_data = {
            "items": items,
            "notes": "Test execution update"
        }
        
        success, response = self.run_test(
            "Update Checklist Execution",
            "PUT",
            f"checklists/executions/{execution_id}",
            200,
            data=update_data
        )
        return success, response

    def test_complete_checklist_execution(self, execution_id, template_items):
        """Test completing a checklist execution"""
        # Create items all completed
        items = []
        for item in template_items:
            items.append({
                "item_id": item["id"],
                "completed": True,
                "notes": f"Completed: {item['text']}",
                "completed_at": datetime.now().isoformat()
            })
        
        completion_data = {
            "items": items,
            "notes": "Test checklist completion"
        }
        
        success, response = self.run_test(
            "Complete Checklist Execution",
            "POST",
            f"checklists/executions/{execution_id}/complete",
            200,
            data=completion_data
        )
        return success, response

    def test_get_checklist_stats(self):
        """Test getting checklist statistics"""
        success, response = self.run_test(
            "Get Checklist Stats",
            "GET",
            "checklists/stats",
            200
        )
        return success, response

    def test_complete_checklist_workflow(self):
        """Test complete checklist workflow"""
        print("\n🔄 Testing Complete Checklist Workflow")
        
        # 1. Get initial templates and stats
        self.test_get_checklist_templates()
        self.test_get_checklist_stats()
        self.test_get_todays_checklists()
        
        # 2. Create a new template
        template_success, template = self.test_create_checklist_template()
        if not template_success or not isinstance(template, dict) or 'id' not in template:
            print("❌ Template creation failed, stopping workflow test")
            return False
        
        template_id = template['id']
        
        # 3. Get the created template
        self.test_get_checklist_template(template_id)
        
        # 4. Update the template
        self.test_update_checklist_template(template_id)
        
        # 5. Start a checklist execution
        execution_success, execution = self.test_start_checklist_execution(template_id)
        if not execution_success or not isinstance(execution, dict) or 'id' not in execution:
            print("❌ Execution start failed, stopping workflow test")
            return False
        
        execution_id = execution['id']
        
        # 6. Get executions
        self.test_get_checklist_executions()
        self.test_get_checklist_execution(execution_id)
        
        # 7. Update execution (partial completion)
        template_items = template.get('items', [])
        self.test_update_checklist_execution(execution_id, template_items)
        
        # 8. Complete the execution
        self.test_complete_checklist_execution(execution_id, template_items)
        
        # 9. Get updated stats
        self.test_get_checklist_stats()
        self.test_get_todays_checklists()
        
        # 10. Clean up - delete template
        self.test_delete_checklist_template(template_id)
        
        return True

    def run_all_tests(self):
        """Run all checklist tests"""
        print("🚀 Starting Checklist API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Login first
        if not self.login_test_user():
            print("❌ Login failed, stopping checklist tests")
            return self.generate_report()

        # Test complete workflow
        self.test_complete_checklist_workflow()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 CHECKLIST TEST SUMMARY")
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

class InspectionAPITester:
    def __init__(self, base_url="https://deploy-prep-check.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_templates = []
        self.created_executions = []
        self.uploaded_photos = []

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        # Don't set Content-Type for file uploads
        if not files:
            test_headers['Content-Type'] = 'application/json'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers=test_headers, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=15)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else str(response_data)[:500]}"
            
            self.log_test(name, success, details)
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def login_test_user(self):
        """Login with test user"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "Login Test User for Inspections",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_create_inspection_template(self):
        """Test creating a new inspection template"""
        template_data = {
            "name": f"Test Safety Inspection {uuid.uuid4().hex[:6]}",
            "description": "Comprehensive safety inspection template for testing",
            "category": "safety",
            "scoring_enabled": True,
            "pass_percentage": 80.0,
            "require_gps": True,
            "require_photos": True,
            "questions": [
                {
                    "question_text": "Are all safety equipment properly maintained?",
                    "question_type": "yes_no",
                    "required": True,
                    "scoring_enabled": True,
                    "order": 0
                },
                {
                    "question_text": "What is the temperature reading?",
                    "question_type": "number",
                    "required": True,
                    "scoring_enabled": True,
                    "pass_score": 20.0,
                    "order": 1
                },
                {
                    "question_text": "Describe any safety concerns",
                    "question_type": "text",
                    "required": False,
                    "scoring_enabled": False,
                    "order": 2
                },
                {
                    "question_text": "What is the overall condition?",
                    "question_type": "multiple_choice",
                    "required": True,
                    "options": ["Excellent", "Good", "Fair", "Poor"],
                    "scoring_enabled": True,
                    "order": 3
                },
                {
                    "question_text": "Take a photo of the area",
                    "question_type": "photo",
                    "required": True,
                    "scoring_enabled": False,
                    "order": 4
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Inspection Template",
            "POST",
            "inspections/templates",
            201,
            data=template_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_templates.append(response['id'])
            return success, response
        return success, response

    def test_complete_inspection_workflow(self):
        """Test complete inspection workflow"""
        # Get templates
        success, templates = self.run_test("Get Templates", "GET", "inspections/templates", 200)
        if not success:
            return False
            
        # Get stats
        success, stats = self.run_test("Get Stats", "GET", "inspections/stats", 200)
        if not success:
            return False
            
        # Create template
        template_success, template = self.test_create_inspection_template()
        if not template_success:
            return False
            
        template_id = template['id']
        
        # Start inspection
        execution_data = {"template_id": template_id, "unit_id": None}
        success, execution = self.run_test("Start Inspection", "POST", "inspections/executions", 201, data=execution_data)
        if not success:
            return False
            
        execution_id = execution['id']
        
        # Upload photo
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {'file': ('test.png', io.BytesIO(test_image), 'image/png')}
        success, photo = self.run_test("Upload Photo", "POST", "inspections/upload-photo", 200, files=files)
        photo_id = photo.get('file_id') if success else None
        
        # Complete inspection with answers
        answers = []
        for q in template['questions']:
            answer = {"question_id": q['id'], "photo_ids": [], "notes": "Test note"}
            if q['question_type'] == 'yes_no':
                answer['answer'] = True
            elif q['question_type'] == 'number':
                answer['answer'] = 25.0
            elif q['question_type'] == 'text':
                answer['answer'] = "Test answer"
            elif q['question_type'] == 'multiple_choice':
                answer['answer'] = "Good"
            elif q['question_type'] == 'photo':
                answer['answer'] = "Photo taken"
                if photo_id:
                    answer['photo_ids'] = [photo_id]
            answers.append(answer)
        
        completion_data = {
            "answers": answers,
            "findings": ["Test finding"],
            "notes": "Test completion"
        }
        
        success, completed = self.run_test("Complete Inspection", "POST", f"inspections/executions/{execution_id}/complete", 200, data=completion_data)
        
        return success

    def run_all_tests(self):
        """Run all inspection tests"""
        print("🚀 Starting Inspection API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Login first
        if not self.login_test_user():
            print("❌ Login failed, stopping inspection tests")
            return self.generate_report()

        # Test complete workflow
        self.test_complete_inspection_workflow()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 INSPECTION TEST SUMMARY")
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
    
    # Test Inspection System
    print("\n🔍 PHASE 3: Inspection System Testing")
    inspection_tester = InspectionAPITester()
    inspection_report = inspection_tester.run_all_tests()
    
    # Combined results
    total_tests = auth_report["total_tests"] + org_report["total_tests"] + inspection_report["total_tests"]
    total_passed = auth_report["passed_tests"] + org_report["passed_tests"] + inspection_report["passed_tests"]
    total_failed = auth_report["failed_tests"] + org_report["failed_tests"] + inspection_report["failed_tests"]
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL TEST SUMMARY")
    print("=" * 80)
    print(f"Authentication Tests: {auth_report['passed_tests']}/{auth_report['total_tests']} ({auth_report['success_rate']:.1f}%)")
    print(f"Organization Tests: {org_report['passed_tests']}/{org_report['total_tests']} ({org_report['success_rate']:.1f}%)")
    print(f"Inspection Tests: {inspection_report['passed_tests']}/{inspection_report['total_tests']} ({inspection_report['success_rate']:.1f}%)")
    print(f"Overall: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.1f}%)")
    
    # Return appropriate exit code
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())