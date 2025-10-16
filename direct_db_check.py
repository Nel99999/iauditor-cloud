"""
Direct MongoDB Database Check
Verifies database connection and counts directly from MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def check_database():
    print("=" * 80)
    print("DIRECT MONGODB DATABASE CHECK")
    print("=" * 80)
    
    # Get MongoDB connection details
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    
    print(f"MongoDB URL: {mongo_url}")
    print(f"Database Name: {db_name}")
    print()
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await db.command('ping')
        print("✅ MongoDB connection successful")
        print()
        
        # Check collections
        collections = await db.list_collection_names()
        print(f"📊 Collections in '{db_name}' database:")
        for coll in sorted(collections):
            print(f"   - {coll}")
        print()
        
        # Count documents in key collections
        print("=" * 80)
        print("DOCUMENT COUNTS")
        print("=" * 80)
        
        # Users count
        users_count = await db.users.count_documents({})
        print(f"👥 Users: {users_count}")
        if users_count == 401:
            print("   ✅ CORRECT: 401 users found (operational_platform)")
        elif users_count == 1:
            print("   ❌ WRONG: Only 1 user found (wrong database!)")
        else:
            print(f"   ⚠️  Unexpected count: {users_count}")
        print()
        
        # Organizations count
        orgs_count = await db.organizations.count_documents({})
        print(f"🏢 Organizations: {orgs_count}")
        if orgs_count == 295:
            print("   ✅ CORRECT: 295 organizations found (operational_platform)")
        elif orgs_count == 1:
            print("   ❌ WRONG: Only 1 organization found (wrong database!)")
        else:
            print(f"   ⚠️  Unexpected count: {orgs_count}")
        print()
        
        # Permissions count
        perms_count = await db.permissions.count_documents({})
        print(f"🔐 Permissions: {perms_count}")
        if perms_count == 26:
            print("   ✅ CORRECT: 26 permissions found")
        else:
            print(f"   ⚠️  Expected 26, found {perms_count}")
        print()
        
        # Check for approval_status field in users
        print("=" * 80)
        print("APPROVAL SYSTEM CHECK")
        print("=" * 80)
        
        # Sample a few users to check for approval_status
        sample_users = await db.users.find({}).limit(10).to_list(10)
        users_with_approval = [u for u in sample_users if 'approval_status' in u]
        
        print(f"📋 Checked {len(sample_users)} sample users")
        print(f"   {len(users_with_approval)} have 'approval_status' field")
        
        if len(users_with_approval) == len(sample_users):
            print("   ✅ All sampled users have approval_status field")
        elif len(users_with_approval) > 0:
            print(f"   ⚠️  Only {len(users_with_approval)}/{len(sample_users)} users have approval_status")
        else:
            print("   ❌ No users have approval_status field")
        
        # Show approval status distribution
        if users_with_approval:
            print("\n   Approval status distribution (sample):")
            for user in users_with_approval[:5]:
                status = user.get('approval_status', 'N/A')
                email = user.get('email', 'N/A')
                print(f"   - {email}: {status}")
        print()
        
        # Check roles
        print("=" * 80)
        print("ROLES CHECK")
        print("=" * 80)
        
        roles_count = await db.roles.count_documents({})
        print(f"👔 Roles: {roles_count}")
        
        # Get sample roles
        sample_roles = await db.roles.find({}).limit(5).to_list(5)
        if sample_roles:
            print("\n   Sample roles:")
            for role in sample_roles:
                name = role.get('name', 'N/A')
                code = role.get('code', 'N/A')
                print(f"   - {name} ({code})")
        print()
        
        # Final verdict
        print("=" * 80)
        print("FINAL VERDICT")
        print("=" * 80)
        
        if users_count >= 401 and orgs_count >= 295 and perms_count == 26:
            print("✅ SUCCESS: Backend is connected to operational_platform database")
            print("✅ All expected data found:")
            print(f"   - {users_count} users (expected 401+)")
            print(f"   - {orgs_count} organizations (expected 295+)")
            print(f"   - {perms_count} permissions (expected 26)")
        elif users_count == 1 and orgs_count == 1:
            print("❌ FAILURE: Backend appears to be connected to WRONG database")
            print("   Only 1 user and 1 organization found")
            print("   This suggests a test/development database, not operational_platform")
        else:
            print("⚠️  UNCLEAR: Database state is unexpected")
            print(f"   Users: {users_count} (expected 401+)")
            print(f"   Organizations: {orgs_count} (expected 295+)")
            print(f"   Permissions: {perms_count} (expected 26)")
        
        print("=" * 80)
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the check
if __name__ == "__main__":
    asyncio.run(check_database())
