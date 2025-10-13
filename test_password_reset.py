"""
Test Password Reset Functionality
"""
import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_password_reset_flow():
    """Test complete password reset flow"""
    print("\n" + "="*70)
    print("🔒 Testing Password Reset Functionality")
    print("="*70)
    
    # Step 1: Register a test user
    print("\n1️⃣ Registering test user...")
    import time
    timestamp = int(time.time())
    
    register_data = {
        "name": "Password Reset Test User",
        "email": f"reset.test.{timestamp}@test.com",
        "password": "OldPassword123!",
        "create_organization": True,
        "organization_name": "Reset Test Org"
    }
    
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if reg_resp.status_code not in [200, 201]:
        print(f"❌ Registration failed: {reg_resp.status_code} - {reg_resp.text}")
        return False
    
    user_data = reg_resp.json()
    email = register_data["email"]
    print(f"✅ User registered: {email}")
    
    # Step 2: Request password reset
    print("\n2️⃣ Requesting password reset...")
    forgot_resp = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": email}
    )
    
    if forgot_resp.status_code != 200:
        print(f"❌ Forgot password request failed: {forgot_resp.status_code}")
        return False
    
    forgot_data = forgot_resp.json()
    print(f"✅ Password reset requested")
    print(f"   Message: {forgot_data['message']}")
    
    # Step 3: Get reset token from database (simulating email click)
    print("\n3️⃣ Retrieving reset token from database...")
    from motor.motor_asyncio import AsyncIOMotorClient
    import asyncio
    import os
    
    async def get_reset_token():
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.operations_db
        
        user = await db.users.find_one({"email": email})
        token = user.get("password_reset_token")
        await client.close()
        return token
    
    reset_token = asyncio.run(get_reset_token())
    
    if not reset_token:
        print(f"❌ No reset token found in database")
        return False
    
    print(f"✅ Reset token retrieved: {reset_token[:20]}...")
    
    # Step 4: Reset password with token
    print("\n4️⃣ Resetting password with token...")
    reset_resp = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "NewPassword456!"
        }
    )
    
    if reset_resp.status_code != 200:
        print(f"❌ Password reset failed: {reset_resp.status_code} - {reset_resp.text}")
        return False
    
    reset_data = reset_resp.json()
    print(f"✅ Password reset successful")
    print(f"   Message: {reset_data['message']}")
    
    # Step 5: Try logging in with old password (should fail)
    print("\n5️⃣ Testing login with OLD password (should fail)...")
    login_old_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": "OldPassword123!"
        }
    )
    
    if login_old_resp.status_code == 200:
        print(f"❌ Login with old password succeeded (should have failed)")
        return False
    
    print(f"✅ Login with old password correctly rejected")
    
    # Step 6: Try logging in with new password (should succeed)
    print("\n6️⃣ Testing login with NEW password (should succeed)...")
    login_new_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": "NewPassword456!"
        }
    )
    
    if login_new_resp.status_code != 200:
        print(f"❌ Login with new password failed: {login_new_resp.status_code}")
        return False
    
    login_data = login_new_resp.json()
    print(f"✅ Login with new password successful")
    print(f"   Token: {login_data['access_token'][:30]}...")
    
    # Step 7: Try reusing the reset token (should fail)
    print("\n7️⃣ Testing token reuse (should fail)...")
    reuse_resp = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "AnotherPassword789!"
        }
    )
    
    if reuse_resp.status_code == 200:
        print(f"❌ Token reuse succeeded (should have failed)")
        return False
    
    print(f"✅ Token reuse correctly rejected")
    
    # Step 8: Test invalid token
    print("\n8️⃣ Testing invalid token (should fail)...")
    invalid_resp = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": "invalid-token-12345",
            "new_password": "NewPassword123!"
        }
    )
    
    if invalid_resp.status_code == 200:
        print(f"❌ Invalid token accepted (should have failed)")
        return False
    
    print(f"✅ Invalid token correctly rejected")
    
    # Step 9: Test password too short
    print("\n9️⃣ Testing short password validation...")
    short_pass_resp = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": email}
    )
    
    if short_pass_resp.status_code == 200:
        # Get new token
        new_token = asyncio.run(get_reset_token())
        
        short_reset_resp = requests.post(
            f"{BASE_URL}/auth/reset-password",
            json={
                "token": new_token,
                "new_password": "123"  # Too short
            }
        )
        
        if short_reset_resp.status_code == 200:
            print(f"❌ Short password accepted (should have failed)")
            return False
        
        print(f"✅ Short password correctly rejected")
    
    return True


if __name__ == "__main__":
    print("\n🧪 Password Reset Functionality Test Suite")
    
    try:
        success = test_password_reset_flow()
        
        print("\n" + "="*70)
        if success:
            print("🎉 ALL PASSWORD RESET TESTS PASSED!")
            print("="*70)
            print("\n✅ Functionality verified:")
            print("   - Password reset request")
            print("   - Token generation and storage")
            print("   - Password update with valid token")
            print("   - Old password rejection")
            print("   - New password acceptance")
            print("   - Token reuse prevention")
            print("   - Invalid token rejection")
            print("   - Password validation")
        else:
            print("❌ SOME PASSWORD RESET TESTS FAILED")
            print("="*70)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
