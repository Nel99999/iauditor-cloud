"""Initialize Phase 1 system data (roles and permissions)"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


async def initialize_phase1_data():
    """Initialize system roles and permissions for all organizations"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 80)
    print("🚀 PHASE 1 SYSTEM DATA INITIALIZATION")
    print("=" * 80)
    
    # Initialize permissions first
    await initialize_permissions(db)
    
    # Get all organizations
    organizations = await db.organizations.find({}, {"_id": 0, "id": 1, "name": 1}).to_list(length=None)
    
    if not organizations:
        print("⚠️  No organizations found. Creating test organization...")
        # Create a test organization
        test_org = {
            "id": "test-org-123",
            "name": "Test Organization",
            "created_at": "2025-01-01T00:00:00Z"
        }
        await db.organizations.insert_one(test_org)
        organizations = [test_org]
    
    # Initialize system roles for each organization
    for org in organizations:
        print(f"\n🏢 Initializing roles for organization: {org['name']} ({org['id']})")
        await initialize_system_roles(db, org['id'])
    
    print("\n" + "=" * 80)
    print("✅ PHASE 1 SYSTEM DATA INITIALIZATION COMPLETE")
    print("=" * 80)
    
    client.close()


async def initialize_permissions(db):
    """Initialize default permission set"""
    
    print("\n🔐 Initializing default permissions...")
    
    default_permissions = [
        # Inspection permissions
        {"resource_type": "inspection", "action": "create", "scope": "own", "description": "Create own inspections"},
        {"resource_type": "inspection", "action": "create", "scope": "team", "description": "Create team inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "own", "description": "View own inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "team", "description": "View team inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "all", "description": "View all inspections"},
        {"resource_type": "inspection", "action": "update", "scope": "own", "description": "Edit own inspections"},
        {"resource_type": "inspection", "action": "delete", "scope": "own", "description": "Delete own inspections"},
        {"resource_type": "inspection", "action": "approve", "scope": "team", "description": "Approve team inspections"},
        
        # Task permissions
        {"resource_type": "task", "action": "create", "scope": "own", "description": "Create tasks"},
        {"resource_type": "task", "action": "read", "scope": "own", "description": "View own tasks"},
        {"resource_type": "task", "action": "read", "scope": "team", "description": "View team tasks"},
        {"resource_type": "task", "action": "update", "scope": "own", "description": "Update own tasks"},
        {"resource_type": "task", "action": "assign", "scope": "team", "description": "Assign tasks to team"},
        {"resource_type": "task", "action": "delete", "scope": "own", "description": "Delete own tasks"},
        
        # User permissions
        {"resource_type": "user", "action": "create", "scope": "organization", "description": "Create users"},
        {"resource_type": "user", "action": "read", "scope": "organization", "description": "View users"},
        {"resource_type": "user", "action": "update", "scope": "organization", "description": "Update users"},
        {"resource_type": "user", "action": "delete", "scope": "organization", "description": "Delete users"},
        
        # Report permissions
        {"resource_type": "report", "action": "read", "scope": "own", "description": "View own reports"},
        {"resource_type": "report", "action": "read", "scope": "all", "description": "View all reports"},
        {"resource_type": "report", "action": "export", "scope": "all", "description": "Export reports"},
        
        # API permissions (for developer role)
        {"resource_type": "api", "action": "manage", "scope": "all", "description": "Manage API keys"},
        {"resource_type": "webhook", "action": "manage", "scope": "all", "description": "Manage webhooks"},
    ]
    
    # Insert permissions if they don't exist
    permissions_created = 0
    for perm_data in default_permissions:
        existing = await db.permissions.find_one({
            "resource_type": perm_data["resource_type"],
            "action": perm_data["action"],
            "scope": perm_data["scope"]
        })
        
        if not existing:
            import uuid
            from datetime import datetime, timezone
            
            perm = {
                "id": str(uuid.uuid4()),
                "resource_type": perm_data["resource_type"],
                "action": perm_data["action"],
                "scope": perm_data["scope"],
                "description": perm_data["description"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.permissions.insert_one(perm)
            permissions_created += 1
    
    print(f"✅ Created {permissions_created} new permissions")
    
    # Get total count
    total_permissions = await db.permissions.count_documents({})
    print(f"📊 Total permissions in system: {total_permissions}")


async def initialize_system_roles(db, organization_id):
    """Initialize system roles for an organization"""
    
    import uuid
    from datetime import datetime, timezone
    
    # System roles that cannot be deleted
    SYSTEM_ROLES = {
        "master": {
            "name": "Master",
            "code": "master",
            "color": "#9333ea",  # Purple
            "level": 1,
            "description": "System administrator with full access",
            "is_system_role": True
        },
        "admin": {
            "name": "Admin",
            "code": "admin",
            "color": "#ef4444",  # Red
            "level": 2,
            "description": "Administrator with full organization access",
            "is_system_role": True
        },
        "developer": {
            "name": "Developer",
            "code": "developer",
            "color": "#8b5cf6",  # Violet
            "level": 3,
            "description": "Developer with API and integration access",
            "is_system_role": True
        },
        "operations_manager": {
            "name": "Operations Manager",
            "code": "operations_manager",
            "color": "#f59e0b",  # Amber
            "level": 4,
            "description": "Manages operational programs and strategic initiatives",
            "is_system_role": True
        },
        "team_lead": {
            "name": "Team Lead",
            "code": "team_lead",
            "color": "#06b6d4",  # Cyan
            "level": 5,
            "description": "Leads teams and manages task assignments",
            "is_system_role": True
        },
        "manager": {
            "name": "Manager",
            "code": "manager",
            "color": "#3b82f6",  # Blue
            "level": 6,
            "description": "Manages teams and approves work",
            "is_system_role": True
        },
        "supervisor": {
            "name": "Supervisor",
            "code": "supervisor",
            "color": "#10b981",  # Emerald
            "level": 7,
            "description": "Supervises field teams and shift assignments",
            "is_system_role": True
        },
        "inspector": {
            "name": "Inspector",
            "code": "inspector",
            "color": "#eab308",  # Yellow
            "level": 8,
            "description": "Executes inspections and operational tasks",
            "is_system_role": True
        },
        "operator": {
            "name": "Operator",
            "code": "operator",
            "color": "#64748b",  # Slate
            "level": 9,
            "description": "Basic operational role for task execution",
            "is_system_role": True
        },
        "viewer": {
            "name": "Viewer",
            "code": "viewer",
            "color": "#22c55e",  # Green
            "level": 10,
            "description": "Read-only access to assigned data",
            "is_system_role": True
        }
    }
    
    roles_created = 0
    for code, role_data in SYSTEM_ROLES.items():
        existing = await db.roles.find_one({
            "code": code,
            "organization_id": organization_id
        })
        
        if not existing:
            role = {
                "id": str(uuid.uuid4()),
                "organization_id": organization_id,
                "name": role_data["name"],
                "code": role_data["code"],
                "color": role_data["color"],
                "level": role_data["level"],
                "description": role_data["description"],
                "parent_role_id": None,
                "is_system_role": role_data["is_system_role"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.roles.insert_one(role)
            roles_created += 1
            print(f"  ✅ Created system role: {role_data['name']}")
    
    if roles_created == 0:
        print(f"  ℹ️  All system roles already exist for this organization")
    else:
        print(f"  ✅ Created {roles_created} new system roles")
    
    # Get total count for this organization
    total_roles = await db.roles.count_documents({"organization_id": organization_id})
    print(f"  📊 Total roles for this organization: {total_roles}")


if __name__ == "__main__":
    asyncio.run(initialize_phase1_data())