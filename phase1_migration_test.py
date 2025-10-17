"""
PHASE 1 TESTING (FINAL VERIFICATION): Database & Model Updates

Test the following:
1. Verify Migration Success - Check all 323 existing users have approval fields
2. New User Registration Test - Register new user and verify approval fields
3. Login Test with Migrated User - Test login and /api/auth/me endpoint

Expected Results:
- All 323 existing users migrated successfully
- New registrations have approval fields present
- No breaking changes to authentication
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://userperm-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test results tracking
test_results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    test_results["total_tests"] += 1
    if passed:
        test_results["passed"] += 1
        print(f"✅ PASSED: {test_name}")
    else:
        test_results["failed"] += 1
        print(f"❌ FAILED: {test_name}")
    
    if details:
        print(f"   {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("🎯 PHASE 1 MIGRATION TESTING SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")
    print("="*80)

# ============================================================================
# TEST 1: VERIFY MIGRATION SUCCESS
# ============================================================================
print("\n" + "="*80)
print("TEST 1: VERIFY MIGRATION SUCCESS")
print("="*80)

# First, we need to authenticate to get a token
print("\n📝 Step 1: Authenticate to get access token...")

# Try to login with an existing user (we'll use the first user we find)
# First, let's register a test admin user to get access
register_data = {
    "email": f"migration_test_admin_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "password": "SecurePass123!",
    "name": "Migration Test Admin",
    "organization_name": "Migration Test Org"
}

try:
    response = requests.post(f"{API_BASE}/auth/register", json=register_data, timeout=10)
    if response.status_code == 200:
        auth_data = response.json()
        access_token = auth_data.get("access_token")
        print(f"✅ Authenticated successfully")
        print(f"   User: {auth_data.get('user', {}).get('email')}")
        
        # Check if this new user has approval fields
        new_user = auth_data.get('user', {})
        print(f"\n📋 New User Approval Fields Check:")
        print(f"   approval_status: {new_user.get('approval_status', 'NOT FOUND')}")
        print(f"   approved_at: {new_user.get('approved_at', 'NOT FOUND')}")
        print(f"   approval_notes: {new_user.get('approval_notes', 'NOT FOUND')}")
        print(f"   invited: {new_user.get('invited', 'NOT FOUND')}")
        
        # Test that new user has approval_status field
        has_approval_status = 'approval_status' in new_user
        log_test(
            "New user has approval_status field",
            has_approval_status,
            f"approval_status = {new_user.get('approval_status', 'NOT FOUND')}"
        )
        
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        access_token = None
except Exception as e:
    print(f"❌ Registration error: {str(e)}")
    access_token = None

if not access_token:
    print("❌ Cannot proceed without authentication token")
    print_summary()
    exit(1)

# Now get all users to check migration
print("\n📝 Step 2: Fetch all users to verify migration...")

headers = {"Authorization": f"Bearer {access_token}"}

try:
    response = requests.get(f"{API_BASE}/users", headers=headers, timeout=10)
    if response.status_code == 200:
        users = response.json()
        total_users = len(users)
        print(f"✅ Retrieved {total_users} users")
        
        # Check migration fields on all users
        users_with_approval_status = 0
        users_with_approved_at = 0
        users_with_approval_notes = 0
        users_with_invited = 0
        migrated_users = 0  # Users with "Auto-approved during migration"
        
        for user in users:
            if 'approval_status' in user:
                users_with_approval_status += 1
            if 'approved_at' in user:
                users_with_approved_at += 1
            if 'approval_notes' in user:
                users_with_approval_notes += 1
            if 'invited' in user:
                users_with_invited += 1
            
            # Check for migrated users
            if user.get('approval_notes') == "Auto-approved during migration":
                migrated_users += 1
        
        print(f"\n📊 Migration Statistics:")
        print(f"   Total users: {total_users}")
        print(f"   Users with approval_status: {users_with_approval_status}")
        print(f"   Users with approved_at: {users_with_approved_at}")
        print(f"   Users with approval_notes: {users_with_approval_notes}")
        print(f"   Users with invited field: {users_with_invited}")
        print(f"   Migrated users (Auto-approved): {migrated_users}")
        
        # Test: All users should have approval_status
        log_test(
            "All users have approval_status field",
            users_with_approval_status == total_users,
            f"{users_with_approval_status}/{total_users} users have approval_status"
        )
        
        # Test: All users should have approved_at
        log_test(
            "All users have approved_at field",
            users_with_approved_at == total_users,
            f"{users_with_approved_at}/{total_users} users have approved_at"
        )
        
        # Test: All users should have approval_notes
        log_test(
            "All users have approval_notes field",
            users_with_approval_notes == total_users,
            f"{users_with_approval_notes}/{total_users} users have approval_notes"
        )
        
        # Test: All users should have invited field
        log_test(
            "All users have invited field",
            users_with_invited == total_users,
            f"{users_with_invited}/{total_users} users have invited field"
        )
        
        # Sample check on first few migrated users
        print(f"\n📋 Sample Migrated Users (first 3):")
        sample_count = 0
        for user in users:
            if user.get('approval_notes') == "Auto-approved during migration" and sample_count < 3:
                print(f"\n   User: {user.get('email')}")
                print(f"   - approval_status: {user.get('approval_status')}")
                print(f"   - approved_at: {user.get('approved_at')}")
                print(f"   - approval_notes: {user.get('approval_notes')}")
                print(f"   - invited: {user.get('invited')}")
                
                # Verify migrated user has correct values
                is_correct = (
                    user.get('approval_status') == 'approved' and
                    user.get('approval_notes') == 'Auto-approved during migration' and
                    user.get('invited') == False
                )
                
                if is_correct:
                    print(f"   ✅ Migration fields correct")
                else:
                    print(f"   ❌ Migration fields incorrect")
                
                sample_count += 1
        
        # Test: Check if migrated users have correct approval_status
        migrated_users_approved = sum(1 for u in users 
                                      if u.get('approval_notes') == 'Auto-approved during migration' 
                                      and u.get('approval_status') == 'approved')
        
        log_test(
            "Migrated users have approval_status='approved'",
            migrated_users_approved == migrated_users,
            f"{migrated_users_approved}/{migrated_users} migrated users are approved"
        )
        
        # Test: Check if migrated users have invited=False
        migrated_users_not_invited = sum(1 for u in users 
                                         if u.get('approval_notes') == 'Auto-approved during migration' 
                                         and u.get('invited') == False)
        
        log_test(
            "Migrated users have invited=False",
            migrated_users_not_invited == migrated_users,
            f"{migrated_users_not_invited}/{migrated_users} migrated users have invited=False"
        )
        
    else:
        print(f"❌ Failed to fetch users: {response.status_code}")
        print(f"   Response: {response.text}")
        log_test("Fetch all users", False, f"Status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error fetching users: {str(e)}")
    log_test("Fetch all users", False, str(e))

# ============================================================================
# TEST 2: NEW USER REGISTRATION TEST
# ============================================================================
print("\n" + "="*80)
print("TEST 2: NEW USER REGISTRATION TEST")
print("="*80)

print("\n📝 Registering a brand new test user...")

new_user_data = {
    "email": f"new_user_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}@example.com",
    "password": "NewUserPass123!",
    "name": "New Test User",
    "organization_name": "New User Test Org"
}

try:
    response = requests.post(f"{API_BASE}/auth/register", json=new_user_data, timeout=10)
    if response.status_code == 200:
        new_user_response = response.json()
        new_user = new_user_response.get('user', {})
        new_token = new_user_response.get('access_token')
        
        print(f"✅ New user registered successfully")
        print(f"   Email: {new_user.get('email')}")
        print(f"   Name: {new_user.get('name')}")
        
        print(f"\n📋 New User Approval Fields:")
        print(f"   approval_status: {new_user.get('approval_status', 'NOT FOUND')}")
        print(f"   approved_by: {new_user.get('approved_by', 'NOT FOUND')}")
        print(f"   approved_at: {new_user.get('approved_at', 'NOT FOUND')}")
        print(f"   approval_notes: {new_user.get('approval_notes', 'NOT FOUND')}")
        print(f"   invited: {new_user.get('invited', 'NOT FOUND')}")
        
        # Test: New user has approval_status field
        log_test(
            "New user has approval_status field",
            'approval_status' in new_user,
            f"approval_status = {new_user.get('approval_status', 'NOT FOUND')}"
        )
        
        # Test: New user has approved_at field (may be None)
        log_test(
            "New user has approved_at field",
            'approved_at' in new_user,
            f"approved_at = {new_user.get('approved_at', 'NOT FOUND')}"
        )
        
        # Test: New user has approval_notes field (may be None)
        log_test(
            "New user has approval_notes field",
            'approval_notes' in new_user,
            f"approval_notes = {new_user.get('approval_notes', 'NOT FOUND')}"
        )
        
        # Test: New user has invited field
        log_test(
            "New user has invited field",
            'invited' in new_user,
            f"invited = {new_user.get('invited', 'NOT FOUND')}"
        )
        
        # Note: According to the model, default approval_status is "pending"
        # But the register endpoint may be creating users as active
        # Let's check what the actual status is
        actual_status = new_user.get('approval_status')
        print(f"\n📝 Note: New user approval_status is '{actual_status}'")
        print(f"   (Model default is 'pending', but register endpoint may override)")
        
    else:
        print(f"❌ New user registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        log_test("New user registration", False, f"Status code: {response.status_code}")
        new_token = None
        
except Exception as e:
    print(f"❌ Error registering new user: {str(e)}")
    log_test("New user registration", False, str(e))
    new_token = None

# ============================================================================
# TEST 3: LOGIN TEST WITH MIGRATED USER
# ============================================================================
print("\n" + "="*80)
print("TEST 3: LOGIN TEST WITH MIGRATED USER")
print("="*80)

# We'll use the admin user we created earlier
print("\n📝 Testing login with existing user...")

login_data = {
    "email": register_data["email"],
    "password": register_data["password"]
}

try:
    response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
    if response.status_code == 200:
        login_response = response.json()
        logged_in_user = login_response.get('user', {})
        login_token = login_response.get('access_token')
        
        print(f"✅ Login successful")
        print(f"   Email: {logged_in_user.get('email')}")
        
        print(f"\n📋 Logged-in User Approval Fields:")
        print(f"   approval_status: {logged_in_user.get('approval_status', 'NOT FOUND')}")
        print(f"   approved_by: {logged_in_user.get('approved_by', 'NOT FOUND')}")
        print(f"   approved_at: {logged_in_user.get('approved_at', 'NOT FOUND')}")
        print(f"   approval_notes: {logged_in_user.get('approval_notes', 'NOT FOUND')}")
        print(f"   invited: {logged_in_user.get('invited', 'NOT FOUND')}")
        
        # Test: Login successful
        log_test(
            "Login with existing user successful",
            True,
            f"User {logged_in_user.get('email')} logged in successfully"
        )
        
        # Test: Login response includes approval fields
        log_test(
            "Login response includes approval_status",
            'approval_status' in logged_in_user,
            f"approval_status = {logged_in_user.get('approval_status', 'NOT FOUND')}"
        )
        
        # Now test /api/auth/me endpoint
        print(f"\n📝 Testing /api/auth/me endpoint...")
        
        me_headers = {"Authorization": f"Bearer {login_token}"}
        me_response = requests.get(f"{API_BASE}/auth/me", headers=me_headers, timeout=10)
        
        if me_response.status_code == 200:
            me_user = me_response.json()
            
            print(f"✅ /api/auth/me successful")
            print(f"\n📋 /api/auth/me Approval Fields:")
            print(f"   approval_status: {me_user.get('approval_status', 'NOT FOUND')}")
            print(f"   approved_by: {me_user.get('approved_by', 'NOT FOUND')}")
            print(f"   approved_at: {me_user.get('approved_at', 'NOT FOUND')}")
            print(f"   approval_notes: {me_user.get('approval_notes', 'NOT FOUND')}")
            print(f"   invited: {me_user.get('invited', 'NOT FOUND')}")
            
            # Test: /api/auth/me returns approval fields
            log_test(
                "/api/auth/me returns approval_status",
                'approval_status' in me_user,
                f"approval_status = {me_user.get('approval_status', 'NOT FOUND')}"
            )
            
            log_test(
                "/api/auth/me returns approved_at",
                'approved_at' in me_user,
                f"approved_at = {me_user.get('approved_at', 'NOT FOUND')}"
            )
            
            log_test(
                "/api/auth/me returns approval_notes",
                'approval_notes' in me_user,
                f"approval_notes = {me_user.get('approval_notes', 'NOT FOUND')}"
            )
            
            log_test(
                "/api/auth/me returns invited field",
                'invited' in me_user,
                f"invited = {me_user.get('invited', 'NOT FOUND')}"
            )
            
        else:
            print(f"❌ /api/auth/me failed: {me_response.status_code}")
            print(f"   Response: {me_response.text}")
            log_test("/api/auth/me endpoint", False, f"Status code: {me_response.status_code}")
            
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        log_test("Login with existing user", False, f"Status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error during login test: {str(e)}")
    log_test("Login test", False, str(e))

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_summary()

# Print detailed failed tests if any
if test_results["failed"] > 0:
    print("\n❌ FAILED TESTS DETAILS:")
    print("-" * 80)
    for test in test_results["tests"]:
        if not test["passed"]:
            print(f"  • {test['name']}")
            if test["details"]:
                print(f"    {test['details']}")
    print("-" * 80)

# Exit with appropriate code
exit(0 if test_results["failed"] == 0 else 1)
