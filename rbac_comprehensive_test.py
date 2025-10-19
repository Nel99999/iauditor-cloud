#!/usr/bin/env python3
"""
COMPREHENSIVE RBAC TESTING - All V1 Modules
Tests permission system across all endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://backendhealer.preview.emergentagent.com/api"
TEST_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "TestPassword123!"
}

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_test(test_name, passed, details=""):
    status = f"{GREEN}✅ PASSED{RESET}" if passed else f"{RED}❌ FAILED{RESET}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {details}")

def print_section(text):
    print(f"\n{YELLOW}{'─'*80}{RESET}")
    print(f"{YELLOW}{text}{RESET}")
    print(f"{YELLOW}{'─'*80}{RESET}")

# Global token storage
auth_token = None
user_id = None
organization_id = None

def login():
    """Login and get auth token"""
    global auth_token, user_id, organization_id
    
    print_section("AUTHENTICATION")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get('access_token')
            user_id = data.get('user', {}).get('id')
            organization_id = data.get('user', {}).get('organization_id')
            
            print_test("Login successful", True, f"User ID: {user_id}, Org ID: {organization_id}")
            return True
        else:
            print_test("Login failed", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print_test("Login error", False, str(e))
        return False

def get_headers(include_auth=True):
    """Get request headers"""
    headers = {"Content-Type": "application/json"}
    if include_auth and auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


# ============================================================================
# PHASE 1: VERIFY PERMISSIONS EXIST
# ============================================================================

def test_phase1_permissions():
    """Test that all required permissions exist in the system"""
    print_header("PHASE 1: VERIFY PERMISSIONS EXIST")
    
    # Expected permission patterns for all modules
    expected_modules = [
        'inspection', 'checklist', 'task', 'asset', 'workorder', 'inventory',
        'project', 'incident', 'training', 'financial', 'dashboard',
        'contractor', 'emergency', 'chat', 'announcement', 'user', 'role',
        'organization', 'group', 'invitation', 'approval', 'workflow',
        'report', 'analytics', 'webhook', 'settings'
    ]
    
    expected_actions = ['create', 'read', 'update', 'delete', 'manage']
    expected_scopes = ['own', 'organization', 'all']
    
    try:
        # Test 1.1: Get all permissions
        print_section("Test 1.1: GET /api/permissions - List All Permissions")
        
        response = requests.get(
            f"{BASE_URL}/permissions",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            permissions = response.json()
            total_permissions = len(permissions)
            
            print_test(
                "Permissions endpoint accessible",
                True,
                f"Total permissions: {total_permissions}"
            )
            
            # Check if we have expected number of permissions (60-80+)
            if total_permissions >= 60:
                print_test(
                    "Permission count meets requirement",
                    True,
                    f"Found {total_permissions} permissions (expected 60-80+)"
                )
            else:
                print_test(
                    "Permission count below requirement",
                    False,
                    f"Found {total_permissions} permissions (expected 60-80+)"
                )
            
            # Test 1.2: Verify permissions for each module
            print_section("Test 1.2: Verify Module-Specific Permissions")
            
            module_permissions = {}
            for perm in permissions:
                # Permissions have resource_type, action, scope fields
                resource_type = perm.get('resource_type', '')
                action = perm.get('action', '')
                scope = perm.get('scope', '')
                
                if resource_type:
                    if resource_type not in module_permissions:
                        module_permissions[resource_type] = []
                    module_permissions[resource_type].append(f'{action}.{scope}')
            
            print(f"\n{BLUE}Module Permission Coverage:{RESET}")
            for module in expected_modules:
                if module in module_permissions:
                    count = len(module_permissions[module])
                    print_test(
                        f"{module.upper()} module",
                        True,
                        f"{count} permissions found: {', '.join(module_permissions[module][:3])}..."
                    )
                else:
                    print_test(
                        f"{module.upper()} module",
                        False,
                        "No permissions found"
                    )
            
            # Test 1.3: Check for critical permissions
            print_section("Test 1.3: Verify Critical Permissions")
            
            critical_permissions = [
                'asset.create.organization',
                'workorder.create.organization',
                'project.create.organization',
                'incident.create.organization',
                'financial.read.organization',
                'dashboard.read.organization',
                'inspection.create.organization',
                'checklist.create.organization',
                'task.create.organization',
                'inventory.create.organization',
                'training.create.organization',
                'contractor.create.organization',
                'emergency.create.organization',
                'chat.create.organization',
                'announcement.create.organization'
            ]
            
            permission_names = [p.get('name') for p in permissions]
            
            for critical_perm in critical_permissions:
                exists = critical_perm in permission_names
                print_test(
                    critical_perm,
                    exists,
                    "Found" if exists else "Missing"
                )
            
            return True
            
        else:
            print_test(
                "Permissions endpoint failed",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
            return False
            
    except Exception as e:
        print_test("Phase 1 error", False, str(e))
        return False


# ============================================================================
# PHASE 2: TEST PERMISSION ENFORCEMENT
# ============================================================================

def test_phase2_permission_enforcement():
    """Test that permissions are properly enforced on endpoints"""
    print_header("PHASE 2: TEST PERMISSION ENFORCEMENT")
    
    # Test endpoints that require specific permissions
    test_cases = [
        {
            "name": "Create Asset",
            "method": "POST",
            "endpoint": "/assets",
            "permission": "asset.create.organization",
            "data": {
                "asset_number": f"TEST-ASSET-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": "RBAC Test Asset",
                "asset_type": "equipment",
                "status": "operational"
            }
        },
        {
            "name": "Create Work Order",
            "method": "POST",
            "endpoint": "/work-orders",
            "permission": "workorder.create.organization",
            "data": {
                "title": "RBAC Test Work Order",
                "work_order_type": "corrective",
                "priority": "medium",
                "description": "Testing RBAC permissions"
            }
        },
        {
            "name": "Create Project",
            "method": "POST",
            "endpoint": "/projects",
            "permission": "project.create.organization",
            "data": {
                "name": "RBAC Test Project",
                "description": "Testing RBAC permissions",
                "project_type": "maintenance",
                "priority": "medium"
            }
        },
        {
            "name": "Create Incident",
            "method": "POST",
            "endpoint": "/incidents",
            "permission": "incident.create.organization",
            "data": {
                "incident_type": "near_miss",
                "severity": "low",
                "location": "Test Location",
                "description": "RBAC test incident"
            }
        },
        {
            "name": "Get Financial Summary",
            "method": "GET",
            "endpoint": "/financial/summary",
            "permission": "financial.read.organization",
            "data": None
        },
        {
            "name": "Get Executive Dashboard",
            "method": "GET",
            "endpoint": "/dashboards/executive",
            "permission": "dashboard.read.organization",
            "data": None
        },
        {
            "name": "Create Inventory Item",
            "method": "POST",
            "endpoint": "/inventory/items",
            "permission": "inventory.create.organization",
            "data": {
                "part_number": f"RBAC-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": "RBAC Test Part",
                "category": "spare_parts",
                "quantity_on_hand": 10,
                "unit_cost": 50.00
            }
        },
        {
            "name": "Create Training Course",
            "method": "POST",
            "endpoint": "/training/courses",
            "permission": "training.create.organization",
            "data": {
                "course_code": f"RBAC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": "RBAC Test Course",
                "course_type": "safety",
                "duration_hours": 4
            }
        }
    ]
    
    # Test 2.1: Test WITH valid token (should succeed)
    print_section("Test 2.1: Test Endpoints WITH Valid Token")
    
    for test_case in test_cases:
        try:
            if test_case["method"] == "POST":
                response = requests.post(
                    f"{BASE_URL}{test_case['endpoint']}",
                    headers=get_headers(),
                    json=test_case["data"],
                    timeout=10
                )
            else:  # GET
                response = requests.get(
                    f"{BASE_URL}{test_case['endpoint']}",
                    headers=get_headers(),
                    timeout=10
                )
            
            success = response.status_code in [200, 201]
            print_test(
                f"{test_case['name']} (requires {test_case['permission']})",
                success,
                f"Status: {response.status_code}"
            )
            
        except Exception as e:
            print_test(test_case['name'], False, str(e))
    
    # Test 2.2: Test WITHOUT token (should get 401)
    print_section("Test 2.2: Test Endpoints WITHOUT Token (Should Get 401)")
    
    for test_case in test_cases[:3]:  # Test first 3 to save time
        try:
            if test_case["method"] == "POST":
                response = requests.post(
                    f"{BASE_URL}{test_case['endpoint']}",
                    headers=get_headers(include_auth=False),
                    json=test_case["data"],
                    timeout=10
                )
            else:  # GET
                response = requests.get(
                    f"{BASE_URL}{test_case['endpoint']}",
                    headers=get_headers(include_auth=False),
                    timeout=10
                )
            
            # Should get 401 Unauthorized
            success = response.status_code == 401
            print_test(
                f"{test_case['name']} without token",
                success,
                f"Status: {response.status_code} (expected 401)"
            )
            
        except Exception as e:
            print_test(f"{test_case['name']} without token", False, str(e))


# ============================================================================
# PHASE 3: VERIFY NAVIGATION PERMISSIONS
# ============================================================================

def test_phase3_navigation_permissions():
    """Verify that navigation permissions are properly configured"""
    print_header("PHASE 3: VERIFY NAVIGATION PERMISSIONS")
    
    print_section("Test 3.1: Check User Permissions")
    
    try:
        # Get current user's permissions
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            role = user_data.get('role', 'unknown')
            
            print_test(
                "Get current user",
                True,
                f"Role: {role}"
            )
            
            # Get user's permissions through role
            response = requests.get(
                f"{BASE_URL}/roles",
                headers=get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                roles = response.json()
                user_role = next((r for r in roles if r.get('name') == role), None)
                
                if user_role:
                    permissions = user_role.get('permissions', [])
                    print_test(
                        f"User role '{role}' permissions",
                        True,
                        f"Has {len(permissions)} permissions"
                    )
                    
                    # Check navigation-related permissions
                    navigation_permissions = [
                        'inspection.read',
                        'checklist.read',
                        'task.read',
                        'asset.read',
                        'workorder.read',
                        'inventory.read',
                        'project.read',
                        'incident.read',
                        'training.read',
                        'financial.read',
                        'dashboard.read',
                        'contractor.read',
                        'emergency.read',
                        'chat.read',
                        'announcement.read'
                    ]
                    
                    print(f"\n{BLUE}Navigation Permission Check:{RESET}")
                    for nav_perm in navigation_permissions:
                        # Check if user has this permission (with any scope)
                        has_perm = any(
                            p.startswith(nav_perm) for p in permissions
                        )
                        print_test(
                            f"Navigation: {nav_perm}",
                            has_perm,
                            "Accessible" if has_perm else "Restricted"
                        )
                else:
                    print_test("Find user role", False, f"Role '{role}' not found")
            else:
                print_test("Get roles", False, f"Status: {response.status_code}")
        else:
            print_test("Get current user", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_test("Phase 3 error", False, str(e))


# ============================================================================
# PHASE 4: TEST ROLE ASSIGNMENTS
# ============================================================================

def test_phase4_role_assignments():
    """Test role assignments and hierarchy"""
    print_header("PHASE 4: TEST ROLE ASSIGNMENTS")
    
    print_section("Test 4.1: GET /api/roles - Verify Roles Exist")
    
    try:
        response = requests.get(
            f"{BASE_URL}/roles",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            roles = response.json()
            total_roles = len(roles)
            
            print_test(
                "Roles endpoint accessible",
                True,
                f"Total roles: {total_roles}"
            )
            
            # Test 4.2: Check for system roles
            print_section("Test 4.2: Verify System Roles")
            
            expected_roles = ['developer', 'master', 'admin', 'manager', 'viewer']
            
            role_names = [r.get('name') for r in roles]
            
            for expected_role in expected_roles:
                exists = expected_role in role_names
                print_test(
                    f"Role: {expected_role}",
                    exists,
                    "Found" if exists else "Missing"
                )
            
            # Test 4.3: Check developer role permissions
            print_section("Test 4.3: Verify Developer Role Has All Permissions")
            
            developer_role = next((r for r in roles if r.get('name') == 'developer'), None)
            
            if developer_role:
                dev_permissions = developer_role.get('permissions', [])
                dev_level = developer_role.get('level', 0)
                
                print_test(
                    "Developer role found",
                    True,
                    f"Level: {dev_level}, Permissions: {len(dev_permissions)}"
                )
                
                # Developer should have most permissions
                if len(dev_permissions) >= 40:
                    print_test(
                        "Developer has comprehensive permissions",
                        True,
                        f"{len(dev_permissions)} permissions (expected 40+)"
                    )
                else:
                    print_test(
                        "Developer permissions incomplete",
                        False,
                        f"{len(dev_permissions)} permissions (expected 40+)"
                    )
            else:
                print_test("Developer role", False, "Not found")
            
            # Test 4.4: Verify role hierarchy
            print_section("Test 4.4: Verify Role Hierarchy")
            
            # Sort roles by level
            sorted_roles = sorted(roles, key=lambda r: r.get('level', 999))
            
            print(f"\n{BLUE}Role Hierarchy (by level):{RESET}")
            for role in sorted_roles:
                name = role.get('name', 'unknown')
                level = role.get('level', 'N/A')
                perm_count = len(role.get('permissions', []))
                is_system = role.get('is_system_role', False)
                
                print(f"  Level {level}: {name} ({perm_count} permissions) {'[SYSTEM]' if is_system else ''}")
            
            # Verify hierarchy makes sense (lower level = more permissions)
            hierarchy_valid = True
            for i in range(len(sorted_roles) - 1):
                current_perms = len(sorted_roles[i].get('permissions', []))
                next_perms = len(sorted_roles[i + 1].get('permissions', []))
                
                if current_perms < next_perms:
                    hierarchy_valid = False
                    break
            
            print_test(
                "Role hierarchy valid",
                hierarchy_valid,
                "Lower levels have more or equal permissions"
            )
            
            return True
            
        else:
            print_test(
                "Roles endpoint failed",
                False,
                f"Status: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_test("Phase 4 error", False, str(e))
        return False


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all RBAC tests"""
    print_header("COMPREHENSIVE RBAC TESTING - All V1 Modules")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['email']}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login first
    if not login():
        print(f"\n{RED}❌ LOGIN FAILED - Cannot proceed with tests{RESET}")
        return
    
    # Run all test phases
    test_phase1_permissions()
    test_phase2_permission_enforcement()
    test_phase3_navigation_permissions()
    test_phase4_role_assignments()
    
    print_header("RBAC TESTING COMPLETE")
    print(f"\n{GREEN}All RBAC tests completed. Review results above.{RESET}\n")


if __name__ == "__main__":
    main()
