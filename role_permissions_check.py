#!/usr/bin/env python3
"""
Check role permissions in database
"""

import requests
import json

BASE_URL = "https://backendhealer.preview.emergentagent.com/api"

def login(email, password):
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

print("="*80)
print("ROLE PERMISSIONS ANALYSIS")
print("="*80)

# Login as developer to access role data
dev_token = login("llewellyn@bluedawncapital.co.za", "Test@1234")
if not dev_token:
    print("Failed to login as developer")
    exit(1)

headers = {"Authorization": f"Bearer {dev_token}"}

# Get all roles
print("\n1. ALL ROLES:")
response = requests.get(f"{BASE_URL}/roles", headers=headers, timeout=10)
if response.status_code == 200:
    roles = response.json()
    for role in roles:
        print(f"  - {role.get('name')} (ID: {role.get('id')}, Code: {role.get('code')}, Level: {role.get('level')})")
else:
    print(f"Failed to get roles: {response.status_code}")

# Get viewer user details
print("\n2. VIEWER USER DETAILS:")
viewer_token = login("viewer_test_1760884598@example.com", "Test@1234")
if viewer_token:
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=viewer_headers, timeout=10)
    if response.status_code == 200:
        viewer_data = response.json()
        print(f"  Email: {viewer_data.get('email')}")
        print(f"  Role: {viewer_data.get('role')}")
        print(f"  Role ID: {viewer_data.get('role_id')}")
        print(f"  Organization ID: {viewer_data.get('organization_id')}")
        
        viewer_role_id = viewer_data.get('role_id')
        
        # Try to get role details
        if viewer_role_id:
            print(f"\n3. VIEWER ROLE DETAILS (ID: {viewer_role_id}):")
            response = requests.get(f"{BASE_URL}/roles/{viewer_role_id}", headers=headers, timeout=10)
            print(f"  GET /roles/{viewer_role_id} status: {response.status_code}")
            if response.status_code == 200:
                role_data = response.json()
                print(f"  Role name: {role_data.get('name')}")
                print(f"  Permission IDs: {len(role_data.get('permission_ids', []))} permissions")
                print(f"  First 5 permission IDs: {role_data.get('permission_ids', [])[:5]}")
            else:
                print(f"  Response: {response.text}")

# Get manager user details
print("\n4. MANAGER USER DETAILS:")
manager_token = login("manager_test_1760884598@example.com", "Test@1234")
if manager_token:
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=manager_headers, timeout=10)
    if response.status_code == 200:
        manager_data = response.json()
        print(f"  Email: {manager_data.get('email')}")
        print(f"  Role: {manager_data.get('role')}")
        print(f"  Role ID: {manager_data.get('role_id')}")
        
        manager_role_id = manager_data.get('role_id')
        
        # Try to get role details
        if manager_role_id:
            print(f"\n5. MANAGER ROLE DETAILS (ID: {manager_role_id}):")
            response = requests.get(f"{BASE_URL}/roles/{manager_role_id}", headers=headers, timeout=10)
            print(f"  GET /roles/{manager_role_id} status: {response.status_code}")
            if response.status_code == 200:
                role_data = response.json()
                print(f"  Role name: {role_data.get('name')}")
                print(f"  Permission IDs: {len(role_data.get('permission_ids', []))} permissions")

# Get all permissions
print("\n6. CHECKING TASK.CREATE.ORGANIZATION PERMISSION:")
response = requests.get(f"{BASE_URL}/permissions", headers=headers, timeout=10)
if response.status_code == 200:
    permissions = response.json()
    task_create_perm = None
    for perm in permissions:
        if perm.get('resource_type') == 'task' and perm.get('action') == 'create' and perm.get('scope') == 'organization':
            task_create_perm = perm
            print(f"  Found permission: {perm.get('id')}")
            print(f"  Name: {perm.get('name')}")
            break
    
    if not task_create_perm:
        print("  ❌ task.create.organization permission NOT FOUND in database!")

# Check user.read.organization permission
print("\n7. CHECKING USER.READ.ORGANIZATION PERMISSION:")
response = requests.get(f"{BASE_URL}/permissions", headers=headers, timeout=10)
if response.status_code == 200:
    permissions = response.json()
    user_read_perm = None
    for perm in permissions:
        if perm.get('resource_type') == 'user' and perm.get('action') == 'read' and perm.get('scope') == 'organization':
            user_read_perm = perm
            print(f"  Found permission: {perm.get('id')}")
            print(f"  Name: {perm.get('name')}")
            break
    
    if not user_read_perm:
        print("  ❌ user.read.organization permission NOT FOUND in database!")

print("\n" + "="*80)
