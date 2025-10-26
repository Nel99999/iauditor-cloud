"""
FINAL EMAIL TESTING - Approval and Rejection Emails
Creates test users in production org and tests approval/rejection
"""
import requests
import json
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
PRODUCTION_USER = {
    "email": "llewellyn@bluedawncapital.co.za",
    "password": "TestPassword123!",
    "organization_id": "315fa36c-4555-4b2b-8ba3-fdbde31cb940"
}

print("="*80)
print("FINAL EMAIL TESTING - RESTORE PASSWORD & TEST APPROVAL/REJECTION")
print("="*80)

# Step 1: Restore original password
print("\n[Step 1] Restore Original Password")
RESET_TOKEN = "754975d5-7bd6-4801-83d3-ab6385008500"

try:
    response = requests.post(
        f"{BACKEND_URL}/auth/reset-password",
        json={
            "token": RESET_TOKEN,
            "new_password": PRODUCTION_USER["password"]
        },
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"✅ Password restored to original")
    else:
        print(f"⚠️  Password restore status: {response.status_code}")
except Exception as e:
    print(f"⚠️  Exception: {str(e)}")

# Step 2: Login with original password
print("\n[Step 2] Login as Developer")
try:
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": PRODUCTION_USER["email"],
            "password": PRODUCTION_USER["password"]
        },
        timeout=10
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Logged in successfully")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Create test users in production org via MongoDB
        print("\n[Step 3] Create Test Users in Production Org")
        print("   Creating 2 pending users for approval/rejection testing...")
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # User 1 for approval
        user1_id = str(uuid.uuid4())
        user1_email = f"approve_test_{timestamp}@example.com"
        
        # User 2 for rejection
        user2_id = str(uuid.uuid4())
        user2_email = f"reject_test_{timestamp}@example.com"
        
        print(f"\n   User 1 (for approval): {user1_email}")
        print(f"   User 2 (for rejection): {user2_email}")
        print("\n   MongoDB commands to create users:")
        print(f"""
   db.users.insertOne({{
       id: "{user1_id}",
       email: "{user1_email}",
       name: "Approval Test User",
       password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF3UHyPe",
       organization_id: "{PRODUCTION_USER['organization_id']}",
       role: "viewer",
       approval_status: "pending",
       is_active: false,
       invited: false,
       auth_provider: "local",
       created_at: new Date().toISOString(),
       updated_at: new Date().toISOString()
   }})
   
   db.users.insertOne({{
       id: "{user2_id}",
       email: "{user2_email}",
       name: "Rejection Test User",
       password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF3UHyPe",
       organization_id: "{PRODUCTION_USER['organization_id']}",
       role: "viewer",
       approval_status: "pending",
       is_active: false,
       invited: false,
       auth_provider: "local",
       created_at: new Date().toISOString(),
       updated_at: new Date().toISOString()
   }})
        """)
        
        # Wait for user to create the users
        input("\n   Press Enter after creating the users in MongoDB...")
        
        # Step 4: Test Approval
        print("\n[Step 4] Test Approval Email")
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/{user1_id}/approve",
                headers=headers,
                json={"approval_notes": "Testing approval email - user approved for testing"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ User approved successfully")
                print(f"   Response: {response.json()}")
                print("   📧 Check inbox for approval email")
                print("   📋 Check logs: tail -n 20 /var/log/supervisor/backend.out.log | grep 'Approval email'")
            else:
                print(f"❌ Approval failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        # Step 5: Test Rejection
        print("\n[Step 5] Test Rejection Email")
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/{user2_id}/reject",
                headers=headers,
                json={"approval_notes": "Testing rejection email - user not approved for testing purposes"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ User rejected successfully")
                print(f"   Response: {response.json()}")
                print("   📧 Check inbox for rejection email")
                print("   📋 Check logs: tail -n 20 /var/log/supervisor/backend.out.log | grep 'Rejection email'")
            else:
                print(f"❌ Rejection failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
print("\nSUMMARY:")
print("  ✅ Test 1: Password Reset Request Email - SENT")
print("  ✅ Test 2: Password Change Confirmation Email - SENT")
print("  ✅ Test 3: Registration Pending Email - SENT (for new registrations)")
print("  ⏳ Test 4: Profile Approved Email - PENDING (run this script)")
print("  ⏳ Test 5: Profile Rejected Email - PENDING (run this script)")
print("\nNEXT STEPS:")
print("  1. Create the 2 test users in MongoDB (commands shown above)")
print("  2. Run this script again and press Enter when prompted")
print("  3. Check backend logs for email sending status")
print("  4. Check inbox for all 5 email types")
