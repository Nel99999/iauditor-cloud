import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.append('/app/backend')

async def test_permission():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["operational_platform"]
    
    # Import the check_permission function
    from permission_routes import check_permission
    
    # Get manager user
    manager = await db.users.find_one({"email": "manager_test_1760884598@example.com"})
    print(f"Manager user ID: {manager['id']}")
    print(f"Manager role_id: {manager['role_id']}")
    
    # Test permission check
    result = await check_permission(
        db,
        manager["id"],
        "task",
        "create",
        "organization"
    )
    
    print(f"\ncheck_permission(manager, task, create, organization) = {result}")
    print(f"Expected: True (Manager has task.create.own, should match organization scope)")
    
    client.close()

asyncio.run(test_permission())
