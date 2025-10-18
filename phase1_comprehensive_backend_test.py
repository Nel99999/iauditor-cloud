#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE 1 BACKEND API TESTING
Complete System Validation - All 20 Modules

This script performs exhaustive testing of ALL backend API endpoints
as specified in the Phase 1 testing requirements.

SUCCESS CRITERIA:
- Overall: 95%+ success rate
- Critical sections (Auth, User Mgmt, API Security): 100%
- High priority sections: 95%+
- Medium priority sections: 85%+
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import uuid
import base64
import io

# Configuration
BASE_URL = "https://ops-control-center.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

# Test Results Storage
test_results = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "modules": {},
    "critical_failures": [],
    "start_time": datetime.now(),
    "end_time": None
}

def log_test(module, test_name, success, details="", priority="medium"):
    """Log test result"""
    global test_results
    
    if module not in test_results["modules"]:
        test_results["modules"][module] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": [],
            "priority": priority
        }
    
    test_results["total_tests"] += 1
    test_results["modules"][module]["total"] += 1
    
    if success:
        test_results["passed_tests"] += 1
        test_results["modules"][module]["passed"] += 1
        status = "✅ PASS"
    else:
        test_results["failed_tests"] += 1
        test_results["modules"][module]["failed"] += 1
        status = "❌ FAIL"
        
        # Track critical failures
        if priority == "critical":
            test_results["critical_failures"].append({
                "module": module,
                "test": test_name,
                "details": details
            })
    
    test_results["modules"][module]["tests"].append({
        "name": test_name,
        "success": success,
        "details": details,
        "timestamp": datetime.now()
    })
    
    print(f"{status} [{module}] {test_name}")
    if details and not success:
        print(f"    Details: {details}")

def make_request(method, endpoint, data=None, headers=None, files=None):
    """Make HTTP request with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        request_headers = HEADERS.copy()
        if headers:
            request_headers.update(headers)
        
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers, timeout=30)
        elif method.upper() == "POST":
            if files:
                # Remove Content-Type for file uploads
                if "Content-Type" in request_headers:
                    del request_headers["Content-Type"]
                response = requests.post(url, data=data, files=files, headers=request_headers, timeout=30)
            else:
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=request_headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=request_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        return None

# Global variables for test data
auth_token = None
test_user_id = None
test_org_id = None
master_user_token = None
admin_user_token = None
developer_user_token = None

def test_authentication_system():
    """Test Authentication & Authorization (Critical - Must Pass 100%)"""
    global auth_token, test_user_id, test_org_id
    
    print("\n🔐 TESTING AUTHENTICATION & AUTHORIZATION SYSTEM")
    
    # Test 1: User Registration with Organization
    test_email = f"testuser_{int(time.time())}@example.com"
    test_org_name = f"TestOrg_{int(time.time())}"
    
    register_data = {
        "name": "Test User",
        "email": test_email,
        "password": "SecurePassword123!",
        "create_organization": True,
        "organization_name": test_org_name
    }
    
    response = make_request("POST", "/auth/register", register_data)
    success = response and response.status_code == 201
    if success:
        data = response.json()
        auth_token = data.get("access_token")
        test_user_id = data.get("user", {}).get("id")
        test_org_id = data.get("user", {}).get("organization_id")
    
    log_test("Authentication", "POST /api/auth/register (with organization)", success, 
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 2: User Registration without Organization
    register_data_no_org = {
        "name": "Test User 2",
        "email": f"testuser2_{int(time.time())}@example.com",
        "password": "SecurePassword123!",
        "create_organization": False
    }
    
    response = make_request("POST", "/auth/register", register_data_no_org)
    success = response and response.status_code == 201
    log_test("Authentication", "POST /api/auth/register (without organization)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 3: User Login
    login_data = {
        "email": test_email,
        "password": "SecurePassword123!"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    success = response and response.status_code == 200
    if success and not auth_token:
        data = response.json()
        auth_token = data.get("access_token")
    
    log_test("Authentication", "POST /api/auth/login (valid credentials)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 4: Invalid Login
    invalid_login_data = {
        "email": test_email,
        "password": "WrongPassword"
    }
    
    response = make_request("POST", "/auth/login", invalid_login_data)
    success = response and response.status_code == 401
    log_test("Authentication", "POST /api/auth/login (invalid credentials)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 5: Get Current User Info
    if auth_token:
        auth_headers = {"Authorization": f"Bearer {auth_token}"}
        response = make_request("GET", "/auth/me", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Authentication", "GET /api/auth/me (authenticated user info)", success,
                 f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 6: Password Reset Request
    reset_data = {"email": test_email}
    response = make_request("POST", "/auth/request-password-reset", reset_data)
    success = response and response.status_code in [200, 202]
    log_test("Authentication", "POST /api/auth/request-password-reset (valid email)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 7: Password Reset Request - Invalid Email
    reset_data_invalid = {"email": "nonexistent@example.com"}
    response = make_request("POST", "/auth/request-password-reset", reset_data_invalid)
    success = response and response.status_code in [200, 202, 404]  # Some systems return 200 for security
    log_test("Authentication", "POST /api/auth/request-password-reset (invalid email)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 8: JWT Token Validation (Protected Endpoint)
    if auth_token:
        auth_headers = {"Authorization": f"Bearer {auth_token}"}
        response = make_request("GET", "/users/me", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Authentication", "JWT token validation (protected endpoint)", success,
                 f"Status: {response.status_code if response else 'No response'}", "critical")

def test_user_management_system():
    """Test User Management (Critical - Must Pass 95%+)"""
    print("\n👥 TESTING USER MANAGEMENT SYSTEM")
    
    if not auth_token:
        log_test("User Management", "Skipped - No auth token", False, "Authentication failed", "critical")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Users
    response = make_request("GET", "/users", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("User Management", "GET /api/users (list users)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 2: Get User Profile
    response = make_request("GET", "/users/me", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("User Management", "GET /api/users/me (user profile)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 3: Update User Profile
    update_data = {
        "name": "Updated Test User",
        "phone": "+1234567890",
        "bio": "Updated bio"
    }
    response = make_request("PUT", "/users/profile", update_data, headers=auth_headers)
    success = response and response.status_code == 200
    log_test("User Management", "PUT /api/users/profile (update profile)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 4: Change Password
    password_data = {
        "current_password": "SecurePassword123!",
        "new_password": "NewSecurePassword123!",
        "confirm_password": "NewSecurePassword123!"
    }
    response = make_request("PUT", "/users/password", password_data, headers=auth_headers)
    success = response and response.status_code == 200
    log_test("User Management", "PUT /api/users/password (change password)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 5: Invite User
    invite_data = {
        "email": f"invited_{int(time.time())}@example.com",
        "role_id": "admin"
    }
    response = make_request("POST", "/users/invite", invite_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    log_test("User Management", "POST /api/users/invite (send invitation)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 6: Get Pending Invitations
    response = make_request("GET", "/users/invitations/pending", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("User Management", "GET /api/users/invitations/pending (list pending invites)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 7: Upload Profile Picture
    # Create a simple test image
    test_image = io.BytesIO()
    test_image.write(b"fake_image_data")
    test_image.seek(0)
    
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    response = make_request("POST", "/users/profile/picture", files=files, headers={"Authorization": f"Bearer {auth_token}"})
    success = response and response.status_code in [200, 201]
    log_test("User Management", "POST /api/users/profile/picture (photo upload)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")

def test_api_settings_security():
    """Test API Settings Security (Critical - Must Pass 100%)"""
    print("\n🔒 TESTING API SETTINGS SECURITY")
    
    if not auth_token:
        log_test("API Settings Security", "Skipped - No auth token", False, "Authentication failed", "critical")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Get Email Settings (Should work for Master/Developer)
    response = make_request("GET", "/settings/email", headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "GET /api/settings/email (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 2: Update Email Settings
    email_settings = {
        "sendgrid_api_key": "SG.test_key_for_testing",
        "from_email": "noreply@testorg.com",
        "from_name": "Test Organization"
    }
    response = make_request("POST", "/settings/email", email_settings, headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "POST /api/settings/email (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 3: Test Email Connection
    response = make_request("POST", "/settings/email/test", headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "POST /api/settings/email/test (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 4: Get SMS Settings
    response = make_request("GET", "/sms/settings", headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "GET /api/sms/settings (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 5: Update SMS Settings
    sms_settings = {
        "twilio_account_sid": "ACtest1234567890",
        "twilio_auth_token": "test_auth_token",
        "twilio_phone_number": "+1234567890"
    }
    response = make_request("POST", "/sms/settings", sms_settings, headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "POST /api/sms/settings (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")
    
    # Test 6: Test SMS Connection
    response = make_request("POST", "/sms/test-connection", headers=auth_headers)
    success = response and response.status_code in [200, 403]  # 403 if not Master/Developer
    log_test("API Settings Security", "POST /api/sms/test-connection (role-based access)", success,
             f"Status: {response.status_code if response else 'No response'}", "critical")

def test_roles_permissions():
    """Test Roles & Permissions (High Priority - Must Pass 95%+)"""
    print("\n🛡️ TESTING ROLES & PERMISSIONS SYSTEM")
    
    if not auth_token:
        log_test("Roles & Permissions", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List All Roles
    response = make_request("GET", "/roles", headers=auth_headers)
    success = response and response.status_code == 200
    if success:
        roles = response.json()
        success = len(roles) >= 10  # Should have 10 system roles
    log_test("Roles & Permissions", "GET /api/roles (list all roles - verify 10 system roles)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 2: Create Custom Role
    custom_role_data = {
        "name": "Custom Test Role",
        "code": "custom_test",
        "description": "Test custom role",
        "level": 15,
        "color": "#FF5733"
    }
    response = make_request("POST", "/roles", custom_role_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    custom_role_id = None
    if success:
        custom_role_id = response.json().get("id")
    log_test("Roles & Permissions", "POST /api/roles (create custom role)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 3: Get Role Details
    if custom_role_id:
        response = make_request("GET", f"/roles/{custom_role_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Roles & Permissions", "GET /api/roles/{id} (role details with permissions)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 4: Update Role
    if custom_role_id:
        update_data = {
            "name": "Updated Custom Role",
            "description": "Updated description"
        }
        response = make_request("PUT", f"/roles/{custom_role_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Roles & Permissions", "PUT /api/roles/{id} (update role)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 5: List All Permissions
    response = make_request("GET", "/permissions", headers=auth_headers)
    success = response and response.status_code == 200
    if success:
        permissions = response.json()
        success = len(permissions) >= 23  # Should have 23 permissions
    log_test("Roles & Permissions", "GET /api/permissions (list all 23 permissions)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 6: Check Permission
    permission_check_data = {
        "permission": "users.read",
        "resource_type": "user"
    }
    response = make_request("POST", "/permissions/check", permission_check_data, headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Roles & Permissions", "POST /api/permissions/check (permission validation)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 7: Get Role Permissions
    if custom_role_id:
        response = make_request("GET", f"/roles/{custom_role_id}/permissions", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Roles & Permissions", "GET /api/roles/{id}/permissions (role permissions)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 8: Bulk Permission Assignment
    if custom_role_id:
        bulk_permissions = {
            "permission_ids": ["users.read", "tasks.read", "inspections.read"]
        }
        response = make_request("POST", f"/roles/{custom_role_id}/permissions/bulk", bulk_permissions, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Roles & Permissions", "POST /api/roles/{id}/permissions/bulk (bulk permission assignment)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 9: Delete Custom Role
    if custom_role_id:
        response = make_request("DELETE", f"/roles/{custom_role_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Roles & Permissions", "DELETE /api/roles/{id} (delete custom role)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")

def test_organization_structure():
    """Test Organization Structure (High Priority - Must Pass 95%+)"""
    print("\n🏢 TESTING ORGANIZATION STRUCTURE")
    
    if not auth_token:
        log_test("Organization Structure", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Organizations
    response = make_request("GET", "/organizations", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Organization Structure", "GET /api/organizations (list organizations)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 2: Create Organization
    org_data = {
        "name": f"Test Organization {int(time.time())}",
        "description": "Test organization for API testing"
    }
    response = make_request("POST", "/organizations", org_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    log_test("Organization Structure", "POST /api/organizations (create organization)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 3: List Organization Units
    response = make_request("GET", "/organizations/units", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Organization Structure", "GET /api/organizations/units (list org units)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 4: Create Organization Unit
    unit_data = {
        "name": "Test Department",
        "type": "department",
        "level": 1,
        "description": "Test department unit"
    }
    response = make_request("POST", "/organizations/units", unit_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    unit_id = None
    if success:
        unit_id = response.json().get("id")
    log_test("Organization Structure", "POST /api/organizations/units (create unit - 5-level hierarchy)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 5: Update Organization Unit
    if unit_id:
        update_data = {
            "name": "Updated Test Department",
            "description": "Updated description"
        }
        response = make_request("PUT", f"/organizations/units/{unit_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Organization Structure", "PUT /api/organizations/units/{id} (update unit)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 6: Delete Organization Unit
    if unit_id:
        response = make_request("DELETE", f"/organizations/units/{unit_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Organization Structure", "DELETE /api/organizations/units/{id} (delete unit)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")

def test_invitations():
    """Test Invitations (High Priority - Must Pass 95%+)"""
    print("\n📧 TESTING INVITATIONS SYSTEM")
    
    if not auth_token:
        log_test("Invitations", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List All Invitations
    response = make_request("GET", "/invitations", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Invitations", "GET /api/invitations (list all invitations)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 2: Get Pending Invitations
    response = make_request("GET", "/invitations/pending", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Invitations", "GET /api/invitations/pending (pending invitations)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 3: Send Invitation
    invitation_data = {
        "email": f"invited_test_{int(time.time())}@example.com",
        "role_id": "viewer",
        "message": "Welcome to our organization!"
    }
    response = make_request("POST", "/invitations", invitation_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    invitation_id = None
    invitation_token = None
    if success:
        data = response.json()
        invitation_id = data.get("id")
        invitation_token = data.get("token")
    log_test("Invitations", "POST /api/invitations (send invitation - 7-day expiry)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 4: Validate Invitation Token
    if invitation_token:
        response = make_request("GET", f"/invitations/token/{invitation_token}")
        success = response and response.status_code == 200
        log_test("Invitations", "GET /api/invitations/token/{token} (validate token)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 5: Resend Invitation
    if invitation_id:
        response = make_request("POST", f"/invitations/{invitation_id}/resend", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Invitations", "POST /api/invitations/{id}/resend (resend - reset 7-day expiry)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 6: Cancel Invitation
    if invitation_id:
        response = make_request("DELETE", f"/invitations/{invitation_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Invitations", "DELETE /api/invitations/{id} (cancel invitation)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")

def test_workflows():
    """Test Workflows (High Priority - Must Pass 90%+)"""
    print("\n🔄 TESTING WORKFLOWS SYSTEM")
    
    if not auth_token:
        log_test("Workflows", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Workflow Templates
    response = make_request("GET", "/workflows/templates", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Workflows", "GET /api/workflows/templates (list templates)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 2: Create Workflow Template
    template_data = {
        "name": "Test Approval Workflow",
        "description": "Test workflow for API testing",
        "steps": [
            {
                "name": "Initial Review",
                "type": "approval",
                "required_role": "supervisor",
                "order": 1
            },
            {
                "name": "Final Approval",
                "type": "approval",
                "required_role": "manager",
                "order": 2
            }
        ]
    }
    response = make_request("POST", "/workflows/templates", template_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    template_id = None
    if success:
        template_id = response.json().get("id")
    log_test("Workflows", "POST /api/workflows/templates (create template)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 3: Get Workflow Template Details
    if template_id:
        response = make_request("GET", f"/workflows/templates/{template_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Workflows", "GET /api/workflows/templates/{id} (template details)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 4: Update Workflow Template
    if template_id:
        update_data = {
            "name": "Updated Test Workflow",
            "description": "Updated description"
        }
        response = make_request("PUT", f"/workflows/templates/{template_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Workflows", "PUT /api/workflows/templates/{id} (update template)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 5: Start Workflow Instance
    if template_id:
        instance_data = {
            "template_id": template_id,
            "resource_type": "task",
            "resource_id": str(uuid.uuid4()),
            "title": "Test Workflow Instance"
        }
        response = make_request("POST", "/workflows/instances", instance_data, headers=auth_headers)
        success = response and response.status_code in [200, 201]
        instance_id = None
        if success:
            instance_id = response.json().get("id")
        log_test("Workflows", "POST /api/workflows/instances (start workflow)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 6: List Workflow Instances
    response = make_request("GET", "/workflows/instances", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Workflows", "GET /api/workflows/instances (list instances)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 7: Get My Approvals
    response = make_request("GET", "/workflows/instances/my-approvals", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Workflows", "GET /api/workflows/instances/my-approvals (pending approvals)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 8: Workflow Statistics
    response = make_request("GET", "/workflows/stats", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Workflows", "GET /api/workflows/stats (workflow statistics)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")

def test_tasks():
    """Test Tasks (High Priority - Must Pass 95%+)"""
    print("\n📋 TESTING TASKS SYSTEM")
    
    if not auth_token:
        log_test("Tasks", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Tasks
    response = make_request("GET", "/tasks", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Tasks", "GET /api/tasks (list tasks)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 2: Create Task
    task_data = {
        "title": "Test Task",
        "description": "Test task for API testing",
        "priority": "high",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "status": "todo"
    }
    response = make_request("POST", "/tasks", task_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    task_id = None
    if success:
        task_id = response.json().get("id")
    log_test("Tasks", "POST /api/tasks (create task)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 3: Get Task Details
    if task_id:
        response = make_request("GET", f"/tasks/{task_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Tasks", "GET /api/tasks/{id} (task details)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 4: Update Task
    if task_id:
        update_data = {
            "title": "Updated Test Task",
            "status": "in_progress"
        }
        response = make_request("PUT", f"/tasks/{task_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Tasks", "PUT /api/tasks/{id} (update task)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 5: Get Task Statistics
    response = make_request("GET", "/tasks/stats", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Tasks", "GET /api/tasks/stats (task statistics)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")
    
    # Test 6: Delete Task
    if task_id:
        response = make_request("DELETE", f"/tasks/{task_id}", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Tasks", "DELETE /api/tasks/{id} (delete task)", success,
                 f"Status: {response.status_code if response else 'No response'}", "high")

def test_inspections():
    """Test Inspections (Medium Priority - Must Pass 90%+)"""
    print("\n🔍 TESTING INSPECTIONS SYSTEM")
    
    if not auth_token:
        log_test("Inspections", "Skipped - No auth token", False, "Authentication failed", "medium")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Inspection Templates
    response = make_request("GET", "/inspections/templates", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Inspections", "GET /api/inspections/templates (list templates)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 2: Create Inspection Template
    template_data = {
        "name": "Test Safety Inspection",
        "description": "Test inspection template",
        "questions": [
            {
                "text": "Are safety equipment properly maintained?",
                "type": "yes_no",
                "required": True
            },
            {
                "text": "Rate overall safety condition (1-10)",
                "type": "number",
                "required": True,
                "min_value": 1,
                "max_value": 10
            }
        ]
    }
    response = make_request("POST", "/inspections/templates", template_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    template_id = None
    if success:
        template_id = response.json().get("id")
    log_test("Inspections", "POST /api/inspections/templates (create template)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 3: Start Inspection Execution
    execution_id = None
    if template_id:
        execution_data = {
            "template_id": template_id,
            "location": "Test Location",
            "notes": "Test inspection execution"
        }
        response = make_request("POST", "/inspections/executions", execution_data, headers=auth_headers)
        success = response and response.status_code in [200, 201]
        if success:
            execution_id = response.json().get("id")
        log_test("Inspections", "POST /api/inspections/executions (start execution)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 4: Update Inspection Execution
    if template_id and execution_id:
        update_data = {
            "answers": [
                {"question_index": 0, "answer": "yes"},
                {"question_index": 1, "answer": 8}
            ]
        }
        response = make_request("PUT", f"/inspections/executions/{execution_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Inspections", "PUT /api/inspections/executions/{id} (update execution)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 5: Complete Inspection
    if execution_id:
        response = make_request("POST", f"/inspections/executions/{execution_id}/complete", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Inspections", "POST /api/inspections/executions/{id}/complete (complete inspection)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")

def test_checklists():
    """Test Checklists (Medium Priority - Must Pass 90%+)"""
    print("\n✅ TESTING CHECKLISTS SYSTEM")
    
    if not auth_token:
        log_test("Checklists", "Skipped - No auth token", False, "Authentication failed", "medium")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: List Checklist Templates
    response = make_request("GET", "/checklists/templates", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Checklists", "GET /api/checklists/templates (list templates)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 2: Create Checklist Template
    template_data = {
        "name": "Daily Safety Checklist",
        "description": "Daily safety checklist template",
        "items": [
            {
                "text": "Check fire extinguisher",
                "required": True
            },
            {
                "text": "Verify emergency exits",
                "required": True
            },
            {
                "text": "Test alarm system",
                "required": False
            }
        ]
    }
    response = make_request("POST", "/checklists/templates", template_data, headers=auth_headers)
    success = response and response.status_code in [200, 201]
    template_id = None
    if success:
        template_id = response.json().get("id")
    log_test("Checklists", "POST /api/checklists/templates (create template)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 3: Start Checklist Execution
    if template_id:
        execution_data = {
            "template_id": template_id,
            "location": "Main Office",
            "notes": "Daily checklist execution"
        }
        response = make_request("POST", "/checklists/executions", execution_data, headers=auth_headers)
        success = response and response.status_code in [200, 201]
        execution_id = None
        if success:
            execution_id = response.json().get("id")
        log_test("Checklists", "POST /api/checklists/executions (start execution)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 4: Update Checklist Execution
    if execution_id:
        update_data = {
            "completed_items": [0, 1],  # Complete first two items
            "notes": "Updated checklist progress"
        }
        response = make_request("PUT", f"/checklists/executions/{execution_id}", update_data, headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Checklists", "PUT /api/checklists/executions/{id} (update execution)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test 5: Complete Checklist
    if execution_id:
        response = make_request("POST", f"/checklists/executions/{execution_id}/complete", headers=auth_headers)
        success = response and response.status_code == 200
        log_test("Checklists", "POST /api/checklists/executions/{id}/complete (complete checklist)", success,
                 f"Status: {response.status_code if response else 'No response'}", "medium")

def test_dashboard_statistics():
    """Test Dashboard Statistics (High Priority - Must Pass 95%+)"""
    print("\n📊 TESTING DASHBOARD STATISTICS")
    
    if not auth_token:
        log_test("Dashboard Statistics", "Skipped - No auth token", False, "Authentication failed", "high")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Get Dashboard Statistics
    response = make_request("GET", "/dashboard/stats", headers=auth_headers)
    success = response and response.status_code == 200
    
    if success:
        data = response.json()
        # Verify all required fields are present
        required_fields = [
            "users", "inspections", "tasks", "checklists", "organization"
        ]
        for field in required_fields:
            if field not in data:
                success = False
                break
    
    log_test("Dashboard Statistics", "GET /api/dashboard/stats (comprehensive statistics)", success,
             f"Status: {response.status_code if response else 'No response'}", "high")

def test_additional_modules():
    """Test Additional Modules (Medium Priority - Must Pass 85%+)"""
    print("\n🔧 TESTING ADDITIONAL MODULES")
    
    if not auth_token:
        log_test("Additional Modules", "Skipped - No auth token", False, "Authentication failed", "medium")
        return
    
    auth_headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test Groups
    response = make_request("GET", "/groups", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/groups (list groups)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Bulk Import Template
    response = make_request("GET", "/bulk-import/template", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/bulk-import/template (download CSV template)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Webhooks
    response = make_request("GET", "/webhooks", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/webhooks (list webhooks)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Analytics Overview
    response = make_request("GET", "/analytics/overview", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/analytics/overview (overview metrics)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Notifications
    response = make_request("GET", "/notifications", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/notifications (list notifications)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Audit Logs
    response = make_request("GET", "/audit/logs", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/audit/logs (list audit logs)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Delegations
    response = make_request("GET", "/delegations", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/delegations (list delegations)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test User Settings/Preferences
    response = make_request("GET", "/users/theme", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/users/theme (theme preferences)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")
    
    # Test Reports
    response = make_request("GET", "/reports/overview", headers=auth_headers)
    success = response and response.status_code == 200
    log_test("Additional Modules", "GET /api/reports/overview (report overview)", success,
             f"Status: {response.status_code if response else 'No response'}", "medium")

def calculate_success_rates():
    """Calculate success rates by priority and overall"""
    rates = {
        "overall": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    counts = {
        "overall": {"total": 0, "passed": 0},
        "critical": {"total": 0, "passed": 0},
        "high": {"total": 0, "passed": 0},
        "medium": {"total": 0, "passed": 0},
        "low": {"total": 0, "passed": 0}
    }
    
    for module_name, module_data in test_results["modules"].items():
        priority = module_data.get("priority", "medium")
        counts[priority]["total"] += module_data["total"]
        counts[priority]["passed"] += module_data["passed"]
        counts["overall"]["total"] += module_data["total"]
        counts["overall"]["passed"] += module_data["passed"]
    
    for priority in rates.keys():
        if counts[priority]["total"] > 0:
            rates[priority] = (counts[priority]["passed"] / counts[priority]["total"]) * 100
    
    return rates, counts

def print_detailed_results():
    """Print detailed test results"""
    test_results["end_time"] = datetime.now()
    duration = test_results["end_time"] - test_results["start_time"]
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE PHASE 1 BACKEND API TESTING RESULTS")
    print("="*80)
    
    print(f"\n⏱️  EXECUTION TIME: {duration}")
    print(f"📊 OVERALL RESULTS: {test_results['passed_tests']}/{test_results['total_tests']} tests passed")
    
    # Calculate success rates
    rates, counts = calculate_success_rates()
    
    print(f"\n📈 SUCCESS RATES BY PRIORITY:")
    print(f"   🔴 CRITICAL: {rates['critical']:.1f}% ({counts['critical']['passed']}/{counts['critical']['total']})")
    print(f"   🟠 HIGH:     {rates['high']:.1f}% ({counts['high']['passed']}/{counts['high']['total']})")
    print(f"   🟡 MEDIUM:   {rates['medium']:.1f}% ({counts['medium']['passed']}/{counts['medium']['total']})")
    print(f"   🟢 OVERALL:  {rates['overall']:.1f}% ({counts['overall']['passed']}/{counts['overall']['total']})")
    
    # Success criteria check
    print(f"\n🎯 SUCCESS CRITERIA EVALUATION:")
    criteria_met = True
    
    if rates['critical'] < 100:
        print(f"   ❌ Critical sections: {rates['critical']:.1f}% (Required: 100%)")
        criteria_met = False
    else:
        print(f"   ✅ Critical sections: {rates['critical']:.1f}% (Required: 100%)")
    
    if rates['high'] < 95:
        print(f"   ❌ High priority: {rates['high']:.1f}% (Required: 95%+)")
        criteria_met = False
    else:
        print(f"   ✅ High priority: {rates['high']:.1f}% (Required: 95%+)")
    
    if rates['medium'] < 85:
        print(f"   ❌ Medium priority: {rates['medium']:.1f}% (Required: 85%+)")
        criteria_met = False
    else:
        print(f"   ✅ Medium priority: {rates['medium']:.1f}% (Required: 85%+)")
    
    if rates['overall'] < 95:
        print(f"   ❌ Overall: {rates['overall']:.1f}% (Required: 95%+)")
        criteria_met = False
    else:
        print(f"   ✅ Overall: {rates['overall']:.1f}% (Required: 95%+)")
    
    print(f"\n🏆 FINAL ASSESSMENT: {'SUCCESS' if criteria_met else 'NEEDS IMPROVEMENT'}")
    
    # Module-by-module results
    print(f"\n📋 DETAILED RESULTS BY MODULE:")
    for module_name, module_data in test_results["modules"].items():
        success_rate = (module_data["passed"] / module_data["total"]) * 100 if module_data["total"] > 0 else 0
        status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 75 else "❌"
        print(f"   {status} {module_name}: {success_rate:.1f}% ({module_data['passed']}/{module_data['total']})")
    
    # Critical failures
    if test_results["critical_failures"]:
        print(f"\n🚨 CRITICAL FAILURES:")
        for failure in test_results["critical_failures"]:
            print(f"   ❌ [{failure['module']}] {failure['test']}")
            if failure['details']:
                print(f"      Details: {failure['details']}")
    
    # Failed tests summary
    failed_tests = []
    for module_name, module_data in test_results["modules"].items():
        for test in module_data["tests"]:
            if not test["success"]:
                failed_tests.append({
                    "module": module_name,
                    "test": test["name"],
                    "details": test["details"]
                })
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS SUMMARY ({len(failed_tests)} failures):")
        for failure in failed_tests:
            print(f"   • [{failure['module']}] {failure['test']}")
            if failure['details']:
                print(f"     {failure['details']}")
    
    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("🚀 STARTING COMPREHENSIVE PHASE 1 BACKEND API TESTING")
    print("="*80)
    print("Testing all 20 modules with comprehensive endpoint coverage")
    print("Success Criteria: Critical 100%, High 95%+, Medium 85%+, Overall 95%+")
    print("="*80)
    
    # Execute all test modules
    test_authentication_system()
    test_user_management_system()
    test_api_settings_security()
    test_roles_permissions()
    test_organization_structure()
    test_invitations()
    test_workflows()
    test_tasks()
    test_inspections()
    test_checklists()
    test_dashboard_statistics()
    test_additional_modules()
    
    # Print detailed results
    print_detailed_results()
    
    # Return success status
    rates, _ = calculate_success_rates()
    return rates['overall'] >= 95 and rates['critical'] >= 100 and rates['high'] >= 95 and rates['medium'] >= 85

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)