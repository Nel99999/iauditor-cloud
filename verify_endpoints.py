#!/usr/bin/env python3
import requests
import json
requests.packages.urllib3.disable_warnings()

BASE_URL = "https://dynamic-sidebar-1.preview.emergentagent.com/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login", 
    json={"email":"llewellyn@bluedawncapital.co.za","password":"Test@1234"}, verify=False)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test all "missing" endpoints with alternatives
tests = [
    ("GET /workflows", ["/workflows", "/workflows/templates"]),
    ("GET /training/programs", ["/training/programs", "/training/courses"]),
    ("GET /financial/stats", ["/financial/stats", "/financial/transactions"]),
    ("GET /hr/stats", ["/hr/stats", "/hr/employees"]),
    ("GET /dashboard/financial", ["/dashboard/financial", "/dashboard/enhanced/financial"]),
    ("GET /attachments", ["/attachments", "/attachments/task/test"]),
    ("GET /analytics/performance", ["/analytics/performance", "/developer/analytics/performance"]),
]

print("="*80)
print("VERIFYING SUPPOSEDLY MISSING ENDPOINTS")
print("="*80)

for test_name, endpoints in tests:
    print(f"\n{test_name}:")
    found = False
    for endpoint in endpoints:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, verify=False, timeout=5)
        status_symbol = "✅" if resp.status_code in [200, 401, 403] else "❌"
        print(f"  {status_symbol} {endpoint}: {resp.status_code}")
        if resp.status_code == 200:
            found = True
            try:
                data = resp.json()
                if isinstance(data, list):
                    print(f"      → Returns array with {len(data)} items")
                elif isinstance(data, dict):
                    print(f"      → Returns dict with keys: {list(data.keys())[:5]}")
            except:
                pass
    if not found:
        print(f"  ⚠️  None of the tested paths returned 200")

print("\n" + "="*80)
