"""
Database Cleanup Script
Retains only production user (llewellyn@bluedawncapital.co.za) and associated data
Cleans all test data from operational_platform database
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
PRODUCTION_ORG_ID = "315fa36c-4555-4b2b-8ba3-fdbde31cb940"

# Collections to completely wipe (test data only)
COLLECTIONS_TO_WIPE = [
    'approval_chains', 'approvals', 'audit_logs', 'delegations',
    'gdpr_exports', 'mentions', 'notification_preferences', 'notifications',
    'sla_configs', 'subtasks', 'time_based_permissions', 'time_entries',
    'user_consents', 'user_deactivations', 'user_function_overrides',
    'user_groups', 'user_invitations', 'webhook_deliveries', 'webhooks',
    'workflow_instances', 'workflow_templates'
]

# Collections to selectively clean (keep production data)
COLLECTIONS_TO_CLEAN = {
    'users': {'email': PRODUCTION_USER_EMAIL},
    'organizations': {'organization_id': PRODUCTION_ORG_ID},
    'organization_units': {'organization_id': PRODUCTION_ORG_ID},
    'organization_settings': {'organization_id': PRODUCTION_ORG_ID},
    'inspection_templates': {'organization_id': PRODUCTION_ORG_ID},
    'inspection_executions': {'organization_id': PRODUCTION_ORG_ID},
    'checklist_templates': {'organization_id': PRODUCTION_ORG_ID},
    'checklist_executions': {'organization_id': PRODUCTION_ORG_ID},
    'tasks': {'organization_id': PRODUCTION_ORG_ID},
    'invitations': {'organization_id': PRODUCTION_ORG_ID},
    'user_preferences': {'organization_id': PRODUCTION_ORG_ID}
}

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
    """Verify production user and organization exist"""
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
    else:
        print(f"❌ ERROR: Production user {PRODUCTION_USER_EMAIL} not found!")
        return False
    
    # Check organization
    org = await db.organizations.find_one({"organization_id": PRODUCTION_ORG_ID})
    if org:
        print(f"✅ Production Organization Found:")
        print(f"   Name: {org.get('name')}")
        print(f"   ID: {org.get('organization_id')}")
    else:
        print(f"❌ ERROR: Production organization {PRODUCTION_ORG_ID} not found!")
        return False
    
    print("="*80)
    return True


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


async def clean_selective_collections(db):
    """Keep only production data, delete everything else"""
    print("\n" + "="*80)
    print("STEP 2: CLEANING SELECTIVE COLLECTIONS (KEEP PRODUCTION DATA)")
    print("="*80)
    
    total_deleted = 0
    total_kept = 0
    
    for collection_name, filter_fields in COLLECTIONS_TO_CLEAN.items():
        count_before = await db[collection_name].count_documents({})
        
        # Build delete query (everything NOT matching production data)
        if 'email' in filter_fields:
            delete_query = {"email": {"$ne": filter_fields['email']}}
            keep_query = {"email": filter_fields['email']}
        elif 'organization_id' in filter_fields:
            delete_query = {"organization_id": {"$ne": filter_fields['organization_id']}}
            keep_query = {"organization_id": filter_fields['organization_id']}
        else:
            continue
        
        # Count documents to keep
        count_to_keep = await db[collection_name].count_documents(keep_query)
        
        # Delete non-production data
        result = await db[collection_name].delete_many(delete_query)
        total_deleted += result.deleted_count
        total_kept += count_to_keep
        
        print(f"  ✅ {collection_name}:")
        print(f"     Before: {count_before} | Deleted: {result.deleted_count} | Kept: {count_to_keep}")
    
    print(f"\n  TOTAL DELETED FROM SELECTIVE COLLECTIONS: {total_deleted}")
    print(f"  TOTAL PRODUCTION DATA KEPT: {total_kept}")
    print("="*80)
    return total_deleted, total_kept


async def wipe_system_collections(db):
    """Delete all system collections (will auto-recreate on app start)"""
    print("\n" + "="*80)
    print("STEP 3: WIPING SYSTEM COLLECTIONS (WILL AUTO-RECREATE)")
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
    print("STEP 4: WIPING GRIDFS FILE STORAGE")
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
    user = await db.users.find_one({"user_id": PRODUCTION_USER_ID})
    if user:
        print(f"✅ Production User Preserved:")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
    else:
        print(f"❌ ERROR: Production user was accidentally deleted!")
    
    # Verify production organization still exists
    org = await db.organizations.find_one({"organization_id": PRODUCTION_ORG_ID})
    if org:
        print(f"✅ Production Organization Preserved:")
        print(f"   Name: {org.get('name')}")
    else:
        print(f"❌ ERROR: Production organization was accidentally deleted!")
    
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
    print("DATABASE CLEANUP SCRIPT")
    print("="*80)
    print(f"Target Database: {DB_NAME}")
    print(f"Production User: {PRODUCTION_USER_EMAIL}")
    print(f"Production Org ID: {PRODUCTION_ORG_ID}")
    print("="*80)
    
    # Connect to database
    db = await connect_db()
    
    # Get initial statistics
    initial_stats, initial_total = await get_collection_stats(db)
    
    # Verify production data exists
    if not await verify_production_data(db):
        print("\n❌ CLEANUP ABORTED - Production data not found!")
        return
    
    # Confirmation
    print("\n" + "="*80)
    print("⚠️  WARNING: This will delete ALL test data!")
    print("⚠️  Only the following will be preserved:")
    print(f"   - User: {PRODUCTION_USER_EMAIL}")
    print(f"   - Organization ID: {PRODUCTION_ORG_ID}")
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
    deleted_selective, kept_selective = await clean_selective_collections(db)
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
    print(f"  Production Data Preserved: {kept_selective} documents")
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
