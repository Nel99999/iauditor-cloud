import requests
import json
import os

# Cloud API URL
BASE_URL = "https://iauditor-cloud.onrender.com/api"

def get_all_users():
    print(f"🔄 Connecting to Cloud API: {BASE_URL}...")
    
    # 1. Login as Master to get a token (using the backdoor if enabled, or a known user)
    # Since we disabled the backdoor by default, we'll try to register a new admin user 
    # or use the one we created in the PowerShell test if we knew the credentials.
    # ACTUALLY: The PowerShell test created a random user. We don't know the email/pass easily.
    # Let's try to hit the health check first.
    
    try:
        resp = requests.get(f"{BASE_URL}/", verify=False)
        print(f"✅ Health Check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return

    # To list users, we need to be an admin. 
    # Since I cannot easily log in without a known admin account (and I just secured the backdoor),
    # I will try to register a NEW admin user to use for verification.
    
    import random
    rand_id = random.randint(1000, 9999)
    email = f"verifier.{rand_id}@testing.com"
    password = "VerifyPass123!"
    
    print(f"\n👤 Registering new verification admin: {email}")
    
    try:
        reg_data = {
            "email": email,
            "password": password,
            "name": "Verification Admin",
            "organization_name": "Verification Org"
        }
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data, verify=False)
        
        if resp.status_code != 200:
            print(f"❌ Registration Failed: {resp.text}")
            return
            
        data = resp.json()
        token = data.get("access_token")
        user = data.get("user")
        
        print(f"✅ Registration Successful! User ID: {user['id']}")
        print(f"🔑 Token received.")
        
        # Now list users (if there is an endpoint for it)
        # Usually /api/users or /api/org/users
        # Let's try to get "My Profile" to confirm DB read
        
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers, verify=False)
        
        if resp.status_code == 200:
            print(f"\n✅ Verified Cloud DB Read (Me):")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Failed to read profile: {resp.text}")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    get_all_users()
