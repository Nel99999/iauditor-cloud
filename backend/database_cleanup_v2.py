"""
Simplified Database Cleanup Script
Retains only production user (llewellyn@bluedawncapital.co.za) and directly associated data
Handles collections with various field structures
"""

import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'operational_platform')

# Target production data to KEEP
PRODUCTION_USER_EMAIL = "llewellyn@bluedawncapital.co.za"

# Collections to completely wipe (test data only)
COLLECTIONS_TO_WIPE = [
    'approval_chains', 'approvals', 'audit_logs', 'delegations',
    'gdpr_exports', 'mentions', 'notification_preferences', 'notifications',
    'sla_configs', 'subtasks', 'time_based_permissions', 'time_entries',
    'user_consents', 'user_deactivations', 'user_function_overrides',
    'user_groups', 'user_invitations', 'webhook_deliveries', 'webhooks',
    'workflow_instances', 'workflow_templates'
]

# System collections to completely wipe (will auto-recreate)
SYSTEM_COLLECTIONS = ['roles', 'permissions', 'role_permissions', 'permission_contexts']

# GridFS collections
GRIDFS_COLLECTIONS = ['fs.files', 'fs.chunks']


async def connect_db():
    """Connect to MongoDB"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"✅ Connected to database: {DB_NAME}")
    return db


async def get_collection_stats(db):
    """Get document counts for all collections before cleanup"""
    print("\n" + "="*80)
    print("CURRENT DATABASE STATE - BEFORE CLEANUP")
    print("="*80)
    
    collection_names = await db.list_collection_names()
    total_docs = 0
    stats = {}
    
    for collection_name in sorted(collection_names):
        count = await db[collection_name].count_documents({})
        stats[collection_name] = count
        total_docs += count
        print(f"  {collection_name}: {count} documents")
    
    print(f"\n  TOTAL DOCUMENTS: {total_docs}")
    print("="*80)
    return stats, total_docs


async def verify_production_data(db):
    """Verify production user exists"""
    print("\n" + "="*80)
    print("VERIFYING PRODUCTION DATA EXISTS")
    print("="*80)
    
    # Check user
    user = await db.users.find_one({"email": PRODUCTION_USER_EMAIL})
    if user:
        print(f"✅ Production User Found:")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Role: {user.get('role')}")
        org_id = user.get('organization_id')
        print(f"   Organization ID: {org_id}")
        print("="*80)
        return True, org_id
    else:
        print(f"❌ ERROR: Production user {PRODUCTION_USER_EMAIL} not found!")
        print("="*80)
        return False, None


async def wipe_test_collections(db):
    """Delete all documents from test-only collections"""
    print("\n" + "="*80)
    print("STEP 1: WIPING TEST-ONLY COLLECTIONS")
    print("="*80)
    
    total_deleted = 0
    for collection_name in COLLECTIONS_TO_WIPE:
        count_before = await db[collection_name].count_documents({})
        if count_before > 0:
            result = await db[collection_name].delete_many({})
            total_deleted += result.deleted_count
            print(f"  ✅ {collection_name}: Deleted {result.deleted_count} documents")
        else:
            print(f"  ⚪ {collection_name}: Already empty (0 documents)")
    
    print(f"\n  TOTAL DELETED FROM TEST COLLECTIONS: {total_deleted}")
    print("="*80)
    return total_deleted


async def clean_users_collection(db):
    """Keep only production user"""
    print("\n" + "="*80)
    print("STEP 2: CLEANING USERS COLLECTION")
    print("="*80)
    
    count_before = await db.users.count_documents({})
    result = await db.users.delete_many({"email": {"$ne": PRODUCTION_USER_EMAIL}})
    count_after = await db.users.count_documents({})
    
    print(f"  Before: {count_before} users")
    print(f"  Deleted: {result.deleted_count} users")
    print(f"  Kept: {count_after} user (production)")
    print("="*80)
    return result.deleted_count


async def clean_org_based_collections(db, production_org_id):
    """Clean collections based on organization_id"""
    print("\n" + "="*80)
    print(f"STEP 3: CLEANING ORGANIZATION-BASED COLLECTIONS (ORG: {production_org_id})")
    print("="*80)
    
    org_collections = [
        'organizations',
        'organization_units',
        'organization_settings',
        'inspection_templates',
        'inspection_executions',
        'checklist_templates',
        'checklist_executions',
        'tasks',
        'invitations',
        'user_preferences'
    ]
    
    total_deleted = 0
    total_kept = 0
    
    for collection_name in org_collections:
        count_before = await db[collection_name].count_documents({})
        
        # Delete documents NOT matching production org_id
        result = await db[collection_name].delete_many({
            "organization_id": {"$ne": production_org_id}
        })
        
        count_after = await db[collection_name].count_documents({})
        
        total_deleted += result.deleted_count
        total_kept += count_after
        
        print(f"  ✅ {collection_name}:")
        print(f"     Before: {count_before} | Deleted: {result.deleted_count} | Kept: {count_after}")
    
    print(f"\n  TOTAL DELETED: {total_deleted}")
    print(f"  TOTAL KEPT: {total_kept}")
    print("="*80)
    return total_deleted, total_kept


async def wipe_system_collections(db):
    """Delete all system collections (will auto-recreate on app start)"""
    print("\n" + "="*80)
    print("STEP 4: WIPING SYSTEM COLLECTIONS (WILL AUTO-RECREATE)")
    print("="*80)
    
    total_deleted = 0
    for collection_name in SYSTEM_COLLECTIONS:
        count_before = await db[collection_name].count_documents({})
        if count_before > 0:
            result = await db[collection_name].delete_many({})
            total_deleted += result.deleted_count
            print(f"  ✅ {collection_name}: Deleted {result.deleted_count} documents")
        else:
            print(f"  ⚪ {collection_name}: Already empty (0 documents)")
    
    print(f"\n  TOTAL DELETED FROM SYSTEM COLLECTIONS: {total_deleted}")
    print("="*80)
    return total_deleted


async def wipe_gridfs_files(db):
    """Delete all GridFS file storage"""
    print("\n" + "="*80)
    print("STEP 5: WIPING GRIDFS FILE STORAGE")
    print("="*80)
    
    total_deleted = 0
    for collection_name in GRIDFS_COLLECTIONS:
        count_before = await db[collection_name].count_documents({})
        if count_before > 0:
            result = await db[collection_name].delete_many({})
            total_deleted += result.deleted_count
            print(f"  ✅ {collection_name}: Deleted {result.deleted_count} documents")
        else:
            print(f"  ⚪ {collection_name}: Already empty (0 documents)")
    
    print(f"\n  TOTAL DELETED FROM GRIDFS: {total_deleted}")
    print("="*80)
    return total_deleted


async def verify_cleanup(db):
    """Verify cleanup results and show final state"""
    print("\n" + "="*80)
    print("CLEANUP VERIFICATION - AFTER CLEANUP")
    print("="*80)
    
    # Verify production user still exists
    user = await db.users.find_one({"email": PRODUCTION_USER_EMAIL})
    if user:
        print(f"✅ Production User Preserved:")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
    else:
        print(f"❌ ERROR: Production user was accidentally deleted!")
    
    # Count all documents
    print("\n📊 FINAL DOCUMENT COUNTS:")
    collection_names = await db.list_collection_names()
    total_docs = 0
    
    for collection_name in sorted(collection_names):
        count = await db[collection_name].count_documents({})
        if count > 0:
            total_docs += count
            print(f"  {collection_name}: {count} documents")
    
    print(f"\n  TOTAL DOCUMENTS REMAINING: {total_docs}")
    print("="*80)
    return total_docs


async def main():
    """Main cleanup execution"""
    print("\n" + "="*80)
    print("DATABASE CLEANUP SCRIPT - SIMPLIFIED")
    print("="*80)
    print(f"Target Database: {DB_NAME}")
    print(f"Production User: {PRODUCTION_USER_EMAIL}")
    print("="*80)
    
    # Connect to database
    db = await connect_db()
    
    # Get initial statistics
    initial_stats, initial_total = await get_collection_stats(db)
    
    # Verify production data exists and get org_id
    exists, production_org_id = await verify_production_data(db)
    if not exists:
        print("\n❌ CLEANUP ABORTED - Production data not found!")
        return
    
    # Confirmation
    print("\n" + "="*80)
    print("⚠️  WARNING: This will delete ALL test data!")
    print("⚠️  Only the following will be preserved:")
    print(f"   - User: {PRODUCTION_USER_EMAIL}")
    print(f"   - Organization ID: {production_org_id}")
    print(f"   - All associated production data")
    print("="*80)
    
    confirm = input("\nType 'CLEANUP' to proceed: ")
    if confirm != "CLEANUP":
        print("\n❌ Cleanup cancelled by user.")
        return
    
    print("\n🚀 Starting cleanup...")
    start_time = datetime.now()
    
    # Execute cleanup steps
    deleted_test = await wipe_test_collections(db)
    deleted_users = await clean_users_collection(db)
    deleted_org, kept_org = await clean_org_based_collections(db, production_org_id)
    deleted_system = await wipe_system_collections(db)
    deleted_gridfs = await wipe_gridfs_files(db)
    
    # Verify cleanup
    final_total = await verify_cleanup(db)
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"  Documents Before Cleanup: {initial_total}")
    print(f"  Documents After Cleanup: {final_total}")
    print(f"  Total Documents Deleted: {initial_total - final_total}")
    print(f"  Data Reduction: {((initial_total - final_total) / initial_total * 100):.1f}%")
    print(f"  Production Data Preserved: {kept_org + 1} documents")  # +1 for user
    print(f"  Execution Time: {duration:.2f} seconds")
    print("="*80)
    print("\n✅ DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
    print("\n📝 Next Steps:")
    print("   1. Restart backend server: sudo supervisorctl restart backend")
    print("   2. System collections (roles, permissions) will auto-recreate")
    print("   3. Verify production user can login")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
