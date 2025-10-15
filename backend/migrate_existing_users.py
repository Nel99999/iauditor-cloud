"""
Migration script to update existing users with new approval fields
Run this ONCE after deploying the new User model
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os


async def migrate_users():
    """Migrate existing users to have approval status fields"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    db_name = os.environ.get('DB_NAME', 'operational_platform')  # Use environment variable or default
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"📡 Connecting to database: {db_name}")
    
    print("🔄 Starting user migration...")
    
    # Get all users
    users = await db.users.find({}).to_list(length=None)
    total_users = len(users)
    
    if total_users == 0:
        print("ℹ️  No users found to migrate")
        return
    
    print(f"📊 Found {total_users} users to migrate")
    
    migrated_count = 0
    skipped_count = 0
    
    for user in users:
        user_id = user.get("id")
        email = user.get("email")
        
        # Check if user already has approval_status field
        if "approval_status" in user:
            print(f"⏭️  Skipping {email} - already migrated")
            skipped_count += 1
            continue
        
        # Prepare update data
        update_data = {
            "approval_status": "approved",  # Grandfather existing users
            "approved_by": None,  # System migration
            "approved_at": user.get("created_at", datetime.now(timezone.utc).isoformat()),
            "approval_notes": "Auto-approved during migration",
            "registration_ip": None,
            "invited": False  # Existing users weren't invited
        }
        
        # Update user
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Migrated {email} - set to approved")
            migrated_count += 1
        else:
            print(f"⚠️  Failed to migrate {email}")
    
    print("\n" + "="*60)
    print("📈 MIGRATION SUMMARY")
    print("="*60)
    print(f"Total users found:    {total_users}")
    print(f"Successfully migrated: {migrated_count}")
    print(f"Already migrated:      {skipped_count}")
    print(f"Failed:                {total_users - migrated_count - skipped_count}")
    print("="*60)
    print("✅ Migration completed!")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_users())
