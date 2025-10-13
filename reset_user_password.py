"""
Reset user password directly in database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    # User details
    email = "Llewellyn@bluedawncapital.co.za"
    new_password = "BlueCapital2024!"
    
    print(f"\n🔐 Resetting password for: {email}")
    print("="*70)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operations_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Find user
    print(f"\n1️⃣ Looking up user...")
    user = await db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found with email: {email}")
        print(f"\n💡 Checking for similar emails...")
        
        # Try case-insensitive search
        user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
        
        if user:
            print(f"✅ Found user with email: {user['email']}")
        else:
            # Show all emails that contain parts of the search
            similar_users = await db.users.find(
                {"email": {"$regex": "llewellyn|bluedawn", "$options": "i"}},
                {"email": 1, "name": 1}
            ).to_list(10)
            
            if similar_users:
                print(f"\n📧 Found similar email addresses:")
                for u in similar_users:
                    print(f"   - {u['email']} (Name: {u.get('name', 'N/A')})")
            else:
                print(f"❌ No similar users found")
            
            await client.close()
            return False
    
    print(f"✅ User found: {user['name']} ({user['email']})")
    print(f"   User ID: {user['id']}")
    print(f"   Organization: {user.get('organization_id', 'N/A')}")
    print(f"   Role: {user.get('role', 'N/A')}")
    
    # Hash new password
    print(f"\n2️⃣ Hashing new password...")
    new_password_hash = pwd_context.hash(new_password)
    print(f"✅ Password hashed successfully")
    
    # Update password
    print(f"\n3️⃣ Updating password in database...")
    from datetime import datetime, timezone
    
    result = await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": new_password_hash,
                "password_changed_at": datetime.now(timezone.utc).isoformat(),
                "password_reset_token": None,
                "password_reset_expires_at": None,
                "failed_login_attempts": 0,
                "account_locked_until": None
            }
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ Password updated successfully!")
    else:
        print(f"⚠️  No changes made (password may already be set)")
    
    # Verify the update
    print(f"\n4️⃣ Verifying password...")
    updated_user = await db.users.find_one({"id": user["id"]})
    
    # Test the password
    if pwd_context.verify(new_password, updated_user["password_hash"]):
        print(f"✅ Password verification successful!")
    else:
        print(f"❌ Password verification failed!")
        await client.close()
        return False
    
    await client.close()
    
    print("\n" + "="*70)
    print("🎉 PASSWORD RESET COMPLETE!")
    print("="*70)
    print(f"\n📧 Email: {email}")
    print(f"🔑 New Password: {new_password}")
    print(f"\n✅ You can now login at: http://localhost:3000/login")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(reset_password())
    if not success:
        print("\n❌ Password reset failed")
