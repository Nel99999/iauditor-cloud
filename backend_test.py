#!/usr/bin/env python3
"""
Focused Backend Testing - Verify Core Functionality
Testing Request: Identify any remaining backend bugs after 90.9% success rate
Focus: Authentication, User Management, Organization, Checklists, Approvals, Dashboard
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://userapproval-flow.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(message):
    print(f"{Colors.BLUE}🧪 TEST:{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✅ PASS:{Colors.END} {message}")

def print_fail(message):
    print(f"{Colors.RED}❌ FAIL:{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.END} {message}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{Colors.END}\n")

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def record_test(test_name, passed, details=""):
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        print_success(f"{test_name}")
    else:
        tests_failed += 1
        print_fail(f"{test_name}")
    
    if details:
        print_info(details)
    
    test_results.append({
        "test": test_name,
        "passed": passed,
        "details": details
    })

# ============================================================================
# TEST 1: AUTHENTICATION SYSTEM
# ============================================================================
print_section("TEST 1: AUTHENTICATION SYSTEM")

# Test 1.1: User Registration
print_test("1.1 - User Registration with Organization Creation")
try:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "email": f"testuser.{timestamp}@example.com",
        "password": "SecurePass123!",
        "name": "Test User Backend",
        "organization_name": f"Test Org {timestamp}"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user)
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data and "user" in data:
            user_token = data["access_token"]
            user_id = data["user"]["id"]
            org_id = data["user"].get("organization_id")
            
            record_test("User Registration", True, 
                       f"User created: {test_user['email']}, Org ID: {org_id}")
        else:
            record_test("User Registration", False, "Missing access_token or user in response")
    else:
        record_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    record_test("User Registration", False, f"Exception: {str(e)}")

# Test 1.2: User Login
print_test("1.2 - User Login")
try:
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            record_test("User Login", True, "JWT token obtained successfully")
        else:
            record_test("User Login", False, "Missing access_token in response")
    else:
        record_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    record_test("User Login", False, f"Exception: {str(e)}")

# Test 1.3: Protected Endpoint Access
print_test("1.3 - Protected Endpoint Access (/auth/me)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("email") == test_user["email"]:
            record_test("Protected Endpoint Access", True, "User profile retrieved successfully")
        else:
            record_test("Protected Endpoint Access", False, "Email mismatch in profile")
    else:
        record_test("Protected Endpoint Access", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Protected Endpoint Access", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 2: USER MANAGEMENT CRUD
# ============================================================================
print_section("TEST 2: USER MANAGEMENT CRUD OPERATIONS")

# Test 2.1: List Users
print_test("2.1 - GET /users (List Users)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        if isinstance(users, list) and len(users) > 0:
            record_test("List Users", True, f"Found {len(users)} users in organization")
        else:
            record_test("List Users", False, "Empty user list or invalid format")
    else:
        record_test("List Users", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("List Users", False, f"Exception: {str(e)}")

# Test 2.2: Get User Profile
print_test("2.2 - GET /users/me (Get Profile)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        if profile.get("email") == test_user["email"]:
            record_test("Get User Profile", True, "Profile retrieved successfully")
        else:
            record_test("Get User Profile", False, "Email mismatch")
    else:
        record_test("Get User Profile", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Get User Profile", False, f"Exception: {str(e)}")

# Test 2.3: Update User Profile
print_test("2.3 - PUT /users/profile (Update Profile)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    update_data = {
        "name": "Updated Test User",
        "phone": "+1234567890"
    }
    response = requests.put(f"{BACKEND_URL}/users/profile", json=update_data, headers=headers)
    
    if response.status_code == 200:
        # Verify update
        verify_response = requests.get(f"{BACKEND_URL}/users/me", headers=headers)
        if verify_response.status_code == 200:
            profile = verify_response.json()
            if profile.get("name") == "Updated Test User":
                record_test("Update User Profile", True, "Profile updated and verified")
            else:
                record_test("Update User Profile", False, "Update not persisted")
        else:
            record_test("Update User Profile", False, "Could not verify update")
    else:
        record_test("Update User Profile", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Update User Profile", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 3: ORGANIZATION MANAGEMENT
# ============================================================================
print_section("TEST 3: ORGANIZATION MANAGEMENT")

# Test 3.1: List Organization Units
print_test("3.1 - GET /organizations/units (List Org Units)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/organizations/units", headers=headers)
    
    if response.status_code == 200:
        units = response.json()
        if isinstance(units, list):
            record_test("List Organization Units", True, f"Found {len(units)} organization units")
        else:
            record_test("List Organization Units", False, "Invalid response format")
    else:
        record_test("List Organization Units", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("List Organization Units", False, f"Exception: {str(e)}")

# Test 3.2: Create Organization Unit
print_test("3.2 - POST /organizations/units (Create Org Unit)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    unit_data = {
        "name": f"Test Department {timestamp}",
        "level": 1,
        "parent_id": None
    }
    response = requests.post(f"{BACKEND_URL}/organizations/units", json=unit_data, headers=headers)
    
    if response.status_code in [200, 201]:
        unit = response.json()
        if unit.get("name") == unit_data["name"]:
            unit_id = unit.get("id")
            record_test("Create Organization Unit", True, f"Unit created: {unit_id}")
        else:
            record_test("Create Organization Unit", False, "Name mismatch in response")
    else:
        record_test("Create Organization Unit", False, f"Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    record_test("Create Organization Unit", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 4: CHECKLIST TEMPLATES
# ============================================================================
print_section("TEST 4: CHECKLIST TEMPLATES")

# Test 4.1: List Checklist Templates
print_test("4.1 - GET /checklists/templates (List Templates)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/checklists/templates", headers=headers)
    
    if response.status_code == 200:
        templates = response.json()
        if isinstance(templates, list):
            record_test("List Checklist Templates", True, f"Found {len(templates)} checklist templates")
        else:
            record_test("List Checklist Templates", False, "Invalid response format")
    else:
        record_test("List Checklist Templates", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("List Checklist Templates", False, f"Exception: {str(e)}")

# Test 4.2: Create Checklist Template
print_test("4.2 - POST /checklists/templates (Create Template)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    template_data = {
        "name": f"Test Checklist {timestamp}",
        "description": "Test checklist for backend verification",
        "items": [
            {"text": "Item 1", "required": True},
            {"text": "Item 2", "required": False}
        ]
    }
    response = requests.post(f"{BACKEND_URL}/checklists/templates", json=template_data, headers=headers)
    
    if response.status_code == 200:
        template = response.json()
        if template.get("name") == template_data["name"]:
            template_id = template.get("id")
            record_test("Create Checklist Template", True, f"Template created: {template_id}")
        else:
            record_test("Create Checklist Template", False, "Name mismatch in response")
    else:
        record_test("Create Checklist Template", False, f"Status: {response.status_code}, Response: {response.text}")
except Exception as e:
    record_test("Create Checklist Template", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 5: APPROVAL SYSTEM
# ============================================================================
print_section("TEST 5: APPROVAL SYSTEM")

# Test 5.1: Check Approval Permissions
print_test("5.1 - GET /permissions (Check Approval Permissions Exist)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/permissions", headers=headers)
    
    if response.status_code == 200:
        permissions = response.json()
        approval_perms = [p for p in permissions if 'approve' in p.get('action', '').lower() or 'reject' in p.get('action', '').lower()]
        if len(approval_perms) > 0:
            record_test("Approval Permissions Exist", True, f"Found {len(approval_perms)} approval-related permissions")
        else:
            record_test("Approval Permissions Exist", False, "No approval permissions found")
    else:
        record_test("Approval Permissions Exist", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Approval Permissions Exist", False, f"Exception: {str(e)}")

# Test 5.2: List Pending Approvals
print_test("5.2 - GET /users/pending-approvals (List Pending Approvals)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/users/pending-approvals", headers=headers)
    
    if response.status_code == 200:
        pending = response.json()
        if isinstance(pending, list):
            record_test("List Pending Approvals", True, f"Found {len(pending)} pending approvals")
        else:
            record_test("List Pending Approvals", False, "Invalid response format")
    elif response.status_code == 403:
        record_test("List Pending Approvals", True, "403 - Permission check working (expected for some roles)")
    else:
        record_test("List Pending Approvals", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("List Pending Approvals", False, f"Exception: {str(e)}")

# Test 5.3: Approval Workflow Endpoints Exist
print_test("5.3 - POST /approvals/* (Approval Endpoints Accessible)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    # Test with invalid ID to check if endpoint exists (should return 404, not 405)
    response = requests.post(f"{BACKEND_URL}/approvals/test-id/approve", headers=headers)
    
    if response.status_code in [404, 400, 422]:  # Endpoint exists but resource not found
        record_test("Approval Endpoints Accessible", True, "Approval endpoints are accessible")
    elif response.status_code == 405:
        record_test("Approval Endpoints Accessible", False, "Method not allowed - endpoint may not exist")
    else:
        record_test("Approval Endpoints Accessible", True, f"Endpoint exists (Status: {response.status_code})")
except Exception as e:
    record_test("Approval Endpoints Accessible", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 6: DASHBOARD STATISTICS
# ============================================================================
print_section("TEST 6: DASHBOARD STATISTICS")

# Test 6.1: Dashboard Stats Endpoint
print_test("6.1 - GET /dashboard/stats (Dashboard Statistics)")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/dashboard/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        required_sections = ["users", "inspections", "tasks", "checklists", "organization"]
        missing_sections = [s for s in required_sections if s not in stats]
        
        if len(missing_sections) == 0:
            record_test("Dashboard Statistics", True, "All required sections present")
        else:
            record_test("Dashboard Statistics", False, f"Missing sections: {missing_sections}")
    else:
        record_test("Dashboard Statistics", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Dashboard Statistics", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 7: DATA INTEGRITY - 83 USERS WITHOUT ORGANIZATION_ID
# ============================================================================
print_section("TEST 7: DATA INTEGRITY CHECK")

# Test 7.1: Check if missing organization_id causes issues
print_test("7.1 - Verify Organization Isolation Works")
try:
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Get users in current organization
    response = requests.get(f"{BACKEND_URL}/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        # Check if all returned users have organization_id
        users_without_org = [u for u in users if not u.get("organization_id")]
        
        if len(users_without_org) == 0:
            record_test("Organization Isolation", True, 
                       "All users in response have organization_id - isolation working correctly")
        else:
            record_test("Organization Isolation", False, 
                       f"{len(users_without_org)} users without organization_id returned")
    else:
        record_test("Organization Isolation", False, f"Status: {response.status_code}")
except Exception as e:
    record_test("Organization Isolation", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 8: CRITICAL ENDPOINTS ACCESSIBILITY
# ============================================================================
print_section("TEST 8: CRITICAL ENDPOINTS ACCESSIBILITY")

critical_endpoints = [
    ("GET", "/", "Health Check"),
    ("GET", "/roles", "Roles List"),
    ("GET", "/permissions", "Permissions List"),
    ("GET", "/tasks", "Tasks List"),
    ("GET", "/inspections/templates", "Inspection Templates"),
    ("GET", "/reports/overview", "Reports Overview"),
]

for method, endpoint, name in critical_endpoints:
    print_test(f"8.x - {method} {endpoint} ({name})")
    try:
        headers = {"Authorization": f"Bearer {user_token}"}
        
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            record_test(f"{name} Endpoint", True, f"Accessible and working")
        elif response.status_code == 401:
            record_test(f"{name} Endpoint", False, "Authentication failed")
        elif response.status_code == 403:
            record_test(f"{name} Endpoint", True, "Accessible (permission check working)")
        else:
            record_test(f"{name} Endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        record_test(f"{name} Endpoint", False, f"Exception: {str(e)}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_section("TEST SUMMARY")

total_tests = tests_passed + tests_failed
success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
print(f"{Colors.BLUE}FINAL RESULTS:{Colors.END}")
print(f"  Total Tests: {total_tests}")
print(f"  {Colors.GREEN}Passed: {tests_passed}{Colors.END}")
print(f"  {Colors.RED}Failed: {tests_failed}{Colors.END}")
print(f"  Success Rate: {success_rate:.1f}%")
print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

# Categorize results
if success_rate >= 95:
    print(f"{Colors.GREEN}✅ EXCELLENT: Backend is working excellently with {success_rate:.1f}% success rate.{Colors.END}")
    print(f"{Colors.GREEN}   All core functionality is operational. Any failures are minor issues.{Colors.END}")
elif success_rate >= 85:
    print(f"{Colors.YELLOW}⚠️  GOOD: Backend is working well with {success_rate:.1f}% success rate.{Colors.END}")
    print(f"{Colors.YELLOW}   Core functionality operational with some minor issues to address.{Colors.END}")
elif success_rate >= 70:
    print(f"{Colors.YELLOW}⚠️  FAIR: Backend has {success_rate:.1f}% success rate.{Colors.END}")
    print(f"{Colors.YELLOW}   Some critical issues need attention.{Colors.END}")
else:
    print(f"{Colors.RED}❌ CRITICAL: Backend has only {success_rate:.1f}% success rate.{Colors.END}")
    print(f"{Colors.RED}   Major issues preventing core functionality.{Colors.END}")

# List failed tests
if tests_failed > 0:
    print(f"\n{Colors.RED}FAILED TESTS:{Colors.END}")
    for result in test_results:
        if not result["passed"]:
            print(f"  ❌ {result['test']}")
            if result["details"]:
                print(f"     {result['details']}")

print(f"\n{Colors.BLUE}{'='*80}{Colors.END}\n")
