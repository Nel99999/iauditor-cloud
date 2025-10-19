#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND RE-TESTING - VERIFY ALL FIXES
Test with production user: llewellyn@bluedawncapital.co.za (password: Test@1234)

Focus Areas:
1. CRITICAL FIX - Contractor Creation
2. PERMISSION FIX - Checklist Operations
3. NEW ENDPOINTS - Verify Implementation
4. STATUS CODE FIXES - Verify 201 Response
5. PATH CORRECTIONS - Test with Correct Paths
6. ALL 20 MODULES - Comprehensive Testing
"""

import requests
import json
from datetime import datetime
import sys

# Backend URL from frontend/.env
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"

# Production user credentials
PROD_EMAIL = "llewellyn@bluedawncapital.co.za"
PROD_PASSWORD = "Test@1234"

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(category, test_name, passed, status_code=None, message="", response_data=None):
    """Log test result"""
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed"] += 1
        status = "❌ FAIL"
    
    result = {
        "category": category,
        "test": test_name,
        "passed": passed,
        "status_code": status_code,
        "message": message
    }
    test_results["tests"].append(result)
    
    print(f"{status} [{category}] {test_name}")
    if status_code:
        print(f"   Status: {status_code}")
    if message:
        print(f"   {message}")
    if response_data and not passed:
        print(f"   Response: {json.dumps(response_data, indent=2)[:200]}")
    print()

def authenticate():
    """Authenticate and get token"""
    print("=" * 80)
    print("AUTHENTICATING WITH PRODUCTION USER")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": PROD_EMAIL, "password": PROD_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_info = data.get("user", {})
            print(f"✅ Authentication successful")
            print(f"   User: {user_info.get('full_name')} ({user_info.get('email')})")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Organization: {user_info.get('organization_id')}")
            print()
            return token, user_info
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def test_critical_fixes(token):
    """Test critical fixes mentioned in review request"""
    print("=" * 80)
    print("PART 1: CRITICAL FIXES VERIFICATION")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. CONTRACTOR CREATION FIX
    print("\n--- Testing Contractor Creation Fix ---")
    contractor_data = {
        "company_name": "Test Contractor Ltd",
        "contact_person": "John Smith",
        "email": "john@testcontractor.com",
        "phone": "+27123456789"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/contractors",
            json=contractor_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("CRITICAL FIX", "POST /api/contractors - Create contractor", True, 
                    201, "Contractor created successfully (previously returned 500)")
        elif response.status_code == 200:
            log_test("CRITICAL FIX", "POST /api/contractors - Create contractor", False,
                    200, "Returns 200 instead of 201 (should be 201 for creation)")
        else:
            log_test("CRITICAL FIX", "POST /api/contractors - Create contractor", False,
                    response.status_code, f"Failed: {response.text[:200]}")
    except Exception as e:
        log_test("CRITICAL FIX", "POST /api/contractors - Create contractor", False,
                None, f"Exception: {str(e)}")
    
    # 2. PERMISSION FIX - Checklist Templates
    print("\n--- Testing Checklist Permission Fix ---")
    
    # GET templates
    try:
        response = requests.get(
            f"{BASE_URL}/checklists/templates",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PERMISSION FIX", "GET /api/checklists/templates", True,
                    200, "Developer role has access (previously 403)")
        elif response.status_code == 403:
            log_test("PERMISSION FIX", "GET /api/checklists/templates", False,
                    403, "Still returns 403 - permission not fixed")
        else:
            log_test("PERMISSION FIX", "GET /api/checklists/templates", False,
                    response.status_code, f"Unexpected status: {response.text[:200]}")
    except Exception as e:
        log_test("PERMISSION FIX", "GET /api/checklists/templates", False,
                None, f"Exception: {str(e)}")
    
    # POST template
    template_data = {
        "name": "Test Checklist Template",
        "description": "Testing permission fix",
        "category": "safety",
        "items": [
            {"text": "Check item 1", "required": True},
            {"text": "Check item 2", "required": False}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/checklists/templates",
            json=template_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("PERMISSION FIX", "POST /api/checklists/templates", True,
                    201, "Developer role can create templates (previously 403)")
        elif response.status_code == 403:
            log_test("PERMISSION FIX", "POST /api/checklists/templates", False,
                    403, "Still returns 403 - permission not fixed")
        else:
            log_test("PERMISSION FIX", "POST /api/checklists/templates", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PERMISSION FIX", "POST /api/checklists/templates", False,
                None, f"Exception: {str(e)}")

def test_new_endpoints(token):
    """Test new endpoints implementation"""
    print("\n" + "=" * 80)
    print("PART 2: NEW ENDPOINTS VERIFICATION")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    new_endpoints = [
        ("GET", "/inspections/scheduled", "Get scheduled inspections"),
        ("GET", "/checklists/scheduled", "Get scheduled checklists"),
        ("GET", "/checklists/pending-approvals", "Get pending checklist approvals"),
        ("GET", "/financial/capex", "Get CAPEX records"),
        ("GET", "/financial/opex", "Get OPEX records"),
        ("GET", "/financial/budgets", "Get budgets"),
    ]
    
    for method, endpoint, description in new_endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                log_test("NEW ENDPOINTS", f"{method} /api{endpoint}", True,
                        200, f"{description} - endpoint implemented")
            elif response.status_code == 404:
                log_test("NEW ENDPOINTS", f"{method} /api{endpoint}", False,
                        404, f"Endpoint not found - not implemented")
            else:
                log_test("NEW ENDPOINTS", f"{method} /api{endpoint}", False,
                        response.status_code, f"Unexpected status: {response.text[:100]}")
        except Exception as e:
            log_test("NEW ENDPOINTS", f"{method} /api{endpoint}", False,
                    None, f"Exception: {str(e)}")
    
    # Test POST endpoints for financial
    print("\n--- Testing Financial POST Endpoints ---")
    
    # POST CAPEX
    capex_data = {
        "name": "Test CAPEX Item",
        "amount": 50000,
        "category": "equipment",
        "date": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial/capex",
            json=capex_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("NEW ENDPOINTS", "POST /api/financial/capex", True,
                    201, "CAPEX creation endpoint working")
        elif response.status_code == 404:
            log_test("NEW ENDPOINTS", "POST /api/financial/capex", False,
                    404, "Endpoint not found")
        else:
            log_test("NEW ENDPOINTS", "POST /api/financial/capex", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("NEW ENDPOINTS", "POST /api/financial/capex", False,
                None, f"Exception: {str(e)}")
    
    # POST OPEX
    opex_data = {
        "name": "Test OPEX Item",
        "amount": 5000,
        "category": "maintenance",
        "date": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial/opex",
            json=opex_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("NEW ENDPOINTS", "POST /api/financial/opex", True,
                    201, "OPEX creation endpoint working")
        elif response.status_code == 404:
            log_test("NEW ENDPOINTS", "POST /api/financial/opex", False,
                    404, "Endpoint not found")
        else:
            log_test("NEW ENDPOINTS", "POST /api/financial/opex", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("NEW ENDPOINTS", "POST /api/financial/opex", False,
                None, f"Exception: {str(e)}")
    
    # POST Budget
    budget_data = {
        "name": "Q1 2024 Budget",
        "amount": 100000,
        "period": "Q1",
        "year": 2024
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/financial/budgets",
            json=budget_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("NEW ENDPOINTS", "POST /api/financial/budgets", True,
                    201, "Budget creation endpoint working")
        elif response.status_code == 404:
            log_test("NEW ENDPOINTS", "POST /api/financial/budgets", False,
                    404, "Endpoint not found")
        else:
            log_test("NEW ENDPOINTS", "POST /api/financial/budgets", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("NEW ENDPOINTS", "POST /api/financial/budgets", False,
                None, f"Exception: {str(e)}")

def test_status_code_fixes(token):
    """Test status code fixes (201 instead of 200)"""
    print("\n" + "=" * 80)
    print("PART 3: STATUS CODE FIXES (201 vs 200)")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test announcements
    announcement_data = {
        "title": "Test Announcement",
        "content": "Testing status code fix",
        "priority": "normal"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/announcements",
            json=announcement_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("STATUS CODE FIX", "POST /api/announcements", True,
                    201, "Returns 201 (correct)")
        elif response.status_code == 200:
            log_test("STATUS CODE FIX", "POST /api/announcements", False,
                    200, "Returns 200 instead of 201 (should be 201)")
        else:
            log_test("STATUS CODE FIX", "POST /api/announcements", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("STATUS CODE FIX", "POST /api/announcements", False,
                None, f"Exception: {str(e)}")
    
    # Test groups
    group_data = {
        "name": "Test Group",
        "description": "Testing status code fix"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/groups",
            json=group_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("STATUS CODE FIX", "POST /api/groups", True,
                    201, "Returns 201 (correct)")
        elif response.status_code == 200:
            log_test("STATUS CODE FIX", "POST /api/groups", False,
                    200, "Returns 200 instead of 201 (should be 201)")
        else:
            log_test("STATUS CODE FIX", "POST /api/groups", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("STATUS CODE FIX", "POST /api/groups", False,
                None, f"Exception: {str(e)}")
    
    # Test webhooks
    webhook_data = {
        "name": "Test Webhook",
        "url": "https://example.com/webhook",
        "events": ["task.created"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhooks",
            json=webhook_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            log_test("STATUS CODE FIX", "POST /api/webhooks", True,
                    201, "Returns 201 (correct)")
        elif response.status_code == 200:
            log_test("STATUS CODE FIX", "POST /api/webhooks", False,
                    200, "Returns 200 instead of 201 (should be 201)")
        else:
            log_test("STATUS CODE FIX", "POST /api/webhooks", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("STATUS CODE FIX", "POST /api/webhooks", False,
                None, f"Exception: {str(e)}")

def test_path_corrections(token):
    """Test corrected paths"""
    print("\n" + "=" * 80)
    print("PART 4: PATH CORRECTIONS")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Work Orders - correct path is /api/work-orders
    try:
        response = requests.get(
            f"{BASE_URL}/work-orders",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PATH CORRECTION", "GET /api/work-orders", True,
                    200, "Correct path working (not /api/workorders)")
        else:
            log_test("PATH CORRECTION", "GET /api/work-orders", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PATH CORRECTION", "GET /api/work-orders", False,
                None, f"Exception: {str(e)}")
    
    # Inventory - correct path
    try:
        response = requests.get(
            f"{BASE_URL}/inventory/items",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PATH CORRECTION", "GET /api/inventory/items", True,
                    200, "Correct inventory path working")
        else:
            log_test("PATH CORRECTION", "GET /api/inventory/items", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PATH CORRECTION", "GET /api/inventory/items", False,
                None, f"Exception: {str(e)}")
    
    # Training - correct paths
    try:
        response = requests.get(
            f"{BASE_URL}/training/courses",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PATH CORRECTION", "GET /api/training/courses", True,
                    200, "Correct training courses path working")
        else:
            log_test("PATH CORRECTION", "GET /api/training/courses", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PATH CORRECTION", "GET /api/training/courses", False,
                None, f"Exception: {str(e)}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/training/completions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PATH CORRECTION", "GET /api/training/completions", True,
                    200, "Correct training completions path working")
        else:
            log_test("PATH CORRECTION", "GET /api/training/completions", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PATH CORRECTION", "GET /api/training/completions", False,
                None, f"Exception: {str(e)}")
    
    # Dashboards - plural
    try:
        response = requests.get(
            f"{BASE_URL}/dashboards/main",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("PATH CORRECTION", "GET /api/dashboards/main", True,
                    200, "Correct dashboards path (plural) working")
        else:
            log_test("PATH CORRECTION", "GET /api/dashboards/main", False,
                    response.status_code, f"Response: {response.text[:200]}")
    except Exception as e:
        log_test("PATH CORRECTION", "GET /api/dashboards/main", False,
                None, f"Exception: {str(e)}")

def test_all_20_modules(token):
    """Test all 20 modules comprehensively"""
    print("\n" + "=" * 80)
    print("PART 5: ALL 20 MODULES COMPREHENSIVE TESTING")
    print("=" * 80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    modules = [
        ("Inspections", "/inspections/templates", "GET"),
        ("Checklists", "/checklists/templates", "GET"),
        ("Tasks", "/tasks", "GET"),
        ("Assets", "/assets", "GET"),
        ("Work Orders", "/work-orders", "GET"),
        ("Inventory", "/inventory/items", "GET"),
        ("Projects", "/projects", "GET"),
        ("Incidents", "/incidents", "GET"),
        ("Training", "/training/courses", "GET"),
        ("Financial", "/financial/transactions", "GET"),
        ("HR", "/hr/employees", "GET"),
        ("Emergency", "/emergency/plans", "GET"),
        ("Dashboards", "/dashboards/main", "GET"),
        ("Team Chat", "/chat/channels", "GET"),
        ("Contractors", "/contractors", "GET"),
        ("Announcements", "/announcements", "GET"),
        ("Comments", "/comments", "GET"),
        ("Attachments", "/attachments", "GET"),
        ("Notifications", "/notifications", "GET"),
        ("Audit Logs", "/audit/logs", "GET"),
    ]
    
    for module_name, endpoint, method in modules:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                log_test("20 MODULES", f"{module_name} - {method} /api{endpoint}", True,
                        200, f"Module accessible, records: {count}")
            elif response.status_code == 404:
                log_test("20 MODULES", f"{module_name} - {method} /api{endpoint}", False,
                        404, "Endpoint not found")
            elif response.status_code == 500:
                log_test("20 MODULES", f"{module_name} - {method} /api{endpoint}", False,
                        500, "Server error - CRITICAL")
            else:
                log_test("20 MODULES", f"{module_name} - {method} /api{endpoint}", False,
                        response.status_code, f"Response: {response.text[:100]}")
        except Exception as e:
            log_test("20 MODULES", f"{module_name} - {method} /api{endpoint}", False,
                    None, f"Exception: {str(e)}")

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Group by category
    categories = {}
    for test in test_results["tests"]:
        cat = test["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if test["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    print("\n--- Results by Category ---")
    for cat, results in categories.items():
        total_cat = results["passed"] + results["failed"]
        rate = (results["passed"] / total_cat * 100) if total_cat > 0 else 0
        print(f"{cat}: {results['passed']}/{total_cat} ({rate:.1f}%)")
    
    # List all failures
    failures = [t for t in test_results["tests"] if not t["passed"]]
    if failures:
        print("\n--- Failed Tests ---")
        for f in failures:
            print(f"❌ [{f['category']}] {f['test']}")
            print(f"   Status: {f['status_code']}, Message: {f['message']}")
    
    # Compare to target
    print("\n--- Target Comparison ---")
    print(f"Current Success Rate: {success_rate:.1f}%")
    print(f"Target Success Rate: 90-95%")
    if success_rate >= 90:
        print("✅ TARGET ACHIEVED!")
    else:
        print(f"❌ Need {90 - success_rate:.1f}% improvement to reach target")
    
    # Check for critical issues
    critical_issues = []
    for test in test_results["tests"]:
        if test["status_code"] == 500:
            critical_issues.append(test)
    
    if critical_issues:
        print("\n--- CRITICAL ISSUES (500 Errors) ---")
        for issue in critical_issues:
            print(f"🔴 {issue['test']}")
    else:
        print("\n✅ ZERO 500 ERRORS - EXCELLENT!")

def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BACKEND RE-TESTING - VERIFY ALL FIXES")
    print("=" * 80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Production User: {PROD_EMAIL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Authenticate
    token, user_info = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Run all test parts
    test_critical_fixes(token)
    test_new_endpoints(token)
    test_status_code_fixes(token)
    test_path_corrections(token)
    test_all_20_modules(token)
    
    # Print summary
    print_summary()
    
    # Save results to file
    with open("/app/retest_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n✅ Results saved to /app/retest_results.json")

if __name__ == "__main__":
    main()
