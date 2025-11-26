import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from passlib.context import CryptContext

# Setup paths and load env
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_master_user():
    # DB Connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    
    print(f"Connecting to database: {db_name} at {mongo_url.split('@')[-1] if '@' in mongo_url else 'localhost'}")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check connection
    try:
        await db.command('ping')
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # 1. Create Organization
    org_name = "System Administration"
    existing_org = await db.organizations.find_one({"name": org_name})
    
    if existing_org:
        org_id = existing_org['id']
        print(f"ℹ️  Using existing organization: {org_name} ({org_id})")
    else:
        org_id = str(uuid.uuid4())
        org_doc = {
            "id": org_id,
            "name": org_name,
            "description": "Master organization for system administrators",
            "owner_id": "", # Will update later
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.organizations.insert_one(org_doc)
        print(f"✅ Created organization: {org_name} ({org_id})")

    # 2. Create Master User
    email = "master@opsplatform.com"
    password = "MasterPassword123!"
    
    existing_user = await db.users.find_one({"email": email})
    
    if existing_user:
        print(f"ℹ️  User {email} already exists. Updating password...")
        await db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "password_hash": get_password_hash(password),
                    "role": "master",
                    "approval_status": "approved",
                    "is_active": True,
                    "organization_id": org_id,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        print(f"✅ Updated user {email} with new password and master role.")
    else:
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": email,
            "name": "System Master",
            "password_hash": get_password_hash(password),
            "auth_provider": "local",
            "organization_id": org_id,
            "role": "master",
            "is_active": True,
            "approval_status": "approved", # Auto-approve master
            "invited": False,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "mfa_enabled": False
        }
        await db.users.insert_one(user_doc)
        print(f"✅ Created new master user: {email}")
        
        # Update org owner if needed
        if not existing_org or not existing_org.get('owner_id'):
            await db.organizations.update_one(
                {"id": org_id},
                {"$set": {"owner_id": user_id}}
            )
            print(f"✅ Set {email} as owner of {org_name}")

    print("\n" + "="*50)
    print("🎉 MASTER USER CREATED SUCCESSFULLY")
    print("="*50)
    print(f"Email:    {email}")
    print(f"Password: {password}")
    print("="*50)
    print("⚠️  Please change this password after logging in!")

    client.close()

if __name__ == "__main__":
    asyncio.run(create_master_user())
