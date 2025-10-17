#!/usr/bin/env python3
"""
Quick Phase 2 Backend API Test
Tests core Phase 2 functionality
"""

import requests
import json
import os
import tempfile

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://devflow-hub-3.preview.emergentagent.com')
API_URL = f"{BASE_URL}/api"

def test_phase2_apis():
    """Test Phase 2 APIs quickly"""
    print("🧪 Quick Phase 2 Backend API Test")
    print("=" * 50)
    
    # Setup test user
    test_email = "phase2.enterprise@company.com"
    test_password = "Enterprise123!@#"
    
    # Register/Login
    user_data = {
        "email": test_email,
        "password": test_password,
        "name": "Phase 2 Tester",
        "organization_name": "Test Corp"
    }
    
    session = requests.Session()
    response = session.post(f"{API_URL}/auth/register", json=user_data)
    
    if response.status_code not in [200, 201]:
        # Try login
        response = session.post(f"{API_URL}/auth/login", json={
            "email": test_email,
            "password": test_password
        })
    
    if response.status_code in [200, 201]:
        data = response.json()
        access_token = data.get("access_token")
        print(f"✅ Authentication successful")
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Test results
    results = {"passed": 0, "failed": 0, "total": 0}
    
    def test_api(name, method, endpoint, **kwargs):
        results["total"] += 1
        try:
            if method.upper() == "GET":
                resp = session.get(f"{API_URL}{endpoint}", headers=headers, **kwargs)
            elif method.upper() == "POST":
                resp = session.post(f"{API_URL}{endpoint}", headers=headers, **kwargs)
            elif method.upper() == "PUT":
                resp = session.put(f"{API_URL}{endpoint}", headers=headers, **kwargs)
            elif method.upper() == "DELETE":
                resp = session.delete(f"{API_URL}{endpoint}", headers=headers, **kwargs)
            
            if resp.status_code < 400:
                print(f"✅ {name}: {resp.status_code}")
                results["passed"] += 1
                return resp.json() if resp.content else {}
            else:
                print(f"❌ {name}: {resp.status_code} - {resp.text[:100]}")
                results["failed"] += 1
                return None
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            results["failed"] += 1
            return None
    
    # 1. Test Groups API
    print("\n👥 Testing Groups API...")
    group_data = {"name": "Test Group", "description": "Test group", "color": "#3B82F6"}
    group_result = test_api("Create Group", "POST", "/groups", json=group_data)
    
    if group_result:
        group_id = group_result.get("id")
        test_api("List Groups", "GET", "/groups")
        test_api("Get Group Stats", "GET", "/groups/stats")
        test_api("Get Group Hierarchy", "GET", "/groups/hierarchy")
        test_api("Get Specific Group", "GET", f"/groups/{group_id}")
        test_api("Update Group", "PUT", f"/groups/{group_id}", json={"name": "Updated Group"})
    
    # 2. Test Bulk Import API
    print("\n📊 Testing Bulk Import API...")
    test_api("Get Import Template", "GET", "/bulk-import/users/template")
    
    # Create test CSV
    csv_content = "email,name,role\ntest@bulk.com,Test User,viewer"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    try:
        with open(temp_path, 'rb') as f:
            files = {'file': ('test.csv', f, 'text/csv')}
            resp = session.post(f"{API_URL}/bulk-import/users/preview", files=files, headers=headers)
            if resp.status_code < 400:
                print(f"✅ CSV Preview: {resp.status_code}")
                results["passed"] += 1
            else:
                print(f"❌ CSV Preview: {resp.status_code}")
                results["failed"] += 1
            results["total"] += 1
    finally:
        os.unlink(temp_path)
    
    # 3. Test Webhooks API
    print("\n🔗 Testing Webhooks API...")
    test_api("Get Webhook Events", "GET", "/webhooks/events")
    
    webhook_data = {
        "name": "Test Webhook",
        "url": "https://webhook.site/test",
        "events": ["task.created"]
    }
    webhook_result = test_api("Create Webhook", "POST", "/webhooks", json=webhook_data)
    
    if webhook_result:
        webhook_id = webhook_result.get("id")
        test_api("List Webhooks", "GET", "/webhooks")
        test_api("Get Specific Webhook", "GET", f"/webhooks/{webhook_id}")
        test_api("Test Webhook", "POST", f"/webhooks/{webhook_id}/test")
        test_api("Get Deliveries", "GET", f"/webhooks/{webhook_id}/deliveries")
    
    # 4. Test Search API
    print("\n🔍 Testing Search API...")
    test_api("Global Search", "GET", "/search/global?q=test&limit=5")
    test_api("Search Users", "GET", "/search/users?q=test&limit=5")
    test_api("Search Suggestions", "GET", "/search/suggestions?q=te")
    
    # Edge cases
    resp = session.get(f"{API_URL}/search/global?q=a", headers=headers)
    if resp.status_code == 400:
        print("✅ Search Query Too Short: 400 (expected)")
        results["passed"] += 1
    else:
        print(f"❌ Search Query Too Short: {resp.status_code} (expected 400)")
        results["failed"] += 1
    results["total"] += 1
    
    # 5. Test Audit Logs
    print("\n📋 Testing Audit Logs...")
    test_api("Get Audit Logs", "GET", "/audit/logs?limit=10")
    
    # Print Results
    print("\n" + "=" * 50)
    print("📊 PHASE 2 QUICK TEST RESULTS")
    print("=" * 50)
    
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Phase 2 APIs are working well!")
    else:
        print("⚠️ Some Phase 2 APIs need attention")

if __name__ == "__main__":
    test_phase2_apis()