import requests
import json
import uuid

# Test theme update with detailed debugging
base_url = "https://auth-workflow-hub.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Create test user
unique_email = f"themetest_{uuid.uuid4().hex[:8]}@testcompany.com"
user_data = {
    "email": unique_email,
    "password": "SecurePass123!",
    "name": "Theme Test User",
    "organization_name": f"Theme Test Org {uuid.uuid4().hex[:6]}"
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
    
    # Test 1: Empty theme data (should not update anything)
    print("\n🔍 Test 1: Empty theme data...")
    theme_data = {}
    theme_put = requests.put(f"{api_url}/users/theme", json=theme_data, headers=headers)
    print(f"Empty Theme PUT Status: {theme_put.status_code}")
    print(f"Empty Theme PUT Response: {json.dumps(theme_put.json(), indent=2)}")
    
    # Test 2: Theme data with None values (should not update anything)
    print("\n🔍 Test 2: Theme data with None values...")
    theme_data = {"theme": None, "accent_color": None}
    theme_put = requests.put(f"{api_url}/users/theme", json=theme_data, headers=headers)
    print(f"None Theme PUT Status: {theme_put.status_code}")
    print(f"None Theme PUT Response: {json.dumps(theme_put.json(), indent=2)}")
    
    # Test 3: Theme data with actual values
    print("\n🔍 Test 3: Theme data with actual values...")
    theme_data = {"theme": "dark", "accent_color": "#ef4444", "font_size": "large", "view_density": "spacious"}
    theme_put = requests.put(f"{api_url}/users/theme", json=theme_data, headers=headers)
    print(f"Valid Theme PUT Status: {theme_put.status_code}")
    print(f"Valid Theme PUT Response: {json.dumps(theme_put.json(), indent=2)}")
    
    # Test 4: Verify the update worked
    print("\n🔍 Test 4: Verify theme was updated...")
    theme_get = requests.get(f"{api_url}/users/theme", headers=headers)
    print(f"Theme GET Status: {theme_get.status_code}")
    print(f"Theme GET Response: {json.dumps(theme_get.json(), indent=2)}")