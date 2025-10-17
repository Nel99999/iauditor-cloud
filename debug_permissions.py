"""
Debug script to check if admin role has invite permission assigned
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://typescript-fixes-4.preview.emergentagent.com/api"
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

print("="*80)
print("DEBUG: Check Admin Role Permissions")
print("="*80)

# Step 1: Create organization and master user
print("\n1. Creating organization and master user...")
org_creator_email = f"perm_debug.{timestamp}@example.com"
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": org_creator_email,
    "password": "SecurePass123!",
    "name": "Perm Debug Master",
    "organization_name": f"PermDebugOrg_{timestamp}"
})

if response.status_code != 200:
    print(f"❌ Failed to create master: {response.text}")
    exit(1)

master_token = response.json()["access_token"]
org_id = response.json()["user"]["organization_id"]
print(f"✅ Master created with org: {org_id}")

# Step 2: Get admin role
print("\n2. Getting admin role...")
response = requests.get(
    f"{BASE_URL}/roles",
    headers={"Authorization": f"Bearer {master_token}"}
)

if response.status_code != 200:
    print(f"❌ Failed to get roles: {response.text}")
    exit(1)

roles = response.json()
admin_role = next((r for r in roles if r.get("code") == "admin"), None)

if not admin_role:
    print(f"❌ Could not find admin role")
    exit(1)

admin_role_id = admin_role["id"]
print(f"✅ Admin role ID: {admin_role_id}")

# Step 3: Get permissions for admin role
print("\n3. Getting permissions for admin role...")
response = requests.get(
    f"{BASE_URL}/permissions/roles/{admin_role_id}",
    headers={"Authorization": f"Bearer {master_token}"}
)

if response.status_code != 200:
    print(f"❌ Failed to get role permissions: {response.text}")
    exit(1)

permissions = response.json()
print(f"✅ Admin role has {len(permissions)} permissions")

# Check for invite permission
invite_perm = next((p for p in permissions if 
                   p.get("resource_type") == "user" and 
                   p.get("action") == "invite" and 
                   p.get("scope") == "organization"), None)

if invite_perm:
    print(f"✅ FOUND: user.invite.organization permission")
    print(f"   Permission ID: {invite_perm.get('id')}")
else:
    print(f"❌ MISSING: user.invite.organization permission")
    print(f"\nAll user.* permissions found:")
    user_perms = [p for p in permissions if p.get("resource_type") == "user"]
    for p in user_perms:
        print(f"   - {p.get('resource_type')}.{p.get('action')}.{p.get('scope')}")

# Step 4: Check all permissions in system
print("\n4. Checking all permissions in system...")
response = requests.get(
    f"{BASE_URL}/permissions",
    headers={"Authorization": f"Bearer {master_token}"}
)

if response.status_code != 200:
    print(f"❌ Failed to get all permissions: {response.text}")
    exit(1)

all_permissions = response.json()
print(f"✅ System has {len(all_permissions)} total permissions")

invite_perm_exists = next((p for p in all_permissions if 
                          p.get("resource_type") == "user" and 
                          p.get("action") == "invite" and 
                          p.get("scope") == "organization"), None)

if invite_perm_exists:
    print(f"✅ user.invite.organization permission EXISTS in system")
    print(f"   Permission ID: {invite_perm_exists.get('id')}")
else:
    print(f"❌ user.invite.organization permission DOES NOT EXIST in system")

print("\n" + "="*80)
