"""
Script to list all registered routes in the FastAPI application.
This helps verify that all endpoints are properly registered.
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Mock the database connection to avoid connection errors
from unittest.mock import MagicMock, AsyncMock
import motor.motor_asyncio

# Mock AsyncIOMotorClient
motor.motor_asyncio.AsyncIOMotorClient = MagicMock

print("Loading FastAPI app...")
from backend.server import app

print("\n" + "="*80)
print("REGISTERED ROUTES IN FASTAPI APP")
print("="*80 + "\n")

# Group routes by prefix
routes_by_prefix = {}
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = sorted(list(route.methods - {'HEAD', 'OPTIONS'}))
        if methods:
            prefix = route.path.split('/')[1] if route.path.count('/') > 1 else 'root'
            if prefix not in routes_by_prefix:
                routes_by_prefix[prefix] = []
            
            for method in methods:
                routes_by_prefix[prefix].append((method, route.path))

# Print routes organized by prefix
for prefix in sorted(routes_by_prefix.keys()):
    print(f"\n[{prefix.upper()}]")
    for method, path in sorted(routes_by_prefix[prefix]):
        print(f"  {method:<8} {path}")

print("\n" + "="*80)
print(f"TOTAL ROUTES: {sum(len(routes) for routes in routes_by_prefix.values())}")
print("="*80)

# Check for specific endpoints we fixed
print("\n" + "="*80)
print("VERIFICATION OF FIXED ENDPOINTS")
print("="*80 + "\n")

endpoints_to_check = [
    ("GET", "/api/workflows"),
    ("GET", "/api/training/programs"),
    ("GET", "/api/financial/stats"),
    ("GET", "/api/hr/stats"),
    ("GET", "/api/dashboard/financial"),
    ("GET", "/api/attachments"),
    ("GET", "/api/analytics/performance"),
]

for method, path in endpoints_to_check:
    found = False
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            if route.path == path and method in route.methods:
                found = True
                break
    
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"{status:<12} {method:<8} {path}")

print("\n" + "="*80)
