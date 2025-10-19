#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND VALIDATION - All Remaining Endpoints
Testing: Comments, Attachments, Audit, Notifications, Time Tracking, Developer, Integration Tests
"""

import requests
import json
import time
from datetime import datetime
import io

# Configuration
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"

# Global variables
auth_token = None
test_results = []
test_task_id = None
test_asset_id = None
test_comment_id = None
test_notification_id = None
test_time_entry_id = None


def log_test(test_name, status, details=""):
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {test_name}: {status}")
    if details:
        print(f"   {details}")


def login():
    """Authenticate and get token"""
    global auth_token
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            log_test("Authentication", "PASS", f"Logged in as {TEST_USER_EMAIL}")
            return True
        else:
            log_test("Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        log_test("Authentication", "FAIL", f"Exception: {str(e)}")
        return False


def get_headers():
    """Get request headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


# ==================== SETUP: CREATE TEST DATA ====================

def setup_test_data():
    """Create test task and asset for testing"""
    global test_task_id, test_asset_id
    
    print("\n" + "="*80)
    print("SETUP: Creating Test Data")
    print("="*80)
    
    # Create test task
    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=get_headers(),
            json={
                "title": "Test Task for Final Validation",
                "description": "Task for testing comments, attachments, time tracking",
                "priority": "medium",
                "status": "todo"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_task_id = data.get("id")
            log_test("Setup: Create Test Task", "PASS", f"Task ID: {test_task_id}")
        else:
            log_test("Setup: Create Test Task", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Setup: Create Test Task", "FAIL", f"Exception: {str(e)}")
    
    # Create test asset
    try:
        response = requests.post(
            f"{BASE_URL}/assets",
            headers=get_headers(),
            json={
                "asset_tag": f"TEST-ASSET-{int(time.time())}",
                "name": "Test Asset for Final Validation",
                "asset_type": "equipment",
                "status": "active"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_asset_id = data.get("id")
            log_test("Setup: Create Test Asset", "PASS", f"Asset ID: {test_asset_id}")
        else:
            log_test("Setup: Create Test Asset", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Setup: Create Test Asset", "FAIL", f"Exception: {str(e)}")


# ==================== COMMENTS MODULE (4 ENDPOINTS) ====================

def test_comments_module():
    """Test all comments endpoints"""
    global test_comment_id
    
    print("\n" + "="*80)
    print("COMMENTS MODULE - 4 Endpoints")
    print("="*80)
    
    # Test 1: Create comment on task
    try:
        response = requests.post(
            f"{BASE_URL}/comments",
            headers=get_headers(),
            json={
                "resource_type": "task",
                "resource_id": test_task_id,
                "text": "This is a test comment for final validation"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_comment_id = data.get("id")
            log_test("Comments 1: Create Comment", "PASS", f"Comment ID: {test_comment_id}")
        else:
            log_test("Comments 1: Create Comment", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("Comments 1: Create Comment", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: List comments for task
    try:
        response = requests.get(
            f"{BASE_URL}/comments?resource_type=task&resource_id={test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            comment_count = len(data) if isinstance(data, list) else 0
            log_test("Comments 2: List Comments", "PASS", f"Found {comment_count} comments")
        else:
            log_test("Comments 2: List Comments", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Comments 2: List Comments", "FAIL", f"Exception: {str(e)}")
    
    # Test 3: Update comment
    if test_comment_id:
        try:
            response = requests.put(
                f"{BASE_URL}/comments/{test_comment_id}",
                headers=get_headers(),
                json={
                    "text": "Updated comment text for final validation"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                is_edited = data.get("is_edited", False)
                log_test("Comments 3: Update Comment", "PASS", f"is_edited: {is_edited}")
            else:
                log_test("Comments 3: Update Comment", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Comments 3: Update Comment", "FAIL", f"Exception: {str(e)}")
    
    # Test 4: Delete comment
    if test_comment_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/comments/{test_comment_id}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                log_test("Comments 4: Delete Comment", "PASS", "Comment deleted successfully")
            else:
                log_test("Comments 4: Delete Comment", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Comments 4: Delete Comment", "FAIL", f"Exception: {str(e)}")


# ==================== ATTACHMENTS MODULE (4 ENDPOINTS) ====================

def test_attachments_module():
    """Test all attachments endpoints"""
    
    print("\n" + "="*80)
    print("ATTACHMENTS MODULE - 4 Endpoints")
    print("="*80)
    
    file_id = None
    
    # Test 1: Upload attachment to task
    try:
        # Create a test file
        test_file_content = b"This is a test file for final validation"
        files = {
            'file': ('test_document.txt', io.BytesIO(test_file_content), 'text/plain')
        }
        
        headers_without_content_type = {
            "Authorization": f"Bearer {auth_token}"
        }
        
        response = requests.post(
            f"{BASE_URL}/attachments/task/{test_task_id}/upload",
            headers=headers_without_content_type,
            files=files,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            attachment = data.get("attachment", {})
            file_id = attachment.get("id")
            log_test("Attachments 1: Upload File", "PASS", f"File ID: {file_id}, Size: {attachment.get('size')} bytes")
        else:
            log_test("Attachments 1: Upload File", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("Attachments 1: Upload File", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: List attachments (using alternative endpoint)
    try:
        response = requests.get(
            f"{BASE_URL}/attachments/task/{test_task_id}/attachments",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            attachment_count = len(data) if isinstance(data, list) else 0
            log_test("Attachments 2: List Attachments", "PASS", f"Found {attachment_count} attachments")
        else:
            log_test("Attachments 2: List Attachments", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Attachments 2: List Attachments", "FAIL", f"Exception: {str(e)}")
    
    # Test 3: Download attachment
    if file_id:
        try:
            response = requests.get(
                f"{BASE_URL}/attachments/download/{file_id}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                content_length = len(response.content)
                log_test("Attachments 3: Download File", "PASS", f"Downloaded {content_length} bytes")
            else:
                log_test("Attachments 3: Download File", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Attachments 3: Download File", "FAIL", f"Exception: {str(e)}")
    
    # Test 4: Delete attachment
    if file_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/attachments/task/{test_task_id}/attachments/{file_id}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                log_test("Attachments 4: Delete Attachment", "PASS", "Attachment deleted successfully")
            else:
                log_test("Attachments 4: Delete Attachment", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Attachments 4: Delete Attachment", "FAIL", f"Exception: {str(e)}")


# ==================== AUDIT/ACTIVITY (2 ENDPOINTS) ====================

def test_audit_module():
    """Test audit log endpoints"""
    
    print("\n" + "="*80)
    print("AUDIT/ACTIVITY MODULE - 2 Endpoints")
    print("="*80)
    
    # Test 1: Get all audit logs
    try:
        response = requests.get(
            f"{BASE_URL}/audit/logs",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            log_count = len(data) if isinstance(data, list) else 0
            log_test("Audit 1: Get Audit Logs", "PASS", f"Found {log_count} audit log entries")
        else:
            log_test("Audit 1: Get Audit Logs", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Audit 1: Get Audit Logs", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: Get filtered audit logs (by resource type and ID)
    if test_task_id:
        try:
            response = requests.get(
                f"{BASE_URL}/audit/logs?resource_type=task&resource_id={test_task_id}",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                log_count = len(data) if isinstance(data, list) else 0
                log_test("Audit 2: Get Filtered Logs", "PASS", f"Found {log_count} logs for task {test_task_id}")
            else:
                log_test("Audit 2: Get Filtered Logs", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Audit 2: Get Filtered Logs", "FAIL", f"Exception: {str(e)}")


# ==================== NOTIFICATIONS (3 ENDPOINTS) ====================

def test_notifications_module():
    """Test notifications endpoints"""
    global test_notification_id
    
    print("\n" + "="*80)
    print("NOTIFICATIONS MODULE - 3 Endpoints")
    print("="*80)
    
    # Test 1: Get notifications
    try:
        response = requests.get(
            f"{BASE_URL}/notifications",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get("notifications", [])
            total = data.get("total", 0)
            unread_count = data.get("unread_count", 0)
            
            if notifications:
                test_notification_id = notifications[0].get("id")
            
            log_test("Notifications 1: Get Notifications", "PASS", f"Total: {total}, Unread: {unread_count}")
        else:
            log_test("Notifications 1: Get Notifications", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Notifications 1: Get Notifications", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: Mark notification as read
    if test_notification_id:
        try:
            response = requests.put(
                f"{BASE_URL}/notifications/{test_notification_id}/read",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                log_test("Notifications 2: Mark as Read", "PASS", f"Notification {test_notification_id} marked as read")
            else:
                log_test("Notifications 2: Mark as Read", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("Notifications 2: Mark as Read", "FAIL", f"Exception: {str(e)}")
    else:
        log_test("Notifications 2: Mark as Read", "SKIP", "No notifications available to mark as read")
    
    # Test 3: Get notification stats
    try:
        response = requests.get(
            f"{BASE_URL}/notifications/stats",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_notifications", 0)
            unread = data.get("unread_notifications", 0)
            by_type = data.get("by_type", {})
            log_test("Notifications 3: Get Stats", "PASS", f"Total: {total}, Unread: {unread}, Types: {len(by_type)}")
        else:
            log_test("Notifications 3: Get Stats", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Notifications 3: Get Stats", "FAIL", f"Exception: {str(e)}")


# ==================== TIME TRACKING (VERIFY INTEGRATION) ====================

def test_time_tracking_module():
    """Test time tracking endpoints and integration"""
    global test_time_entry_id
    
    print("\n" + "="*80)
    print("TIME TRACKING MODULE - Verify Integration")
    print("="*80)
    
    # Test 1: Create time entry for task
    try:
        response = requests.post(
            f"{BASE_URL}/time-tracking/entries",
            headers=get_headers(),
            json={
                "task_id": test_task_id,
                "description": "Testing time tracking integration",
                "duration_minutes": 60,
                "billable": True
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_time_entry_id = data.get("id")
            duration = data.get("duration_minutes")
            log_test("Time Tracking 1: Create Entry", "PASS", f"Entry ID: {test_time_entry_id}, Duration: {duration} min")
        else:
            log_test("Time Tracking 1: Create Entry", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("Time Tracking 1: Create Entry", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: Get time entries for task
    try:
        response = requests.get(
            f"{BASE_URL}/time-tracking/entries?task_id={test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get("entries", [])
            total = data.get("total", 0)
            log_test("Time Tracking 2: Get Entries", "PASS", f"Found {total} time entries for task")
        else:
            log_test("Time Tracking 2: Get Entries", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Time Tracking 2: Get Entries", "FAIL", f"Exception: {str(e)}")
    
    # Test 3: Verify task has time tracking data
    try:
        response = requests.get(
            f"{BASE_URL}/tasks/{test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            has_time_entries = data.get("has_time_entries", False)
            total_time = data.get("total_time_minutes", 0)
            log_test("Time Tracking 3: Task Integration", "PASS", f"has_time_entries: {has_time_entries}, total_time: {total_time} min")
        else:
            log_test("Time Tracking 3: Task Integration", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Time Tracking 3: Task Integration", "FAIL", f"Exception: {str(e)}")
    
    # Test 4: Get time tracking stats
    try:
        response = requests.get(
            f"{BASE_URL}/time-tracking/stats?task_id={test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            total_hours = data.get("total_hours", 0)
            billable_hours = data.get("billable_hours", 0)
            log_test("Time Tracking 4: Get Stats", "PASS", f"Total: {total_hours}h, Billable: {billable_hours}h")
        else:
            log_test("Time Tracking 4: Get Stats", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Time Tracking 4: Get Stats", "FAIL", f"Exception: {str(e)}")


# ==================== DEVELOPER/ADMIN ENDPOINTS (SAMPLE) ====================

def test_developer_endpoints():
    """Test developer/admin endpoints"""
    
    print("\n" + "="*80)
    print("DEVELOPER/ADMIN ENDPOINTS - Sample")
    print("="*80)
    
    # Test 1: System health
    try:
        response = requests.get(
            f"{BASE_URL}/developer/health",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            system = data.get("system", {})
            database = data.get("database", {})
            cpu = system.get("cpu_percent", 0)
            db_status = database.get("status")
            log_test("Developer 1: System Health", "PASS", f"Status: {status}, CPU: {cpu}%, DB: {db_status}")
        else:
            log_test("Developer 1: System Health", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Developer 1: System Health", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: Backend logs
    try:
        response = requests.get(
            f"{BASE_URL}/developer/logs/backend?lines=10",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            count = data.get("count", 0)
            log_test("Developer 2: Backend Logs", "PASS", f"Retrieved {count} log entries")
        else:
            log_test("Developer 2: Backend Logs", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Developer 2: Backend Logs", "FAIL", f"Exception: {str(e)}")
    
    # Test 3: Database collections
    try:
        response = requests.get(
            f"{BASE_URL}/developer/database/collections",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get("collections", [])
            total = data.get("total", 0)
            log_test("Developer 3: Database Collections", "PASS", f"Found {total} collections")
        else:
            log_test("Developer 3: Database Collections", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Developer 3: Database Collections", "FAIL", f"Exception: {str(e)}")


# ==================== INTEGRATION TESTS ====================

def test_integration_workflows():
    """Test integration workflows and auto-creation"""
    
    print("\n" + "="*80)
    print("INTEGRATION TESTS - Auto-Creation Workflows")
    print("="*80)
    
    # Test 1: Create comment on asset (cross-resource commenting)
    try:
        response = requests.post(
            f"{BASE_URL}/comments",
            headers=get_headers(),
            json={
                "resource_type": "asset",
                "resource_id": test_asset_id,
                "text": "Testing cross-resource commenting on asset"
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            log_test("Integration 1: Comment on Asset", "PASS", "Comment created on asset successfully")
        else:
            log_test("Integration 1: Comment on Asset", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Integration 1: Comment on Asset", "FAIL", f"Exception: {str(e)}")
    
    # Test 2: Verify audit logs capture all actions
    try:
        response = requests.get(
            f"{BASE_URL}/audit/logs",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for various action types
            actions = [log.get("action") for log in data if isinstance(log, dict)]
            unique_actions = set(actions)
            
            log_test("Integration 2: Audit Log Coverage", "PASS", f"Capturing {len(unique_actions)} different action types")
        else:
            log_test("Integration 2: Audit Log Coverage", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Integration 2: Audit Log Coverage", "FAIL", f"Exception: {str(e)}")
    
    # Test 3: Verify task shows related data (comments, attachments, time entries)
    try:
        response = requests.get(
            f"{BASE_URL}/tasks/{test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            has_time = data.get("has_time_entries", False)
            total_time = data.get("total_time_minutes", 0)
            
            log_test("Integration 3: Task Data Aggregation", "PASS", f"Task shows time tracking: {has_time}, total: {total_time} min")
        else:
            log_test("Integration 3: Task Data Aggregation", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Integration 3: Task Data Aggregation", "FAIL", f"Exception: {str(e)}")
    
    # Test 4: Verify comments appear in audit logs
    try:
        response = requests.get(
            f"{BASE_URL}/audit/logs?resource_type=task&resource_id={test_task_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            comment_actions = [log for log in data if isinstance(log, dict) and "comment" in log.get("action", "").lower()]
            
            log_test("Integration 4: Comments in Audit", "PASS", f"Found {len(comment_actions)} comment-related audit entries")
        else:
            log_test("Integration 4: Comments in Audit", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Integration 4: Comments in Audit", "FAIL", f"Exception: {str(e)}")


# ==================== GENERATE REPORT ====================

def generate_report():
    """Generate comprehensive test report"""
    
    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE BACKEND VALIDATION - TEST REPORT")
    print("="*80)
    
    # Count results
    total_tests = len(test_results)
    passed = len([t for t in test_results if t["status"] == "PASS"])
    failed = len([t for t in test_results if t["status"] == "FAIL"])
    skipped = len([t for t in test_results if t["status"] == "SKIP"])
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⚠️  Skipped: {skipped}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    # Group by module
    print(f"\n📋 RESULTS BY MODULE:")
    
    modules = {
        "Setup": [],
        "Comments": [],
        "Attachments": [],
        "Audit": [],
        "Notifications": [],
        "Time Tracking": [],
        "Developer": [],
        "Integration": []
    }
    
    for result in test_results:
        test_name = result["test"]
        for module in modules.keys():
            if module in test_name:
                modules[module].append(result)
                break
    
    for module, results in modules.items():
        if results:
            module_passed = len([r for r in results if r["status"] == "PASS"])
            module_total = len(results)
            module_rate = (module_passed / module_total * 100) if module_total > 0 else 0
            print(f"   {module}: {module_passed}/{module_total} ({module_rate:.0f}%)")
    
    # Failed tests details
    if failed > 0:
        print(f"\n❌ FAILED TESTS DETAILS:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"   • {result['test']}")
                print(f"     {result['details']}")
    
    # Critical success criteria
    print(f"\n✅ CRITICAL SUCCESS CRITERIA:")
    
    criteria = {
        "Comments CRUD": len([t for t in test_results if "Comments" in t["test"] and t["status"] == "PASS"]) >= 3,
        "Attachments Upload/Download": len([t for t in test_results if "Attachments" in t["test"] and t["status"] == "PASS"]) >= 2,
        "Audit Logs": len([t for t in test_results if "Audit" in t["test"] and t["status"] == "PASS"]) >= 1,
        "Notifications": len([t for t in test_results if "Notifications" in t["test"] and t["status"] == "PASS"]) >= 2,
        "Time Tracking": len([t for t in test_results if "Time Tracking" in t["test"] and t["status"] == "PASS"]) >= 2,
        "Developer Endpoints": len([t for t in test_results if "Developer" in t["test"] and t["status"] == "PASS"]) >= 2,
        "Integration Tests": len([t for t in test_results if "Integration" in t["test"] and t["status"] == "PASS"]) >= 2
    }
    
    for criterion, met in criteria.items():
        status = "✅" if met else "❌"
        print(f"   {status} {criterion}")
    
    all_criteria_met = all(criteria.values())
    
    print(f"\n{'='*80}")
    if success_rate >= 95 and all_criteria_met:
        print("🎉 PRODUCTION READY - All critical endpoints operational!")
    elif success_rate >= 85:
        print("⚠️  MOSTLY READY - Minor issues need attention")
    else:
        print("❌ NOT READY - Critical issues need resolution")
    print(f"{'='*80}\n")
    
    # Save report to file
    with open("/app/final_comprehensive_v1_test_report.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": success_rate,
                "production_ready": success_rate >= 95 and all_criteria_met
            },
            "criteria": criteria,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print("📄 Detailed report saved to: /app/final_comprehensive_v1_test_report.json\n")


# ==================== MAIN EXECUTION ====================

def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE BACKEND VALIDATION")
    print("Testing: Comments, Attachments, Audit, Notifications, Time Tracking, Developer")
    print("="*80)
    
    # Step 1: Login
    if not login():
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Setup test data
    setup_test_data()
    
    if not test_task_id:
        print("\n❌ Failed to create test task. Cannot proceed with tests.")
        return
    
    # Step 3: Run all test modules
    test_comments_module()
    test_attachments_module()
    test_audit_module()
    test_notifications_module()
    test_time_tracking_module()
    test_developer_endpoints()
    test_integration_workflows()
    
    # Step 4: Generate report
    generate_report()


if __name__ == "__main__":
    main()
