#!/usr/bin/env python3
"""Diagnose all failed endpoints"""
import requests
import json
from pymongo import MongoClient

# Setup
BASE_URL = "https://dynamic-sidebar-1.preview.emergentagent.com/api"
TOKEN = None

# Get auth token first
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "Test@1234"
}, verify=False)

if response.status_code == 200:
    TOKEN = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print(f"✅ Authenticated successfully\n")
else:
    print(f"❌ Authentication failed: {response.status_code}")
    exit(1)

# Test each failed endpoint
failed_endpoints = [
    ("POST", "/auth/login", {"email": "test@example.com", "password": "wrong"}, "Wrong password test"),
    ("POST", "/auth/login", {"email": "nonexistent@example.com", "password": "Test@1234"}, "Non-existent user test"),
    ("GET", "/users/me", None, "Missing token test", {}),
    ("POST", "/auth/reset-password", {"token": "invalid", "new_password": "Test@1234"}, "Invalid reset token"),
    ("GET", "/workflows", None, "Workflows list"),
    ("GET", "/tasks/templates", None, "Task templates"),
    ("GET", "/assets/stats", None, "Asset statistics"),
    ("GET", "/inventory/items", None, "Inventory items"),
    ("GET", "/inventory/items/reorder", None, "Low stock alerts"),
    ("GET", "/projects/stats", None, "Project statistics"),
    ("GET", "/training/programs", None, "Training programs"),
    ("GET", "/training/stats", None, "Training statistics"),
    ("GET", "/financial/stats", None, "Financial statistics"),
    ("GET", "/hr/stats", None, "HR statistics"),
    ("GET", "/dashboard/financial", None, "Financial dashboard"),
    ("GET", "/attachments", None, "Attachments list"),
    ("GET", "/developer/health", None, "System health"),
    ("GET", "/analytics/performance", None, "Performance metrics"),
]

print("="*80)
print("DIAGNOSING ALL FAILED ENDPOINTS")
print("="*80)

for item in failed_endpoints:
    if len(item) == 4:
        method, endpoint, data, description = item
        test_headers = headers.copy()
    else:
        method, endpoint, data, description, test_headers = item
    
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=test_headers, verify=False, timeout=5)
        else:
            resp = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=test_headers, verify=False, timeout=5)
        
        print(f"\n{description}")
        print(f"  Endpoint: {method} {endpoint}")
        print(f"  Status: {resp.status_code}")
        if resp.status_code >= 400:
            try:
                error = resp.json()
                print(f"  Error: {error}")
            except:
                print(f"  Response: {resp.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"\n{description}")
        print(f"  Endpoint: {method} {endpoint}")
        print(f"  Status: TIMEOUT")
    except Exception as e:
        print(f"\n{description}")
        print(f"  Endpoint: {method} {endpoint}")
        print(f"  Error: {str(e)}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
