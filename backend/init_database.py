"""Database initialization script for Phase 1"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


async def initialize_phase1_database():
    """Initialize all Phase 1 collections and indexes"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 80)
    print("🚀 PHASE 1 DATABASE INITIALIZATION")
    print("=" * 80)
    
    # Create collections
    collections_to_create = [
        'permissions',
        'role_permissions',
        'user_function_overrides',
        'roles',
        'invitations',
        'user_deactivations',
        'approval_chains',
        'approvals',
        'audit_logs'
    ]
    
    existing_collections = await db.list_collection_names()
    
    for collection_name in collections_to_create:
        if collection_name not in existing_collections:
            await db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"ℹ️  Collection already exists: {collection_name}")
    
    # Create indexes
    print("\n📊 Creating indexes...")
    
    # Permissions indexes
    await db.permissions.create_index([("resource_type", 1), ("action", 1), ("scope", 1)], unique=True)
    print("✅ Created index: permissions (resource_type, action, scope)")
    
    # Role permissions indexes
    await db.role_permissions.create_index([("role_id", 1), ("permission_id", 1)])
    print("✅ Created index: role_permissions (role_id, permission_id)")
    
    # User function overrides indexes
    await db.user_function_overrides.create_index([("user_id", 1), ("permission_id", 1)])
    print("✅ Created index: user_function_overrides (user_id, permission_id)")
    
    # Roles indexes
    await db.roles.create_index([("organization_id", 1), ("code", 1)], unique=True)
    await db.roles.create_index([("level", 1)])
    print("✅ Created index: roles (organization_id, code)")
    
    # Invitations indexes
    await db.invitations.create_index([("token", 1)], unique=True)
    await db.invitations.create_index([("email", 1), ("organization_id", 1)])
    await db.invitations.create_index([("status", 1)])
    await db.invitations.create_index([("expires_at", 1)])
    print("✅ Created index: invitations (token, email, status)")
    
    # User deactivations indexes
    await db.user_deactivations.create_index([("user_id", 1)])
    await db.user_deactivations.create_index([("deactivated_at", 1)])
    print("✅ Created index: user_deactivations (user_id, deactivated_at)")
    
    # Approval chains indexes
    await db.approval_chains.create_index([("approvable_type", 1), ("approvable_id", 1)])
    await db.approval_chains.create_index([("organization_id", 1), ("status", 1)])
    print("✅ Created index: approval_chains (approvable_type, approvable_id)")
    
    # Approvals indexes
    await db.approvals.create_index([("approval_chain_id", 1)])
    await db.approvals.create_index([("user_id", 1)])
    print("✅ Created index: approvals (approval_chain_id, user_id)")
    
    # Audit logs indexes
    await db.audit_logs.create_index([("user_id", 1)])
    await db.audit_logs.create_index([("organization_id", 1), ("created_at", -1)])
    await db.audit_logs.create_index([("resource_type", 1), ("resource_id", 1)])
    print("✅ Created index: audit_logs (user_id, organization_id, resource)")
    
    print("\n" + "=" * 80)
    print("✅ PHASE 1 DATABASE INITIALIZATION COMPLETE")
    print("=" * 80)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_phase1_database())