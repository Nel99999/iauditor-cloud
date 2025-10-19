#!/usr/bin/env python3
"""
Helper script to create test users directly in MongoDB
"""

from pymongo import MongoClient
import bcrypt
import uuid
from datetime import datetime, timezone

# Configuration
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "operational_platform"
ORGANIZATION_ID = "315fa36c-4555-4b2b-8ba3-fdbde31cb940"

def create_test_users():
    """Create test users with different roles"""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    timestamp = int(datetime.now().timestamp())
    
    users_to_create = [
        {
            "role_name": "master",
            "email": f"master_test_{timestamp}@example.com",
            "name": "Master Test User",
            "password": "Test@1234"
        },
        {
            "role_name": "admin",
            "email": f"admin_test_{timestamp}@example.com",
            "name": "Admin Test User",
            "password": "Test@1234"
        },
        {
            "role_name": "manager",
            "email": f"manager_test_{timestamp}@example.com",
            "name": "Manager Test User",
            "password": "Test@1234"
        },
        {
            "role_name": "viewer",
            "email": f"viewer_test_{timestamp}@example.com",
            "name": "Viewer Test User",
            "password": "Test@1234"
        }
    ]
    
    created_users = []
    
    for user_info in users_to_create:
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash = bcrypt.hashpw(user_info["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user document
        now = datetime.now(timezone.utc).isoformat()
        user_doc = {
            "id": user_id,
            "email": user_info["email"],
            "name": user_info["name"],
            "password_hash": password_hash,
            "auth_provider": "local",
            "organization_id": ORGANIZATION_ID,
            "role": user_info["role_name"],
            "approval_status": "approved",
            "is_active": True,
            "invited": False,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "failed_login_attempts": 0,
            "account_locked_until": None
        }
        
        # Insert into MongoDB
        try:
            result = db.users.insert_one(user_doc)
            print(f"✅ Created {user_info['role_name']} user: {user_info['email']} (ID: {user_id})")
            created_users.append({
                "role": user_info["role_name"],
                "email": user_info["email"],
                "password": user_info["password"],
                "id": user_id
            })
        except Exception as e:
            print(f"❌ Failed to create {user_info['role_name']} user: {str(e)}")
    
    client.close()
    return created_users

if __name__ == "__main__":
    print("Creating test users in MongoDB...")
    users = create_test_users()
    print(f"\n✅ Created {len(users)} test users")
    print("\nTest user credentials:")
    for user in users:
        print(f"  {user['role']}: {user['email']} / {user['password']}")
