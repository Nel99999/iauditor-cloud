#!/usr/bin/env python3
"""
Initialize V1 Module Permissions
Adds missing permissions for new V1 modules to the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def initialize_v1_permissions():
    """Initialize permissions for V1 modules"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("✅ Connected to MongoDB")
    
    # Define V1 module permissions (from permission_routes.py lines 436-504)
    v1_permissions = [
        # Asset permissions
        {"resource_type": "asset", "action": "create", "scope": "organization", "description": "Create assets"},
        {"resource_type": "asset", "action": "read", "scope": "own", "description": "View own assets"},
        {"resource_type": "asset", "action": "read", "scope": "organization", "description": "View all assets"},
        {"resource_type": "asset", "action": "update", "scope": "organization", "description": "Update assets"},
        {"resource_type": "asset", "action": "delete", "scope": "organization", "description": "Delete assets"},
        
        # Work Order permissions
        {"resource_type": "workorder", "action": "create", "scope": "own", "description": "Create work orders"},
        {"resource_type": "workorder", "action": "create", "scope": "organization", "description": "Create all work orders"},
        {"resource_type": "workorder", "action": "read", "scope": "own", "description": "View own work orders"},
        {"resource_type": "workorder", "action": "read", "scope": "organization", "description": "View all work orders"},
        {"resource_type": "workorder", "action": "update", "scope": "own", "description": "Update own work orders"},
        {"resource_type": "workorder", "action": "update", "scope": "organization", "description": "Update all work orders"},
        {"resource_type": "workorder", "action": "delete", "scope": "organization", "description": "Delete work orders"},
        
        # Inventory permissions
        {"resource_type": "inventory", "action": "create", "scope": "organization", "description": "Create inventory items"},
        {"resource_type": "inventory", "action": "read", "scope": "own", "description": "View inventory"},
        {"resource_type": "inventory", "action": "read", "scope": "organization", "description": "View all inventory"},
        {"resource_type": "inventory", "action": "update", "scope": "organization", "description": "Update inventory"},
        {"resource_type": "inventory", "action": "delete", "scope": "organization", "description": "Delete inventory items"},
        
        # Project permissions
        {"resource_type": "project", "action": "create", "scope": "organization", "description": "Create projects"},
        {"resource_type": "project", "action": "read", "scope": "own", "description": "View own projects"},
        {"resource_type": "project", "action": "read", "scope": "organization", "description": "View all projects"},
        {"resource_type": "project", "action": "update", "scope": "own", "description": "Update own projects"},
        {"resource_type": "project", "action": "update", "scope": "organization", "description": "Update all projects"},
        {"resource_type": "project", "action": "delete", "scope": "organization", "description": "Delete projects"},
        
        # Incident permissions
        {"resource_type": "incident", "action": "create", "scope": "organization", "description": "Report incidents"},
        {"resource_type": "incident", "action": "read", "scope": "own", "description": "View own incidents"},
        {"resource_type": "incident", "action": "read", "scope": "organization", "description": "View all incidents"},
        {"resource_type": "incident", "action": "update", "scope": "organization", "description": "Update incidents"},
        {"resource_type": "incident", "action": "investigate", "scope": "organization", "description": "Investigate incidents"},
        
        # Training permissions
        {"resource_type": "training", "action": "create", "scope": "organization", "description": "Create training courses"},
        {"resource_type": "training", "action": "read", "scope": "own", "description": "View own training"},
        {"resource_type": "training", "action": "read", "scope": "organization", "description": "View all training"},
        {"resource_type": "training", "action": "manage", "scope": "organization", "description": "Manage training"},
        
        # Financial permissions
        {"resource_type": "financial", "action": "read", "scope": "organization", "description": "View financial data"},
        {"resource_type": "financial", "action": "create", "scope": "organization", "description": "Create financial entries"},
        {"resource_type": "financial", "action": "manage", "scope": "organization", "description": "Manage finances"},
        
        # Contractor permissions
        {"resource_type": "contractor", "action": "create", "scope": "organization", "description": "Create contractors"},
        {"resource_type": "contractor", "action": "read", "scope": "organization", "description": "View contractors"},
        {"resource_type": "contractor", "action": "update", "scope": "organization", "description": "Update contractors"},
        
        # Emergency permissions
        {"resource_type": "emergency", "action": "create", "scope": "organization", "description": "Declare emergencies"},
        {"resource_type": "emergency", "action": "read", "scope": "organization", "description": "View emergencies"},
        {"resource_type": "emergency", "action": "manage", "scope": "organization", "description": "Manage emergencies"},
        
        # Chat permissions
        {"resource_type": "chat", "action": "read", "scope": "organization", "description": "Access team chat"},
        {"resource_type": "chat", "action": "create", "scope": "organization", "description": "Send messages"},
        
        # Announcement permissions
        {"resource_type": "announcement", "action": "create", "scope": "organization", "description": "Create announcements"},
        {"resource_type": "announcement", "action": "read", "scope": "organization", "description": "View announcements"},
    ]
    
    print(f"\n📋 Initializing {len(v1_permissions)} V1 module permissions...")
    
    created_count = 0
    existing_count = 0
    
    for perm_data in v1_permissions:
        # Check if permission already exists
        existing = await db.permissions.find_one({
            "resource_type": perm_data["resource_type"],
            "action": perm_data["action"],
            "scope": perm_data["scope"]
        })
        
        if not existing:
            # Create new permission
            perm_doc = {
                "id": str(uuid.uuid4()),
                "resource_type": perm_data["resource_type"],
                "action": perm_data["action"],
                "scope": perm_data["scope"],
                "description": perm_data["description"],
                "created_at": datetime.now(timezone.utc)
            }
            
            await db.permissions.insert_one(perm_doc)
            print(f"  ✅ Created: {perm_data['resource_type']}.{perm_data['action']}.{perm_data['scope']}")
            created_count += 1
        else:
            existing_count += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Created: {created_count} new permissions")
    print(f"  ℹ️  Existing: {existing_count} permissions already exist")
    
    # Now assign these permissions to Developer and Master roles
    print(f"\n🔐 Assigning permissions to system roles...")
    
    # Get all organizations
    orgs = await db.organizations.find({}).to_list(length=1000)
    print(f"  Found {len(orgs)} organizations")
    
    for org in orgs:
        org_id = org.get('id')
        org_name = org.get('name', 'Unknown')
        
        print(f"\n  📁 Organization: {org_name} ({org_id})")
        
        # Get Developer and Master roles for this org
        developer_role = await db.roles.find_one({
            "code": "developer",
            "organization_id": org_id
        })
        
        master_role = await db.roles.find_one({
            "code": "master",
            "organization_id": org_id
        })
        
        # Get all V1 permissions
        all_v1_perms = await db.permissions.find({
            "resource_type": {"$in": [
                "asset", "workorder", "inventory", "project", "incident",
                "training", "financial", "contractor", "emergency", "chat", "announcement"
            ]}
        }).to_list(length=1000)
        
        # Assign to Developer role
        if developer_role:
            role_id = developer_role['id']
            assigned = 0
            
            for perm in all_v1_perms:
                perm_id = perm['id']
                
                # Check if already assigned
                existing_assignment = await db.role_permissions.find_one({
                    "role_id": role_id,
                    "permission_id": perm_id
                })
                
                if not existing_assignment:
                    # Create assignment
                    assignment = {
                        "id": f"{role_id}_{perm_id}",
                        "role_id": role_id,
                        "permission_id": perm_id,
                        "organization_id": org_id,
                        "granted": True,
                        "created_at": datetime.now(timezone.utc)
                    }
                    
                    await db.role_permissions.insert_one(assignment)
                    assigned += 1
            
            print(f"    ✅ Developer role: Assigned {assigned} new permissions")
        else:
            print(f"    ⚠️  Developer role not found")
        
        # Assign to Master role
        if master_role:
            role_id = master_role['id']
            assigned = 0
            
            for perm in all_v1_perms:
                perm_id = perm['id']
                
                # Check if already assigned
                existing_assignment = await db.role_permissions.find_one({
                    "role_id": role_id,
                    "permission_id": perm_id
                })
                
                if not existing_assignment:
                    # Create assignment
                    assignment = {
                        "id": f"{role_id}_{perm_id}",
                        "role_id": role_id,
                        "permission_id": perm_id,
                        "organization_id": org_id,
                        "granted": True,
                        "created_at": datetime.now(timezone.utc)
                    }
                    
                    await db.role_permissions.insert_one(assignment)
                    assigned += 1
            
            print(f"    ✅ Master role: Assigned {assigned} new permissions")
        else:
            print(f"    ⚠️  Master role not found")
    
    print(f"\n✅ V1 permissions initialization complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(initialize_v1_permissions())
