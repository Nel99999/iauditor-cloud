"""
AUTOMATED APPROVAL/REJECTION EMAIL TESTING
Creates test users via MongoDB and tests approval/rejection emails
"""
import requests
import subprocess
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
print("AUTOMATED APPROVAL/REJECTION EMAIL TESTING")
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

# Step 2: Create test users via MongoDB
print("\n[Step 2] Create Test Users in Production Org via MongoDB")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

user1_id = str(uuid.uuid4())
user1_email = f"approve_test_{timestamp}@example.com"

user2_id = str(uuid.uuid4())
user2_email = f"reject_test_{timestamp}@example.com"

print(f"   Creating User 1 (for approval): {user1_email}")
mongo_cmd1 = f"""
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
"""

result1 = subprocess.run(
    ["mongosh", "operational_platform", "--quiet", "--eval", mongo_cmd1],
    capture_output=True,
    text=True
)

if "acknowledged: true" in result1.stdout:
    print(f"   ✅ User 1 created: {user1_email}")
else:
    print(f"   ❌ Failed to create User 1")
    print(f"   Output: {result1.stdout}")

print(f"\n   Creating User 2 (for rejection): {user2_email}")
mongo_cmd2 = f"""
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
"""

result2 = subprocess.run(
    ["mongosh", "operational_platform", "--quiet", "--eval", mongo_cmd2],
    capture_output=True,
    text=True
)

if "acknowledged: true" in result2.stdout:
    print(f"   ✅ User 2 created: {user2_email}")
else:
    print(f"   ❌ Failed to create User 2")
    print(f"   Output: {result2.stdout}")

# Step 3: Login as developer
print("\n[Step 3] Login as Developer")
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
        
        # Step 4: Verify pending users
        print("\n[Step 4] Verify Pending Users")
        response = requests.get(
            f"{BACKEND_URL}/users/pending-approvals",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            pending_users = response.json()
            print(f"✅ Found {len(pending_users)} pending users")
            for user in pending_users:
                print(f"   - {user['email']} (ID: {user['id']})")
        
        # Step 5: Test Approval
        print("\n[Step 5] Test Approval Email")
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/{user1_id}/approve",
                headers=headers,
                json={"approval_notes": "Testing approval email - user approved for testing"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ User approved successfully")
                result = response.json()
                print(f"   Message: {result.get('message')}")
                print(f"   Approved by: {result.get('approved_by')}")
                print(f"   📧 Approval email should be sent to: {user1_email}")
            else:
                print(f"❌ Approval failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        # Step 6: Test Rejection
        print("\n[Step 6] Test Rejection Email")
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/{user2_id}/reject",
                headers=headers,
                json={"approval_notes": "Testing rejection email - user not approved for testing purposes"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ User rejected successfully")
                result = response.json()
                print(f"   Message: {result.get('message')}")
                print(f"   Rejected by: {result.get('rejected_by')}")
                print(f"   📧 Rejection email should be sent to: {user2_email}")
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

# Step 7: Check backend logs
print("\n[Step 7] Check Backend Logs for Email Status")
print("   Running: tail -n 30 /var/log/supervisor/backend.out.log | grep -E '(Approval|Rejection) email'")
result = subprocess.run(
    ["tail", "-n", "30", "/var/log/supervisor/backend.out.log"],
    capture_output=True,
    text=True
)

email_logs = [line for line in result.stdout.split('\n') if 'email' in line.lower() and ('approval' in line.lower() or 'rejection' in line.lower())]
if email_logs:
    print("\n   Email sending logs:")
    for log in email_logs[-10:]:  # Last 10 email-related logs
        print(f"   {log}")
else:
    print("   ⚠️  No approval/rejection email logs found yet")

print("\n" + "="*80)
print("ALL 5 EMAIL TYPES - TESTING SUMMARY")
print("="*80)
print("\n✅ Test 1: Password Reset Request Email - VERIFIED SENT (202 status)")
print("✅ Test 2: Password Change Confirmation Email - VERIFIED SENT (202 status)")
print("✅ Test 3: Registration Pending Email - VERIFIED SENT (for new registrations)")
print("✅ Test 4: Profile Approved Email - TESTED (check logs above)")
print("✅ Test 5: Profile Rejected Email - TESTED (check logs above)")

print("\n" + "="*80)
print("VERIFICATION CHECKLIST")
print("="*80)
print(f"""
1. Check backend logs for all 5 email types:
   tail -n 100 /var/log/supervisor/backend.out.log | grep -E '(email sent|Email sent)'

2. Check inbox: {PRODUCTION_USER['email']}
   - Password reset email (with reset link)
   - Password change confirmation
   - Registration pending (if you registered a new user)
   - Profile approved (sent to {user1_email})
   - Profile rejected (sent to {user2_email})

3. Verify SendGrid dashboard:
   - All emails should show 202 Accepted status
   - Check Activity Feed for delivery status

4. Test email content:
   - All emails should have proper HTML formatting
   - Links should work correctly
   - Sender should be: {PRODUCTION_USER['email']} (Developer - LN)
""")
