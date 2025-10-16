"""
Database Fix Verification Test
Verifies backend is connected to operational_platform with 401 users
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL'):
            BACKEND_URL = line.split('=')[1].strip()
            break

BASE_URL = f"{BACKEND_URL}/api"

print("=" * 80)
print("DATABASE FIX VERIFICATION TEST")
print("=" * 80)
print(f"Backend URL: {BASE_URL}")
print()

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_result(test_name, passed, details=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
        print(f"✅ PASS: {test_name}")
    else:
        failed_tests += 1
        print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   {details}")
    print()

# ============================================================================
# TEST 1: Database Connection Verification
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: DATABASE CONNECTION VERIFICATION")
print("=" * 80)

# First, let's check the health endpoint
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    test_result(
        "Backend Health Check",
        response.status_code == 200,
        f"Status: {response.status_code}, Response: {response.json()}"
    )
except Exception as e:
    test_result("Backend Health Check", False, f"Error: {str(e)}")

# Check database name from environment
db_name = os.environ.get('DB_NAME', 'operational_platform')
test_result(
    "Database Name Configuration",
    db_name == "operational_platform",
    f"DB_NAME={db_name} (Expected: operational_platform)"
)

# ============================================================================
# TEST 2: User Count Verification (Should be 401, not 1)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: USER COUNT VERIFICATION")
print("=" * 80)

# We need to authenticate first to access user endpoints
# Let's try to get users list - we'll need to register/login first

# Try to register a test user
test_email = "dbverify.test@example.com"
test_password = "SecurePass123!"

try:
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "name": "DB Verify Test User",
            "organization_name": "DB Verify Test Org"
        },
        timeout=10
    )
    
    if register_response.status_code in [200, 201]:
        print(f"✓ Registered new test user: {test_email}")
        response_data = register_response.json()
        token = response_data.get("access_token")
        if not token:
            print(f"⚠️  Response: {response_data}")
    elif register_response.status_code == 400 and "already exists" in register_response.text.lower():
        # User already exists, try to login
        print(f"✓ Test user already exists, attempting login...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            },
            timeout=10
        )
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✓ Logged in successfully")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            token = None
    else:
        print(f"❌ Registration failed: {register_response.status_code}")
        print(f"   Response: {register_response.text}")
        token = None
        
except Exception as e:
    print(f"❌ Authentication error: {str(e)}")
    token = None

# Now check user count
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get users list
        users_response = requests.get(f"{BASE_URL}/users", headers=headers, timeout=10)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            user_count = len(users_data) if isinstance(users_data, list) else users_data.get('total', 0)
            
            test_result(
                "User Count Verification",
                user_count >= 401,  # Should be 401 or more
                f"Found {user_count} users (Expected: 401+)"
            )
            
            if user_count == 1:
                print("⚠️  WARNING: Only 1 user found - backend may be connected to wrong database!")
            elif user_count >= 401:
                print(f"✓ Correct database detected with {user_count} users")
        else:
            test_result(
                "User Count Verification",
                False,
                f"Failed to get users: {users_response.status_code}"
            )
    except Exception as e:
        test_result("User Count Verification", False, f"Error: {str(e)}")
else:
    test_result("User Count Verification", False, "No authentication token available")

# ============================================================================
# TEST 3: Organization Count Verification (Should be 295, not 1)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: ORGANIZATION COUNT VERIFICATION")
print("=" * 80)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get organizations list
        orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers, timeout=10)
        
        if orgs_response.status_code == 200:
            orgs_data = orgs_response.json()
            org_count = len(orgs_data) if isinstance(orgs_data, list) else orgs_data.get('total', 0)
            
            test_result(
                "Organization Count Verification",
                org_count >= 295,  # Should be 295 or more
                f"Found {org_count} organizations (Expected: 295+)"
            )
            
            if org_count == 1:
                print("⚠️  WARNING: Only 1 organization found - backend may be connected to wrong database!")
            elif org_count >= 295:
                print(f"✓ Correct database detected with {org_count} organizations")
        else:
            test_result(
                "Organization Count Verification",
                False,
                f"Failed to get organizations: {orgs_response.status_code}"
            )
    except Exception as e:
        test_result("Organization Count Verification", False, f"Error: {str(e)}")
else:
    test_result("Organization Count Verification", False, "No authentication token available")

# ============================================================================
# TEST 4: Permission Count Verification (Should be 26)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: PERMISSION COUNT VERIFICATION")
print("=" * 80)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get permissions list
        perms_response = requests.get(f"{BASE_URL}/permissions", headers=headers, timeout=10)
        
        if perms_response.status_code == 200:
            perms_data = perms_response.json()
            perm_count = len(perms_data) if isinstance(perms_data, list) else perms_data.get('total', 0)
            
            test_result(
                "Permission Count Verification",
                perm_count == 26,
                f"Found {perm_count} permissions (Expected: 26)"
            )
            
            if perm_count == 26:
                print(f"✓ Correct permission count: {perm_count}")
        else:
            test_result(
                "Permission Count Verification",
                False,
                f"Failed to get permissions: {perms_response.status_code}"
            )
    except Exception as e:
        test_result("Permission Count Verification", False, f"Error: {str(e)}")
else:
    test_result("Permission Count Verification", False, "No authentication token available")

# ============================================================================
# TEST 5: Approval System Verification
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: APPROVAL SYSTEM VERIFICATION")
print("=" * 80)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if users have approval_status field
    try:
        users_response = requests.get(f"{BASE_URL}/users", headers=headers, timeout=10)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            if isinstance(users_data, list) and len(users_data) > 0:
                # Check first few users for approval_status field
                users_with_approval = [u for u in users_data[:10] if 'approval_status' in u]
                
                test_result(
                    "Users Have approval_status Field",
                    len(users_with_approval) > 0,
                    f"{len(users_with_approval)}/10 users have approval_status field"
                )
            else:
                test_result("Users Have approval_status Field", False, "No users found")
        else:
            test_result("Users Have approval_status Field", False, f"Status: {users_response.status_code}")
    except Exception as e:
        test_result("Users Have approval_status Field", False, f"Error: {str(e)}")
    
    # Check pending approvals endpoint
    try:
        approvals_response = requests.get(f"{BASE_URL}/approvals/pending", headers=headers, timeout=10)
        
        test_result(
            "Pending Approvals Endpoint",
            approvals_response.status_code in [200, 404],  # 200 OK or 404 if no pending
            f"Status: {approvals_response.status_code}"
        )
        
        if approvals_response.status_code == 200:
            approvals_data = approvals_response.json()
            pending_count = len(approvals_data) if isinstance(approvals_data, list) else 0
            print(f"   Found {pending_count} pending approvals")
    except Exception as e:
        test_result("Pending Approvals Endpoint", False, f"Error: {str(e)}")
else:
    test_result("Approval System Verification", False, "No authentication token available")

# ============================================================================
# TEST 6: Permission System - Approval Permissions
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: APPROVAL PERMISSIONS VERIFICATION")
print("=" * 80)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get permissions and check for approval-related permissions
        perms_response = requests.get(f"{BASE_URL}/permissions", headers=headers, timeout=10)
        
        if perms_response.status_code == 200:
            perms_data = perms_response.json()
            
            # Look for approval permissions
            approval_perms = [p for p in perms_data if 'approval' in p.get('code', '').lower()]
            
            test_result(
                "Approval Permissions Exist",
                len(approval_perms) > 0,
                f"Found {len(approval_perms)} approval-related permissions"
            )
            
            if approval_perms:
                print("   Approval permissions found:")
                for perm in approval_perms:
                    print(f"   - {perm.get('name', 'N/A')} ({perm.get('code', 'N/A')})")
        else:
            test_result("Approval Permissions Exist", False, f"Status: {perms_response.status_code}")
    except Exception as e:
        test_result("Approval Permissions Exist", False, f"Error: {str(e)}")
    
    # Test permission check endpoint
    try:
        check_response = requests.post(
            f"{BASE_URL}/permissions/check",
            headers=headers,
            json={"permission_code": "view_users"},
            timeout=10
        )
        
        test_result(
            "Permission Check Endpoint",
            check_response.status_code == 200,
            f"Status: {check_response.status_code}"
        )
    except Exception as e:
        test_result("Permission Check Endpoint", False, f"Error: {str(e)}")
else:
    test_result("Permission System Verification", False, "No authentication token available")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests} ✅")
print(f"Failed: {failed_tests} ❌")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
print("=" * 80)

if failed_tests == 0:
    print("\n🎉 ALL TESTS PASSED! Database fix verified successfully!")
    print("✓ Backend connected to operational_platform")
    print("✓ 401+ users found")
    print("✓ 295+ organizations found")
    print("✓ 26 permissions found")
    print("✓ Approval system operational")
else:
    print("\n⚠️  SOME TESTS FAILED - Review results above")
    if failed_tests > 5:
        print("❌ CRITICAL: Backend may still be connected to wrong database!")
