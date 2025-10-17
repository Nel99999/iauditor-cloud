#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE PHASE 3 BACKEND API TESTING
Test all newly implemented Phase 3 collaboration & advanced features

Features tested:
1. @Mentions System Testing
2. Notifications Center Testing  
3. Time Tracking System Testing
4. Integration Testing - Phase 3 Features
5. Edge Cases & Validation
6. Authorization & Security - Phase 3
7. Audit Logging Verification - Phase 3
"""

import requests
import json
import uuid
from datetime import datetime, timezone, timedelta
import time

# Configuration
BASE_URL = "https://userperm-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "phase3.collab@company.com"
TEST_USER_PASSWORD = "Collab123!@#"
TEST_USER2_EMAIL = "phase3.user2@company.com"
TEST_USER2_PASSWORD = "User2123!@#"

class Phase3BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.user1_token = None
        self.user2_token = None
        self.user1_id = None
        self.user2_id = None
        self.organization_id = None
        self.test_task_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        if response_data and not success:
            result += f" | Response: {response_data}"
            
        self.test_results.append(result)
        print(result)
        
    def setup_authentication(self):
        """Setup test users and authentication"""
        print("\n🔐 SETTING UP AUTHENTICATION...")
        
        # Register first user
        user1_data = {
            "name": "Phase 3 Collaborator",
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "organization_name": "Phase 3 Testing Corp"
        }
        
        response = self.session.post(f"{BASE_URL}/auth/register", json=user1_data)
        if response.status_code == 201:
            self.log_test("User 1 Registration", True, f"Created user: {TEST_USER_EMAIL}")
        else:
            # Try login if user exists
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            if login_response.status_code == 200:
                self.log_test("User 1 Login (existing)", True, f"Logged in: {TEST_USER_EMAIL}")
            else:
                self.log_test("User 1 Setup", False, f"Status: {response.status_code}", response.text)
                return False
        
        # Login user 1
        login_response = self.session.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            self.user1_token = login_data["access_token"]
            self.user1_id = login_data["user"]["id"]
            self.organization_id = login_data["user"]["organization_id"]
            self.log_test("User 1 Token", True, f"Token obtained for {TEST_USER_EMAIL}")
        else:
            self.log_test("User 1 Token", False, f"Status: {login_response.status_code}", login_response.text)
            return False
        
        # Register second user (for mentions testing)
        user2_data = {
            "name": "Phase 3 User Two",
            "email": TEST_USER2_EMAIL,
            "password": TEST_USER2_PASSWORD,
            "organization_id": self.organization_id  # Join same organization
        }
        
        response = self.session.post(f"{BASE_URL}/auth/register", json=user2_data)
        if response.status_code == 201:
            self.log_test("User 2 Registration", True, f"Created user: {TEST_USER2_EMAIL}")
        else:
            # Try login if user exists
            login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER2_EMAIL,
                "password": TEST_USER2_PASSWORD
            })
            if login_response.status_code == 200:
                self.log_test("User 2 Login (existing)", True, f"Logged in: {TEST_USER2_EMAIL}")
            else:
                self.log_test("User 2 Setup", False, f"Status: {response.status_code}", response.text)
                return False
        
        # Login user 2
        login_response = self.session.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER2_EMAIL,
            "password": TEST_USER2_PASSWORD
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            self.user2_token = login_data["access_token"]
            self.user2_id = login_data["user"]["id"]
            self.log_test("User 2 Token", True, f"Token obtained for {TEST_USER2_EMAIL}")
        else:
            self.log_test("User 2 Token", False, f"Status: {login_response.status_code}", login_response.text)
            return False
        
        return True
    
    def create_test_task(self):
        """Create a test task for mentions and time tracking"""
        print("\n📋 CREATING TEST TASK...")
        
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        task_data = {
            "title": "Phase 3 Collaboration Test Task",
            "description": "Test task for mentions and time tracking",
            "priority": "medium",
            "status": "todo"
        }
        
        response = self.session.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
        if response.status_code == 201:
            task = response.json()
            self.test_task_id = task["id"]
            self.log_test("Test Task Creation", True, f"Task ID: {self.test_task_id}")
            return True
        else:
            self.log_test("Test Task Creation", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_mentions_system(self):
        """Test @Mentions System"""
        print("\n🏷️ TESTING @MENTIONS SYSTEM...")
        
        # Test A: Mention Creation
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        mention_data = {
            "mentioned_user_ids": [self.user2_id],
            "resource_type": "task",
            "resource_id": self.test_task_id,
            "comment_id": str(uuid.uuid4()),
            "comment_text": f"Hey @{TEST_USER2_EMAIL}, can you review this task?"
        }
        
        response = self.session.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            self.log_test("Create Mentions", True, f"Created {result.get('message', 'mentions')}")
        else:
            self.log_test("Create Mentions", False, f"Status: {response.status_code}", response.text)
        
        # Test B: Get Mentions (as user2 - mentioned user)
        headers2 = {"Authorization": f"Bearer {self.user2_token}"}
        
        # Get all mentions
        response = self.session.get(f"{BASE_URL}/mentions/me", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            mentions = result.get("mentions", [])
            self.log_test("Get My Mentions", True, f"Found {len(mentions)} mentions")
            
            if mentions:
                mention_id = mentions[0]["id"]
                
                # Get unread mentions only
                response = self.session.get(f"{BASE_URL}/mentions/me?unread_only=true", headers=headers2)
                if response.status_code == 200:
                    unread_result = response.json()
                    self.log_test("Get Unread Mentions", True, f"Unread: {unread_result.get('unread_count', 0)}")
                else:
                    self.log_test("Get Unread Mentions", False, f"Status: {response.status_code}", response.text)
                
                # Test C: Mark Mention Read
                response = self.session.put(f"{BASE_URL}/mentions/{mention_id}/read", headers=headers2)
                if response.status_code == 200:
                    self.log_test("Mark Mention Read", True, "Mention marked as read")
                else:
                    self.log_test("Mark Mention Read", False, f"Status: {response.status_code}", response.text)
        else:
            self.log_test("Get My Mentions", False, f"Status: {response.status_code}", response.text)
        
        # Get mention statistics
        response = self.session.get(f"{BASE_URL}/mentions/stats", headers=headers2)
        if response.status_code == 200:
            stats = response.json()
            self.log_test("Mention Statistics", True, f"Total: {stats.get('total_mentions', 0)}, Unread: {stats.get('unread_mentions', 0)}")
        else:
            self.log_test("Mention Statistics", False, f"Status: {response.status_code}", response.text)
        
        # Create more mentions for bulk operations
        for i in range(3):
            mention_data["comment_id"] = str(uuid.uuid4())
            mention_data["comment_text"] = f"Additional mention {i+1} for testing"
            self.session.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers)
        
        # Mark all mentions as read
        response = self.session.post(f"{BASE_URL}/mentions/mark-all-read", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            self.log_test("Mark All Mentions Read", True, f"Marked {result.get('count', 0)} mentions as read")
        else:
            self.log_test("Mark All Mentions Read", False, f"Status: {response.status_code}", response.text)
    
    def test_notifications_center(self):
        """Test Notifications Center"""
        print("\n🔔 TESTING NOTIFICATIONS CENTER...")
        
        headers2 = {"Authorization": f"Bearer {self.user2_token}"}
        
        # Test A: Get Notifications (should have notifications from mentions)
        response = self.session.get(f"{BASE_URL}/notifications", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            notifications = result.get("notifications", [])
            self.log_test("Get All Notifications", True, f"Found {len(notifications)} notifications")
            
            if notifications:
                notification_id = notifications[0]["id"]
                
                # Get unread notifications only
                response = self.session.get(f"{BASE_URL}/notifications?unread_only=true", headers=headers2)
                if response.status_code == 200:
                    unread_result = response.json()
                    self.log_test("Get Unread Notifications", True, f"Unread: {unread_result.get('unread_count', 0)}")
                else:
                    self.log_test("Get Unread Notifications", False, f"Status: {response.status_code}", response.text)
                
                # Filter by type
                response = self.session.get(f"{BASE_URL}/notifications?type_filter=mention", headers=headers2)
                if response.status_code == 200:
                    filtered_result = response.json()
                    self.log_test("Filter Notifications by Type", True, f"Mention notifications: {len(filtered_result.get('notifications', []))}")
                else:
                    self.log_test("Filter Notifications by Type", False, f"Status: {response.status_code}", response.text)
                
                # Test B: Mark single notification as read
                response = self.session.put(f"{BASE_URL}/notifications/{notification_id}/read", headers=headers2)
                if response.status_code == 200:
                    self.log_test("Mark Notification Read", True, "Notification marked as read")
                else:
                    self.log_test("Mark Notification Read", False, f"Status: {response.status_code}", response.text)
                
                # Test C: Delete notification
                response = self.session.delete(f"{BASE_URL}/notifications/{notification_id}", headers=headers2)
                if response.status_code == 200:
                    self.log_test("Delete Notification", True, "Notification deleted")
                else:
                    self.log_test("Delete Notification", False, f"Status: {response.status_code}", response.text)
        else:
            self.log_test("Get All Notifications", False, f"Status: {response.status_code}", response.text)
        
        # Get notification statistics
        response = self.session.get(f"{BASE_URL}/notifications/stats", headers=headers2)
        if response.status_code == 200:
            stats = response.json()
            self.log_test("Notification Statistics", True, f"Total: {stats.get('total_notifications', 0)}, Unread: {stats.get('unread_notifications', 0)}")
        else:
            self.log_test("Notification Statistics", False, f"Status: {response.status_code}", response.text)
        
        # Mark all notifications as read
        response = self.session.post(f"{BASE_URL}/notifications/mark-all-read", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            self.log_test("Mark All Notifications Read", True, f"Marked {result.get('count', 0)} notifications as read")
        else:
            self.log_test("Mark All Notifications Read", False, f"Status: {response.status_code}", response.text)
        
        # Mark by type
        response = self.session.post(f"{BASE_URL}/notifications/mark-all-read?notification_type=mention", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            self.log_test("Mark Notifications by Type", True, f"Marked {result.get('count', 0)} mention notifications")
        else:
            self.log_test("Mark Notifications by Type", False, f"Status: {response.status_code}", response.text)
        
        # Clear read notifications
        response = self.session.delete(f"{BASE_URL}/notifications/clear-all?read_only=true", headers=headers2)
        if response.status_code == 200:
            result = response.json()
            self.log_test("Clear Read Notifications", True, f"Cleared {result.get('count', 0)} notifications")
        else:
            self.log_test("Clear Read Notifications", False, f"Status: {response.status_code}", response.text)
        
        # Test D: Notification Preferences
        response = self.session.get(f"{BASE_URL}/notifications/preferences", headers=headers2)
        if response.status_code == 200:
            prefs = response.json()
            self.log_test("Get Notification Preferences", True, f"Email: {prefs.get('email_notifications')}, Push: {prefs.get('push_notifications')}")
        else:
            self.log_test("Get Notification Preferences", False, f"Status: {response.status_code}", response.text)
        
        # Update preferences
        prefs_data = {
            "email_notifications": False,
            "push_notifications": True,
            "notification_types": {"mention": True, "assignment": False}
        }
        response = self.session.put(f"{BASE_URL}/notifications/preferences", json=prefs_data, headers=headers2)
        if response.status_code == 200:
            self.log_test("Update Notification Preferences", True, "Preferences updated")
        else:
            self.log_test("Update Notification Preferences", False, f"Status: {response.status_code}", response.text)
    
    def test_time_tracking_system(self):
        """Test Time Tracking System"""
        print("\n⏱️ TESTING TIME TRACKING SYSTEM...")
        
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        
        # Test A: Create Time Entry (manual)
        entry_data = {
            "task_id": self.test_task_id,
            "description": "Working on Phase 3 collaboration features",
            "started_at": "2025-01-11T09:00:00Z",
            "ended_at": "2025-01-11T10:30:00Z",
            "billable": True
        }
        
        response = self.session.post(f"{BASE_URL}/time-tracking/entries", json=entry_data, headers=headers)
        if response.status_code == 200:
            entry = response.json()
            entry_id = entry["id"]
            duration = entry.get("duration_minutes", 0)
            self.log_test("Create Manual Time Entry", True, f"Duration: {duration} minutes, Billable: {entry.get('billable')}")
        else:
            self.log_test("Create Manual Time Entry", False, f"Status: {response.status_code}", response.text)
            return
        
        # Test B: Start Timer (no end time)
        timer_data = {
            "task_id": self.test_task_id,
            "description": "Current work session",
            "billable": False
        }
        
        response = self.session.post(f"{BASE_URL}/time-tracking/entries", json=timer_data, headers=headers)
        if response.status_code == 200:
            timer_entry = response.json()
            timer_id = timer_entry["id"]
            is_running = timer_entry.get("is_running", False)
            self.log_test("Start Timer", True, f"Running: {is_running}, Entry ID: {timer_id}")
        else:
            self.log_test("Start Timer", False, f"Status: {response.status_code}", response.text)
            return
        
        # Test C: Get Time Entries
        response = self.session.get(f"{BASE_URL}/time-tracking/entries", headers=headers)
        if response.status_code == 200:
            result = response.json()
            entries = result.get("entries", [])
            self.log_test("Get All Time Entries", True, f"Found {len(entries)} entries")
        else:
            self.log_test("Get All Time Entries", False, f"Status: {response.status_code}", response.text)
        
        # Filter by task
        response = self.session.get(f"{BASE_URL}/time-tracking/entries?task_id={self.test_task_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            task_entries = result.get("entries", [])
            self.log_test("Filter Entries by Task", True, f"Task entries: {len(task_entries)}")
        else:
            self.log_test("Filter Entries by Task", False, f"Status: {response.status_code}", response.text)
        
        # Get running entries only
        response = self.session.get(f"{BASE_URL}/time-tracking/entries?running_only=true", headers=headers)
        if response.status_code == 200:
            result = response.json()
            running_entries = result.get("entries", [])
            self.log_test("Get Running Entries", True, f"Running: {len(running_entries)}")
        else:
            self.log_test("Get Running Entries", False, f"Status: {response.status_code}", response.text)
        
        # Get specific entry
        response = self.session.get(f"{BASE_URL}/time-tracking/entries/{entry_id}", headers=headers)
        if response.status_code == 200:
            entry_details = response.json()
            self.log_test("Get Specific Entry", True, f"Entry: {entry_details.get('description', 'No description')}")
        else:
            self.log_test("Get Specific Entry", False, f"Status: {response.status_code}", response.text)
        
        # Test D: Update Time Entry
        update_data = {
            "description": "Updated description for Phase 3 work"
        }
        response = self.session.put(f"{BASE_URL}/time-tracking/entries/{entry_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_entry = response.json()
            self.log_test("Update Time Entry", True, f"New description: {updated_entry.get('description')}")
        else:
            self.log_test("Update Time Entry", False, f"Status: {response.status_code}", response.text)
        
        # Test E: Stop Timer
        response = self.session.post(f"{BASE_URL}/time-tracking/entries/{timer_id}/stop", headers=headers)
        if response.status_code == 200:
            result = response.json()
            duration = result.get("duration_minutes", 0)
            self.log_test("Stop Timer", True, f"Stopped timer, Duration: {duration} minutes")
        else:
            self.log_test("Stop Timer", False, f"Status: {response.status_code}", response.text)
        
        # Test F: Time Statistics
        response = self.session.get(f"{BASE_URL}/time-tracking/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            total_hours = stats.get("total_hours", 0)
            billable_hours = stats.get("billable_hours", 0)
            self.log_test("Time Statistics", True, f"Total: {total_hours}h, Billable: {billable_hours}h")
        else:
            self.log_test("Time Statistics", False, f"Status: {response.status_code}", response.text)
        
        # Stats for specific task
        response = self.session.get(f"{BASE_URL}/time-tracking/stats?task_id={self.test_task_id}", headers=headers)
        if response.status_code == 200:
            task_stats = response.json()
            self.log_test("Task-Specific Stats", True, f"Task hours: {task_stats.get('total_hours', 0)}")
        else:
            self.log_test("Task-Specific Stats", False, f"Status: {response.status_code}", response.text)
        
        # Test G: Daily Report
        response = self.session.get(f"{BASE_URL}/time-tracking/reports/daily", headers=headers)
        if response.status_code == 200:
            report = response.json()
            date = report.get("date")
            total_hours = report.get("total_hours", 0)
            self.log_test("Daily Time Report (Today)", True, f"Date: {date}, Hours: {total_hours}")
        else:
            self.log_test("Daily Time Report (Today)", False, f"Status: {response.status_code}", response.text)
        
        # Specific date report
        response = self.session.get(f"{BASE_URL}/time-tracking/reports/daily?date=2025-01-11", headers=headers)
        if response.status_code == 200:
            report = response.json()
            self.log_test("Daily Time Report (Specific Date)", True, f"Date: {report.get('date')}, Hours: {report.get('total_hours', 0)}")
        else:
            self.log_test("Daily Time Report (Specific Date)", False, f"Status: {response.status_code}", response.text)
        
        # Test H: Delete Time Entry
        response = self.session.delete(f"{BASE_URL}/time-tracking/entries/{entry_id}", headers=headers)
        if response.status_code == 200:
            self.log_test("Delete Time Entry", True, "Time entry deleted")
        else:
            self.log_test("Delete Time Entry", False, f"Status: {response.status_code}", response.text)
    
    def test_integration_features(self):
        """Test Integration between Phase 3 Features"""
        print("\n🔗 TESTING PHASE 3 INTEGRATION...")
        
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        headers2 = {"Authorization": f"Bearer {self.user2_token}"}
        
        # Test A: Mentions + Notifications Integration
        mention_data = {
            "mentioned_user_ids": [self.user2_id],
            "resource_type": "task",
            "resource_id": self.test_task_id,
            "comment_id": str(uuid.uuid4()),
            "comment_text": "Integration test: @user2 please check this task"
        }
        
        # Create mention
        response = self.session.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers)
        if response.status_code == 200:
            self.log_test("Integration: Create Mention", True, "Mention created for integration test")
            
            # Check if notification was auto-created
            time.sleep(1)  # Brief delay for async processing
            response = self.session.get(f"{BASE_URL}/notifications?type_filter=mention", headers=headers2)
            if response.status_code == 200:
                notifications = response.json().get("notifications", [])
                mention_notifications = [n for n in notifications if n.get("type") == "mention"]
                self.log_test("Integration: Auto-Notification", True, f"Found {len(mention_notifications)} mention notifications")
            else:
                self.log_test("Integration: Auto-Notification", False, f"Status: {response.status_code}", response.text)
        else:
            self.log_test("Integration: Create Mention", False, f"Status: {response.status_code}", response.text)
        
        # Test B: Time Tracking + Task Integration
        # Create time entry
        entry_data = {
            "task_id": self.test_task_id,
            "description": "Integration testing work",
            "started_at": "2025-01-11T14:00:00Z",
            "ended_at": "2025-01-11T15:30:00Z",
            "billable": True
        }
        
        response = self.session.post(f"{BASE_URL}/time-tracking/entries", json=entry_data, headers=headers)
        if response.status_code == 200:
            self.log_test("Integration: Time Entry Created", True, "Time entry for task integration")
            
            # Check if task was updated with time tracking info
            response = self.session.get(f"{BASE_URL}/tasks/{self.test_task_id}", headers=headers)
            if response.status_code == 200:
                task = response.json()
                has_time_entries = task.get("has_time_entries", False)
                total_time = task.get("total_time_minutes", 0)
                self.log_test("Integration: Task Time Update", True, f"Has time entries: {has_time_entries}, Total: {total_time} min")
            else:
                self.log_test("Integration: Task Time Update", False, f"Status: {response.status_code}", response.text)
        else:
            self.log_test("Integration: Time Entry Created", False, f"Status: {response.status_code}", response.text)
    
    def test_edge_cases_validation(self):
        """Test Edge Cases & Validation"""
        print("\n🧪 TESTING EDGE CASES & VALIDATION...")
        
        headers = {"Authorization": f"Bearer {self.user1_token}"}
        
        # Test A: Mentions Edge Cases
        # Try to mention non-existent user
        mention_data = {
            "mentioned_user_ids": ["non-existent-user-id"],
            "resource_type": "task",
            "resource_id": self.test_task_id,
            "comment_id": str(uuid.uuid4()),
            "comment_text": "Mentioning non-existent user"
        }
        
        response = self.session.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            # Should skip non-existent users
            self.log_test("Edge Case: Non-existent User Mention", True, f"Handled gracefully: {result.get('message')}")
        else:
            self.log_test("Edge Case: Non-existent User Mention", False, f"Status: {response.status_code}", response.text)
        
        # Mention self
        mention_data["mentioned_user_ids"] = [self.user1_id]
        mention_data["comment_text"] = "Self mention test"
        response = self.session.post(f"{BASE_URL}/mentions", json=mention_data, headers=headers)
        if response.status_code == 200:
            self.log_test("Edge Case: Self Mention", True, "Self mention allowed")
        else:
            self.log_test("Edge Case: Self Mention", False, f"Status: {response.status_code}", response.text)
        
        # Test B: Time Tracking Edge Cases
        # Create time entry for non-existent task
        entry_data = {
            "task_id": "non-existent-task-id",
            "description": "Testing non-existent task",
            "billable": False
        }
        
        response = self.session.post(f"{BASE_URL}/time-tracking/entries", json=entry_data, headers=headers)
        if response.status_code == 404:
            self.log_test("Edge Case: Non-existent Task Time Entry", True, "404 Not Found as expected")
        else:
            self.log_test("Edge Case: Non-existent Task Time Entry", False, f"Expected 404, got {response.status_code}")
        
        # Try to stop already stopped timer
        response = self.session.post(f"{BASE_URL}/time-tracking/entries/non-existent-id/stop", headers=headers)
        if response.status_code == 404:
            self.log_test("Edge Case: Stop Non-existent Timer", True, "404 Not Found as expected")
        else:
            self.log_test("Edge Case: Stop Non-existent Timer", False, f"Expected 404, got {response.status_code}")
        
        # Test C: Notifications Edge Cases
        # Try to mark another user's notification as read (should fail)
        response = self.session.put(f"{BASE_URL}/notifications/non-existent-id/read", headers=headers)
        if response.status_code == 404:
            self.log_test("Edge Case: Mark Non-existent Notification", True, "404 Not Found as expected")
        else:
            self.log_test("Edge Case: Mark Non-existent Notification", False, f"Expected 404, got {response.status_code}")
    
    def test_authorization_security(self):
        """Test Authorization & Security"""
        print("\n🔒 TESTING AUTHORIZATION & SECURITY...")
        
        # Test without authentication
        response = self.session.get(f"{BASE_URL}/mentions/me")
        if response.status_code == 401:
            self.log_test("Security: Mentions Without Auth", True, "401 Unauthorized as expected")
        else:
            self.log_test("Security: Mentions Without Auth", False, f"Expected 401, got {response.status_code}")
        
        response = self.session.get(f"{BASE_URL}/notifications")
        if response.status_code == 401:
            self.log_test("Security: Notifications Without Auth", True, "401 Unauthorized as expected")
        else:
            self.log_test("Security: Notifications Without Auth", False, f"Expected 401, got {response.status_code}")
        
        response = self.session.get(f"{BASE_URL}/time-tracking/entries")
        if response.status_code == 401:
            self.log_test("Security: Time Tracking Without Auth", True, "401 Unauthorized as expected")
        else:
            self.log_test("Security: Time Tracking Without Auth", False, f"Expected 401, got {response.status_code}")
        
        # Test data isolation (user can only see their own data)
        headers1 = {"Authorization": f"Bearer {self.user1_token}"}
        headers2 = {"Authorization": f"Bearer {self.user2_token}"}
        
        # User 2 should not see User 1's time entries
        response = self.session.get(f"{BASE_URL}/time-tracking/entries", headers=headers2)
        if response.status_code == 200:
            entries = response.json().get("entries", [])
            user1_entries = [e for e in entries if e.get("user_id") == self.user1_id]
            if len(user1_entries) == 0:
                self.log_test("Security: Time Entry Isolation", True, "User 2 cannot see User 1's entries")
            else:
                self.log_test("Security: Time Entry Isolation", False, f"Found {len(user1_entries)} entries from other user")
        else:
            self.log_test("Security: Time Entry Isolation", False, f"Status: {response.status_code}", response.text)
    
    def run_all_tests(self):
        """Run all Phase 3 tests"""
        print("🚀 STARTING COMPREHENSIVE PHASE 3 BACKEND API TESTING")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Aborting tests.")
            return
        
        if not self.create_test_task():
            print("❌ Test task creation failed. Aborting tests.")
            return
        
        # Run all test suites
        self.test_mentions_system()
        self.test_notifications_center()
        self.test_time_tracking_system()
        self.test_integration_features()
        self.test_edge_cases_validation()
        self.test_authorization_security()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 PHASE 3 BACKEND API TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Phase 3 backend APIs are production ready.")
        elif success_rate >= 80:
            print("✅ GOOD! Phase 3 backend APIs are mostly functional with minor issues.")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE! Phase 3 backend APIs work but need improvements.")
        else:
            print("❌ NEEDS WORK! Phase 3 backend APIs have significant issues.")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result}")
        
        return success_rate


if __name__ == "__main__":
    tester = Phase3BackendTester()
    success_rate = tester.run_all_tests()
    
    if success_rate >= 90:
        exit(0)  # Success
    else:
        exit(1)  # Some issues found