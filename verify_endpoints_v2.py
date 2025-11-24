
import sys
import os
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock database before importing server
sys.modules["motor.motor_asyncio"] = MagicMock()
sys.modules["motor.motor_asyncio"].AsyncIOMotorClient = MagicMock()

# Import app
from backend.server import app

# Override dependency
async def mock_get_db():
    return AsyncMock()

# We need to override the get_db dependency in all routers
# But since they import it from their own files, it's tricky.
# However, FastAPI allows overriding dependencies at the app level.
# But the routers use `Depends(get_db)` where `get_db` is defined in the router file.
# So app.dependency_overrides might not work if the function objects are different.
# Let's try to just hit the endpoints. If they exist, we should get 401 (Unauthorized) or 422 (Validation Error) or 500 (DB Error).
# We shouldn't get 404 if the route exists.

client = TestClient(app)

endpoints_to_check = [
    ("GET", "/api/workflows"),
    ("GET", "/api/training/programs"),
    ("GET", "/api/financial/stats"),
    ("GET", "/api/hr/stats"),
    ("GET", "/api/dashboard/financial"),
    ("GET", "/api/attachments"),
    ("GET", "/api/analytics/performance"),
    # Also check the ones we think exist
    ("GET", "/api/workflows/templates"),
    ("GET", "/api/training/courses"),
    ("GET", "/api/dashboard/stats"),
]

print(f"{'METHOD':<8} {'PATH':<40} {'STATUS':<10} {'RESULT'}")
print("-" * 70)

for method, path in endpoints_to_check:
    try:
        response = client.request(method, path)
        status_code = response.status_code
        
        result = "EXISTS"
        if status_code == 404:
            result = "MISSING"
        
        print(f"{method:<8} {path:<40} {status_code:<10} {result}")
    except Exception as e:
        print(f"{method:<8} {path:<40} ERROR: {str(e)}")
