#!/usr/bin/env python3
"""
Debug Backend Test - Check specific failing endpoints
"""

import requests
import json
import os
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://typed-ops-platform.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

def setup_user():
    """Setup test user"""
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"debug.test.{unique_id}@test.com"
    test_password = "DebugTest123!@#"
    
    user_data = {
        "email": test_email,
        "password": test_password,
        "name": "Debug Test User",
        "organization_name": "Debug Testing Corp"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user_data)
    if response.status_code in [200, 201]:
        data = response.json()
        access_token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        org_id = data.get("user", {}).get("organization_id")
        print(f"✅ User setup successful: {user_id}")
        return access_token, user_id, org_id, test_email, test_password
    else:
        print(f"❌ User setup failed: {response.status_code} - {response.text}")
        return None, None, None, None, None

def make_request(method, endpoint, token, **kwargs):
    """Make authenticated request"""
    if token:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f'Bearer {token}'
    
    url = f"{API_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    return response

def debug_workflow_template():
    """Debug workflow template creation"""
    print("\n🔍 Debugging Workflow Template Creation...")
    
    token, user_id, org_id, email, password = setup_user()
    if not token:
        return
    
    # Test minimal workflow template
    template_data = {
        "name": "Debug Test Workflow",
        "description": "Testing workflow creation",
        "resource_type": "inspection",
        "approval_steps": [
            {
                "step_number": 1,
                "approver_role": "supervisor",
                "context": "organization",
                "approval_type": "any_one"
            }
        ]
    }
    
    response = make_request("POST", "/workflows/templates", token, json=template_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        try:
            error_detail = response.json()
            print(f"Validation Error Details: {json.dumps(error_detail, indent=2)}")
        except:
            pass

def debug_delegation():
    """Debug delegation creation"""
    print("\n🔍 Debugging Delegation Creation...")
    
    token, user_id, org_id, email, password = setup_user()
    if not token:
        return
    
    # Create second user for delegation
    user2_data = {
        "email": f"debug2.{uuid.uuid4().hex[:8]}@test.com",
        "password": "DebugTest123!@#",
        "name": "Debug Test User 2"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user2_data)
    if response.status_code in [200, 201]:
        user2_id = response.json().get("user", {}).get("id")
        print(f"✅ Second user created: {user2_id}")
    else:
        print(f"❌ Failed to create second user: {response.text}")
        return
    
    # Test delegation
    delegation_data = {
        "delegate_to": user2_id,
        "context_type": "organization",
        "context_id": org_id,
        "permissions": ["task.create", "task.read"],
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "reason": "Testing delegation"
    }
    
    response = make_request("POST", "/context-permissions/delegations", token, json=delegation_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        try:
            error_detail = response.json()
            print(f"Validation Error Details: {json.dumps(error_detail, indent=2)}")
        except:
            pass

def debug_time_tracking():
    """Debug time tracking creation"""
    print("\n🔍 Debugging Time Tracking Creation...")
    
    token, user_id, org_id, email, password = setup_user()
    if not token:
        return
    
    time_entry_data = {
        "task_id": str(uuid.uuid4()),
        "description": "Debug time tracking test",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "duration_minutes": 120,
        "category": "development"
    }
    
    response = make_request("POST", "/time-tracking/entries", token, json=time_entry_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def debug_organizations():
    """Debug organizations endpoint"""
    print("\n🔍 Debugging Organizations Endpoint...")
    
    token, user_id, org_id, email, password = setup_user()
    if not token:
        return
    
    response = make_request("GET", "/organizations", token)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def debug_checklist_template():
    """Debug checklist template creation"""
    print("\n🔍 Debugging Checklist Template Creation...")
    
    token, user_id, org_id, email, password = setup_user()
    if not token:
        return
    
    template_data = {
        "name": "Debug Checklist",
        "description": "Testing checklist creation",
        "category": "testing",
        "items": [
            {
                "title": "Test item",
                "description": "Test description",
                "required": True,
                "order": 1
            }
        ]
    }
    
    response = make_request("POST", "/checklists/templates", token, json=template_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 422:
        try:
            error_detail = response.json()
            print(f"Validation Error Details: {json.dumps(error_detail, indent=2)}")
        except:
            pass

if __name__ == "__main__":
    print("🔍 Debug Backend Test - Checking Failing Endpoints")
    print("=" * 60)
    
    debug_workflow_template()
    debug_delegation()
    debug_time_tracking()
    debug_organizations()
    debug_checklist_template()