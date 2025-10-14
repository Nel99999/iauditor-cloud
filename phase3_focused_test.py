#!/usr/bin/env python3
"""
🧪 FOCUSED PHASE 3 BACKEND API TESTING
Test specific Phase 3 features that were showing issues
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Configuration
BASE_URL = "https://ops-revamp.preview.emergentagent.com/api"
TEST_USER_EMAIL = "phase3.collab@company.com"
TEST_USER_PASSWORD = "Collab123!@#"
TEST_USER2_EMAIL = "phase3.user2@company.com"
TEST_USER2_PASSWORD = "User2123!@#"

def test_phase3_apis():
    """Test Phase 3 APIs with better error handling"""
    
    # Login user 1
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    user1_data = login_response.json()
    user1_token = user1_data["access_token"]
    user1_id = user1_data["user"]["id"]
    headers1 = {"Authorization": f"Bearer {user1_token}"}
    
    print(f"✅ User 1 logged in: {user1_id}")
    
    # Login user 2
    login_response2 = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER2_EMAIL,
        "password": TEST_USER2_PASSWORD
    })
    
    if login_response2.status_code != 200:
        print(f"❌ User 2 login failed: {login_response2.status_code}")
        return
    
    user2_data = login_response2.json()
    user2_token = user2_data["access_token"]
    user2_id = user2_data["user"]["id"]
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    
    print(f"✅ User 2 logged in: {user2_id}")
    
    # Get existing task
    tasks_response = requests.get(f"{BASE_URL}/tasks", headers=headers1)
    if tasks_response.status_code == 200:
        tasks_data = tasks_response.json()
        if isinstance(tasks_data, list):
            tasks = tasks_data
        else:
            tasks = tasks_data.get("tasks", [])
        if tasks:
            task_id = tasks[0]["id"]
            print(f"✅ Using existing task: {task_id}")
        else:
            # Create new task
            task_data = {
                "title": "Phase 3 Test Task",
                "description": "Test task for Phase 3 features",
                "priority": "medium",
                "status": "todo"
            }
            task_response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers1)
            if task_response.status_code == 201:
                task_id = task_response.json()["id"]
                print(f"✅ Created new task: {task_id}")
            else:
                print(f"❌ Task creation failed: {task_response.status_code}")
                return
    else:
        print(f"❌ Failed to get tasks: {tasks_response.status_code}")
        return
    
    print("\n🏷️ TESTING MENTIONS...")
    
    # Test mention creation with proper data
    mention_data = {
        "mentioned_user_ids": [user2_id],
        "resource_type": "task",
        "resource_id": task_id,
        "comment_id": str(uuid.uuid4()),
        "comment_text": f"Hey @user2, please review this task!"
    }
    
    try:
        mention_response = requests.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers1)
        print(f"Mention creation: {mention_response.status_code}")
        if mention_response.status_code == 200:
            result = mention_response.json()
            print(f"✅ Mentions created: {result}")
        else:
            print(f"❌ Mention creation failed: {mention_response.text}")
    except Exception as e:
        print(f"❌ Mention creation error: {e}")
    
    # Test getting mentions
    try:
        mentions_response = requests.get(f"{BASE_URL}/mentions/me", headers=headers2)
        print(f"Get mentions: {mentions_response.status_code}")
        if mentions_response.status_code == 200:
            mentions_data = mentions_response.json()
            print(f"✅ Found {len(mentions_data.get('mentions', []))} mentions")
        else:
            print(f"❌ Get mentions failed: {mentions_response.text}")
    except Exception as e:
        print(f"❌ Get mentions error: {e}")
    
    print("\n🔔 TESTING NOTIFICATIONS...")
    
    # Test getting notifications
    try:
        notif_response = requests.get(f"{BASE_URL}/notifications", headers=headers2)
        print(f"Get notifications: {notif_response.status_code}")
        if notif_response.status_code == 200:
            notif_data = notif_response.json()
            notifications = notif_data.get("notifications", [])
            print(f"✅ Found {len(notifications)} notifications")
            
            if notifications:
                # Test marking notification as read
                notif_id = notifications[0]["id"]
                read_response = requests.put(f"{BASE_URL}/notifications/{notif_id}/read", headers=headers2)
                print(f"Mark notification read: {read_response.status_code}")
                if read_response.status_code == 200:
                    print("✅ Notification marked as read")
                else:
                    print(f"❌ Mark read failed: {read_response.text}")
        else:
            print(f"❌ Get notifications failed: {notif_response.text}")
    except Exception as e:
        print(f"❌ Notifications error: {e}")
    
    print("\n⏱️ TESTING TIME TRACKING...")
    
    # Test time entry creation with simpler data
    entry_data = {
        "task_id": task_id,
        "description": "Testing time tracking",
        "billable": True,
        "duration_minutes": 90
    }
    
    try:
        time_response = requests.post(f"{BASE_URL}/time-tracking/entries", json=entry_data, headers=headers1)
        print(f"Time entry creation: {time_response.status_code}")
        if time_response.status_code == 200:
            entry = time_response.json()
            print(f"✅ Time entry created: {entry.get('id')}")
            entry_id = entry["id"]
            
            # Test stopping timer if it's running
            if entry.get("is_running"):
                stop_response = requests.post(f"{BASE_URL}/time-tracking/entries/{entry_id}/stop", headers=headers1)
                print(f"Stop timer: {stop_response.status_code}")
                if stop_response.status_code == 200:
                    print("✅ Timer stopped")
                else:
                    print(f"❌ Stop timer failed: {stop_response.text}")
        else:
            print(f"❌ Time entry creation failed: {time_response.text}")
    except Exception as e:
        print(f"❌ Time tracking error: {e}")
    
    # Test getting time entries
    try:
        entries_response = requests.get(f"{BASE_URL}/time-tracking/entries", headers=headers1)
        print(f"Get time entries: {entries_response.status_code}")
        if entries_response.status_code == 200:
            entries_data = entries_response.json()
            print(f"✅ Found {len(entries_data.get('entries', []))} time entries")
        else:
            print(f"❌ Get time entries failed: {entries_response.text}")
    except Exception as e:
        print(f"❌ Get time entries error: {e}")
    
    print("\n📊 TESTING STATISTICS...")
    
    # Test all stats endpoints
    stats_endpoints = [
        ("mentions/stats", "Mentions Stats"),
        ("notifications/stats", "Notifications Stats"),
        ("time-tracking/stats", "Time Tracking Stats")
    ]
    
    for endpoint, name in stats_endpoints:
        try:
            stats_response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers1)
            print(f"{name}: {stats_response.status_code}")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ {name}: {stats}")
            else:
                print(f"❌ {name} failed: {stats_response.text}")
        except Exception as e:
            print(f"❌ {name} error: {e}")

if __name__ == "__main__":
    test_phase3_apis()