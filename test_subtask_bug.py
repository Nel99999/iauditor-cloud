#!/usr/bin/env python3
import requests
import json
requests.packages.urllib3.disable_warnings()

BASE_URL = "https://backendhealer.preview.emergentagent.com/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login",
    json={"email":"llewellyn@bluedawncapital.co.za","password":"Test@1234"}, verify=False)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("="*80)
print("TESTING SUBTASK FUNCTIONALITY")
print("="*80)

# Step 1: Create parent task
print("\n1. Creating parent task...")
response = requests.post(f"{BASE_URL}/tasks",
    json={"title":"Parent Task for Subtask Test","description":"Parent"},
    headers=headers, verify=False)
parent_id = response.json()["id"]
print(f"   Parent created: {parent_id}")

# Step 2: Create subtask using subtasks endpoint
print("\n2. Creating subtask using POST /tasks/{parent_id}/subtasks...")
response = requests.post(f"{BASE_URL}/tasks/{parent_id}/subtasks",
    json={"title":"Subtask 1","description":"First subtask"},
    headers=headers, verify=False)
print(f"   Status: {response.status_code}")
if response.status_code in [200, 201]:
    subtask_data = response.json()
    subtask_id = subtask_data.get("id")
    parent_task_id = subtask_data.get("parent_task_id")
    print(f"   Subtask ID: {subtask_id}")
    print(f"   parent_task_id: {parent_task_id}")
    print(f"   ✅ RESULT: parent_task_id is {'SET' if parent_task_id else 'NULL'}")
else:
    print(f"   ❌ Failed: {response.text}")

# Step 3: Get parent task
print("\n3. Getting parent task...")
response = requests.get(f"{BASE_URL}/tasks/{parent_id}", headers=headers, verify=False)
if response.status_code == 200:
    parent_data = response.json()
    subtask_count = parent_data.get("subtask_count", 0)
    print(f"   subtask_count: {subtask_count}")
    print(f"   ✅ RESULT: subtask_count is {subtask_count}")

# Step 4: List subtasks
print("\n4. Listing subtasks...")
response = requests.get(f"{BASE_URL}/tasks/{parent_id}/subtasks", headers=headers, verify=False)
if response.status_code == 200:
    subtasks = response.json()
    print(f"   Subtasks returned: {len(subtasks)}")
    print(f"   ✅ RESULT: Found {len(subtasks)} subtask(s)")
    if len(subtasks) > 0:
        print(f"   First subtask parent_task_id: {subtasks[0].get('parent_task_id')}")

# Step 5: Query database directly
print("\n5. Checking database directly...")
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["operational_platform"]
subtasks_db = list(db.tasks.find({"parent_task_id": parent_id}, {"_id": 0, "id": 1, "title": 1, "parent_task_id": 1}))
print(f"   Subtasks in DB with parent_task_id={parent_id}: {len(subtasks_db)}")
for st in subtasks_db:
    print(f"     - {st['title']}: parent_task_id = {st.get('parent_task_id')}")

print("\n" + "="*80)
