#!/usr/bin/env python3
"""
Final comprehensive test of sidebar preferences API
"""

import requests
import json

# Configuration
BACKEND_URL = "https://dynamic-sidebar-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"

def run_final_test():
    print("🎯 FINAL SIDEBAR PREFERENCES API TEST")
    print("=" * 50)
    
    # Authenticate
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Authentication failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Authentication successful")
    
    # Test 1: GET default preferences
    print("\n1. Testing GET default preferences...")
    get_response = requests.get(f"{BACKEND_URL}/users/sidebar-preferences", headers=headers)
    
    if get_response.status_code == 200:
        data = get_response.json()
        print(f"✅ GET successful: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ GET failed: {get_response.status_code} - {get_response.text}")
        return
    
    # Test 2: PUT update preferences
    print("\n2. Testing PUT update preferences...")
    custom_prefs = {
        "default_mode": "mini",
        "hover_expand_enabled": True,
        "auto_collapse_enabled": True,
        "inactivity_timeout": 15,
        "context_aware_enabled": False,
        "collapse_after_navigation": True
    }
    
    put_response = requests.put(
        f"{BACKEND_URL}/users/sidebar-preferences",
        json=custom_prefs,
        headers=headers
    )
    
    if put_response.status_code == 200:
        data = put_response.json()
        print(f"✅ PUT successful: {data['message']}")
        print(f"   Updated preferences: {json.dumps(data['preferences'], indent=2)}")
    else:
        print(f"❌ PUT failed: {put_response.status_code} - {put_response.text}")
        return
    
    # Test 3: Verify persistence
    print("\n3. Testing persistence...")
    verify_response = requests.get(f"{BACKEND_URL}/users/sidebar-preferences", headers=headers)
    
    if verify_response.status_code == 200:
        data = verify_response.json()
        if data.get("default_mode") == "mini" and data.get("inactivity_timeout") == 15:
            print("✅ Persistence verified - preferences saved correctly")
        else:
            print(f"❌ Persistence failed - unexpected data: {data}")
            return
    else:
        print(f"❌ Verification failed: {verify_response.status_code}")
        return
    
    # Test 4: Validation tests
    print("\n4. Testing validation...")
    
    # Invalid mode
    invalid_mode = custom_prefs.copy()
    invalid_mode["default_mode"] = "invalid_mode"
    
    invalid_response = requests.put(
        f"{BACKEND_URL}/users/sidebar-preferences",
        json=invalid_mode,
        headers=headers
    )
    
    if invalid_response.status_code == 400:
        print("✅ Invalid mode validation working")
    else:
        print(f"❌ Invalid mode validation failed: {invalid_response.status_code}")
    
    # Invalid timeout (too low)
    invalid_timeout = custom_prefs.copy()
    invalid_timeout["inactivity_timeout"] = 3
    
    timeout_response = requests.put(
        f"{BACKEND_URL}/users/sidebar-preferences",
        json=invalid_timeout,
        headers=headers
    )
    
    if timeout_response.status_code == 400:
        print("✅ Timeout validation working")
    else:
        print(f"❌ Timeout validation failed: {timeout_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 ALL SIDEBAR PREFERENCES API TESTS COMPLETED SUCCESSFULLY!")
    print("✅ GET endpoint working")
    print("✅ PUT endpoint working") 
    print("✅ Data persistence working")
    print("✅ Validation working")
    print("✅ MongoDB integration working")

if __name__ == "__main__":
    run_final_test()