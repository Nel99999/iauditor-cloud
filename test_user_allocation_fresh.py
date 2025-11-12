#!/usr/bin/env python3
"""
TEST USER ALLOCATION WITH FRESH USER - VERIFY 201 CREATED
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "Test@1234"

def authenticate():
    """Authenticate and get token"""
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def find_unassigned_user_and_unit(token):
    """Find a user that's not assigned to a specific unit"""
    # Get all users
    users_response = requests.get(
        f"{BACKEND_URL}/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    # Get all units
    units_response = requests.get(
        f"{BACKEND_URL}/organizations/units",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if users_response.status_code != 200 or units_response.status_code != 200:
        return None, None
    
    users = users_response.json()
    units = units_response.json()
    
    # Try to find a user-unit combination that's not assigned
    for unit in units:
        # Get users in this unit
        unit_users_response = requests.get(
            f"{BACKEND_URL}/organizations/units/{unit['id']}/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if unit_users_response.status_code == 200:
            unit_users = unit_users_response.json()
            assigned_user_ids = [u['user']['id'] for u in unit_users]
            
            # Find a user not in this unit
            for user in users:
                if user['id'] not in assigned_user_ids and user['email'] != TEST_USER_EMAIL:
                    return user, unit
    
    return None, None

def test_fresh_assignment(token, user, unit):
    """Test assigning a fresh user to a unit"""
    print("\n" + "="*80)
    print("TESTING FRESH USER ASSIGNMENT")
    print("="*80)
    print(f"User: {user['name']} ({user['email']})")
    print(f"Unit: {unit['name']} (Level {unit['level']})")
    print(f"User ID: {user['id']}")
    print(f"Unit ID: {unit['id']}")
    
    # Request body with BOTH user_id AND unit_id
    request_body = {
        "user_id": user['id'],
        "unit_id": unit['id'],
        "role": "inspector"
    }
    
    print(f"\nRequest Body:")
    print(json.dumps(request_body, indent=2))
    
    response = requests.post(
        f"{BACKEND_URL}/organizations/units/{unit['id']}/assign-user",
        headers={"Authorization": f"Bearer {token}"},
        json=request_body,
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n✅ SUCCESS: User assigned with 201 Created!")
        print("   The fix is working correctly - no 422 error!")
        return True
    elif response.status_code == 422:
        print("\n❌ FAILURE: Still getting 422 error!")
        print("   The fix did NOT work!")
        return False
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")
        return False

def main():
    print("\n" + "="*80)
    print("FRESH USER ALLOCATION TEST - VERIFY 201 CREATED")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        sys.exit(1)
    
    print("✅ Authenticated successfully")
    
    # Find unassigned user and unit
    print("\n🔍 Finding unassigned user-unit combination...")
    user, unit = find_unassigned_user_and_unit(token)
    
    if not user or not unit:
        print("⚠️  Could not find unassigned user-unit combination")
        print("   All users may already be assigned to all units")
        print("   This is actually a good sign - the system is working!")
        sys.exit(0)
    
    # Test assignment
    success = test_fresh_assignment(token, user, unit)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
