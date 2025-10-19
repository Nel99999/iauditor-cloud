"""
Debug Role Hierarchy Test
Check what's happening with role levels
"""

import requests
import json
import os
from datetime import datetime

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://workflow-engine-18.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print("="*80)
print("DEBUG: Role Hierarchy Test")
print("="*80)

# Create org creator (Master)
org_creator_data = {
    "email": f"debug.master.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "name": "Debug Master",
    "password": "SecurePass123!",
    "organization_name": f"DebugOrg_{datetime.now().strftime('%Y%m%d%H%M%S')}"
}

response = requests.post(f"{API_BASE}/auth/register", json=org_creator_data)
if response.status_code == 200:
    master_token = response.json()["access_token"]
    master_user = response.json()["user"]
    org_id = master_user["organization_id"]
    print(f"\n✅ Created Master user: {master_user['email']}")
    print(f"   Role: {master_user.get('role')}")
    print(f"   Org ID: {org_id}")
else:
    print(f"\n❌ Failed to create master: {response.status_code}")
    exit(1)

# Get all roles
headers = {"Authorization": f"Bearer {master_token}"}
roles_response = requests.get(f"{API_BASE}/roles", headers=headers)

if roles_response.status_code == 200:
    roles = roles_response.json()
    print(f"\n📋 Available Roles:")
    for role in roles:
        print(f"   - {role.get('name')} (code: {role.get('code')}, level: {role.get('level')}, id: {role.get('id')})")
    
    # Find admin and master roles
    admin_role = next((r for r in roles if r.get("code") == "admin"), None)
    master_role = next((r for r in roles if r.get("code") == "master"), None)
    
    if admin_role and master_role:
        print(f"\n🔍 Role Levels:")
        print(f"   Master: level {master_role.get('level')}")
        print(f"   Admin: level {admin_role.get('level')}")
        
        # Create admin user
        invite_data = {
            "email": f"debug.admin.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "role_id": admin_role["id"],
            "scope_type": "organization",
            "scope_id": org_id
        }
        
        invite_response = requests.post(f"{API_BASE}/invitations", json=invite_data, headers=headers)
        
        if invite_response.status_code == 201:
            invitation = invite_response.json().get("invitation", {})
            token = invitation.get("token")
            
            # Accept invitation
            accept_data = {
                "token": token,
                "name": "Debug Admin",
                "password": "SecurePass123!"
            }
            
            accept_response = requests.post(f"{API_BASE}/invitations/accept", json=accept_data)
            
            if accept_response.status_code == 200:
                admin_token = accept_response.json().get("access_token")
                admin_user = accept_response.json().get("user")
                print(f"\n✅ Created Admin user: {admin_user['email']}")
                print(f"   Role: {admin_user.get('role')}")
                
                # Check admin's actual role in database
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                me_response = requests.get(f"{API_BASE}/auth/me", headers=admin_headers)
                
                if me_response.status_code == 200:
                    admin_me = me_response.json()
                    print(f"\n🔍 Admin user details from /auth/me:")
                    print(f"   Role field: {admin_me.get('role')}")
                    print(f"   Role type: {type(admin_me.get('role'))}")
                    
                    # Now try to invite master as admin
                    print(f"\n🧪 Testing: Admin (level {admin_role.get('level')}) trying to invite Master (level {master_role.get('level')})")
                    
                    higher_invite_data = {
                        "email": f"debug.shouldfail.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                        "role_id": master_role["id"],
                        "scope_type": "organization",
                        "scope_id": org_id
                    }
                    
                    higher_response = requests.post(f"{API_BASE}/invitations", json=higher_invite_data, headers=admin_headers)
                    
                    print(f"\n📊 Result:")
                    print(f"   Status Code: {higher_response.status_code}")
                    print(f"   Response: {json.dumps(higher_response.json(), indent=2)}")
                    
                    if higher_response.status_code == 403:
                        print(f"\n✅ CORRECT: Admin cannot invite Master (higher level)")
                    else:
                        print(f"\n❌ BUG: Admin was able to invite Master (should be blocked)")
                        
                        # Debug: Check what role code is being used
                        print(f"\n🔍 Debugging role lookup:")
                        print(f"   Admin user role field: {admin_me.get('role')}")
                        print(f"   Expected: 'admin' (code)")
                        print(f"   Actual type: {type(admin_me.get('role'))}")
                        
                        # Check if role is stored as ID instead of code
                        if admin_me.get('role') == admin_role['id']:
                            print(f"   ⚠️ ISSUE: Role is stored as ID ({admin_role['id']}) instead of code ('admin')")
                        elif admin_me.get('role') == admin_role['code']:
                            print(f"   ✅ Role is correctly stored as code")
                        else:
                            print(f"   ⚠️ Role value doesn't match ID or code")
