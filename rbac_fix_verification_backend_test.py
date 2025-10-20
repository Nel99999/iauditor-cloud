#!/usr/bin/env python3
"""
RBAC FIX VERIFICATION - COMPREHENSIVE BACKEND TESTING
Tests ALL 20 modules after assigning 121 permissions to developer role
Target: 95%+ success rate (up from 79.8%)
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"
PRODUCTION_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "Test@1234"
}

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "permission_errors": 0,
    "server_errors": 0,
    "tests": []
}

def log_test(module, endpoint, method, status_code, expected, result, details=""):
    """Log test result"""
    test_results["total"] += 1
    passed = result == "PASS"
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        if status_code == 403:
            test_results["permission_errors"] += 1
        elif status_code >= 500:
            test_results["server_errors"] += 1
    
    test_results["tests"].append({
        "module": module,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "expected": expected,
        "result": result,
        "details": details
    })
    
    icon = "✅" if passed else "❌"
    print(f"{icon} {module} - {method} {endpoint}: {status_code} ({result}) {details}")

def authenticate():
    """Authenticate and get token"""
    print("\n🔐 AUTHENTICATING...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=PRODUCTION_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_info = data.get("user", {})
            print(f"✅ Authentication successful")
            print(f"   User: {user_info.get('full_name')} ({user_info.get('email')})")
            print(f"   Role: {user_info.get('role')} (Level {user_info.get('role_level')})")
            print(f"   Organization: {user_info.get('organization_id')}")
            print(f"   Permissions: {len(user_info.get('permissions', []))} assigned")
            return token, user_info
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def test_module(token, module_name, tests):
    """Test a module with multiple endpoints"""
    print(f"\n{'='*80}")
    print(f"📦 MODULE: {module_name}")
    print(f"{'='*80}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for test in tests:
        endpoint = test["endpoint"]
        method = test["method"]
        expected_status = test.get("expected_status", [200, 201])
        payload = test.get("payload", None)
        description = test.get("description", "")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=payload, timeout=10)
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=payload, timeout=10)
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            
            status = response.status_code
            
            # Check if status is in expected range
            if isinstance(expected_status, list):
                passed = status in expected_status
            else:
                passed = status == expected_status
            
            result = "PASS" if passed else "FAIL"
            
            # Additional details
            details = description
            if status == 403:
                details += " [PERMISSION DENIED]"
            elif status >= 500:
                details += " [SERVER ERROR]"
            elif status in [200, 201]:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        details += f" (returned {len(data)} items)"
                    elif isinstance(data, dict):
                        if "id" in data:
                            details += f" (created ID: {data['id'][:8]}...)"
                        elif "message" in data:
                            details += f" ({data['message']})"
                except:
                    pass
            
            log_test(module_name, endpoint, method, status, expected_status, result, details)
            
        except requests.exceptions.Timeout:
            log_test(module_name, endpoint, method, 0, expected_status, "FAIL", "TIMEOUT")
        except Exception as e:
            log_test(module_name, endpoint, method, 0, expected_status, "FAIL", f"ERROR: {str(e)}")
        
        time.sleep(0.1)  # Rate limiting

def run_comprehensive_tests(token, user_info):
    """Run comprehensive tests across all 20 modules"""
    
    org_id = user_info.get("organization_id")
    user_id = user_info.get("id")
    
    # MODULE 1: INSPECTIONS
    test_module(token, "INSPECTIONS", [
        {"endpoint": "/inspections/templates", "method": "GET", "description": "List templates"},
        {"endpoint": "/inspections/templates", "method": "POST", "description": "Create template",
         "payload": {
             "name": f"RBAC Test Inspection {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "category": "Safety",
             "sections": [{"title": "Section 1", "questions": [{"text": "Question 1", "type": "text"}]}]
         }},
        {"endpoint": "/inspections/executions", "method": "GET", "description": "List executions"},
    ])
    
    # MODULE 2: CHECKLISTS
    test_module(token, "CHECKLISTS", [
        {"endpoint": "/checklists/templates", "method": "GET", "description": "List templates"},
        {"endpoint": "/checklists/templates", "method": "POST", "description": "Create template",
         "payload": {
             "name": f"RBAC Test Checklist {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "category": "Operations",
             "items": [{"text": "Item 1", "required": True}]
         }},
        {"endpoint": "/checklists/executions", "method": "GET", "description": "List executions"},
    ])
    
    # MODULE 3: TASKS
    test_module(token, "TASKS", [
        {"endpoint": "/tasks", "method": "GET", "description": "List tasks"},
        {"endpoint": "/tasks", "method": "POST", "description": "Create task",
         "payload": {
             "title": f"RBAC Test Task {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "priority": "medium",
             "status": "pending"
         }},
    ])
    
    # MODULE 4: ASSETS
    test_module(token, "ASSETS", [
        {"endpoint": "/assets", "method": "GET", "description": "List assets"},
        {"endpoint": "/assets", "method": "POST", "description": "Create asset",
         "payload": {
             "name": f"RBAC Test Asset {datetime.now().strftime('%H%M%S')}",
             "asset_type": "Equipment",
             "status": "operational",
             "location": "Warehouse A"
         }},
    ])
    
    # MODULE 5: WORK ORDERS
    test_module(token, "WORK ORDERS", [
        {"endpoint": "/workorders", "method": "GET", "description": "List work orders"},
        {"endpoint": "/workorders", "method": "POST", "description": "Create work order",
         "payload": {
             "title": f"RBAC Test Work Order {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "priority": "medium",
             "status": "pending"
         }},
    ])
    
    # MODULE 6: INVENTORY
    test_module(token, "INVENTORY", [
        {"endpoint": "/inventory", "method": "GET", "description": "List inventory"},
        {"endpoint": "/inventory", "method": "POST", "description": "Create inventory item",
         "payload": {
             "name": f"RBAC Test Item {datetime.now().strftime('%H%M%S')}",
             "sku": f"SKU{datetime.now().strftime('%H%M%S')}",
             "quantity": 100,
             "unit": "pieces"
         }},
    ])
    
    # MODULE 7: PROJECTS
    test_module(token, "PROJECTS", [
        {"endpoint": "/projects", "method": "GET", "description": "List projects"},
        {"endpoint": "/projects", "method": "POST", "description": "Create project",
         "payload": {
             "name": f"RBAC Test Project {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "status": "planning"
         }},
    ])
    
    # MODULE 8: INCIDENTS
    test_module(token, "INCIDENTS", [
        {"endpoint": "/incidents", "method": "GET", "description": "List incidents"},
        {"endpoint": "/incidents", "method": "POST", "description": "Create incident",
         "payload": {
             "title": f"RBAC Test Incident {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "severity": "medium",
             "status": "open"
         }},
    ])
    
    # MODULE 9: TRAINING
    test_module(token, "TRAINING", [
        {"endpoint": "/training/programs", "method": "GET", "description": "List programs"},
        {"endpoint": "/training/programs", "method": "POST", "description": "Create program",
         "payload": {
             "name": f"RBAC Test Training {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "duration_hours": 8
         }},
    ])
    
    # MODULE 10: FINANCIAL
    test_module(token, "FINANCIAL", [
        {"endpoint": "/financial/transactions", "method": "GET", "description": "List transactions"},
        {"endpoint": "/financial/transactions", "method": "POST", "description": "Create transaction",
         "payload": {
             "description": f"RBAC Test Transaction {datetime.now().strftime('%H%M%S')}",
             "amount": 1000.00,
             "transaction_type": "expense",
             "category": "operations"
         }},
    ])
    
    # MODULE 11: HR
    test_module(token, "HR", [
        {"endpoint": "/hr/employees", "method": "GET", "description": "List employees"},
    ])
    
    # MODULE 12: EMERGENCIES
    test_module(token, "EMERGENCIES", [
        {"endpoint": "/emergencies", "method": "GET", "description": "List emergencies"},
        {"endpoint": "/emergencies", "method": "POST", "description": "Create emergency",
         "payload": {
             "title": f"RBAC Test Emergency {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions",
             "severity": "medium",
             "status": "active"
         }},
    ])
    
    # MODULE 13: TEAM CHAT
    test_module(token, "TEAM CHAT", [
        {"endpoint": "/chat/channels", "method": "GET", "description": "List channels"},
    ])
    
    # MODULE 14: ANNOUNCEMENTS
    test_module(token, "ANNOUNCEMENTS", [
        {"endpoint": "/announcements", "method": "GET", "description": "List announcements"},
        {"endpoint": "/announcements", "method": "POST", "description": "Create announcement",
         "payload": {
             "title": f"RBAC Test Announcement {datetime.now().strftime('%H%M%S')}",
             "content": "Testing RBAC permissions",
             "priority": "normal"
         }},
    ])
    
    # MODULE 15: CONTRACTORS
    test_module(token, "CONTRACTORS", [
        {"endpoint": "/contractors", "method": "GET", "description": "List contractors"},
        {"endpoint": "/contractors", "method": "POST", "description": "Create contractor",
         "payload": {
             "name": f"RBAC Test Contractor {datetime.now().strftime('%H%M%S')}",
             "company": "Test Company",
             "email": f"contractor{datetime.now().strftime('%H%M%S')}@test.com",
             "phone": "+1234567890"
         }},
    ])
    
    # MODULE 16: GROUPS
    test_module(token, "GROUPS", [
        {"endpoint": "/groups", "method": "GET", "description": "List groups"},
        {"endpoint": "/groups", "method": "POST", "description": "Create group",
         "payload": {
             "name": f"RBAC Test Group {datetime.now().strftime('%H%M%S')}",
             "description": "Testing RBAC permissions"
         }},
    ])
    
    # MODULE 17: WEBHOOKS
    test_module(token, "WEBHOOKS", [
        {"endpoint": "/webhooks", "method": "GET", "description": "List webhooks"},
        {"endpoint": "/webhooks", "method": "POST", "description": "Create webhook",
         "payload": {
             "name": f"RBAC Test Webhook {datetime.now().strftime('%H%M%S')}",
             "url": "https://example.com/webhook",
             "events": ["task.created"],
             "is_active": True
         }},
    ])
    
    # MODULE 18: REPORTS
    test_module(token, "REPORTS", [
        {"endpoint": "/reports/overview", "method": "GET", "description": "Reports overview"},
    ])
    
    # MODULE 19: ANALYTICS
    test_module(token, "ANALYTICS", [
        {"endpoint": "/analytics/overview", "method": "GET", "description": "Analytics overview"},
    ])
    
    # MODULE 20: AUDIT LOGS
    test_module(token, "AUDIT LOGS", [
        {"endpoint": "/audit/logs", "method": "GET", "description": "List audit logs"},
    ])
    
    # CORE MANAGEMENT MODULES
    test_module(token, "USER MANAGEMENT", [
        {"endpoint": "/users", "method": "GET", "description": "List users"},
    ])
    
    test_module(token, "ROLE MANAGEMENT", [
        {"endpoint": "/roles", "method": "GET", "description": "List roles"},
    ])
    
    test_module(token, "ORGANIZATION", [
        {"endpoint": "/organizations/units", "method": "GET", "description": "List org units"},
    ])
    
    test_module(token, "INVITATIONS", [
        {"endpoint": "/invitations", "method": "GET", "description": "List invitations"},
    ])
    
    test_module(token, "WORKFLOWS", [
        {"endpoint": "/workflows", "method": "GET", "description": "List workflows"},
    ])

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    success_rate = (test_results["passed"] / test_results["total"] * 100) if test_results["total"] > 0 else 0
    
    print(f"\n✅ PASSED: {test_results['passed']}/{test_results['total']} ({success_rate:.1f}%)")
    print(f"❌ FAILED: {test_results['failed']}/{test_results['total']}")
    print(f"🚫 Permission Errors (403): {test_results['permission_errors']}")
    print(f"💥 Server Errors (500): {test_results['server_errors']}")
    
    # Target assessment
    print(f"\n🎯 TARGET ASSESSMENT:")
    if success_rate >= 95:
        print(f"   ✅ SUCCESS RATE {success_rate:.1f}% - EXCEEDS 95% TARGET!")
    elif success_rate >= 90:
        print(f"   ⚠️  SUCCESS RATE {success_rate:.1f}% - CLOSE TO TARGET (90-95%)")
    else:
        print(f"   ❌ SUCCESS RATE {success_rate:.1f}% - BELOW 90% TARGET")
    
    # Show failed tests by category
    if test_results["failed"] > 0:
        print(f"\n❌ FAILED TESTS BY CATEGORY:")
        
        permission_failures = [t for t in test_results["tests"] if t["result"] == "FAIL" and t["status_code"] == 403]
        server_failures = [t for t in test_results["tests"] if t["result"] == "FAIL" and t["status_code"] >= 500]
        other_failures = [t for t in test_results["tests"] if t["result"] == "FAIL" and t["status_code"] not in [403] and t["status_code"] < 500]
        
        if permission_failures:
            print(f"\n   🚫 PERMISSION ERRORS (403) - {len(permission_failures)} tests:")
            for test in permission_failures[:10]:  # Show first 10
                print(f"      • {test['module']}: {test['method']} {test['endpoint']}")
        
        if server_failures:
            print(f"\n   💥 SERVER ERRORS (500+) - {len(server_failures)} tests:")
            for test in server_failures[:10]:
                print(f"      • {test['module']}: {test['method']} {test['endpoint']} ({test['status_code']})")
        
        if other_failures:
            print(f"\n   ⚠️  OTHER FAILURES - {len(other_failures)} tests:")
            for test in other_failures[:10]:
                print(f"      • {test['module']}: {test['method']} {test['endpoint']} ({test['status_code']})")
    
    # Show successful modules
    successful_modules = {}
    for test in test_results["tests"]:
        module = test["module"]
        if module not in successful_modules:
            successful_modules[module] = {"passed": 0, "total": 0}
        successful_modules[module]["total"] += 1
        if test["result"] == "PASS":
            successful_modules[module]["passed"] += 1
    
    print(f"\n✅ MODULE SUCCESS RATES:")
    for module, stats in sorted(successful_modules.items()):
        rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        icon = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
        print(f"   {icon} {module}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")

def main():
    """Main test execution"""
    print("="*80)
    print("🚀 RBAC FIX VERIFICATION - COMPREHENSIVE BACKEND TESTING")
    print("="*80)
    print(f"Target: 95%+ success rate (up from 79.8%)")
    print(f"Testing ALL 20 modules with production user")
    print(f"Expected: Zero 403 permission errors after assigning 121 permissions")
    
    # Authenticate
    token, user_info = authenticate()
    if not token:
        print("\n❌ CANNOT PROCEED - Authentication failed")
        return
    
    # Run comprehensive tests
    run_comprehensive_tests(token, user_info)
    
    # Print summary
    print_summary()
    
    # Save results to file
    with open("/app/rbac_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n💾 Detailed results saved to: /app/rbac_test_results.json")

if __name__ == "__main__":
    main()
