"""
Debug script to understand why Admin cannot invite Viewer
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://typescript-complete-1.preview.emergentagent.com/api"
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

print("="*80)
print("DEBUG: Admin Invite Viewer Issue")
print("="*80)

# Step 1: Create organization and master user
print("\n1. Creating organization and master user...")
org_creator_email = f"debug_master.{timestamp}@example.com"
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": org_creator_email,
    "password": "SecurePass123!",
    "name": "Debug Master",
    "organization_name": f"DebugOrg_{timestamp}"
})

if response.status_code != 200:
    print(f"❌ Failed to create master: {response.text}")
    exit(1)

master_token = response.json()["access_token"]
org_id = response.json()["user"]["organization_id"]
print(f"✅ Master created with org: {org_id}")

# Step 2: Get roles
print("\n2. Getting roles...")
response = requests.get(
    f"{BASE_URL}/roles",
    headers={"Authorization": f"Bearer {master_token}"}
)

if response.status_code != 200:
    print(f"❌ Failed to get roles: {response.text}")
    exit(1)

roles = response.json()
admin_role = next((r for r in roles if r.get("code") == "admin"), None)
viewer_role = next((r for r in roles if r.get("code") == "viewer"), None)

if not admin_role or not viewer_role:
    print(f"❌ Could not find admin or viewer role")
    exit(1)

print(f"✅ Admin role: {admin_role['name']} (level: {admin_role.get('level')})")
print(f"✅ Viewer role: {viewer_role['name']} (level: {viewer_role.get('level')})")

# Step 3: Create admin user via invitation
print("\n3. Creating admin user...")
admin_email = f"debug_admin.{timestamp}@example.com"
response = requests.post(
    f"{BASE_URL}/invitations",
    headers={"Authorization": f"Bearer {master_token}"},
    json={
        "email": admin_email,
        "role_id": admin_role["id"]
    }
)

if response.status_code != 201:
    print(f"❌ Failed to invite admin: {response.text}")
    exit(1)

invitation_token = response.json()["invitation"]["token"]
print(f"✅ Admin invited")

# Accept invitation
response = requests.post(
    f"{BASE_URL}/invitations/accept",
    json={
        "token": invitation_token,
        "name": "Debug Admin",
        "password": "SecurePass123!"
    }
)

if response.status_code != 200:
    print(f"❌ Failed to accept invitation: {response.text}")
    exit(1)

admin_token = response.json()["access_token"]
admin_user = response.json()["user"]
print(f"✅ Admin user created")
print(f"   Role: {admin_user.get('role')}")
print(f"   Approval status: {admin_user.get('approval_status')}")

# Step 4: Check admin's permissions
print("\n4. Checking admin's permissions...")
response = requests.post(
    f"{BASE_URL}/permissions/check",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={
        "resource": "user",
        "action": "invite",
        "scope": "organization"
    }
)

if response.status_code == 200:
    perm_result = response.json()
    print(f"   Has permission: {perm_result.get('has_permission')}")
    print(f"   Full response: {json.dumps(perm_result, indent=2)}")
else:
    print(f"   Permission check failed: {response.status_code} - {response.text}")

# Step 5: Try to invite viewer as admin
print("\n5. Admin trying to invite viewer...")
viewer_email = f"debug_viewer.{timestamp}@example.com"
response = requests.post(
    f"{BASE_URL}/invitations",
    headers={"Authorization": f"Bearer {admin_token}"},
    json={
        "email": viewer_email,
        "role_id": viewer_role["id"]
    }
)

print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code == 403:
    print("\n❌ ISSUE CONFIRMED: Admin cannot invite Viewer")
    print("   This is the bug we need to investigate")
elif response.status_code == 201:
    print("\n✅ SUCCESS: Admin can invite Viewer")
else:
    print(f"\n⚠️ UNEXPECTED: Got status {response.status_code}")

print("\n" + "="*80)
