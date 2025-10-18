"""
Comprehensive Backend Testing: Password Reset & New Profile Creation Workflow
Test Suites:
1. Password Reset Flow (5 tests)
2. New Profile Creation (6 tests)
3. User Rejection Flow (4 tests)
4. Permission Verification (2 tests)
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://ops-control-center.preview.emergentagent.com/api"
PRODUCTION_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
PRODUCTION_USER_PASSWORD = "TestPassword123!"  # Set for testing
PRODUCTION_ORG_ID = "315fa36c-4555-4b2b-8ba3-fdbde31cb940"

# Test results tracking
test_results = {
    "suite_1_password_reset": [],
    "suite_2_profile_creation": [],
    "suite_3_user_rejection": [],
    "suite_4_permissions": []
}

def log_test(suite, test_name, passed, details=""):
    """Log test result"""
    result = {
        "test": test_name,
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results[suite].append(result)
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    print()

def get_developer_token():
    """Login as production developer user"""
    print("=" * 80)
    print("AUTHENTICATING AS PRODUCTION DEVELOPER USER")
    print("=" * 80)
    
    # First, let's try to login with the production user
    # We'll need to get the password from MongoDB or use a known password
    # For now, let's try a common password or we'll need to reset it
    
    # Try to login
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": PRODUCTION_USER_EMAIL,
            "password": PRODUCTION_USER_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully logged in as {PRODUCTION_USER_EMAIL}")
        print(f"   Role: {data.get('user', {}).get('role')}")
        return data.get("access_token")
    else:
        print(f"❌ Failed to login: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

# ==================== TEST SUITE 1: PASSWORD RESET FLOW ====================

def test_suite_1_password_reset():
    """Test Suite 1: Password Reset Flow (5 tests)"""
    print("\n" + "=" * 80)
    print("TEST SUITE 1: PASSWORD RESET FLOW")
    print("=" * 80 + "\n")
    
    # Test 1.1: Forgot Password - Valid Email
    print("Test 1.1: Forgot Password - Valid Email")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/forgot-password",
        json={"email": PRODUCTION_USER_EMAIL}
    )
    
    passed = (
        response.status_code == 200 and
        "password reset link has been sent" in response.text.lower()
    )
    log_test(
        "suite_1_password_reset",
        "Test 1.1: Forgot Password - Valid Email",
        passed,
        f"Status: {response.status_code}, Response: {response.text[:200]}"
    )
    
    # Test 1.2: Forgot Password - Non-existent Email
    print("Test 1.2: Forgot Password - Non-existent Email")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/forgot-password",
        json={"email": "nonexistent@test.com"}
    )
    
    passed = (
        response.status_code == 200 and
        "password reset link has been sent" in response.text.lower()
    )
    log_test(
        "suite_1_password_reset",
        "Test 1.2: Forgot Password - Non-existent Email",
        passed,
        f"Status: {response.status_code}, Response: {response.text[:200]}"
    )
    
    # Test 1.3: Get Reset Token from Database
    print("Test 1.3: Get Reset Token from Database")
    print("-" * 80)
    print("⚠️  Manual step: Need to query MongoDB for password_reset_token")
    print(f"   Command: db.users.findOne({{email: '{PRODUCTION_USER_EMAIL}'}}, {{password_reset_token: 1, password_reset_expires_at: 1}})")
    
    # For automated testing, we'll try to get it via a different method
    # Since we can't directly access MongoDB from here, we'll skip this for now
    reset_token = None
    log_test(
        "suite_1_password_reset",
        "Test 1.3: Get Reset Token from Database",
        False,
        "Manual MongoDB query required - cannot automate from test script"
    )
    
    # Test 1.4: Reset Password - Valid Token (will be skipped if no token)
    print("Test 1.4: Reset Password - Valid Token")
    print("-" * 80)
    if reset_token:
        response = requests.post(
            f"{BACKEND_URL}/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "TestPass123!"
            }
        )
        
        passed = (
            response.status_code == 200 and
            "password has been reset successfully" in response.text.lower()
        )
        log_test(
            "suite_1_password_reset",
            "Test 1.4: Reset Password - Valid Token",
            passed,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    else:
        log_test(
            "suite_1_password_reset",
            "Test 1.4: Reset Password - Valid Token",
            False,
            "Skipped - no reset token available"
        )
    
    # Test 1.5: Reset Password - Invalid Token
    print("Test 1.5: Reset Password - Invalid Token")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/reset-password",
        json={
            "token": "invalid-token-12345",
            "new_password": "TestPass123!"
        }
    )
    
    passed = (
        response.status_code == 400 and
        "invalid or expired reset token" in response.text.lower()
    )
    log_test(
        "suite_1_password_reset",
        "Test 1.5: Reset Password - Invalid Token",
        passed,
        f"Status: {response.status_code}, Response: {response.text[:200]}"
    )

# ==================== TEST SUITE 2: NEW PROFILE CREATION ====================

def test_suite_2_profile_creation(developer_token):
    """Test Suite 2: New Profile Creation (6 tests)"""
    print("\n" + "=" * 80)
    print("TEST SUITE 2: NEW PROFILE CREATION")
    print("=" * 80 + "\n")
    
    # Generate unique email with timestamp
    timestamp = int(time.time())
    test_email = f"testuser_{timestamp}@example.com"
    test_password = "TestPass123!"
    test_name = "Test User Profile"
    test_org = "Test Organization"
    test_user_id = None
    
    # Test 2.1: Register New User (Pending Status)
    print("Test 2.1: Register New User (Pending Status)")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "name": test_name,
            "organization_name": test_org
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        test_user_id = data.get("user", {}).get("id")
        
        passed = (
            data.get("access_token") == "" and
            data.get("user", {}).get("approval_status") == "pending" and
            "pending" in data.get("user", {}).get("message", "").lower()
        )
        log_test(
            "suite_2_profile_creation",
            "Test 2.1: Register New User (Pending Status)",
            passed,
            f"User ID: {test_user_id}, Status: {data.get('user', {}).get('approval_status')}, Token: '{data.get('access_token')}'"
        )
    else:
        log_test(
            "suite_2_profile_creation",
            "Test 2.1: Register New User (Pending Status)",
            False,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    
    # Test 2.2: Verify User in Database (Manual check)
    print("Test 2.2: Verify User in Database")
    print("-" * 80)
    print("⚠️  Manual step: Need to query MongoDB")
    print(f"   Command: db.users.findOne({{email: '{test_email}'}})")
    print(f"   Expected: approval_status='pending', is_active=false, role='viewer', invited=false")
    log_test(
        "suite_2_profile_creation",
        "Test 2.2: Verify User in Database",
        False,
        "Manual MongoDB query required"
    )
    
    # Test 2.3: Login Attempt with Pending User (Should Fail)
    print("Test 2.3: Login Attempt with Pending User (Should Fail)")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    
    passed = (
        response.status_code == 403 and
        "pending admin approval" in response.text.lower()
    )
    log_test(
        "suite_2_profile_creation",
        "Test 2.3: Login Attempt with Pending User (Should Fail)",
        passed,
        f"Status: {response.status_code}, Response: {response.text[:200]}"
    )
    
    # Test 2.4: Get Pending Approvals (As Developer)
    print("Test 2.4: Get Pending Approvals (As Developer)")
    print("-" * 80)
    if developer_token:
        response = requests.get(
            f"{BACKEND_URL}/users/pending-approvals",
            headers={"Authorization": f"Bearer {developer_token}"}
        )
        
        if response.status_code == 200:
            pending_users = response.json()
            found_user = any(u.get("email") == test_email for u in pending_users)
            
            passed = found_user and all(
                u.get("approval_status") == "pending" and u.get("invited") == False
                for u in pending_users if u.get("email") == test_email
            )
            log_test(
                "suite_2_profile_creation",
                "Test 2.4: Get Pending Approvals (As Developer)",
                passed,
                f"Found {len(pending_users)} pending users, Test user found: {found_user}"
            )
        else:
            log_test(
                "suite_2_profile_creation",
                "Test 2.4: Get Pending Approvals (As Developer)",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
    else:
        log_test(
            "suite_2_profile_creation",
            "Test 2.4: Get Pending Approvals (As Developer)",
            False,
            "No developer token available"
        )
    
    # Test 2.5: Approve User (As Developer)
    print("Test 2.5: Approve User (As Developer)")
    print("-" * 80)
    if developer_token and test_user_id:
        response = requests.post(
            f"{BACKEND_URL}/users/{test_user_id}/approve",
            headers={"Authorization": f"Bearer {developer_token}"},
            json={"approval_notes": "Approved for testing purposes"}
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = (
                "has been approved" in data.get("message", "").lower() and
                data.get("approved_by") is not None and
                data.get("approved_at") is not None
            )
            log_test(
                "suite_2_profile_creation",
                "Test 2.5: Approve User (As Developer)",
                passed,
                f"Message: {data.get('message')}, Approved by: {data.get('approved_by')}"
            )
        else:
            log_test(
                "suite_2_profile_creation",
                "Test 2.5: Approve User (As Developer)",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
    else:
        log_test(
            "suite_2_profile_creation",
            "Test 2.5: Approve User (As Developer)",
            False,
            "No developer token or user ID available"
        )
    
    # Test 2.6: Login After Approval (Should Succeed)
    print("Test 2.6: Login After Approval (Should Succeed)")
    print("-" * 80)
    time.sleep(1)  # Give database a moment to update
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        passed = (
            data.get("access_token") != "" and
            data.get("user", {}).get("approval_status") == "approved" and
            data.get("user", {}).get("is_active") == True
        )
        log_test(
            "suite_2_profile_creation",
            "Test 2.6: Login After Approval (Should Succeed)",
            passed,
            f"Token received: {bool(data.get('access_token'))}, Status: {data.get('user', {}).get('approval_status')}, Active: {data.get('user', {}).get('is_active')}"
        )
    else:
        log_test(
            "suite_2_profile_creation",
            "Test 2.6: Login After Approval (Should Succeed)",
            False,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    
    return test_email, test_user_id

# ==================== TEST SUITE 3: USER REJECTION FLOW ====================

def test_suite_3_user_rejection(developer_token):
    """Test Suite 3: User Rejection Flow (4 tests)"""
    print("\n" + "=" * 80)
    print("TEST SUITE 3: USER REJECTION FLOW")
    print("=" * 80 + "\n")
    
    # Generate unique email with timestamp
    timestamp = int(time.time())
    reject_email = f"reject_user_{timestamp}@example.com"
    reject_password = "TestPass123!"
    reject_name = "User To Reject"
    reject_org = "Reject Test Org"
    reject_user_id = None
    
    # Test 3.1: Register Another New User
    print("Test 3.1: Register Another New User")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={
            "email": reject_email,
            "password": reject_password,
            "name": reject_name,
            "organization_name": reject_org
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        reject_user_id = data.get("user", {}).get("id")
        
        passed = (
            data.get("user", {}).get("approval_status") == "pending"
        )
        log_test(
            "suite_3_user_rejection",
            "Test 3.1: Register Another New User",
            passed,
            f"User ID: {reject_user_id}, Status: {data.get('user', {}).get('approval_status')}"
        )
    else:
        log_test(
            "suite_3_user_rejection",
            "Test 3.1: Register Another New User",
            False,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    
    # Test 3.2: Reject User (As Developer)
    print("Test 3.2: Reject User (As Developer)")
    print("-" * 80)
    if developer_token and reject_user_id:
        response = requests.post(
            f"{BACKEND_URL}/users/{reject_user_id}/reject",
            headers={"Authorization": f"Bearer {developer_token}"},
            json={"approval_notes": "Profile does not meet requirements"}
        )
        
        if response.status_code == 200:
            data = response.json()
            passed = "has been rejected" in data.get("message", "").lower()
            log_test(
                "suite_3_user_rejection",
                "Test 3.2: Reject User (As Developer)",
                passed,
                f"Message: {data.get('message')}"
            )
        else:
            log_test(
                "suite_3_user_rejection",
                "Test 3.2: Reject User (As Developer)",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
    else:
        log_test(
            "suite_3_user_rejection",
            "Test 3.2: Reject User (As Developer)",
            False,
            "No developer token or user ID available"
        )
    
    # Test 3.3: Verify Rejection in Database (Manual check)
    print("Test 3.3: Verify Rejection in Database")
    print("-" * 80)
    print("⚠️  Manual step: Need to query MongoDB")
    print(f"   Command: db.users.findOne({{email: '{reject_email}'}})")
    print(f"   Expected: approval_status='rejected', is_active=false")
    log_test(
        "suite_3_user_rejection",
        "Test 3.3: Verify Rejection in Database",
        False,
        "Manual MongoDB query required"
    )
    
    # Test 3.4: Login Attempt with Rejected User (Should Fail)
    print("Test 3.4: Login Attempt with Rejected User (Should Fail)")
    print("-" * 80)
    time.sleep(1)  # Give database a moment to update
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": reject_email,
            "password": reject_password
        }
    )
    
    passed = (
        response.status_code == 403 and
        "registration was not approved" in response.text.lower()
    )
    log_test(
        "suite_3_user_rejection",
        "Test 3.4: Login Attempt with Rejected User (Should Fail)",
        passed,
        f"Status: {response.status_code}, Response: {response.text[:200]}"
    )

# ==================== TEST SUITE 4: PERMISSION VERIFICATION ====================

def test_suite_4_permissions(developer_token):
    """Test Suite 4: Permission Verification (2 tests)"""
    print("\n" + "=" * 80)
    print("TEST SUITE 4: PERMISSION VERIFICATION")
    print("=" * 80 + "\n")
    
    # First, create a non-developer user (viewer role)
    timestamp = int(time.time())
    viewer_email = f"viewer_{timestamp}@example.com"
    viewer_password = "TestPass123!"
    viewer_token = None
    
    # Register and approve a viewer user
    print("Setup: Creating viewer user for permission tests")
    print("-" * 80)
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={
            "email": viewer_email,
            "password": viewer_password,
            "name": "Viewer User",
            "organization_name": "Viewer Org"
        }
    )
    
    if response.status_code == 200:
        viewer_user_id = response.json().get("user", {}).get("id")
        
        # Approve the viewer user
        if developer_token and viewer_user_id:
            requests.post(
                f"{BACKEND_URL}/users/{viewer_user_id}/approve",
                headers={"Authorization": f"Bearer {developer_token}"},
                json={"approval_notes": "Approved for permission testing"}
            )
            
            # Login as viewer
            time.sleep(1)
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": viewer_email,
                    "password": viewer_password
                }
            )
            
            if response.status_code == 200:
                viewer_token = response.json().get("access_token")
                print(f"✅ Viewer user created and logged in")
            else:
                print(f"❌ Failed to login as viewer: {response.status_code}")
        else:
            print(f"❌ Failed to approve viewer user")
    else:
        print(f"❌ Failed to create viewer user: {response.status_code}")
    
    # Create a pending user for permission tests
    pending_email = f"pending_{timestamp}@example.com"
    response = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={
            "email": pending_email,
            "password": "TestPass123!",
            "name": "Pending User",
            "organization_name": "Pending Org"
        }
    )
    pending_user_id = response.json().get("user", {}).get("id") if response.status_code == 200 else None
    
    # Test 4.1: Approve as Non-Developer (Should Fail)
    print("\nTest 4.1: Approve as Non-Developer (Should Fail)")
    print("-" * 80)
    if viewer_token and pending_user_id:
        response = requests.post(
            f"{BACKEND_URL}/users/{pending_user_id}/approve",
            headers={"Authorization": f"Bearer {viewer_token}"},
            json={"approval_notes": "Trying to approve"}
        )
        
        passed = (
            response.status_code == 403 and
            "don't have permission to approve" in response.text.lower()
        )
        log_test(
            "suite_4_permissions",
            "Test 4.1: Approve as Non-Developer (Should Fail)",
            passed,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    else:
        log_test(
            "suite_4_permissions",
            "Test 4.1: Approve as Non-Developer (Should Fail)",
            False,
            "No viewer token or pending user ID available"
        )
    
    # Test 4.2: Reject as Non-Developer (Should Fail)
    print("Test 4.2: Reject as Non-Developer (Should Fail)")
    print("-" * 80)
    if viewer_token and pending_user_id:
        response = requests.post(
            f"{BACKEND_URL}/users/{pending_user_id}/reject",
            headers={"Authorization": f"Bearer {viewer_token}"},
            json={"approval_notes": "Trying to reject"}
        )
        
        passed = (
            response.status_code == 403 and
            "don't have permission to reject" in response.text.lower()
        )
        log_test(
            "suite_4_permissions",
            "Test 4.2: Reject as Non-Developer (Should Fail)",
            passed,
            f"Status: {response.status_code}, Response: {response.text[:200]}"
        )
    else:
        log_test(
            "suite_4_permissions",
            "Test 4.2: Reject as Non-Developer (Should Fail)",
            False,
            "No viewer token or pending user ID available"
        )

# ==================== MAIN TEST EXECUTION ====================

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")
    
    total_tests = 0
    passed_tests = 0
    
    for suite_name, results in test_results.items():
        suite_total = len(results)
        suite_passed = sum(1 for r in results if r["passed"])
        total_tests += suite_total
        passed_tests += suite_passed
        
        print(f"{suite_name.upper().replace('_', ' ')}:")
        print(f"  Passed: {suite_passed}/{suite_total} ({suite_passed/suite_total*100:.1f}%)")
        
        # Show failed tests
        failed = [r for r in results if not r["passed"]]
        if failed:
            print(f"  Failed tests:")
            for r in failed:
                print(f"    - {r['test']}")
                if r['details']:
                    print(f"      {r['details'][:100]}")
        print()
    
    print(f"OVERALL: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    print()
    
    # Success criteria
    print("SUCCESS CRITERIA:")
    suite1_passed = sum(1 for r in test_results["suite_1_password_reset"] if r["passed"])
    suite2_passed = sum(1 for r in test_results["suite_2_profile_creation"] if r["passed"])
    suite3_passed = sum(1 for r in test_results["suite_3_user_rejection"] if r["passed"])
    suite4_passed = sum(1 for r in test_results["suite_4_permissions"] if r["passed"])
    
    print(f"  Password Reset: {suite1_passed}/5 ({'✅' if suite1_passed >= 4 else '❌'})")
    print(f"  Profile Creation: {suite2_passed}/6 ({'✅' if suite2_passed >= 6 else '❌'})")
    print(f"  User Rejection: {suite3_passed}/4 ({'✅' if suite3_passed >= 4 else '❌'})")
    print(f"  Permissions: {suite4_passed}/2 ({'✅' if suite4_passed >= 2 else '❌'})")
    print()

def main():
    """Main test execution"""
    print("=" * 80)
    print("COMPREHENSIVE BACKEND TESTING")
    print("Password Reset & New Profile Creation Workflow")
    print("=" * 80)
    print()
    
    # Note about production user password
    print("⚠️  IMPORTANT: This test requires the production user password")
    print(f"   User: {PRODUCTION_USER_EMAIL}")
    print(f"   Please update PRODUCTION_USER_PASSWORD in the script")
    print()
    
    # Get developer token
    developer_token = get_developer_token()
    
    if not developer_token:
        print("\n❌ Cannot proceed without developer authentication")
        print("   Please check the production user credentials")
        return
    
    # Run all test suites
    test_suite_1_password_reset()
    test_suite_2_profile_creation(developer_token)
    test_suite_3_user_rejection(developer_token)
    test_suite_4_permissions(developer_token)
    
    # Print summary
    print_summary()
    
    # Save results to file
    with open("/app/test_results_password_reset_approval.json", "w") as f:
        json.dump(test_results, f, indent=2)
    print("📄 Detailed results saved to: /app/test_results_password_reset_approval.json")

if __name__ == "__main__":
    main()
