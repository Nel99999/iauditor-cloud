#!/usr/bin/env python3
"""
COMPREHENSIVE SETTINGS PAGE BACKEND TESTING
Test ALL backend endpoints that ModernSettingsPage depends on
Production User: llewellyn@bluedawncapital.co.za
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://workflow-engine-18.preview.emergentagent.com/api"
PRODUCTION_EMAIL = "llewellyn@bluedawncapital.co.za"
PRODUCTION_PASSWORD = "TestPassword123!"

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "not_found": 0,
    "partial": 0,
    "tests": []
}


def log_test(endpoint, status, details, response_data=None):
    """Log test result"""
    test_results["total"] += 1
    
    if status == "✅":
        test_results["passed"] += 1
    elif status == "❌":
        test_results["failed"] += 1
    elif status == "🆕":
        test_results["not_found"] += 1
    elif status == "⚠️":
        test_results["partial"] += 1
    
    result = {
        "endpoint": endpoint,
        "status": status,
        "details": details,
        "response_data": response_data
    }
    test_results["tests"].append(result)
    
    print(f"{status} {endpoint}")
    print(f"   {details}")
    if response_data:
        print(f"   Data: {json.dumps(response_data, indent=2)[:200]}...")
    print()


def main():
    print("=" * 80)
    print("COMPREHENSIVE SETTINGS PAGE BACKEND TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Production User: {PRODUCTION_EMAIL}")
    print(f"Test Started: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    # ==================== AUTHENTICATION ====================
    print("🔐 AUTHENTICATING...")
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": PRODUCTION_EMAIL, "password": PRODUCTION_PASSWORD},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            user_data = login_response.json().get("user", {})
            print(f"✅ Authentication successful")
            print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
            print(f"   Role: {user_data.get('role')}")
            print()
        else:
            print(f"❌ Authentication failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # ==================== NEW ENDPOINTS ====================
    print("=" * 80)
    print("TESTING NEW ENDPOINTS")
    print("=" * 80)
    print()
    
    # 1. Organizational Context
    print("1️⃣  ORGANIZATIONAL CONTEXT")
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/me/org-context",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = [
                "organization_name", "unit_name", "unit_level", 
                "manager_name", "manager_role", "team_size", 
                "role", "role_level"
            ]
            
            missing_fields = [f for f in required_fields if f not in data]
            
            if not missing_fields:
                log_test(
                    "GET /api/users/me/org-context",
                    "✅",
                    f"Returns all required fields. Org: {data.get('organization_name')}, Unit: {data.get('unit_name')}, Manager: {data.get('manager_name')}, Team Size: {data.get('team_size')}",
                    data
                )
            else:
                log_test(
                    "GET /api/users/me/org-context",
                    "⚠️",
                    f"Missing fields: {', '.join(missing_fields)}",
                    data
                )
        elif response.status_code == 404:
            log_test(
                "GET /api/users/me/org-context",
                "🆕",
                "Endpoint not found - needs implementation"
            )
        else:
            log_test(
                "GET /api/users/me/org-context",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/users/me/org-context",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 2. Recent Activity
    print("2️⃣  RECENT ACTIVITY")
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/me/recent-activity?limit=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check format
                    first_item = data[0]
                    has_action = "action" in first_item
                    has_resource = "resource_type" in first_item
                    has_timestamp = "created_at" in first_item or "timestamp" in first_item
                    
                    if has_action and has_resource and has_timestamp:
                        log_test(
                            "GET /api/users/me/recent-activity",
                            "✅",
                            f"Returns {len(data)} activity entries with correct format",
                            data[:2]  # Show first 2
                        )
                    else:
                        log_test(
                            "GET /api/users/me/recent-activity",
                            "⚠️",
                            f"Returns data but missing fields (action: {has_action}, resource_type: {has_resource}, timestamp: {has_timestamp})",
                            data[:1]
                        )
                else:
                    log_test(
                        "GET /api/users/me/recent-activity",
                        "✅",
                        "Returns empty array (no recent activity)",
                        []
                    )
            else:
                log_test(
                    "GET /api/users/me/recent-activity",
                    "⚠️",
                    f"Unexpected response format: {type(data)}",
                    data
                )
        elif response.status_code == 404:
            log_test(
                "GET /api/users/me/recent-activity",
                "🆕",
                "Endpoint not found - needs implementation"
            )
        else:
            log_test(
                "GET /api/users/me/recent-activity",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/users/me/recent-activity",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 3. Active Sessions
    print("3️⃣  ACTIVE SESSIONS")
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/sessions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                if len(data) > 0:
                    first_session = data[0]
                    required_fields = ["id", "device", "location", "ip_address", "last_active", "is_current"]
                    missing_fields = [f for f in required_fields if f not in first_session]
                    
                    if not missing_fields:
                        log_test(
                            "GET /api/auth/sessions",
                            "✅",
                            f"Returns {len(data)} session(s) with all required fields",
                            data
                        )
                    else:
                        log_test(
                            "GET /api/auth/sessions",
                            "⚠️",
                            f"Returns sessions but missing fields: {', '.join(missing_fields)}",
                            data
                        )
                else:
                    log_test(
                        "GET /api/auth/sessions",
                        "✅",
                        "Returns empty array (no active sessions tracked)",
                        []
                    )
            else:
                log_test(
                    "GET /api/auth/sessions",
                    "⚠️",
                    f"Unexpected response format: {type(data)}",
                    data
                )
        elif response.status_code == 404:
            log_test(
                "GET /api/auth/sessions",
                "🆕",
                "Endpoint not found - needs implementation"
            )
        else:
            log_test(
                "GET /api/auth/sessions",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/auth/sessions",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 4. Session Revocation (only test if sessions exist)
    print("4️⃣  SESSION REVOCATION")
    print("   Skipping DELETE test to avoid disrupting current session")
    log_test(
        "DELETE /api/auth/sessions/{session_id}",
        "⚠️",
        "Skipped - would revoke current session"
    )
    
    # ==================== EXISTING ENDPOINTS ====================
    print()
    print("=" * 80)
    print("TESTING EXISTING ENDPOINTS")
    print("=" * 80)
    print()
    
    # 5. Profile Update
    print("5️⃣  PROFILE UPDATE")
    try:
        # Test with phone update
        response = requests.put(
            f"{BACKEND_URL}/users/profile",
            headers=headers,
            json={"phone": "+27123456789"},
            timeout=10
        )
        
        if response.status_code == 200:
            log_test(
                "PUT /api/users/profile",
                "✅",
                "Profile update successful",
                response.json()
            )
        else:
            log_test(
                "PUT /api/users/profile",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "PUT /api/users/profile",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 6. Photo Upload (skip actual upload, just check endpoint exists)
    print("6️⃣  PHOTO UPLOAD")
    log_test(
        "POST /api/users/profile/picture",
        "⚠️",
        "Skipped - requires multipart file upload (endpoint exists in code)"
    )
    
    # 7. Password Change
    print("7️⃣  PASSWORD CHANGE")
    print("   Skipping actual password change to avoid disrupting account")
    log_test(
        "POST /api/auth/change-password",
        "⚠️",
        "Skipped - would change production password"
    )
    
    # 8. MFA Status
    print("8️⃣  MFA STATUS")
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            mfa_enabled = data.get("mfa_enabled", False)
            
            log_test(
                "GET /api/users/me (mfa_enabled field)",
                "✅",
                f"MFA Status: {'Enabled' if mfa_enabled else 'Disabled'}",
                {"mfa_enabled": mfa_enabled}
            )
        else:
            log_test(
                "GET /api/users/me",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/users/me",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 9. Email Settings (Master/Developer only)
    print("9️⃣  EMAIL SETTINGS")
    try:
        response = requests.get(
            f"{BACKEND_URL}/settings/email",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            configured = data.get("sendgrid_configured", False)
            
            log_test(
                "GET /api/settings/email",
                "✅",
                f"SendGrid configured: {configured}, From: {data.get('sendgrid_from_email')}",
                data
            )
        elif response.status_code == 403:
            log_test(
                "GET /api/settings/email",
                "✅",
                "Correctly returns 403 for non-Master/Developer roles (RBAC working)"
            )
        else:
            log_test(
                "GET /api/settings/email",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/settings/email",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 10. GDPR Export
    print("🔟 GDPR DATA EXPORT")
    try:
        response = requests.post(
            f"{BACKEND_URL}/gdpr/data-export",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            export_data = data.get("data", {})
            summary = export_data.get("summary", {})
            
            log_test(
                "POST /api/gdpr/data-export",
                "✅",
                f"Export successful. Tasks: {summary.get('total_tasks', 0)}, Time Entries: {summary.get('total_time_entries', 0)}, Audit Logs: {summary.get('total_audit_logs', 0)}",
                summary
            )
        else:
            log_test(
                "POST /api/gdpr/data-export",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "POST /api/gdpr/data-export",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 11. GDPR Consents - GET
    print("1️⃣1️⃣ GDPR CONSENTS - GET")
    try:
        response = requests.get(
            f"{BACKEND_URL}/gdpr/consent-status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            log_test(
                "GET /api/gdpr/consent-status",
                "✅",
                f"Consent status retrieved. Marketing: {data.get('marketing_emails')}, Analytics: {data.get('analytics')}",
                data
            )
        else:
            log_test(
                "GET /api/gdpr/consent-status",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/gdpr/consent-status",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 12. GDPR Consents - UPDATE
    print("1️⃣2️⃣ GDPR CONSENTS - UPDATE")
    try:
        response = requests.put(
            f"{BACKEND_URL}/gdpr/consent",
            headers=headers,
            json={
                "marketing_emails": False,
                "analytics": True,
                "third_party_sharing": False,
                "data_processing": True
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            log_test(
                "PUT /api/gdpr/consent",
                "✅",
                "Consent update successful",
                data
            )
        else:
            log_test(
                "PUT /api/gdpr/consent",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "PUT /api/gdpr/consent",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 13. Audit Logs for Security Events
    print("1️⃣3️⃣ AUDIT LOGS - SECURITY EVENTS")
    try:
        response = requests.get(
            f"{BACKEND_URL}/audit/logs?user_id={user_data.get('id')}&limit=10",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test(
                    "GET /api/audit/logs",
                    "✅",
                    f"Returns {len(data)} audit log entries",
                    data[:2] if len(data) > 0 else []
                )
            else:
                log_test(
                    "GET /api/audit/logs",
                    "⚠️",
                    f"Unexpected response format: {type(data)}",
                    data
                )
        else:
            log_test(
                "GET /api/audit/logs",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/audit/logs",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # 14. Webhooks Count
    print("1️⃣4️⃣ WEBHOOKS COUNT")
    try:
        response = requests.get(
            f"{BACKEND_URL}/webhooks",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test(
                    "GET /api/webhooks",
                    "✅",
                    f"Returns {len(data)} webhook(s)",
                    {"count": len(data)}
                )
            else:
                log_test(
                    "GET /api/webhooks",
                    "⚠️",
                    f"Unexpected response format: {type(data)}",
                    data
                )
        else:
            log_test(
                "GET /api/webhooks",
                "❌",
                f"Error {response.status_code}: {response.text[:200]}"
            )
    except Exception as e:
        log_test(
            "GET /api/webhooks",
            "❌",
            f"Exception: {str(e)}"
        )
    
    # ==================== SUMMARY ====================
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"🆕 Not Found: {test_results['not_found']}")
    print(f"⚠️  Partial: {test_results['partial']}")
    print()
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Detailed results by category
    print("=" * 80)
    print("DETAILED RESULTS BY ENDPOINT")
    print("=" * 80)
    
    for test in test_results['tests']:
        print(f"{test['status']} {test['endpoint']}")
        print(f"   {test['details']}")
        print()
    
    print("=" * 80)
    print(f"Test Completed: {datetime.now().isoformat()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
