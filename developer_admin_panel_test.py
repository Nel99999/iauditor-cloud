#!/usr/bin/env python3
"""
Developer Admin Panel - Full DevOps Dashboard Backend Testing
Tests all 15 endpoints across 9 categories
Production User: llewellyn@bluedawncapital.co.za (role: developer)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://userperm-hub.preview.emergentagent.com/api"
PROD_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
PROD_USER_PASSWORD = "Llewellyn@123"  # Will need to be provided

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class DeveloperPanelTester:
    def __init__(self):
        self.token = None
        self.user_info = None
        self.results = {
            "passed": [],
            "failed": [],
            "skipped": []
        }
        
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    def print_test(self, test_name: str, status: str, details: str = ""):
        if status == "PASS":
            symbol = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            symbol = "❌"
            color = Colors.RED
        else:  # SKIP
            symbol = "⚠️"
            color = Colors.YELLOW
        
        print(f"{symbol} {color}{status}{Colors.RESET} - {test_name}")
        if details:
            print(f"   {details}")
    
    def authenticate(self) -> bool:
        """Authenticate with production user"""
        self.print_header("AUTHENTICATION")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": PROD_USER_EMAIL,
                    "password": PROD_USER_PASSWORD
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user", {})
                
                if self.user_info.get("role") != "developer":
                    self.print_test("Authentication", "FAIL", 
                                  f"User role is '{self.user_info.get('role')}', expected 'developer'")
                    return False
                
                self.print_test("Authentication", "PASS", 
                              f"Logged in as {self.user_info.get('name')} (role: developer)")
                return True
            else:
                self.print_test("Authentication", "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Authentication", "FAIL", f"Error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ========================================================================
    # CATEGORY 1: SYSTEM HEALTH & MONITORING (CRITICAL)
    # ========================================================================
    
    def test_system_health(self):
        """Test GET /api/developer/health"""
        test_name = "GET /api/developer/health - System Health"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/health",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "system", "database", "services"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                # Verify system metrics
                system = data.get("system", {})
                if "cpu_percent" not in system or "memory" not in system or "disk" not in system:
                    self.print_test(test_name, "FAIL", "Missing system metrics")
                    self.results["failed"].append(test_name)
                    return
                
                # Verify database info
                database = data.get("database", {})
                if "status" not in database or "collections" not in database:
                    self.print_test(test_name, "FAIL", "Missing database info")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Status: {data['status']}, "
                          f"CPU: {system.get('cpu_percent', 0):.1f}%, "
                          f"Memory: {system.get('memory', {}).get('percent', 0):.1f}%, "
                          f"DB Status: {database.get('status')}, "
                          f"Collections: {database.get('collections', 0)}")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_environment_info(self):
        """Test GET /api/developer/environment"""
        test_name = "GET /api/developer/environment - Environment Info"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/environment",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["python_version", "environment_variables"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                # Verify sensitive data is masked
                env_vars = data.get("environment_variables", {})
                api_key = env_vars.get("SENDGRID_API_KEY", "")
                jwt_secret = env_vars.get("JWT_SECRET", "")
                
                # Check masking (should have ******** + last 4 chars)
                masked_correctly = True
                if api_key and api_key != "Not Set":
                    if not api_key.startswith("********"):
                        masked_correctly = False
                
                if not masked_correctly:
                    self.print_test(test_name, "FAIL", "Sensitive data not properly masked")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Python: {data.get('python_version')}, "
                          f"Env: {data.get('environment', 'N/A')}, "
                          f"API Key Masked: {api_key[:12]}...")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 2: API TESTING TOOL (HIGH)
    # ========================================================================
    
    def test_api_testing_tool(self):
        """Test POST /api/developer/test/api"""
        test_name = "POST /api/developer/test/api - API Testing Tool"
        
        try:
            # Test with /api/users/me endpoint
            response = requests.post(
                f"{BACKEND_URL}/developer/test/api",
                headers=self.get_headers(),
                json={
                    "method": "GET",
                    "endpoint": "/api/users/me",
                    "headers": {"Authorization": f"Bearer {self.token}"},
                    "body": {}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status_code", "headers", "body", "elapsed_ms"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                # Check if test was successful
                if data.get("status_code") != 200:
                    self.print_test(test_name, "FAIL", 
                                  f"Test endpoint returned {data.get('status_code')}")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Test Status: {data.get('status_code')}, "
                          f"Elapsed: {data.get('elapsed_ms', 0):.0f}ms")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 3: EMAIL TESTING TOOL (HIGH)
    # ========================================================================
    
    def test_email_testing_tool(self):
        """Test POST /api/developer/test/email"""
        test_name = "POST /api/developer/test/email - Email Testing Tool"
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/developer/test/email",
                headers=self.get_headers(),
                json={
                    "recipient": PROD_USER_EMAIL,
                    "template_type": "welcome",
                    "test_data": {
                        "name": "Test User",
                        "login_url": "https://app.example.com"
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "recipient", "template"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Success: {data.get('success')}, "
                          f"Recipient: {data.get('recipient')}, "
                          f"Template: {data.get('template')}")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                # Email might fail due to SendGrid config - check error
                error_text = response.text
                if "SendGrid" in error_text or "not configured" in error_text:
                    self.print_test(test_name, "FAIL", 
                                  f"SendGrid configuration issue: {error_text[:100]}")
                else:
                    self.print_test(test_name, "FAIL", 
                                  f"Status: {response.status_code}, Response: {error_text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 4: DATABASE INTERFACE (CRITICAL)
    # ========================================================================
    
    def test_database_collections(self):
        """Test GET /api/developer/database/collections"""
        test_name = "GET /api/developer/database/collections - Database Collections"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/database/collections",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "collections" not in data:
                    self.print_test(test_name, "FAIL", "Missing 'collections' field")
                    self.results["failed"].append(test_name)
                    return
                
                collections = data.get("collections", [])
                
                # Verify structure of collection items
                if collections and len(collections) > 0:
                    first_coll = collections[0]
                    if "name" not in first_coll or "count" not in first_coll:
                        self.print_test(test_name, "FAIL", "Invalid collection structure")
                        self.results["failed"].append(test_name)
                        return
                
                details = f"Found {len(collections)} collections"
                if collections:
                    details += f" (e.g., {collections[0].get('name')}: {collections[0].get('count')} docs)"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_database_query(self):
        """Test POST /api/developer/database/query"""
        test_name = "POST /api/developer/database/query - Database Query"
        
        try:
            # Test with users collection
            response = requests.post(
                f"{BACKEND_URL}/developer/database/query",
                headers=self.get_headers(),
                json={
                    "collection": "users",
                    "operation": "find",
                    "query": {},
                    "limit": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["operation", "collection", "count", "results"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Operation: {data.get('operation')}, "
                          f"Collection: {data.get('collection')}, "
                          f"Results: {data.get('count')} documents")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 5: LOGS VIEWER (CRITICAL)
    # ========================================================================
    
    def test_backend_logs(self):
        """Test GET /api/developer/logs/backend"""
        test_name = "GET /api/developer/logs/backend - Backend Logs"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/logs/backend?lines=50",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "logs" not in data:
                    self.print_test(test_name, "FAIL", "Missing 'logs' field")
                    self.results["failed"].append(test_name)
                    return
                
                logs = data.get("logs", [])
                
                # Verify log structure if logs exist
                if logs and len(logs) > 0:
                    first_log = logs[0]
                    if "type" not in first_log or "message" not in first_log or "source" not in first_log:
                        self.print_test(test_name, "FAIL", "Invalid log structure")
                        self.results["failed"].append(test_name)
                        return
                
                details = f"Retrieved {len(logs)} log entries"
                if len(logs) == 0:
                    details += " (empty - acceptable)"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_frontend_logs(self):
        """Test GET /api/developer/logs/frontend"""
        test_name = "GET /api/developer/logs/frontend - Frontend Logs"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/logs/frontend?lines=50",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "logs" not in data:
                    self.print_test(test_name, "FAIL", "Missing 'logs' field")
                    self.results["failed"].append(test_name)
                    return
                
                logs = data.get("logs", [])
                
                details = f"Retrieved {len(logs)} log entries"
                if len(logs) == 0:
                    details += " (empty - acceptable)"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 6: SESSION MANAGEMENT (MEDIUM)
    # ========================================================================
    
    def test_active_sessions(self):
        """Test GET /api/developer/sessions/active"""
        test_name = "GET /api/developer/sessions/active - Active Sessions"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/sessions/active",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "sessions" not in data:
                    self.print_test(test_name, "FAIL", "Missing 'sessions' field")
                    self.results["failed"].append(test_name)
                    return
                
                sessions = data.get("sessions", [])
                
                details = f"Found {len(sessions)} active sessions"
                if len(sessions) == 0:
                    details += " (empty - acceptable, sessions may not be tracked)"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_delete_session(self):
        """Test DELETE /api/developer/sessions/{session_id} - SKIPPED"""
        test_name = "DELETE /api/developer/sessions/{session_id} - Delete Session"
        
        self.print_test(test_name, "SKIP", "Skipped to avoid disrupting active sessions")
        self.results["skipped"].append(test_name)
    
    # ========================================================================
    # CATEGORY 7: QUICK ACTIONS (MEDIUM)
    # ========================================================================
    
    def test_clear_cache(self):
        """Test POST /api/developer/actions/clear-cache"""
        test_name = "POST /api/developer/actions/clear-cache - Clear Cache"
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/developer/actions/clear-cache",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "success" not in data or "message" not in data:
                    self.print_test(test_name, "FAIL", "Missing required fields")
                    self.results["failed"].append(test_name)
                    return
                
                details = f"Success: {data.get('success')}, Message: {data.get('message')}"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_impersonate_user(self):
        """Test POST /api/developer/actions/impersonate"""
        test_name = "POST /api/developer/actions/impersonate - Impersonate User"
        
        try:
            # First, get a user ID from database
            db_response = requests.post(
                f"{BACKEND_URL}/developer/database/query",
                headers=self.get_headers(),
                json={
                    "collection": "users",
                    "operation": "find",
                    "query": {},
                    "limit": 1
                },
                timeout=10
            )
            
            if db_response.status_code != 200:
                self.print_test(test_name, "FAIL", "Could not fetch user for impersonation test")
                self.results["failed"].append(test_name)
                return
            
            users = db_response.json().get("results", [])
            if not users:
                self.print_test(test_name, "FAIL", "No users found for impersonation test")
                self.results["failed"].append(test_name)
                return
            
            user_id = users[0].get("id")
            
            # Now test impersonation
            response = requests.post(
                f"{BACKEND_URL}/developer/actions/impersonate",
                headers=self.get_headers(),
                json={"user_id": user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "token", "user", "expires_in_minutes"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                # Verify expires_in_minutes is 30
                if data.get("expires_in_minutes") != 30:
                    self.print_test(test_name, "FAIL", 
                                  f"Expected expires_in_minutes=30, got {data.get('expires_in_minutes')}")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Success: {data.get('success')}, "
                          f"User: {data.get('user', {}).get('email')}, "
                          f"Expires: {data.get('expires_in_minutes')}min")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 8: PERFORMANCE METRICS (MEDIUM)
    # ========================================================================
    
    def test_performance_metrics(self):
        """Test GET /api/developer/metrics/performance"""
        test_name = "GET /api/developer/metrics/performance - Performance Metrics"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/metrics/performance",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["action_stats", "slow_queries", "total_requests"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    self.print_test(test_name, "FAIL", f"Missing fields: {missing}")
                    self.results["failed"].append(test_name)
                    return
                
                details = (f"Total Requests: {data.get('total_requests')}, "
                          f"Actions Tracked: {len(data.get('action_stats', {}))}, "
                          f"Slow Queries: {len(data.get('slow_queries', []))}")
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    # ========================================================================
    # CATEGORY 9: WEBHOOKS (MEDIUM)
    # ========================================================================
    
    def test_get_webhooks(self):
        """Test GET /api/developer/webhooks"""
        test_name = "GET /api/developer/webhooks - Get Webhooks"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/developer/webhooks",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "webhooks" not in data or "count" not in data:
                    self.print_test(test_name, "FAIL", "Missing required fields")
                    self.results["failed"].append(test_name)
                    return
                
                webhooks = data.get("webhooks", [])
                
                details = f"Found {len(webhooks)} webhooks"
                if len(webhooks) == 0:
                    details += " (empty - acceptable)"
                
                self.print_test(test_name, "PASS", details)
                self.results["passed"].append(test_name)
            else:
                self.print_test(test_name, "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text[:200]}")
                self.results["failed"].append(test_name)
                
        except Exception as e:
            self.print_test(test_name, "FAIL", f"Error: {str(e)}")
            self.results["failed"].append(test_name)
    
    def test_webhook_test(self):
        """Test POST /api/developer/webhooks/test - SKIPPED"""
        test_name = "POST /api/developer/webhooks/test - Test Webhook"
        
        self.print_test(test_name, "SKIP", "Skipped - requires valid webhook URL")
        self.results["skipped"].append(test_name)
    
    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================
    
    def run_all_tests(self):
        """Run all tests in priority order"""
        
        # Authenticate first
        if not self.authenticate():
            print(f"\n{Colors.RED}Authentication failed. Cannot proceed with tests.{Colors.RESET}")
            return False
        
        # CRITICAL PRIORITY
        self.print_header("CRITICAL PRIORITY: SYSTEM HEALTH & MONITORING")
        self.test_system_health()
        self.test_environment_info()
        
        self.print_header("CRITICAL PRIORITY: DATABASE INTERFACE")
        self.test_database_collections()
        self.test_database_query()
        
        self.print_header("CRITICAL PRIORITY: LOGS VIEWER")
        self.test_backend_logs()
        self.test_frontend_logs()
        
        # HIGH PRIORITY
        self.print_header("HIGH PRIORITY: API TESTING TOOL")
        self.test_api_testing_tool()
        
        self.print_header("HIGH PRIORITY: EMAIL TESTING TOOL")
        self.test_email_testing_tool()
        
        # MEDIUM PRIORITY
        self.print_header("MEDIUM PRIORITY: PERFORMANCE METRICS")
        self.test_performance_metrics()
        
        self.print_header("MEDIUM PRIORITY: SESSION MANAGEMENT")
        self.test_active_sessions()
        self.test_delete_session()
        
        self.print_header("MEDIUM PRIORITY: QUICK ACTIONS")
        self.test_clear_cache()
        self.test_impersonate_user()
        
        self.print_header("MEDIUM PRIORITY: WEBHOOKS")
        self.test_get_webhooks()
        self.test_webhook_test()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["skipped"])
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        skipped = len(self.results["skipped"])
        
        success_rate = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        
        print(f"{Colors.BOLD}Total Tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️  Skipped: {skipped}{Colors.RESET}")
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")
        
        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for test in self.results["failed"]:
                print(f"  ❌ {test}")
        
        if skipped > 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Skipped Tests:{Colors.RESET}")
            for test in self.results["skipped"]:
                print(f"  ⚠️  {test}")


def main():
    """Main entry point"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 80)
    print("Developer Admin Panel - Full DevOps Dashboard Backend Testing")
    print("=" * 80)
    print(f"{Colors.RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Production User: {PROD_USER_EMAIL}")
    print(f"Total Endpoints to Test: 15 (13 active + 2 skipped)")
    print()
    
    tester = DeveloperPanelTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
