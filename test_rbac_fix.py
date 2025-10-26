#!/usr/bin/env python3
import requests
requests.packages.urllib3.disable_warnings()

BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"

# Test users (from testing agent's output)
TEST_USERS = {
    "developer": {"email": "llewellyn@bluedawncapital.co.za", "password": "Test@1234"},
    "manager": {"email": "manager_test_1760884598@example.com", "password": "Test@1234"},
    "viewer": {"email": "viewer_test_1760884598@example.com", "password": "Test@1234"}
}

print("="*80)
print("TESTING RBAC FIX - USER LISTING ENDPOINT")
print("="*80)

for role, creds in TEST_USERS.items():
    print(f"\n--- Testing {role.upper()} role ---")
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json=creds, verify=False)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        continue
    
    token = response.json()["access_token"]
    
    # Try to list users
    response = requests.get(f"{BASE_URL}/users", headers={"Authorization": f"Bearer {token}"}, verify=False)
    
    print(f"GET /users: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Access GRANTED - returned {len(response.json())} users")
    elif response.status_code == 403:
        print(f"✅ Access DENIED (correct) - {response.json().get('detail')}")
    else:
        print(f"❌ Unexpected status - {response.text[:200]}")

print("\n" + "="*80)
print("EXPECTED RESULTS:")
print("- Developer: ✅ Access GRANTED (has user.read.organization permission)")
print("- Manager: ✅ Access DENIED (403 - doesn't have user.read.organization)")
print("- Viewer: ✅ Access DENIED (403 - doesn't have user.read.organization)")
print("="*80)
