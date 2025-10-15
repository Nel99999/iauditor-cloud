"""
Script to assign new approval permissions to existing Master, Admin, and Developer roles
Run this ONCE after adding the new permissions
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid


async def assign_permissions_to_roles():
    """Assign new approval permissions to Master, Admin, and Developer roles"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"📡 Connecting to database: {db_name}")
    print("🔄 Assigning new approval permissions to roles...")
    
    # Get the new permissions
    new_permissions = []
    for action in ["invite", "approve", "reject"]:
        perm = await db.permissions.find_one({
            "resource_type": "user",
            "action": action,
            "scope": "organization"
        })
        if perm:
            new_permissions.append(perm)
            print(f"✅ Found permission: user.{action}.organization ({perm['id']})")
        else:
            print(f"❌ Permission not found: user.{action}.organization")
    
    if len(new_permissions) != 3:
        print("❌ Error: Could not find all 3 new permissions")
        client.close()
        return
    
    # Get all organizations
    organizations = await db.organizations.find({}, {"_id": 0}).to_list(length=None)
    print(f"\n📊 Found {len(organizations)} organizations")
    
    total_assignments = 0
    
    # For each organization, find Master, Admin, and Developer roles
    for org in organizations:
        org_id = org["id"]
        org_name = org["name"]
        print(f"\n🏢 Processing organization: {org_name}")
        
        # Get roles for this organization
        for role_code in ["master", "admin", "developer"]:
            role = await db.roles.find_one({
                "code": role_code,
                "organization_id": org_id
            })
            
            if not role:
                print(f"  ⚠️  {role_code} role not found")
                continue
            
            print(f"  📝 Assigning permissions to {role_code} role...")
            
            # Assign each new permission to this role
            for perm in new_permissions:
                # Check if already assigned
                existing = await db.role_permissions.find_one({
                    "role_id": role["id"],
                    "permission_id": perm["id"]
                })
                
                if existing:
                    print(f"    ⏭️  {perm['action']} - already assigned")
                    continue
                
                # Create role permission assignment
                role_perm = {
                    "id": str(uuid.uuid4()),
                    "role_id": role["id"],
                    "permission_id": perm["id"],
                    "granted": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.role_permissions.insert_one(role_perm)
                print(f"    ✅ {perm['action']} - assigned")
                total_assignments += 1
    
    print("\n" + "="*60)
    print("📈 PERMISSION ASSIGNMENT SUMMARY")
    print("="*60)
    print(f"Organizations processed:  {len(organizations)}")
    print(f"Total assignments made:   {total_assignments}")
    print("="*60)
    print("✅ Permission assignment completed!")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(assign_permissions_to_roles())
