import requests
import json
import uuid

# Test auth endpoints to see where the issue is
base_url = "https://userperm-hub.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Create test user
unique_email = f"authtest_{uuid.uuid4().hex[:8]}@testcompany.com"
user_data = {
    "email": unique_email,
    "password": "SecurePass123!",
    "name": "Auth Test User",
    "organization_name": f"Auth Test Org {uuid.uuid4().hex[:6]}"
}

print("🔍 Creating test user...")
response = requests.post(f"{api_url}/auth/register", json=user_data)
print(f"Registration Status: {response.status_code}")

if response.status_code == 200:
    token = response.json()['access_token']
    user_id = response.json()['user']['id']
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 User ID: {user_id}")
    
    # Test various endpoints that use get_current_user
    endpoints_to_test = [
        ("GET", "auth/me", None),
        ("GET", "users/me", None),
        ("GET", "users/theme", None),
        ("GET", "users/regional", None),
        ("GET", "users/privacy", None),
        ("GET", "users/settings", None),
        ("PUT", "users/settings", {"email_notifications": False}),
        ("PUT", "users/theme", {"theme": "dark"}),
    ]
    
    for method, endpoint, data in endpoints_to_test:
        print(f"\n🔍 Testing {method} {endpoint}...")
        try:
            if method == "GET":
                resp = requests.get(f"{api_url}/{endpoint}", headers=headers, timeout=5)
            elif method == "PUT":
                resp = requests.put(f"{api_url}/{endpoint}", json=data, headers=headers, timeout=5)
            
            print(f"   Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"   Error: {resp.text}")
            else:
                print(f"   Success: {len(resp.text)} chars")
        except Exception as e:
            print(f"   Exception: {e}")