"""
Script to add new user approval permissions to the database
Run this ONCE after updating init_phase1_data.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid


async def add_new_permissions():
    """Add new user approval permissions to database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"📡 Connecting to database: {db_name}")
    print("🔄 Adding new user approval permissions...")
    
    new_permissions = [
        {
            "resource_type": "user",
            "action": "invite",
            "scope": "organization",
            "description": "Invite users to organization"
        },
        {
            "resource_type": "user",
            "action": "approve",
            "scope": "organization",
            "description": "Approve pending user registrations"
        },
        {
            "resource_type": "user",
            "action": "reject",
            "scope": "organization",
            "description": "Reject pending user registrations"
        }
    ]
    
    added_count = 0
    skipped_count = 0
    
    for perm_data in new_permissions:
        # Check if permission already exists
        existing = await db.permissions.find_one({
            "resource_type": perm_data["resource_type"],
            "action": perm_data["action"],
            "scope": perm_data["scope"]
        })
        
        if existing:
            print(f"⏭️  Skipping {perm_data['resource_type']}.{perm_data['action']}.{perm_data['scope']} - already exists")
            skipped_count += 1
            continue
        
        # Create new permission
        perm = {
            "id": str(uuid.uuid4()),
            "resource_type": perm_data["resource_type"],
            "action": perm_data["action"],
            "scope": perm_data["scope"],
            "description": perm_data["description"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.permissions.insert_one(perm)
        print(f"✅ Added {perm_data['resource_type']}.{perm_data['action']}.{perm_data['scope']}")
        added_count += 1
    
    print("\n" + "="*60)
    print("📈 PERMISSION ADDITION SUMMARY")
    print("="*60)
    print(f"New permissions added: {added_count}")
    print(f"Already existed:       {skipped_count}")
    print("="*60)
    print("✅ Permission addition completed!")
    
    # Get total permission count
    total_permissions = await db.permissions.count_documents({})
    print(f"📊 Total permissions in database: {total_permissions}")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(add_new_permissions())
