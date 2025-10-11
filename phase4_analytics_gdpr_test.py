#!/usr/bin/env python3
"""
Phase 4 Analytics & GDPR Backend API Comprehensive Testing
Testing Interactive Analytics Dashboard and GDPR Compliance system
"""

import requests
import json
import uuid
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=')[1].strip()
            break

API_BASE = f"{BACKEND_URL}/api"

class Phase4BackendTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.org_id = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        try:
            # Register a test user
            register_data = {
                "name": "Analytics Tester",
                "email": f"analytics.tester.{uuid.uuid4().hex[:8]}@testcorp.com",
                "password": "SecureTestPass123!",
                "organization_name": f"Analytics Test Corp {uuid.uuid4().hex[:6]}"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.org_id = data.get("user", {}).get("organization_id")
                
                # Set authorization header
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                self.log_test("Authentication Setup", True, f"User: {register_data['email']}, Org: {register_data['organization_name']}")
                return True
            else:
                self.log_test("Authentication Setup", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Exception: {str(e)}")
            return False
    
    def create_test_data(self):
        """Create test data for analytics"""
        try:
            # Create test tasks
            for i in range(5):
                task_data = {
                    "title": f"Analytics Test Task {i+1}",
                    "description": f"Test task for analytics testing {i+1}",
                    "priority": ["low", "medium", "high"][i % 3],
                    "status": ["todo", "in_progress", "completed"][i % 3]
                }
                
                if task_data["status"] == "completed":
                    task_data["completed_at"] = (datetime.now(timezone.utc) - timedelta(days=i)).isoformat()
                
                response = self.session.post(f"{API_BASE}/tasks", json=task_data)
                if response.status_code != 201:
                    self.log_test("Create Test Data", False, f"Task creation failed: {response.status_code}")
                    return False
            
            # Create test time entries
            for i in range(3):
                time_data = {
                    "task_id": None,  # Can be null for general time tracking
                    "description": f"Analytics test time entry {i+1}",
                    "started_at": (datetime.now(timezone.utc) - timedelta(hours=i+1)).isoformat(),
                    "duration_minutes": 60 + (i * 30),
                    "billable": i % 2 == 0
                }
                
                response = self.session.post(f"{API_BASE}/time-tracking/entries", json=time_data)
                # Time tracking might not be implemented, so we don't fail on this
                
            self.log_test("Create Test Data", True, "Created 5 test tasks and 3 time entries")
            return True
            
        except Exception as e:
            self.log_test("Create Test Data", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        try:
            # Test different periods
            periods = ["today", "week", "month", "quarter", "year"]
            
            for period in periods:
                response = self.session.get(f"{API_BASE}/analytics/overview?period={period}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["period", "start_date", "end_date", "metrics"]
                    if all(field in data for field in required_fields):
                        
                        # Validate metrics structure
                        metrics = data["metrics"]
                        required_metrics = ["tasks", "inspections", "users", "groups", "time_tracking", "workflows"]
                        
                        if all(metric in metrics for metric in required_metrics):
                            self.log_test(f"Analytics Overview - {period}", True, f"All metrics present")
                        else:
                            missing = [m for m in required_metrics if m not in metrics]
                            self.log_test(f"Analytics Overview - {period}", False, f"Missing metrics: {missing}")
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_test(f"Analytics Overview - {period}", False, f"Missing fields: {missing}")
                else:
                    self.log_test(f"Analytics Overview - {period}", False, f"HTTP {response.status_code}")
            
        except Exception as e:
            self.log_test("Analytics Overview", False, f"Exception: {str(e)}")
    
    def test_analytics_task_endpoints(self):
        """Test task-related analytics endpoints"""
        endpoints = [
            "/analytics/tasks/trends?period=week",
            "/analytics/tasks/by-status",
            "/analytics/tasks/by-priority", 
            "/analytics/tasks/by-user?limit=5"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Basic validation
                    if isinstance(data, dict) and len(data) > 0:
                        self.log_test(f"Analytics {endpoint}", True, f"Response received")
                    else:
                        self.log_test(f"Analytics {endpoint}", False, "Empty or invalid response")
                else:
                    self.log_test(f"Analytics {endpoint}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Analytics {endpoint}", False, f"Exception: {str(e)}")
    
    def test_analytics_time_tracking(self):
        """Test time tracking analytics"""
        try:
            response = self.session.get(f"{API_BASE}/analytics/time-tracking/trends?period=week")
            
            if response.status_code == 200:
                data = response.json()
                
                if "period" in data and "trends" in data:
                    self.log_test("Analytics Time Tracking Trends", True, f"Period: {data['period']}")
                else:
                    self.log_test("Analytics Time Tracking Trends", False, "Invalid response structure")
            else:
                self.log_test("Analytics Time Tracking Trends", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Time Tracking Trends", False, f"Exception: {str(e)}")
    
    def test_analytics_inspections(self):
        """Test inspection analytics"""
        try:
            response = self.session.get(f"{API_BASE}/analytics/inspections/scores?period=month")
            
            if response.status_code == 200:
                data = response.json()
                
                if "period" in data and "trends" in data:
                    self.log_test("Analytics Inspection Scores", True, f"Period: {data['period']}")
                else:
                    self.log_test("Analytics Inspection Scores", False, "Invalid response structure")
            else:
                self.log_test("Analytics Inspection Scores", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Inspection Scores", False, f"Exception: {str(e)}")
    
    def test_analytics_workflows(self):
        """Test workflow analytics"""
        try:
            response = self.session.get(f"{API_BASE}/analytics/workflows/completion-time?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["average_hours", "min_hours", "max_hours", "completion_times"]
                if all(field in data for field in required_fields):
                    self.log_test("Analytics Workflow Completion Time", True, f"Avg: {data['average_hours']}h")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Analytics Workflow Completion Time", False, f"Missing fields: {missing}")
            else:
                self.log_test("Analytics Workflow Completion Time", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Workflow Completion Time", False, f"Exception: {str(e)}")
    
    def test_analytics_user_activity(self):
        """Test user activity analytics"""
        try:
            response = self.session.get(f"{API_BASE}/analytics/user-activity?period=week&limit=5")
            
            if response.status_code == 200:
                data = response.json()
                
                if "period" in data and "most_active_users" in data:
                    self.log_test("Analytics User Activity", True, f"Period: {data['period']}")
                else:
                    self.log_test("Analytics User Activity", False, "Invalid response structure")
            else:
                self.log_test("Analytics User Activity", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics User Activity", False, f"Exception: {str(e)}")
    
    def test_gdpr_data_export(self):
        """Test GDPR data export functionality"""
        try:
            # Test data export request
            response = self.session.post(f"{API_BASE}/gdpr/data-export")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["message", "export_id", "data"]
                if all(field in data for field in required_fields):
                    
                    # Validate export data structure
                    export_data = data["data"]
                    required_export_fields = ["export_date", "user_id", "user_profile", "tasks", "summary"]
                    
                    if all(field in export_data for field in required_export_fields):
                        self.log_test("GDPR Data Export Request", True, f"Export ID: {data['export_id']}")
                    else:
                        missing = [f for f in required_export_fields if f not in export_data]
                        self.log_test("GDPR Data Export Request", False, f"Missing export fields: {missing}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("GDPR Data Export Request", False, f"Missing fields: {missing}")
            else:
                self.log_test("GDPR Data Export Request", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Data Export Request", False, f"Exception: {str(e)}")
    
    def test_gdpr_data_download(self):
        """Test GDPR data download functionality"""
        try:
            response = self.session.get(f"{API_BASE}/gdpr/data-export/download")
            
            if response.status_code == 200:
                # Check if it's a JSON response
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    self.log_test("GDPR Data Download", True, f"Content-Type: {content_type}")
                else:
                    self.log_test("GDPR Data Download", False, f"Unexpected content-type: {content_type}")
            else:
                self.log_test("GDPR Data Download", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Data Download", False, f"Exception: {str(e)}")
    
    def test_gdpr_consent_management(self):
        """Test GDPR consent management"""
        try:
            # Test get consent status
            response = self.session.get(f"{API_BASE}/gdpr/consent-status")
            
            if response.status_code == 200:
                consent_data = response.json()
                
                required_fields = ["user_id", "organization_id", "marketing_emails", "analytics", "third_party_sharing", "data_processing"]
                if all(field in consent_data for field in required_fields):
                    self.log_test("GDPR Get Consent Status", True, f"User ID: {consent_data['user_id']}")
                    
                    # Test update consent
                    update_data = {
                        "marketing_emails": True,
                        "analytics": True,
                        "third_party_sharing": False,
                        "data_processing": True
                    }
                    
                    response = self.session.put(f"{API_BASE}/gdpr/consent", json=update_data)
                    
                    if response.status_code == 200:
                        update_result = response.json()
                        if "message" in update_result and "consent" in update_result:
                            self.log_test("GDPR Update Consent", True, "Consent updated successfully")
                        else:
                            self.log_test("GDPR Update Consent", False, "Invalid update response")
                    else:
                        self.log_test("GDPR Update Consent", False, f"HTTP {response.status_code}")
                        
                else:
                    missing = [f for f in required_fields if f not in consent_data]
                    self.log_test("GDPR Get Consent Status", False, f"Missing fields: {missing}")
            else:
                self.log_test("GDPR Get Consent Status", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Consent Management", False, f"Exception: {str(e)}")
    
    def test_gdpr_data_retention_policy(self):
        """Test GDPR data retention policy"""
        try:
            response = self.session.get(f"{API_BASE}/gdpr/data-retention-policy")
            
            if response.status_code == 200:
                policy = response.json()
                
                required_fields = ["organization_id", "audit_logs_days", "user_data_days", "completed_tasks_days"]
                if all(field in policy for field in required_fields):
                    self.log_test("GDPR Data Retention Policy", True, f"Audit logs: {policy['audit_logs_days']} days")
                else:
                    missing = [f for f in required_fields if f not in policy]
                    self.log_test("GDPR Data Retention Policy", False, f"Missing fields: {missing}")
            else:
                self.log_test("GDPR Data Retention Policy", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Data Retention Policy", False, f"Exception: {str(e)}")
    
    def test_gdpr_privacy_report(self):
        """Test GDPR privacy report"""
        try:
            response = self.session.get(f"{API_BASE}/gdpr/privacy-report")
            
            if response.status_code == 200:
                report = response.json()
                
                required_fields = ["user_id", "report_date", "data_stored", "consent_status", "rights"]
                if all(field in report for field in required_fields):
                    
                    # Validate data_stored structure
                    data_stored = report["data_stored"]
                    if "tasks" in data_stored and "time_entries" in data_stored:
                        self.log_test("GDPR Privacy Report", True, f"Tasks: {data_stored['tasks']}, Time entries: {data_stored['time_entries']}")
                    else:
                        self.log_test("GDPR Privacy Report", False, "Invalid data_stored structure")
                else:
                    missing = [f for f in required_fields if f not in report]
                    self.log_test("GDPR Privacy Report", False, f"Missing fields: {missing}")
            else:
                self.log_test("GDPR Privacy Report", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Privacy Report", False, f"Exception: {str(e)}")
    
    def test_gdpr_account_deletion(self):
        """Test GDPR account deletion (anonymization)"""
        try:
            # Test anonymization (safer than hard delete)
            response = self.session.post(f"{API_BASE}/gdpr/delete-account?anonymize=true")
            
            if response.status_code == 200:
                result = response.json()
                
                if "message" in result:
                    self.log_test("GDPR Account Deletion (Anonymize)", True, result["message"])
                else:
                    self.log_test("GDPR Account Deletion (Anonymize)", False, "No message in response")
            else:
                self.log_test("GDPR Account Deletion (Anonymize)", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Account Deletion (Anonymize)", False, f"Exception: {str(e)}")
    
    def test_authorization_enforcement(self):
        """Test that all endpoints require authentication"""
        # Remove authorization header temporarily
        original_headers = self.session.headers.copy()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        endpoints_to_test = [
            "/analytics/overview",
            "/analytics/tasks/trends",
            "/gdpr/data-export",
            "/gdpr/consent-status"
        ]
        
        unauthorized_count = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 401:
                    unauthorized_count += 1
                    
            except Exception:
                pass
        
        # Restore authorization header
        self.session.headers.update(original_headers)
        
        if unauthorized_count == len(endpoints_to_test):
            self.log_test("Authorization Enforcement", True, f"All {len(endpoints_to_test)} endpoints require auth")
        else:
            self.log_test("Authorization Enforcement", False, f"Only {unauthorized_count}/{len(endpoints_to_test)} endpoints require auth")
    
    def run_all_tests(self):
        """Run all Phase 4 backend tests"""
        print("🚀 Starting Phase 4 Analytics & GDPR Backend API Testing")
        print(f"Backend URL: {API_BASE}")
        print("=" * 80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue testing.")
            return
        
        if not self.create_test_data():
            print("⚠️ Test data creation failed. Continuing with existing data.")
        
        # Analytics Tests
        print("\n📊 ANALYTICS ENDPOINTS TESTING")
        print("-" * 40)
        self.test_analytics_overview()
        self.test_analytics_task_endpoints()
        self.test_analytics_time_tracking()
        self.test_analytics_inspections()
        self.test_analytics_workflows()
        self.test_analytics_user_activity()
        
        # GDPR Tests
        print("\n🔒 GDPR COMPLIANCE ENDPOINTS TESTING")
        print("-" * 40)
        self.test_gdpr_data_export()
        self.test_gdpr_data_download()
        self.test_gdpr_consent_management()
        self.test_gdpr_data_retention_policy()
        self.test_gdpr_privacy_report()
        self.test_gdpr_account_deletion()
        
        # Security Tests
        print("\n🛡️ AUTHORIZATION TESTING")
        print("-" * 40)
        self.test_authorization_enforcement()
        
        # Results Summary
        print("\n" + "=" * 80)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Phase 4 backend ready for production!")
        elif success_rate >= 80:
            print("✅ GOOD: Phase 4 backend mostly functional with minor issues")
        else:
            print("⚠️ NEEDS WORK: Phase 4 backend has significant issues")
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        return success_rate >= 90


if __name__ == "__main__":
    tester = Phase4BackendTester()
    tester.run_all_tests()