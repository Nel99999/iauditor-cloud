"""
DETAILED EMAIL TESTING - Tests 2, 4, and 5
Tests password reset completion, approval, and rejection emails
"""
import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
PRODUCTION_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "TestPassword123!",
    "organization_id": "315fa36c-4555-4b2b-8ba3-fdbde31cb940"
}

# Reset token from MongoDB
RESET_TOKEN = "54156473-145e-4108-879d-483a5fd17702"

print("="*80)
print("DETAILED EMAIL TESTING - PASSWORD RESET COMPLETION")
print("="*80)

# ==================== TEST 2: PASSWORD RESET COMPLETION ====================
print("\n[Test 2.1] Reset Password with Token")
try:
    response = requests.post(
        f"{BACKEND_URL}/auth/reset-password",
        json={
            "token": RESET_TOKEN,
            "new_password": "TempTestPass123!"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"✅ Password reset successful: {response.json().get('message')}")
        print("   Check backend logs for: '✅ Password change confirmation email sent'")
    else:
        print(f"❌ Password reset failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Restore original password
print("\n[Test 2.2] Restore Original Password")
print("   Step 1: Trigger forgot password again")
try:
    response = requests.post(
        f"{BACKEND_URL}/auth/forgot-password",
        json={"email": PRODUCTION_USER["email"]},
        timeout=10
    )
    print(f"   ✅ Forgot password triggered: {response.status_code}")
    print("   Step 2: Get new reset token from MongoDB")
    print(f"   Query: db.users.findOne({{email: '{PRODUCTION_USER['email']}'}}, {{password_reset_token: 1}})")
    print("   Step 3: Use new token to reset back to original password")
except Exception as e:
    print(f"   ❌ Exception: {str(e)}")

# ==================== TEST 4 & 5: APPROVAL/REJECTION ====================
print("\n" + "="*80)
print("DETAILED EMAIL TESTING - APPROVAL/REJECTION")
print("="*80)

# Login as developer
print("\n[Setup] Login as Developer")
try:
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": PRODUCTION_USER["email"],
            "password": "TempTestPass123!"  # Using the temp password we just set
        },
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Logged in successfully")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check for pending approvals
        print("\n[Test 4.1] Check Pending Approvals")
        response = requests.get(
            f"{BACKEND_URL}/users/pending-approvals",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            pending_users = response.json()
            print(f"✅ Found {len(pending_users)} pending users")
            
            if len(pending_users) > 0:
                # Test approval with first pending user
                user = pending_users[0]
                print(f"\n[Test 4.2] Approve User: {user['email']}")
                
                approve_response = requests.post(
                    f"{BACKEND_URL}/users/{user['id']}/approve",
                    headers=headers,
                    json={"approval_notes": "Testing approval email functionality"},
                    timeout=10
                )
                
                if approve_response.status_code == 200:
                    print(f"✅ User approved successfully")
                    print(f"   Response: {approve_response.json()}")
                    print("   Check backend logs for: '✅ Approval email sent successfully'")
                else:
                    print(f"❌ Approval failed: {approve_response.status_code}")
                    print(f"   Response: {approve_response.text}")
                
                # Test rejection with another pending user if available
                if len(pending_users) > 1:
                    user = pending_users[1]
                    print(f"\n[Test 5.1] Reject User: {user['email']}")
                    
                    reject_response = requests.post(
                        f"{BACKEND_URL}/users/{user['id']}/reject",
                        headers=headers,
                        json={"approval_notes": "Testing rejection email functionality - not approved"},
                        timeout=10
                    )
                    
                    if reject_response.status_code == 200:
                        print(f"✅ User rejected successfully")
                        print(f"   Response: {reject_response.json()}")
                        print("   Check backend logs for: '✅ Rejection email sent successfully'")
                    else:
                        print(f"❌ Rejection failed: {reject_response.status_code}")
                        print(f"   Response: {reject_response.text}")
                else:
                    print("\n⚠️  Only 1 pending user found - cannot test rejection")
                    print("   Create another pending user to test rejection email")
            else:
                print("\n⚠️  No pending users found in production organization")
                print("   The test users created earlier are in different organizations")
                print("   To test approval/rejection emails:")
                print("   1. Create a pending user in production org using MongoDB")
                print("   2. Or have a real user register and select the production org")
        else:
            print(f"❌ Failed to get pending approvals: {response.status_code}")
            print(f"   Response: {response.text}")
            
    elif response.status_code == 401:
        print("❌ Login failed - trying with original password")
        # Try with original password
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "email": PRODUCTION_USER["email"],
                "password": PRODUCTION_USER["password"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Logged in with original password")
            print("   Note: Password reset may not have completed successfully")
        else:
            print(f"❌ Login failed with both passwords")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")

print("\n" + "="*80)
print("CHECK BACKEND LOGS")
print("="*80)
print("\nRun this command to see email sending status:")
print("  tail -n 50 /var/log/supervisor/backend.out.log | grep -E '(email|Email)'")
print("\nLook for:")
print("  ✅ Password change confirmation email sent")
print("  ✅ Approval email sent successfully")
print("  ✅ Rejection email sent successfully")
