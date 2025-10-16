"""
Script to find the production organization
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'operational_platform')
TARGET_ORG_ID = "315fa36c-4555-4b2b-8ba3-fdbde31cb940"
TARGET_EMAIL = "llewellyn@bluedawncapital.co.za"


async def find_org():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # First find the user
    user = await db.users.find_one({"email": TARGET_EMAIL})
    if user:
        print("✅ USER FOUND:")
        print(f"   Email: {user.get('email')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Organization ID from user: {user.get('organization_id')}")
        
        # Search for organization with this ID
        if user.get('organization_id'):
            org = await db.organizations.find_one({"organization_id": user.get('organization_id')})
            if org:
                print(f"\n✅ ORGANIZATION FOUND:")
                print(f"   Name: {org.get('name')}")
                print(f"   Organization ID: {org.get('organization_id')}")
            else:
                print(f"\n❌ Organization with ID {user.get('organization_id')} not found")
                print("\nSearching all organizations...")
                cursor = db.organizations.find({}).limit(10)
                orgs = await cursor.to_list(length=10)
                print(f"Found {len(orgs)} organizations:")
                for o in orgs:
                    print(f"  - {o.get('name')} | ID: {o.get('organization_id')}")
    else:
        print("❌ User not found")


if __name__ == "__main__":
    asyncio.run(find_org())
