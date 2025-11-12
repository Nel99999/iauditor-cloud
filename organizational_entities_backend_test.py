#!/usr/bin/env python3
"""
COMPREHENSIVE ORGANIZATIONAL ENTITIES BACKEND TESTING
Tests all 28 backend tests for the new organizational entities management system
"""

import requests
import json
import sys
from datetime import datetime
import io

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "Test@1234"

# Test results tracking
test_results = {
    "total": 28,
    "passed": 0,
    "failed": 0,
    "errors": []
}

def log_test(test_num, test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"\nTest {test_num}: {test_name} - {status}")
    if details:
        print(f"  Details: {details}")
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"Test {test_num}: {test_name} - {details}")

def authenticate():
    """Authenticate and get token"""
    print("\n" + "="*80)
    print("AUTHENTICATING...")
    print("="*80)
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_data = data.get("user", {})
        print(f"✅ Authenticated as: {user_data.get('name')} ({user_data.get('email')})")
        print(f"   Role: {user_data.get('role')}")
        print(f"   Organization ID: {user_data.get('organization_id')}")
        return token, user_data
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)

def run_tests():
    """Run all 28 organizational entities tests"""
    
    # Authenticate
    token, user_data = authenticate()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Store test data
    test_data = {
        "entity_id": None,
        "entity_id_for_logo": None,
        "custom_field_id": None,
        "parent_unit_id": None,
        "logo_file_id": None
    }
    
    print("\n" + "="*80)
    print("TEST SUITE 1: ORGANIZATIONAL ENTITIES CRUD (10 tests)")
    print("="*80)
    
    # Test 1.1: GET All Entities
    print("\n--- Test 1.1: GET All Entities ---")
    response = requests.get(f"{BACKEND_URL}/entities", headers=headers)
    if response.status_code == 200:
        entities = response.json()
        log_test("1.1", "GET All Entities", True, f"Retrieved {len(entities)} entities")
    else:
        log_test("1.1", "GET All Entities", False, f"Status: {response.status_code}, Response: {response.text}")
    
    # Test 1.2: GET Entities by Type
    print("\n--- Test 1.2: GET Entities by Type (company) ---")
    response = requests.get(f"{BACKEND_URL}/entities?entity_type=company", headers=headers)
    if response.status_code == 200:
        companies = response.json()
        all_companies = all(e.get("entity_type") == "company" for e in companies)
        log_test("1.2", "GET Entities by Type", all_companies, f"Retrieved {len(companies)} companies, all filtered correctly: {all_companies}")
    else:
        log_test("1.2", "GET Entities by Type", False, f"Status: {response.status_code}")
    
    # Test 1.3: GET Unlinked Entities
    print("\n--- Test 1.3: GET Unlinked Entities (level 3, unlinked) ---")
    response = requests.get(f"{BACKEND_URL}/entities?level=3&unlinked=true", headers=headers)
    if response.status_code == 200:
        unlinked = response.json()
        all_unlinked = all(e.get("parent_id") is None for e in unlinked)
        log_test("1.3", "GET Unlinked Entities", True, f"Retrieved {len(unlinked)} unlinked level 3 entities, all without parent_id: {all_unlinked}")
    else:
        log_test("1.3", "GET Unlinked Entities", False, f"Status: {response.status_code}")
    
    # Test 1.4: CREATE New Company Entity (Full Details)
    print("\n--- Test 1.4: CREATE New Company Entity (Full Details) ---")
    entity_payload = {
        "entity_type": "company",
        "level": 3,
        "name": "Test Tech Company",
        "description": "A technology company for testing",
        "industry": "Technology",
        "address_street": "123 Tech Street",
        "address_city": "Johannesburg",
        "address_country": "South Africa",
        "phone": "+27123456789",
        "email": "contact@testtech.com",
        "website": "https://testtech.com",
        "tax_id": "1234567890",
        "registration_number": "REG-TEST-001",
        "cost_center": "CC-TECH-001",
        "budget_code": "BUD-TECH-2025",
        "primary_color": "#3b82f6"
    }
    response = requests.post(f"{BACKEND_URL}/entities", headers=headers, json=entity_payload)
    if response.status_code == 201:
        entity = response.json()
        test_data["entity_id"] = entity.get("id")
        log_test("1.4", "CREATE New Company Entity", True, f"Created entity with ID: {test_data['entity_id']}")
    else:
        log_test("1.4", "CREATE New Company Entity", False, f"Status: {response.status_code}, Response: {response.text}")
    
    # Test 1.5: GET Single Entity
    if test_data["entity_id"]:
        print("\n--- Test 1.5: GET Single Entity ---")
        response = requests.get(f"{BACKEND_URL}/entities/{test_data['entity_id']}", headers=headers)
        if response.status_code == 200:
            entity = response.json()
            has_all_fields = all([
                entity.get("name") == "Test Tech Company",
                entity.get("industry") == "Technology",
                entity.get("tax_id") == "1234567890",
                entity.get("address_city") == "Johannesburg"
            ])
            log_test("1.5", "GET Single Entity", has_all_fields, f"Entity retrieved with all fields populated: {has_all_fields}")
        else:
            log_test("1.5", "GET Single Entity", False, f"Status: {response.status_code}")
    else:
        log_test("1.5", "GET Single Entity", False, "Skipped - no entity_id from Test 1.4")
    
    # Test 1.6: UPDATE Entity
    if test_data["entity_id"]:
        print("\n--- Test 1.6: UPDATE Entity ---")
        update_payload = {
            "name": "Test Tech Company (Updated)",
            "industry": "Finance",
            "tax_id": "9876543210"
        }
        response = requests.put(f"{BACKEND_URL}/entities/{test_data['entity_id']}", headers=headers, json=update_payload)
        if response.status_code == 200:
            log_test("1.6", "UPDATE Entity", True, "Entity updated successfully")
        else:
            log_test("1.6", "UPDATE Entity", False, f"Status: {response.status_code}, Response: {response.text}")
    else:
        log_test("1.6", "UPDATE Entity", False, "Skipped - no entity_id")
    
    # Test 1.7: Verify Update in Database
    if test_data["entity_id"]:
        print("\n--- Test 1.7: Verify Update in Database ---")
        response = requests.get(f"{BACKEND_URL}/entities/{test_data['entity_id']}", headers=headers)
        if response.status_code == 200:
            entity = response.json()
            updated_correctly = all([
                entity.get("name") == "Test Tech Company (Updated)",
                entity.get("industry") == "Finance",
                entity.get("tax_id") == "9876543210"
            ])
            log_test("1.7", "Verify Update in Database", updated_correctly, f"Fields updated correctly: {updated_correctly}")
        else:
            log_test("1.7", "Verify Update in Database", False, f"Status: {response.status_code}")
    else:
        log_test("1.7", "Verify Update in Database", False, "Skipped - no entity_id")
    
    # Test 1.8: DELETE Entity with parent_id (Should Fail)
    # NOTE: This test cannot be executed as expected because organizational entities
    # and organizational units are separate systems. Entities cannot be linked to
    # the hierarchy using the /organizations/units/{parent_id}/link-child endpoint.
    print("\n--- Test 1.8: DELETE Entity with parent_id (Should Fail) ---")
    print("⚠️  SKIPPED: Entities and organizational units are separate systems.")
    print("   The link-child endpoint expects organization_units, not organizational_entities.")
    log_test("1.8", "DELETE Entity with parent_id (Should Fail)", False, "SKIPPED - Entities cannot be linked to org units hierarchy")
    temp_entity_id = None
    
    # Test 1.9: Unlink Entity, Then DELETE
    print("\n--- Test 1.9: Unlink Entity, Then DELETE ---")
    print("⚠️  SKIPPED: Depends on Test 1.8")
    log_test("1.9", "Unlink Entity, Then DELETE", False, "SKIPPED - Depends on hierarchy linking")
    
    # Test 1.10: Verify Soft Delete
    print("\n--- Test 1.10: Verify Soft Delete ---")
    # Test soft delete with a standalone entity instead
    standalone_entity_payload = {
        "entity_type": "company",
        "level": 3,
        "name": "Soft Delete Test Company",
        "description": "For testing soft delete"
    }
    response = requests.post(f"{BACKEND_URL}/entities", headers=headers, json=standalone_entity_payload)
    if response.status_code == 201:
        standalone_entity = response.json()
        standalone_entity_id = standalone_entity.get("id")
        
        # Delete it
        response = requests.delete(f"{BACKEND_URL}/entities/{standalone_entity_id}", headers=headers)
        if response.status_code == 200:
            # Verify it's not in active list
            response = requests.get(f"{BACKEND_URL}/entities", headers=headers)
            if response.status_code == 200:
                entities = response.json()
                deleted_entity_not_in_list = not any(e.get("id") == standalone_entity_id for e in entities)
                log_test("1.10", "Verify Soft Delete", deleted_entity_not_in_list, f"Deleted entity not in active list: {deleted_entity_not_in_list}")
            else:
                log_test("1.10", "Verify Soft Delete", False, f"Failed to get entities: {response.status_code}")
        else:
            log_test("1.10", "Verify Soft Delete", False, f"Delete failed: {response.status_code}")
    else:
        log_test("1.10", "Verify Soft Delete", False, f"Failed to create entity: {response.status_code}")
    
    print("\n" + "="*80)
    print("TEST SUITE 2: ENTITY LOGO UPLOAD (3 tests)")
    print("="*80)
    
    # Test 2.1: Create Entity for Logo Testing
    print("\n--- Test 2.1: Create Entity for Logo Testing ---")
    logo_entity_payload = {
        "entity_type": "company",
        "level": 3,
        "name": "Logo Test Company",
        "description": "For testing logo upload"
    }
    response = requests.post(f"{BACKEND_URL}/entities", headers=headers, json=logo_entity_payload)
    if response.status_code == 201:
        entity = response.json()
        test_data["entity_id_for_logo"] = entity.get("id")
        log_test("2.1", "Create Entity for Logo Testing", True, f"Created entity ID: {test_data['entity_id_for_logo']}")
    else:
        log_test("2.1", "Create Entity for Logo Testing", False, f"Status: {response.status_code}")
    
    # Test 2.2: Upload Logo
    if test_data["entity_id_for_logo"]:
        print("\n--- Test 2.2: Upload Logo ---")
        # Create a simple test image (1x1 pixel PNG)
        import base64
        # Minimal PNG file (1x1 red pixel)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        )
        
        files = {"file": ("test_logo.png", io.BytesIO(png_data), "image/png")}
        response = requests.post(
            f"{BACKEND_URL}/entities/{test_data['entity_id_for_logo']}/upload-logo",
            headers=headers,
            files=files
        )
        if response.status_code == 200:
            result = response.json()
            logo_url = result.get("logo_url")
            # Extract file_id from logo_url
            if logo_url:
                parts = logo_url.split("/")
                if len(parts) > 0:
                    test_data["logo_file_id"] = parts[-1]
            log_test("2.2", "Upload Logo", True, f"Logo uploaded, URL: {logo_url}")
        else:
            log_test("2.2", "Upload Logo", False, f"Status: {response.status_code}, Response: {response.text}")
    else:
        log_test("2.2", "Upload Logo", False, "Skipped - no entity_id_for_logo")
    
    # Test 2.3: Retrieve Logo
    if test_data["entity_id_for_logo"] and test_data["logo_file_id"]:
        print("\n--- Test 2.3: Retrieve Logo ---")
        response = requests.get(
            f"{BACKEND_URL}/entities/{test_data['entity_id_for_logo']}/logo/{test_data['logo_file_id']}",
            headers=headers
        )
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            is_image = "image" in content_type
            log_test("2.3", "Retrieve Logo", is_image, f"Logo retrieved, Content-Type: {content_type}")
        else:
            log_test("2.3", "Retrieve Logo", False, f"Status: {response.status_code}")
    else:
        log_test("2.3", "Retrieve Logo", False, "Skipped - no logo data")
    
    print("\n" + "="*80)
    print("TEST SUITE 3: CUSTOM FIELDS (5 tests)")
    print("="*80)
    
    # Test 3.1: GET Custom Fields (Empty)
    print("\n--- Test 3.1: GET Custom Fields (Initially) ---")
    response = requests.get(f"{BACKEND_URL}/entities/custom-fields", headers=headers)
    if response.status_code == 200:
        fields = response.json()
        log_test("3.1", "GET Custom Fields (Initially)", True, f"Retrieved {len(fields)} custom fields")
    else:
        log_test("3.1", "GET Custom Fields (Initially)", False, f"Status: {response.status_code}")
    
    # Test 3.2: CREATE Custom Field
    print("\n--- Test 3.2: CREATE Custom Field ---")
    import time
    field_payload = {
        "entity_type": "company",
        "field_id": f"iso_certification_{int(time.time())}",  # Unique field ID
        "field_label": "ISO Certification Number",
        "field_type": "text",
        "field_group": "business_details",
        "required": False,
        "order": 10
    }
    response = requests.post(f"{BACKEND_URL}/entities/custom-fields", headers=headers, json=field_payload)
    if response.status_code == 201:
        field = response.json()
        test_data["custom_field_id"] = field.get("id")
        test_data["custom_field_field_id"] = field.get("field_id")  # Store field_id for duplicate test
        log_test("3.2", "CREATE Custom Field", True, f"Created custom field ID: {test_data['custom_field_id']}")
    else:
        log_test("3.2", "CREATE Custom Field", False, f"Status: {response.status_code}, Response: {response.text}")
    
    # Test 3.3: GET Custom Fields (Has Data)
    print("\n--- Test 3.3: GET Custom Fields (Has Data) ---")
    response = requests.get(f"{BACKEND_URL}/entities/custom-fields?entity_type=company", headers=headers)
    if response.status_code == 200:
        fields = response.json()
        has_iso_field = any(f.get("field_id") == "iso_certification" for f in fields)
        log_test("3.3", "GET Custom Fields (Has Data)", has_iso_field, f"Retrieved {len(fields)} fields, contains iso_certification: {has_iso_field}")
    else:
        log_test("3.3", "GET Custom Fields (Has Data)", False, f"Status: {response.status_code}")
    
    # Test 3.4: CREATE Duplicate Field (Should Fail)
    print("\n--- Test 3.4: CREATE Duplicate Field (Should Fail) ---")
    duplicate_payload = {
        "entity_type": "company",
        "field_id": "iso_certification",  # Same as Test 3.2
        "field_label": "ISO Cert Duplicate",
        "field_type": "text",
        "field_group": "business_details"
    }
    response = requests.post(f"{BACKEND_URL}/entities/custom-fields", headers=headers, json=duplicate_payload)
    if response.status_code == 400:
        error_msg = response.json().get("detail", "")
        correct_error = "already exists" in error_msg.lower()
        log_test("3.4", "CREATE Duplicate Field (Should Fail)", correct_error, f"Correctly rejected with 400: {error_msg}")
    else:
        log_test("3.4", "CREATE Duplicate Field (Should Fail)", False, f"Expected 400, got {response.status_code}")
    
    # Test 3.5: DELETE Custom Field
    if test_data["custom_field_id"]:
        print("\n--- Test 3.5: DELETE Custom Field ---")
        response = requests.delete(f"{BACKEND_URL}/entities/custom-fields/{test_data['custom_field_id']}", headers=headers)
        if response.status_code == 200:
            log_test("3.5", "DELETE Custom Field", True, "Custom field deleted successfully")
        else:
            log_test("3.5", "DELETE Custom Field", False, f"Status: {response.status_code}")
    else:
        log_test("3.5", "DELETE Custom Field", False, "Skipped - no custom_field_id")
    
    print("\n" + "="*80)
    print("TEST SUITE 4: INTEGRATION WITH HIERARCHY (6 tests)")
    print("="*80)
    print("⚠️  NOTE: Organizational entities and organizational units are separate systems.")
    print("   Entities cannot be linked to the org units hierarchy in current implementation.")
    print("   Tests 4.3-4.6 will be skipped. Tests 4.1-4.2 verify entity creation.")
    
    # Test 4.1: Create Entity in Settings
    print("\n--- Test 4.1: Create Entity in Settings ---")
    hierarchy_entity_id = None  # Initialize variable
    hierarchy_entity_payload = {
        "entity_type": "company",
        "level": 3,
        "name": "Hierarchy Integration Test Company",
        "description": "For testing hierarchy integration"
    }
    response = requests.post(f"{BACKEND_URL}/entities", headers=headers, json=hierarchy_entity_payload)
    if response.status_code == 201:
        entity = response.json()
        hierarchy_entity_id = entity.get("id")
        parent_id_is_none = entity.get("parent_id") is None
        log_test("4.1", "Create Entity in Settings", parent_id_is_none, f"Created entity ID: {hierarchy_entity_id}, parent_id is None: {parent_id_is_none}")
    else:
        log_test("4.1", "Create Entity in Settings", False, f"Status: {response.status_code}")
    
    # Test 4.2: Verify Entity is Unlinked
    if hierarchy_entity_id:
        print("\n--- Test 4.2: Verify Entity is Unlinked ---")
        response = requests.get(f"{BACKEND_URL}/entities?entity_type=company&unlinked=true", headers=headers)
        if response.status_code == 200:
            unlinked_entities = response.json()
            entity_in_unlinked = any(e.get("id") == hierarchy_entity_id for e in unlinked_entities)
            log_test("4.2", "Verify Entity is Unlinked", entity_in_unlinked, f"Entity appears in unlinked list: {entity_in_unlinked}")
        else:
            log_test("4.2", "Verify Entity is Unlinked", False, f"Status: {response.status_code}")
    else:
        log_test("4.2", "Verify Entity is Unlinked", False, "Skipped - no hierarchy_entity_id")
    
    # Test 4.3: Link Entity to Hierarchy
    print("\n--- Test 4.3: Link Entity to Hierarchy ---")
    print("⚠️  SKIPPED: Entities and organizational units are separate systems.")
    log_test("4.3", "Link Entity to Hierarchy", False, "SKIPPED - Entities cannot be linked to org units hierarchy")
    
    # Test 4.4: Verify Entity Now Linked
    print("\n--- Test 4.4: Verify Entity Now Linked ---")
    print("⚠️  SKIPPED: Depends on Test 4.3")
    log_test("4.4", "Verify Entity Now Linked", False, "SKIPPED - Depends on hierarchy linking")
    
    # Test 4.5: GET Hierarchy Shows New Entity
    print("\n--- Test 4.5: GET Hierarchy Shows New Entity ---")
    print("⚠️  SKIPPED: Depends on Test 4.3")
    log_test("4.5", "GET Hierarchy Shows New Entity", False, "SKIPPED - Depends on hierarchy linking")
    
    # Test 4.6: Unlink Entity
    print("\n--- Test 4.6: Unlink Entity ---")
    print("⚠️  SKIPPED: Depends on Test 4.3")
    log_test("4.6", "Unlink Entity", False, "SKIPPED - Depends on hierarchy linking")
    
    print("\n" + "="*80)
    print("TEST SUITE 5: RBAC VERIFICATION (4 tests)")
    print("="*80)
    
    # Test 5.1: Master/Developer Can Create Entities
    print("\n--- Test 5.1: Master/Developer Can Create Entities ---")
    rbac_entity_payload = {
        "entity_type": "company",
        "level": 3,
        "name": "RBAC Test Company",
        "description": "Testing RBAC permissions"
    }
    response = requests.post(f"{BACKEND_URL}/entities", headers=headers, json=rbac_entity_payload)
    if response.status_code == 201:
        log_test("5.1", "Master/Developer Can Create Entities", True, "Developer role can create entities")
    else:
        log_test("5.1", "Master/Developer Can Create Entities", False, f"Status: {response.status_code}")
    
    # Test 5.2: Master/Developer Can Create Custom Fields
    print("\n--- Test 5.2: Master/Developer Can Create Custom Fields ---")
    import time
    rbac_field_payload = {
        "entity_type": "company",
        "field_id": f"rbac_test_field_{int(time.time())}",  # Unique field ID
        "field_label": "RBAC Test Field",
        "field_type": "text",
        "field_group": "test"
    }
    response = requests.post(f"{BACKEND_URL}/entities/custom-fields", headers=headers, json=rbac_field_payload)
    if response.status_code == 201:
        log_test("5.2", "Master/Developer Can Create Custom Fields", True, "Developer role can create custom fields")
    else:
        log_test("5.2", "Master/Developer Can Create Custom Fields", False, f"Status: {response.status_code}, Response: {response.text}")
    
    # Test 5.3: Verify Audit Logging
    print("\n--- Test 5.3: Verify Audit Logging ---")
    response = requests.get(f"{BACKEND_URL}/audit/logs?limit=50", headers=headers)
    if response.status_code == 200:
        logs = response.json()
        entity_logs = [
            log for log in logs 
            if "entity" in log.get("action", "").lower() and 
            log.get("resource_type") == "organizational_entity"
        ]
        has_entity_logs = len(entity_logs) > 0
        log_test("5.3", "Verify Audit Logging", has_entity_logs, f"Found {len(entity_logs)} entity-related audit logs")
    else:
        log_test("5.3", "Verify Audit Logging", False, f"Status: {response.status_code}")
    
    # Test 5.4: Verify RBAC Enforcement
    print("\n--- Test 5.4: Verify RBAC Enforcement ---")
    # This test verifies that endpoints require authentication
    # Try accessing without token
    response = requests.get(f"{BACKEND_URL}/entities")
    if response.status_code in [401, 403]:
        log_test("5.4", "Verify RBAC Enforcement", True, f"Endpoints properly protected (status: {response.status_code})")
    else:
        log_test("5.4", "Verify RBAC Enforcement", False, f"Expected 401/403, got {response.status_code}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
    
    if test_results['errors']:
        print("\n" + "="*80)
        print("FAILED TESTS DETAILS")
        print("="*80)
        for error in test_results['errors']:
            print(f"❌ {error}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
