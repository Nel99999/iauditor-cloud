"""
Test specific scenarios for ObjectId serialization issues
"""
import requests
import json
from datetime import datetime, timezone, timedelta

# Configuration
BASE_URL = "http://localhost:8001/api"

def test_workflow_instance_creation():
    """Test workflow instance creation for ObjectId issues"""
    print("\n" + "="*70)
    print("🔄 Testing Workflow Instance Creation")
    print("="*70)
    
    # Register and login
    register_data = {
        "name": "ObjectID Test User",
        "email": f"objectid.test.{datetime.now().timestamp()}@test.com",
        "password": "SecurePass123!",
        "create_organization": True,
        "organization_name": "ObjectID Test Org"
    }
    
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if reg_resp.status_code not in [200, 201]:
        print(f"❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        return False
    
    resp_data = reg_resp.json()
    token = resp_data.get("access_token")
    user_data = resp_data.get("user", resp_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ User registered: {user_data.get('id')}")
    
    # Create workflow template
    template_data = {
        "name": "ObjectID Test Workflow",
        "description": "Testing ObjectID serialization",
        "resource_type": "task",
        "steps": [
            {
                "step_number": 1,
                "name": "Approval Step",
                "approver_role": "supervisor",
                "approver_context": "organization",
                "approval_type": "any",
                "timeout_hours": 24
            }
        ]
    }
    
    template_resp = requests.post(
        f"{BASE_URL}/workflows/templates",
        json=template_data,
        headers=headers
    )
    
    if template_resp.status_code != 201:
        print(f"❌ Template creation failed: {template_resp.status_code} - {template_resp.text}")
        return False
    
    template = template_resp.json()
    print(f"✅ Template created: {template.get('id')}")
    
    # Check for MongoDB _id field (not just '_id' substring)
    if '_id' in template:
        print(f"⚠️ WARNING: MongoDB _id field found in template response")
        print(f"   Response: {json.dumps(template, indent=2)}")
    
    # Create task for workflow
    task_data = {
        "title": "ObjectID Test Task",
        "description": "Task for testing",
        "priority": "medium",
        "status": "todo"
    }
    
    task_resp = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    if task_resp.status_code != 201:
        print(f"❌ Task creation failed: {task_resp.status_code}")
        return False
    
    task = task_resp.json()
    print(f"✅ Task created: {task.get('id')}")
    
    # Create workflow instance
    instance_data = {
        "template_id": template.get('id'),
        "resource_type": "task",
        "resource_id": task.get('id'),
        "resource_name": "Test Task"
    }
    
    instance_resp = requests.post(
        f"{BASE_URL}/workflows/instances",
        json=instance_data,
        headers=headers
    )
    
    if instance_resp.status_code != 201:
        print(f"❌ Workflow instance creation failed: {instance_resp.status_code}")
        print(f"   Response: {instance_resp.text}")
        
        # Check if it's an ObjectId serialization error
        if 'ObjectId' in instance_resp.text or 'not JSON serializable' in instance_resp.text:
            print(f"🔴 CONFIRMED: ObjectId serialization error detected!")
            return False
        return False
    
    instance = instance_resp.json()
    print(f"✅ Workflow instance created: {instance.get('id')}")
    
    # Check for MongoDB _id field or ObjectId strings
    if '_id' in instance:
        print(f"⚠️ WARNING: MongoDB _id field found in instance response")
        print(f"   Response: {json.dumps(instance, indent=2)}")
        return False
    
    response_str = json.dumps(instance)
    if 'ObjectId' in response_str:
        print(f"🔴 CONFIRMED: ObjectId string found in response!")
        return False
    
    print(f"✅ No ObjectId issues detected in workflow instance")
    return True


def test_delegation_creation():
    """Test delegation creation for ObjectId issues"""
    print("\n" + "="*70)
    print("👥 Testing Delegation Creation")
    print("="*70)
    
    # Register first user (delegator)
    register_data1 = {
        "name": "Delegator User",
        "email": f"delegator.{datetime.now().timestamp()}@test.com",
        "password": "SecurePass123!",
        "create_organization": True,
        "organization_name": "Delegation Test Org"
    }
    
    reg_resp1 = requests.post(f"{BASE_URL}/auth/register", json=register_data1)
    if reg_resp1.status_code not in [200, 201]:
        print(f"❌ Delegator registration failed: {reg_resp1.status_code}")
        return False
    
    resp_data1 = reg_resp1.json()
    token1 = resp_data1.get("access_token")
    user1_data = resp_data1.get("user", resp_data1)
    headers1 = {"Authorization": f"Bearer {token1}"}
    org_id = user1_data.get("organization_id")
    
    print(f"✅ Delegator registered: {user1_data.get('id')}")
    
    # Register second user (delegate) - same org
    register_data2 = {
        "name": "Delegate User",
        "email": f"delegate.{datetime.now().timestamp()}@test.com",
        "password": "SecurePass123!",
        "organization_id": org_id
    }
    
    reg_resp2 = requests.post(f"{BASE_URL}/auth/register", json=register_data2)
    if reg_resp2.status_code not in [200, 201]:
        print(f"❌ Delegate registration failed: {reg_resp2.status_code}")
        return False
    
    resp_data2 = reg_resp2.json()
    user2_data = resp_data2.get("user", resp_data2)
    print(f"✅ Delegate registered: {user2_data.get('id')}")
    
    # Test self-delegation (should fail)
    self_delegation_data = {
        "delegate_id": user1_data.get('id'),
        "scope": "all_tasks",
        "reason": "Testing self-delegation",
        "valid_from": datetime.now(timezone.utc).isoformat(),
        "valid_until": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    }
    
    self_resp = requests.post(
        f"{BASE_URL}/context-permissions/delegations",
        json=self_delegation_data,
        headers=headers1
    )
    
    if self_resp.status_code == 201:
        print(f"❌ ISSUE: Self-delegation should have been rejected but was accepted!")
        return False
    elif self_resp.status_code == 400:
        print(f"✅ Self-delegation correctly rejected")
    
    # Create delegation to another user
    delegation_data = {
        "delegate_id": user2_data.get('id'),
        "scope": "all_tasks",
        "reason": "Testing delegation creation",
        "valid_from": datetime.now(timezone.utc).isoformat(),
        "valid_until": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    }
    
    deleg_resp = requests.post(
        f"{BASE_URL}/context-permissions/delegations",
        json=delegation_data,
        headers=headers1
    )
    
    if deleg_resp.status_code != 201:
        print(f"❌ Delegation creation failed: {deleg_resp.status_code}")
        print(f"   Response: {deleg_resp.text}")
        
        # Check if it's an ObjectId serialization error
        if 'ObjectId' in deleg_resp.text or 'not JSON serializable' in deleg_resp.text:
            print(f"🔴 CONFIRMED: ObjectId serialization error detected!")
            return False
        return False
    
    delegation = deleg_resp.json()
    print(f"✅ Delegation created: {delegation.get('id')}")
    
    # Check for MongoDB _id field or ObjectId strings
    if '_id' in delegation:
        print(f"⚠️ WARNING: MongoDB _id field found in delegation response")
        print(f"   Response: {json.dumps(delegation, indent=2)}")
        return False
    
    response_str = json.dumps(delegation)
    if 'ObjectId' in response_str:
        print(f"🔴 CONFIRMED: ObjectId string found in response!")
        return False
    
    print(f"✅ No ObjectId issues detected in delegation")
    return True


def test_time_entry_creation():
    """Test time entry creation for ObjectId issues"""
    print("\n" + "="*70)
    print("⏱️  Testing Time Entry Creation")
    print("="*70)
    
    # Register and login
    register_data = {
        "name": "Time Entry Test User",
        "email": f"timeentry.{datetime.now().timestamp()}@test.com",
        "password": "SecurePass123!",
        "create_organization": True,
        "organization_name": "Time Entry Test Org"
    }
    
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if reg_resp.status_code not in [200, 201]:
        print(f"❌ Registration failed: {reg_resp.status_code}")
        return False
    
    resp_data = reg_resp.json()
    token = resp_data.get("access_token")
    user_data = resp_data.get("user", resp_data)
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ User registered: {user_data.get('id')}")
    
    # Create task
    task_data = {
        "title": "Time Tracking Test Task",
        "description": "Task for time entry testing",
        "priority": "medium",
        "status": "in_progress"
    }
    
    task_resp = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    if task_resp.status_code != 201:
        print(f"❌ Task creation failed: {task_resp.status_code}")
        return False
    
    task = task_resp.json()
    print(f"✅ Task created: {task.get('id')}")
    
    # Create time entry
    time_entry_data = {
        "task_id": task.get('id'),
        "description": "Working on ObjectID test",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        "billable": True
    }
    
    entry_resp = requests.post(
        f"{BASE_URL}/time-tracking/entries",
        json=time_entry_data,
        headers=headers
    )
    
    if entry_resp.status_code != 200:
        print(f"❌ Time entry creation failed: {entry_resp.status_code}")
        print(f"   Response: {entry_resp.text}")
        
        # Check if it's an ObjectId serialization error
        if 'ObjectId' in entry_resp.text or 'not JSON serializable' in entry_resp.text:
            print(f"🔴 CONFIRMED: ObjectId serialization error detected!")
            return False
        return False
    
    time_entry = entry_resp.json()
    print(f"✅ Time entry created: {time_entry.get('id')}")
    
    # Check for MongoDB _id field or ObjectId strings
    if '_id' in time_entry:
        print(f"⚠️ WARNING: MongoDB _id field found in time entry response")
        print(f"   Response: {json.dumps(time_entry, indent=2)}")
        return False
    
    response_str = json.dumps(time_entry)
    if 'ObjectId' in response_str:
        print(f"🔴 CONFIRMED: ObjectId string found in response!")
        return False
    
    print(f"✅ No ObjectId issues detected in time entry")
    return True


if __name__ == "__main__":
    print("\n" + "🔍 SPECIFIC OBJECTID SERIALIZATION TESTS" + "\n" + "="*70)
    
    results = {
        "Workflow Instance": test_workflow_instance_creation(),
        "Delegation": test_delegation_creation(),
        "Time Entry": test_time_entry_creation()
    }
    
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\nSuccess Rate: {passed_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 All ObjectId tests passed! No serialization issues detected.")
    else:
        print("\n⚠️  Some ObjectId issues detected. Review failures above.")
