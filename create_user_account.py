"""
Create user account directly in database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
import uuid
from datetime import datetime, timezone

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_account():
    # User details
    email = "Llewellyn@bluedawncapital.co.za"
    name = "Llewellyn"
    password = "BlueCapital2024!"
    org_name = "Blue Dawn Capital"
    
    print(f"\n🆕 Creating account for: {email}")
    print("="*70)
    
    # Connect to database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operations_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if user already exists
    print(f"\n1️⃣ Checking for existing user...")
    existing = await db.users.find_one({"email": email})
    
    if existing:
        print(f"⚠️  User already exists!")
        print(f"   Updating password instead...")
        
        password_hash = pwd_context.hash(password)
        await db.users.update_one(
            {"id": existing["id"]},
            {
                "$set": {
                    "password_hash": password_hash,
                    "password_changed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        client.close()
        print(f"✅ Password updated!")
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password: {password}")
        return True
    
    print(f"✅ No existing user found")
    
    # Create organization
    print(f"\n2️⃣ Creating organization: {org_name}")
    org_id = str(uuid.uuid4())
    
    org_data = {
        "id": org_id,
        "name": org_name,
        "owner_id": "",  # Will update after user creation
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.organizations.insert_one(org_data.copy())
    print(f"✅ Organization created: {org_id}")
    
    # Hash password
    print(f"\n3️⃣ Hashing password...")
    password_hash = pwd_context.hash(password)
    print(f"✅ Password hashed")
    
    # Create user
    print(f"\n4️⃣ Creating user account...")
    user_id = str(uuid.uuid4())
    
    user_data = {
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "auth_provider": "local",
        "organization_id": org_id,
        "role": "master",  # Highest role
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "mfa_enabled": False,
        "email_verified": True,
        "failed_login_attempts": 0
    }
    
    await db.users.insert_one(user_data.copy())
    print(f"✅ User created: {user_id}")
    
    # Update organization owner
    print(f"\n5️⃣ Setting organization owner...")
    await db.organizations.update_one(
        {"id": org_id},
        {"$set": {"owner_id": user_id}}
    )
    print(f"✅ Organization ownership set")
    
    # Initialize system roles for the organization
    print(f"\n6️⃣ Initializing system roles...")
    
    system_roles = [
        {"name": "master", "level": 10, "description": "Full system access"},
        {"name": "admin", "level": 9, "description": "Administrative access"},
        {"name": "developer", "level": 8, "description": "Developer access"},
        {"name": "manager", "level": 7, "description": "Management access"},
        {"name": "supervisor", "level": 6, "description": "Supervisory access"},
        {"name": "lead", "level": 5, "description": "Team lead access"},
        {"name": "senior", "level": 4, "description": "Senior staff access"},
        {"name": "staff", "level": 3, "description": "Standard staff access"},
        {"name": "inspector", "level": 2, "description": "Inspector access"},
        {"name": "viewer", "level": 1, "description": "Read-only access"}
    ]
    
    for role_data in system_roles:
        role = {
            "id": str(uuid.uuid4()),
            "name": role_data["name"],
            "organization_id": org_id,
            "level": role_data["level"],
            "description": role_data["description"],
            "is_system_role": True,
            "permissions": []
        }
        await db.roles.insert_one(role.copy())
    
    print(f"✅ {len(system_roles)} system roles initialized")
    
    client.close()
    
    print("\n" + "="*70)
    print("🎉 ACCOUNT CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n👤 Name: {name}")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🏢 Organization: {org_name}")
    print(f"👑 Role: Master (highest level)")
    print(f"\n✅ You can now login at: http://localhost:3000/login")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(create_account())
    if not success:
        print("\n❌ Account creation failed")
