#!/usr/bin/env python3
"""
Debug script to understand the sidebar preferences authentication issue
"""

import requests
import json
import jwt

# Configuration
BACKEND_URL = "https://twilio-ops.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"

def debug_auth_issue():
    print("🔍 DEBUGGING SIDEBAR PREFERENCES AUTHENTICATION ISSUE")
    print("=" * 60)
    
    # Step 1: Login and get token
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data["access_token"]
    user_data = login_data["user"]
    
    print(f"✅ Login successful")
    print(f"   User ID: {user_data['id']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Role: {user_data['role']}")
    
    # Step 2: Decode JWT token
    print("\n2. Decoding JWT token...")
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"✅ JWT decoded successfully")
        print(f"   Subject (user_id): {payload.get('sub')}")
        print(f"   Expires: {payload.get('exp')}")
        
        # Check if JWT user_id matches login user_id
        if payload.get("sub") == user_data["id"]:
            print("✅ JWT user_id matches login user_id")
        else:
            print(f"❌ JWT user_id mismatch! JWT: {payload.get('sub')}, Login: {user_data['id']}")
            
    except Exception as e:
        print(f"❌ JWT decode error: {str(e)}")
        return
    
    # Step 3: Test GET endpoint (working)
    print("\n3. Testing GET /api/users/sidebar-preferences...")
    get_response = requests.get(
        f"{BACKEND_URL}/users/sidebar-preferences",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {get_response.status_code}")
    if get_response.status_code == 200:
        print("✅ GET endpoint working correctly")
        print(f"   Response: {json.dumps(get_response.json(), indent=2)}")
    else:
        print(f"❌ GET endpoint failed: {get_response.text}")
    
    # Step 4: Test PUT endpoint (failing)
    print("\n4. Testing PUT /api/users/sidebar-preferences...")
    put_data = {
        "default_mode": "mini",
        "hover_expand_enabled": True,
        "auto_collapse_enabled": True,
        "inactivity_timeout": 15,
        "context_aware_enabled": False,
        "collapse_after_navigation": True
    }
    
    put_response = requests.put(
        f"{BACKEND_URL}/users/sidebar-preferences",
        json=put_data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    
    print(f"   Status: {put_response.status_code}")
    if put_response.status_code == 200:
        print("✅ PUT endpoint working correctly")
        print(f"   Response: {json.dumps(put_response.json(), indent=2)}")
    else:
        print(f"❌ PUT endpoint failed: {put_response.text}")
        
        # Try to get more details
        try:
            error_data = put_response.json()
            print(f"   Error detail: {error_data.get('detail', 'No detail provided')}")
        except:
            print(f"   Raw error: {put_response.text}")
    
    # Step 5: Test other user endpoints to see if it's a general issue
    print("\n5. Testing other user endpoints for comparison...")
    
    # Test /users/me
    me_response = requests.get(
        f"{BACKEND_URL}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"   GET /users/me: {me_response.status_code}")
    
    # Test /users/profile (PUT)
    profile_response = requests.put(
        f"{BACKEND_URL}/users/profile",
        json={"phone": "+1234567890"},  # Small update
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    print(f"   PUT /users/profile: {profile_response.status_code}")
    
    if profile_response.status_code != 200:
        print(f"      Profile error: {profile_response.text}")
    
    print("\n" + "=" * 60)
    print("🔍 DEBUGGING COMPLETE")
    
    # Summary
    if get_response.status_code == 200 and put_response.status_code != 200:
        print("\n📋 ISSUE SUMMARY:")
        print("- GET /users/sidebar-preferences works ✅")
        print("- PUT /users/sidebar-preferences fails ❌")
        print("- This suggests the issue is specific to the PUT endpoint")
        print("- Likely causes:")
        print("  1. Route definition issue")
        print("  2. Request body parsing issue")
        print("  3. Different auth handling in PUT vs GET")

if __name__ == "__main__":
    debug_auth_issue()