"""
Initialize missing invitation permissions in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid

async def initialize_permissions():
    """Initialize invitation permissions"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"Connected to MongoDB: {db_name}")
    
    # Define new invitation permissions
    new_permissions = [
        {
            "id": str(uuid.uuid4()),
            "resource_type": "invitation",
            "action": "read",
            "scope": "organization",
            "description": "View pending invitations"
        },
        {
            "id": str(uuid.uuid4()),
            "resource_type": "invitation",
            "action": "cancel",
            "scope": "organization",
            "description": "Cancel pending invitations"
        },
        {
            "id": str(uuid.uuid4()),
            "resource_type": "invitation",
            "action": "resend",
            "scope": "organization",
            "description": "Resend invitation emails"
        }
    ]
    
    # Insert permissions if they don't exist
    for perm in new_permissions:
        existing = await db.permissions.find_one({
            "resource_type": perm["resource_type"],
            "action": perm["action"],
            "scope": perm["scope"]
        })
        
        if not existing:
            await db.permissions.insert_one(perm)
            print(f"✅ Created permission: {perm['resource_type']}.{perm['action']}.{perm['scope']}")
        else:
            print(f"⏭️ Permission already exists: {perm['resource_type']}.{perm['action']}.{perm['scope']}")
    
    # Now assign these permissions to developer, master, and admin roles
    print("\nAssigning permissions to roles...")
    
    # Get all organizations
    orgs = await db.organizations.find({}).to_list(length=None)
    
    for org in orgs:
        org_id = org.get("id")
        print(f"\nProcessing organization: {org.get('name', 'Unknown')} ({org_id})")
        
        # Get developer, master, admin roles for this org
        target_roles = ["developer", "master", "admin"]
        
        for role_code in target_roles:
            role = await db.roles.find_one({
                "code": role_code,
                "organization_id": org_id
            })
            
            if not role:
                print(f"  ⚠️ Role '{role_code}' not found for this organization")
                continue
            
            role_id = role["id"]
            
            # Assign all three new permissions to this role
            for perm in new_permissions:
                # Check if already assigned
                existing_assignment = await db.role_permissions.find_one({
                    "role_id": role_id,
                    "permission_id": perm["id"]
                })
                
                if not existing_assignment:
                    role_perm = {
                        "id": str(uuid.uuid4()),
                        "role_id": role_id,
                        "permission_id": perm["id"],
                        "granted": True
                    }
                    await db.role_permissions.insert_one(role_perm)
                    print(f"  ✅ Assigned {perm['resource_type']}.{perm['action']} to {role_code}")
                else:
                    print(f"  ⏭️ {perm['resource_type']}.{perm['action']} already assigned to {role_code}")
    
    print("\n✅ Permission initialization complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(initialize_permissions())
