"""
FINAL COMPREHENSIVE SYSTEM VALIDATION TEST
Testing with REAL production organization: llewellyn's org (315fa36c-4555-4b2b-8ba3-fdbde31cb940)

Expected Baseline:
- Users: 2
- Roles: 12
- Permissions: 26
- Inspection Templates: 7
- Inspection Executions: 13
- Checklist Templates: 6 (FIXED from 2)
- Checklist Executions: 5
- Organization Units: 40 (FIXED from 9)
- Tasks: 0
- Workflows: 0
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://twilio-ops.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Production organization ID
PROD_ORG_ID = "315fa36c-4555-4b2b-8ba3-fdbde31cb940"

# Expected baseline counts
EXPECTED_COUNTS = {
    "users": 2,
    "roles": 12,
    "permissions": 26,
    "inspection_templates": 7,
    "inspection_executions": 13,
    "checklist_templates": 6,
    "checklist_executions": 5,
    "organization_units": 40,
    "tasks": 0,
    "workflows": 0
}

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, message="", details=None):
    """Log test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "✅ PASSED"
    else:
        test_results["failed"] += 1
        status = "❌ FAILED"
    
    result = {
        "name": test_name,
        "status": status,
        "message": message,
        "details": details
    }
    test_results["tests"].append(result)
    print(f"{status}: {test_name}")
    if message:
        print(f"  {message}")
    if details:
        print(f"  Details: {details}")

def get_auth_token():
    """Get authentication token for testing"""
    # Try to login with a test user or use existing credentials
    # For production org, we need valid credentials
    print("\n🔐 Attempting to authenticate...")
    
    # Try common test credentials
    login_data = {
        "email": "llewellyn@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Authentication successful")
            return token
        else:
            print(f"⚠️  Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_endpoint_count(endpoint, expected_count, token, test_name, count_field=None):
    """Test an endpoint and verify count matches expected"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        
        if response.status_code != 200:
            log_test(test_name, False, f"HTTP {response.status_code}", response.text[:200])
            return None
        
        data = response.json()
        
        # Determine count based on response structure
        if isinstance(data, list):
            actual_count = len(data)
        elif isinstance(data, dict):
            if count_field and count_field in data:
                actual_count = data[count_field]
            elif 'items' in data:
                actual_count = len(data['items'])
            elif 'data' in data:
                actual_count = len(data['data'])
            else:
                # Try to find a count field
                for key in ['count', 'total', 'total_count']:
                    if key in data:
                        actual_count = data[key]
                        break
                else:
                    actual_count = len(data)
        else:
            actual_count = 0
        
        passed = actual_count == expected_count
        message = f"Expected: {expected_count}, Actual: {actual_count}"
        
        log_test(test_name, passed, message, {"endpoint": endpoint, "count": actual_count})
        return actual_count
        
    except Exception as e:
        log_test(test_name, False, f"Exception: {str(e)}")
        return None

def test_show_inactive_parameter(endpoint, token, test_name):
    """Test show_inactive parameter functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test with show_inactive=true
        response_true = requests.get(f"{API_BASE}{endpoint}?show_inactive=true", headers=headers)
        # Test with show_inactive=false
        response_false = requests.get(f"{API_BASE}{endpoint}?show_inactive=false", headers=headers)
        
        if response_true.status_code != 200 or response_false.status_code != 200:
            log_test(test_name, False, f"HTTP errors: true={response_true.status_code}, false={response_false.status_code}")
            return
        
        data_true = response_true.json()
        data_false = response_false.json()
        
        count_true = len(data_true) if isinstance(data_true, list) else len(data_true.get('items', []))
        count_false = len(data_false) if isinstance(data_false, list) else len(data_false.get('items', []))
        
        # show_inactive=true should return >= show_inactive=false
        passed = count_true >= count_false
        message = f"show_inactive=true: {count_true}, show_inactive=false: {count_false}"
        
        log_test(test_name, passed, message)
        
    except Exception as e:
        log_test(test_name, False, f"Exception: {str(e)}")

def test_approval_system(token):
    """Test approval system functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 Testing Approval System...")
    
    # Test 1: Check if approval permissions exist
    try:
        response = requests.get(f"{API_BASE}/permissions", headers=headers)
        if response.status_code == 200:
            permissions = response.json()
            approval_perms = [p for p in permissions if 'approval' in p.get('name', '').lower() or 'approve' in p.get('name', '').lower()]
            
            passed = len(approval_perms) >= 3
            message = f"Found {len(approval_perms)} approval permissions (expected >= 3)"
            log_test("Approval Permissions Exist", passed, message, {"permissions": [p.get('name') for p in approval_perms]})
        else:
            log_test("Approval Permissions Exist", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Approval Permissions Exist", False, f"Exception: {str(e)}")
    
    # Test 2: Check pending approvals endpoint
    try:
        response = requests.get(f"{API_BASE}/users/pending-approvals", headers=headers)
        passed = response.status_code in [200, 404]  # 404 is ok if no pending approvals
        message = f"HTTP {response.status_code}"
        log_test("Pending Approvals Endpoint Accessible", passed, message)
    except Exception as e:
        log_test("Pending Approvals Endpoint Accessible", False, f"Exception: {str(e)}")
    
    # Test 3: Verify users have approval_status field
    try:
        response = requests.get(f"{API_BASE}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            users_list = users if isinstance(users, list) else users.get('items', [])
            
            users_with_approval = [u for u in users_list if 'approval_status' in u]
            total_users = len(users_list)
            
            # All users should have approval_status
            passed = len(users_with_approval) == total_users
            message = f"{len(users_with_approval)}/{total_users} users have approval_status"
            log_test("Users Have Approval Status", passed, message)
        else:
            log_test("Users Have Approval Status", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Users Have Approval Status", False, f"Exception: {str(e)}")

def test_data_integrity(token):
    """Test data integrity - no orphaned records, proper organization linking"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Testing Data Integrity...")
    
    # Test 1: All users belong to organizations
    try:
        response = requests.get(f"{API_BASE}/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            users_list = users if isinstance(users, list) else users.get('items', [])
            
            users_with_org = [u for u in users_list if u.get('organization_id')]
            total_users = len(users_list)
            
            passed = len(users_with_org) == total_users
            message = f"{len(users_with_org)}/{total_users} users have organization_id"
            log_test("All Users Have Organization", passed, message)
        else:
            log_test("All Users Have Organization", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("All Users Have Organization", False, f"Exception: {str(e)}")
    
    # Test 2: All organization units have valid structure
    try:
        response = requests.get(f"{API_BASE}/organizations/units", headers=headers)
        if response.status_code == 200:
            units = response.json()
            units_list = units if isinstance(units, list) else units.get('items', [])
            
            valid_units = [u for u in units_list if u.get('name') and u.get('level') and u.get('organization_id')]
            total_units = len(units_list)
            
            passed = len(valid_units) == total_units
            message = f"{len(valid_units)}/{total_units} units have valid structure"
            log_test("Organization Units Valid Structure", passed, message)
        else:
            log_test("Organization Units Valid Structure", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Organization Units Valid Structure", False, f"Exception: {str(e)}")
    
    # Test 3: All inspections belong to organizations
    try:
        response = requests.get(f"{API_BASE}/inspections/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            templates_list = templates if isinstance(templates, list) else templates.get('items', [])
            
            templates_with_org = [t for t in templates_list if t.get('organization_id')]
            total_templates = len(templates_list)
            
            passed = len(templates_with_org) == total_templates
            message = f"{len(templates_with_org)}/{total_templates} inspection templates have organization_id"
            log_test("Inspection Templates Have Organization", passed, message)
        else:
            log_test("Inspection Templates Have Organization", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("Inspection Templates Have Organization", False, f"Exception: {str(e)}")

def test_organization_isolation(token):
    """Test that organization isolation is working"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔒 Testing Organization Isolation...")
    
    # Get current user's organization
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            user_org_id = user.get('organization_id')
            
            if not user_org_id:
                log_test("Organization Isolation", False, "User has no organization_id")
                return
            
            # Check that all returned data belongs to user's organization
            endpoints_to_check = [
                "/users",
                "/organizations/units",
                "/inspections/templates",
                "/checklists/templates",
                "/tasks"
            ]
            
            all_isolated = True
            for endpoint in endpoints_to_check:
                resp = requests.get(f"{API_BASE}{endpoint}", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data if isinstance(data, list) else data.get('items', [])
                    
                    # Check if all items belong to user's org
                    for item in items:
                        if item.get('organization_id') and item.get('organization_id') != user_org_id:
                            all_isolated = False
                            log_test(f"Organization Isolation - {endpoint}", False, 
                                   f"Found item from different org: {item.get('organization_id')}")
                            break
            
            if all_isolated:
                log_test("Organization Isolation", True, "All data properly isolated to user's organization")
        else:
            log_test("Organization Isolation", False, f"Cannot get current user: HTTP {response.status_code}")
    except Exception as e:
        log_test("Organization Isolation", False, f"Exception: {str(e)}")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("=" * 80)
    print("FINAL COMPREHENSIVE SYSTEM VALIDATION TEST")
    print("=" * 80)
    print(f"Backend URL: {API_BASE}")
    print(f"Production Org ID: {PROD_ORG_ID}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("\n❌ CRITICAL: Cannot proceed without authentication token")
        print("Please ensure valid credentials are available for the production organization")
        return None
    
    print("\n" + "=" * 80)
    print("PHASE 1: API ENDPOINT VERIFICATION")
    print("=" * 80)
    
    # Test all main endpoints with expected counts
    test_endpoint_count("/users", EXPECTED_COUNTS["users"], token, "GET /api/users")
    test_endpoint_count("/roles", EXPECTED_COUNTS["roles"], token, "GET /api/roles")
    test_endpoint_count("/permissions", EXPECTED_COUNTS["permissions"], token, "GET /api/permissions")
    test_endpoint_count("/inspections/templates", EXPECTED_COUNTS["inspection_templates"], token, "GET /api/inspections/templates")
    test_endpoint_count("/inspections/executions", EXPECTED_COUNTS["inspection_executions"], token, "GET /api/inspections/executions")
    test_endpoint_count("/checklists/templates", EXPECTED_COUNTS["checklist_templates"], token, "GET /api/checklists/templates")
    test_endpoint_count("/checklists/executions", EXPECTED_COUNTS["checklist_executions"], token, "GET /api/checklists/executions")
    test_endpoint_count("/organizations/units", EXPECTED_COUNTS["organization_units"], token, "GET /api/organizations/units")
    test_endpoint_count("/tasks", EXPECTED_COUNTS["tasks"], token, "GET /api/tasks")
    
    # Test additional endpoints
    print("\n📊 Testing Additional Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/dashboard/stats", headers=headers)
        passed = response.status_code == 200
        log_test("GET /api/dashboard/stats", passed, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("GET /api/dashboard/stats", False, f"Exception: {str(e)}")
    
    try:
        response = requests.get(f"{API_BASE}/invitations", headers=headers)
        passed = response.status_code == 200
        log_test("GET /api/invitations", passed, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("GET /api/invitations", False, f"Exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("PHASE 2: SHOW_INACTIVE PARAMETER TESTING")
    print("=" * 80)
    
    test_show_inactive_parameter("/organizations/units", token, "Organization Units - show_inactive parameter")
    test_show_inactive_parameter("/checklists/templates", token, "Checklist Templates - show_inactive parameter")
    
    print("\n" + "=" * 80)
    print("PHASE 3: APPROVAL SYSTEM VERIFICATION")
    print("=" * 80)
    
    test_approval_system(token)
    
    print("\n" + "=" * 80)
    print("PHASE 4: DATA INTEGRITY CHECKS")
    print("=" * 80)
    
    test_data_integrity(token)
    
    print("\n" + "=" * 80)
    print("PHASE 5: ORGANIZATION ISOLATION")
    print("=" * 80)
    
    test_organization_isolation(token)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
    print("=" * 80)
    
    # Print failed tests details
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS DETAILS:")
        print("=" * 80)
        for test in test_results['tests']:
            if "❌" in test['status']:
                print(f"\n{test['name']}")
                print(f"  Status: {test['status']}")
                print(f"  Message: {test['message']}")
                if test['details']:
                    print(f"  Details: {test['details']}")
    
    # Save results to file
    with open('/app/final_validation_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("\n✅ Results saved to: /app/final_validation_results.json")
    
    return test_results

if __name__ == "__main__":
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    if results is None:
        print("\n❌ TESTS COULD NOT RUN - CHECK AUTHENTICATION")
        exit(1)
    elif results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        exit(0)
    else:
        print(f"\n⚠️  {results['failed']} TEST(S) FAILED")
        exit(1)
