"""
Script to find the production user by email
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'operational_platform')
TARGET_EMAIL = "llewellyn@bluedawncapital.co.za"


async def find_user():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"Searching for user: {TARGET_EMAIL}")
    print("="*80)
    
    # Search by exact email
    user = await db.users.find_one({"email": TARGET_EMAIL})
    
    if user:
        print("✅ USER FOUND:")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
        print(f"   User ID: {user.get('user_id')}")
        print(f"   Organization ID: {user.get('organization_id')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Status: {user.get('status', 'N/A')}")
        print(f"   Is Active: {user.get('is_active', 'N/A')}")
    else:
        print("❌ USER NOT FOUND - Searching for similar emails...")
        # Search for similar emails
        cursor = db.users.find({"email": {"$regex": "llewellyn", "$options": "i"}})
        users = await cursor.to_list(length=10)
        
        if users:
            print(f"\nFound {len(users)} users with similar email:")
            for u in users:
                print(f"  - {u.get('email')} | Name: {u.get('name')} | ID: {u.get('user_id')}")
        else:
            print("\nNo similar users found. Showing all users:")
            cursor = db.users.find({}).limit(20)
            all_users = await cursor.to_list(length=20)
            for u in all_users:
                print(f"  - {u.get('email')} | Name: {u.get('name')} | ID: {u.get('user_id')}")


if __name__ == "__main__":
    asyncio.run(find_user())
