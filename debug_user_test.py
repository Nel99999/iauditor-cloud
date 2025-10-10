import requests
import json
import uuid

# Test user creation and settings update
base_url = "https://orgflow-1.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Create test user
unique_email = f"debugtest_{uuid.uuid4().hex[:8]}@testcompany.com"
user_data = {
    "email": unique_email,
    "password": "SecurePass123!",
    "name": "Debug Test User",
    "organization_name": f"Debug Test Org {uuid.uuid4().hex[:6]}"
}

print("🔍 Creating test user...")
response = requests.post(f"{api_url}/auth/register", json=user_data)
print(f"Registration Status: {response.status_code}")
print(f"Registration Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    token = response.json()['access_token']
    user_id = response.json()['user']['id']
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 User ID from registration: {user_id}")
    
    # Test /auth/me endpoint
    print("\n🔍 Testing /auth/me endpoint...")
    me_response = requests.get(f"{api_url}/auth/me", headers=headers)
    print(f"Auth/me Status: {me_response.status_code}")
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"Auth/me User ID: {me_data.get('id')}")
        print(f"User IDs match: {user_id == me_data.get('id')}")
    
    # Test theme GET (should work)
    print("\n🔍 Testing GET theme...")
    theme_get = requests.get(f"{api_url}/users/theme", headers=headers)
    print(f"Theme GET Status: {theme_get.status_code}")
    print(f"Theme GET Response: {json.dumps(theme_get.json(), indent=2)}")
    
    # Test theme PUT (currently failing)
    print("\n🔍 Testing PUT theme...")
    theme_data = {"theme": "dark", "accent_color": "#ef4444"}
    theme_put = requests.put(f"{api_url}/users/theme", json=theme_data, headers=headers)
    print(f"Theme PUT Status: {theme_put.status_code}")
    print(f"Theme PUT Response: {json.dumps(theme_put.json(), indent=2)}")
    
    # Test notification settings (should work)
    print("\n🔍 Testing PUT notification settings...")
    notif_data = {"email_notifications": False, "push_notifications": True}
    notif_put = requests.put(f"{api_url}/users/settings", json=notif_data, headers=headers)
    print(f"Notification PUT Status: {notif_put.status_code}")
    print(f"Notification PUT Response: {json.dumps(notif_put.json(), indent=2)}")