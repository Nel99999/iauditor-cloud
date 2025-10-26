#!/usr/bin/env python3
"""
Diagnostic script to get detailed error messages
"""

import requests
import json

BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"

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
print("DIAGNOSTIC TESTS - DETAILED ERROR MESSAGES")
print("="*80)

# Test 1: Asset creation error details
print("\n1. ASSET CREATION ERROR DETAILS:")
dev_token = login("llewellyn@bluedawncapital.co.za", "Test@1234")
if dev_token:
    headers = {"Authorization": f"Bearer {dev_token}"}
    response = requests.post(
        f"{BASE_URL}/assets",
        headers=headers,
        json={
            "name": "Test Asset",
            "asset_type": "Equipment",
            "status": "operational"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

# Test 2: Role creation error details
print("\n2. ROLE CREATION ERROR DETAILS:")
if dev_token:
    response = requests.post(
        f"{BASE_URL}/roles",
        headers=headers,
        json={
            "name": "Test Role",
            "description": "Test role",
            "level": 5
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

# Test 3: Comment creation error details
print("\n3. COMMENT CREATION ERROR DETAILS:")
if dev_token:
    # First create a task
    task_response = requests.post(
        f"{BASE_URL}/tasks",
        headers=headers,
        json={
            "title": "Test Task for Comment",
            "description": "Test",
            "priority": "low",
            "status": "pending"
        },
        timeout=10
    )
    if task_response.status_code == 201:
        task_id = task_response.json().get("id")
        response = requests.post(
            f"{BASE_URL}/comments",
            headers=headers,
            json={
                "resource_type": "task",
                "resource_id": task_id,
                "content": "Test comment"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

# Test 4: File upload error details
print("\n4. FILE UPLOAD ERROR DETAILS:")
if dev_token:
    import base64
    # Use existing task
    if task_response.status_code == 201:
        task_id = task_response.json().get("id")
        test_content = "Test file content"
        test_base64 = base64.b64encode(test_content.encode()).decode()
        response = requests.post(
            f"{BASE_URL}/attachments/task/{task_id}/upload",
            headers=headers,
            json={
                "filename": "test.txt",
                "content": test_base64,
                "content_type": "text/plain"
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

# Test 5: Viewer RBAC - should be 403 but getting 201
print("\n5. VIEWER RBAC TEST (CRITICAL BUG):")
viewer_token = login("viewer_test_1760884598@example.com", "Test@1234")
if viewer_token:
    headers = {"Authorization": f"Bearer {viewer_token}"}
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=headers,
        json={
            "title": "Viewer Test Task",
            "description": "Should fail with 403",
            "priority": "low",
            "status": "pending"
        },
        timeout=10
    )
    print(f"Status: {response.status_code} (Expected: 403)")
    print(f"Response: {response.text[:200]}")
    
    # Check viewer's role and permissions
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers=headers,
        timeout=10
    )
    if response.status_code == 200:
        user_data = response.json()
        print(f"\nViewer user data:")
        print(f"  Role: {user_data.get('role')}")
        print(f"  Role ID: {user_data.get('role_id')}")
        print(f"  Organization ID: {user_data.get('organization_id')}")

# Test 6: Manager accessing /users - should be 403 but getting 200
print("\n6. MANAGER ACCESSING /users (CRITICAL BUG):")
manager_token = login("manager_test_1760884598@example.com", "Test@1234")
if manager_token:
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(
        f"{BASE_URL}/users",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code} (Expected: 403)")
    print(f"Response length: {len(response.text)} chars")
    
    # Check manager's role and permissions
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers=headers,
        timeout=10
    )
    if response.status_code == 200:
        user_data = response.json()
        print(f"\nManager user data:")
        print(f"  Role: {user_data.get('role')}")
        print(f"  Role ID: {user_data.get('role_id')}")

# Test 7: Subtask count issue
print("\n7. SUBTASK COUNT ISSUE:")
dev_token = login("llewellyn@bluedawncapital.co.za", "Test@1234")
if dev_token:
    headers = {"Authorization": f"Bearer {dev_token}"}
    # Create parent task
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=headers,
        json={
            "title": "Parent Task for Subtask Test",
            "description": "Parent",
            "priority": "high",
            "status": "pending"
        },
        timeout=10
    )
    if response.status_code == 201:
        parent_id = response.json().get("id")
        print(f"Parent task created: {parent_id}")
        
        # Create subtask
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=headers,
            json={
                "title": "Subtask 1",
                "description": "Subtask",
                "parent_task_id": parent_id,
                "priority": "medium",
                "status": "pending"
            },
            timeout=10
        )
        print(f"Subtask creation status: {response.status_code}")
        if response.status_code == 201:
            print(f"Subtask created: {response.json().get('id')}")
        
        # Get parent task
        response = requests.get(
            f"{BASE_URL}/tasks/{parent_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            parent_data = response.json()
            print(f"Parent task subtask_count: {parent_data.get('subtask_count', 'NOT PRESENT')}")
        
        # Try to get subtasks
        response = requests.get(
            f"{BASE_URL}/tasks/{parent_id}/subtasks",
            headers=headers,
            timeout=10
        )
        print(f"GET subtasks status: {response.status_code}")
        if response.status_code == 200:
            subtasks = response.json()
            print(f"Subtasks returned: {len(subtasks)}")

# Test 8: Get role by ID (404 error)
print("\n8. GET ROLE BY ID (404 ERROR):")
dev_token = login("llewellyn@bluedawncapital.co.za", "Test@1234")
if dev_token:
    headers = {"Authorization": f"Bearer {dev_token}"}
    # Get current user
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers=headers,
        timeout=10
    )
    if response.status_code == 200:
        user_data = response.json()
        role_id = user_data.get("role_id")
        print(f"User's role_id: {role_id}")
        
        if role_id:
            # Try to get role
            response = requests.get(
                f"{BASE_URL}/roles/{role_id}",
                headers=headers,
                timeout=10
            )
            print(f"GET role status: {response.status_code}")
            print(f"Response: {response.text}")

print("\n" + "="*80)
