#!/usr/bin/env python3
import requests
import json
requests.packages.urllib3.disable_warnings()

BASE_URL = "https://backendhealer.preview.emergentagent.com/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", 
    json={"email":"llewellyn@bluedawncapital.co.za","password":"Test@1234"}, verify=False)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("="*80)
print("TESTING ALL FIXED ENDPOINTS")
print("="*80)

tests = [
    ("Training Stats (500 error fixed)", "GET", "/training/stats"),
    ("Assets Stats (500 error fixed)", "GET", "/assets/stats"),
    ("Task Templates (route ordering fixed)", "GET", "/tasks/templates"),
    ("Task Stats Overview (route ordering)", "GET", "/tasks/stats/overview"),
    ("Task Analytics (route ordering)", "GET", "/tasks/analytics/overview"),
    ("Financial Stats (new endpoint)", "GET", "/financial/stats"),
    ("HR Stats (new endpoint)", "GET", "/hr/stats"),
    ("Dashboard Financial (new endpoint)", "GET", "/dashboard/financial"),
    ("Attachments List (new endpoint)", "GET", "/attachments"),
    ("Analytics Performance (new endpoint)", "GET", "/analytics/performance"),
]

passed = 0
failed = 0

for test_name, method, endpoint in tests:
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, verify=False, timeout=5)
        
        if resp.status_code == 200:
            print(f"✅ {test_name}: {endpoint}")
            print(f"   Status: {resp.status_code}")
            try:
                data = resp.json()
                if isinstance(data, list):
                    print(f"   → Returns array with {len(data)} items")
                elif isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"   → Returns dict with keys: {keys}")
            except:
                pass
            passed += 1
        else:
            print(f"❌ {test_name}: {endpoint}")
            print(f"   Status: {resp.status_code}")
            print(f"   Error: {resp.text[:200]}")
            failed += 1
    except Exception as e:
        print(f"❌ {test_name}: {endpoint}")
        print(f"   Exception: {str(e)}")
        failed += 1
    print()

print("="*80)
print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
print("="*80)
