"""
Assets Module Backend Testing - All 10 Endpoints
Test User: llewellyn@bluedawncapital.co.za
Base URL: https://rbacmaster-1.preview.emergentagent.com/api
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_PASSWORD = "TestPassword123!"

# Test results tracking
test_results = {
    "total": 10,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1


def login():
    """Login and get access token"""
    print("\n🔐 Logging in...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login successful - Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None


def test_create_asset(token):
    """TEST 1: Create Asset"""
    print("\n" + "="*80)
    print("TEST 1: Create Asset - POST /api/assets")
    print("="*80)
    
    # Use timestamp to ensure unique asset tag
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "asset_tag": f"TEST-ASSET-{timestamp}",
        "name": "Test Equipment",
        "description": "Testing asset creation",
        "asset_type": "equipment",
        "criticality": "B",
        "make": "TestMake",
        "model": "TestModel",
        "serial_number": "SN12345",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/assets", json=payload, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            asset_id = data.get("id")
            
            # Verify required fields
            checks = [
                data.get("id") is not None,
                data.get("asset_tag") == f"TEST-ASSET-{timestamp}",
                data.get("name") == "Test Equipment",
                data.get("asset_type") == "equipment",
                data.get("criticality") == "B",
                data.get("status") == "active"
            ]
            
            if all(checks):
                log_test("TEST 1: Create Asset", True, f"Asset created with ID: {asset_id}")
                return asset_id
            else:
                log_test("TEST 1: Create Asset", False, "Missing required fields in response")
                return None
        else:
            log_test("TEST 1: Create Asset", False, f"Status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("TEST 1: Create Asset", False, f"Exception: {str(e)}")
        return None


def test_list_assets(token):
    """TEST 2: List Assets"""
    print("\n" + "="*80)
    print("TEST 2: List Assets - GET /api/assets")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                log_test("TEST 2: List Assets", True, f"Returned {len(data)} assets")
                return True
            else:
                log_test("TEST 2: List Assets", False, "Response is not an array")
                return False
        else:
            log_test("TEST 2: List Assets", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 2: List Assets", False, f"Exception: {str(e)}")
        return False


def test_get_asset(token, asset_id):
    """TEST 3: Get Asset by ID"""
    print("\n" + "="*80)
    print(f"TEST 3: Get Asset by ID - GET /api/assets/{asset_id}")
    print("="*80)
    
    if not asset_id:
        log_test("TEST 3: Get Asset by ID", False, "No asset_id from Test 1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets/{asset_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify it's the correct asset
            if data.get("id") == asset_id:
                log_test("TEST 3: Get Asset by ID", True, f"Asset details retrieved correctly")
                return True
            else:
                log_test("TEST 3: Get Asset by ID", False, "Asset data mismatch")
                return False
        else:
            log_test("TEST 3: Get Asset by ID", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 3: Get Asset by ID", False, f"Exception: {str(e)}")
        return False


def test_update_asset(token, asset_id):
    """TEST 4: Update Asset"""
    print("\n" + "="*80)
    print(f"TEST 4: Update Asset - PUT /api/assets/{asset_id}")
    print("="*80)
    
    if not asset_id:
        log_test("TEST 4: Update Asset", False, "No asset_id from Test 1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"description": "Updated description"}
    
    try:
        response = requests.put(f"{BASE_URL}/assets/{asset_id}", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("description") == "Updated description":
                log_test("TEST 4: Update Asset", True, "Asset updated successfully")
                return True
            else:
                log_test("TEST 4: Update Asset", False, "Description not updated")
                return False
        else:
            log_test("TEST 4: Update Asset", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 4: Update Asset", False, f"Exception: {str(e)}")
        return False


def test_get_asset_history(token, asset_id):
    """TEST 5: Get Asset History"""
    print("\n" + "="*80)
    print(f"TEST 5: Get Asset History - GET /api/assets/{asset_id}/history")
    print("="*80)
    
    if not asset_id:
        log_test("TEST 5: Get Asset History", False, "No asset_id from Test 1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets/{asset_id}/history", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify structure
            if "asset" in data and "history" in data and "total_entries" in data:
                log_test("TEST 5: Get Asset History", True, f"History retrieved with {data['total_entries']} entries")
                return True
            else:
                log_test("TEST 5: Get Asset History", False, "Missing required fields in response")
                return False
        else:
            log_test("TEST 5: Get Asset History", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 5: Get Asset History", False, f"Exception: {str(e)}")
        return False


def test_generate_qr_code(token, asset_id):
    """TEST 6: Generate QR Code"""
    print("\n" + "="*80)
    print(f"TEST 6: Generate QR Code - POST /api/assets/{asset_id}/qr-code")
    print("="*80)
    
    if not asset_id:
        log_test("TEST 6: Generate QR Code", False, "No asset_id from Test 1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/assets/{asset_id}/qr-code", headers=headers)
        
        if response.status_code == 200:
            # Check if response is an image
            content_type = response.headers.get("content-type", "")
            
            if "image/png" in content_type and len(response.content) > 0:
                log_test("TEST 6: Generate QR Code", True, f"QR code generated ({len(response.content)} bytes)")
                return True
            else:
                log_test("TEST 6: Generate QR Code", False, f"Invalid content type: {content_type}")
                return False
        else:
            log_test("TEST 6: Generate QR Code", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 6: Generate QR Code", False, f"Exception: {str(e)}")
        return False


def test_get_asset_types(token):
    """TEST 7: Get Asset Types"""
    print("\n" + "="*80)
    print("TEST 7: Get Asset Types - GET /api/assets/types/catalog")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets/types/catalog", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify structure
            if "standard_types" in data and "organization_types" in data:
                standard_count = len(data.get("standard_types", []))
                org_count = len(data.get("organization_types", []))
                log_test("TEST 7: Get Asset Types", True, f"Types retrieved: {standard_count} standard, {org_count} organization")
                return True
            else:
                log_test("TEST 7: Get Asset Types", False, "Missing required fields in response")
                return False
        else:
            log_test("TEST 7: Get Asset Types", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 7: Get Asset Types", False, f"Exception: {str(e)}")
        return False


def test_get_asset_stats(token):
    """TEST 8: Get Asset Stats"""
    print("\n" + "="*80)
    print("TEST 8: Get Asset Stats - GET /api/assets/stats")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required fields
            required_fields = ["total_assets", "by_type", "by_criticality", "by_status", "total_value"]
            missing = [f for f in required_fields if f not in data]
            
            if not missing:
                log_test("TEST 8: Get Asset Stats", True, f"Stats retrieved: {data['total_assets']} total assets")
                return True
            else:
                log_test("TEST 8: Get Asset Stats", False, f"Missing fields: {missing}")
                return False
        else:
            log_test("TEST 8: Get Asset Stats", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 8: Get Asset Stats", False, f"Exception: {str(e)}")
        return False


def test_filter_assets_by_type(token):
    """TEST 9: Filter Assets by Type"""
    print("\n" + "="*80)
    print("TEST 9: Filter Assets by Type - GET /api/assets?asset_type=equipment")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assets?asset_type=equipment", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                # Verify all returned assets are of type 'equipment'
                all_equipment = all(asset.get("asset_type") == "equipment" for asset in data)
                
                if all_equipment:
                    log_test("TEST 9: Filter Assets by Type", True, f"Filtered results: {len(data)} equipment assets")
                    return True
                else:
                    log_test("TEST 9: Filter Assets by Type", False, "Filter not working correctly")
                    return False
            else:
                log_test("TEST 9: Filter Assets by Type", False, "Response is not an array")
                return False
        else:
            log_test("TEST 9: Filter Assets by Type", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 9: Filter Assets by Type", False, f"Exception: {str(e)}")
        return False


def test_delete_asset(token, asset_id):
    """TEST 10: Delete Asset"""
    print("\n" + "="*80)
    print(f"TEST 10: Delete Asset - DELETE /api/assets/{asset_id}")
    print("="*80)
    
    if not asset_id:
        log_test("TEST 10: Delete Asset", False, "No asset_id from Test 1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/assets/{asset_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if "message" in data:
                log_test("TEST 10: Delete Asset", True, "Asset deleted successfully")
                return True
            else:
                log_test("TEST 10: Delete Asset", False, "No confirmation message")
                return False
        else:
            log_test("TEST 10: Delete Asset", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("TEST 10: Delete Asset", False, f"Exception: {str(e)}")
        return False


def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed']/test_results['total']*100):.1f}%")
    print("\nDetailed Results:")
    for test in test_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"{status} {test['name']}")
        if test["details"]:
            print(f"   {test['details']}")
    print("="*80)


def main():
    """Run all tests"""
    print("="*80)
    print("ASSETS MODULE BACKEND TESTING - ALL 10 ENDPOINTS")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Run all tests in sequence
    asset_id = test_create_asset(token)
    test_list_assets(token)
    test_get_asset(token, asset_id)
    test_update_asset(token, asset_id)
    test_get_asset_history(token, asset_id)
    test_generate_qr_code(token, asset_id)
    test_get_asset_types(token)
    test_get_asset_stats(token)
    test_filter_assets_by_type(token)
    test_delete_asset(token, asset_id)
    
    # Print summary
    print_summary()
    
    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    if test_results["failed"] == 0:
        print("✅ ALL TESTS PASSED - Assets module is fully operational!")
    elif test_results["passed"] >= 8:
        print("⚠️ MOSTLY WORKING - Minor issues found")
    else:
        print("❌ CRITICAL ISSUES - Multiple endpoints failing")
    
    print("="*80)


if __name__ == "__main__":
    main()
