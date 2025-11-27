import requests
import time
import random
import string
import json

# Configuration
BASE_URL = "https://iauditor-cloud.onrender.com/api"
PRINT_DELAY = 1.5  # Seconds to wait between steps for readability

def print_step(message):
    print(f"\n🔹 {message}")
    time.sleep(PRINT_DELAY)

def print_system(message, success=True):
    icon = "✅" if success else "❌"
    print(f"   {icon} System: {message}")

def generate_random_email():
    return f"uat.user.{random.randint(1000, 9999)}@example.com"

def run_story_1_new_user():
    print("\n" + "="*50)
    print("📖 STORY 1: The New User Journey")
    print("="*50)
    
    email = generate_random_email()
    password = "SecurePass2025!"
    
    print_step(f"Alice visits the site and tries to register as '{email}'.")
    
    # Step 1: Weak Password
    print_step("Alice accidentally types a weak password '123'.")
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": "123",
            "name": "Alice UAT",
            "organization_name": "Alice Corp"
        }, verify=False)
        
        if resp.status_code == 400:
            print_system("Password is too weak. Please use a stronger password.", success=True)
        else:
            print_system(f"Unexpected response: {resp.status_code}", success=False)
    except Exception as e:
        print_system(f"Connection failed: {e}", success=False)

    # Step 2: Success
    print_step("Alice corrects her password to 'SecurePass2025!'.")
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "name": "Alice UAT",
            "organization_name": "Alice Corp"
        }, verify=False)
        
        if resp.status_code == 200:
            data = resp.json()
            print_system(f"Welcome, {data['user']['name']}! Your account is created.", success=True)
            return email, password
        else:
            print_system(f"Registration failed: {resp.text}", success=False)
            return None, None
    except Exception as e:
        print_system(f"Connection failed: {e}", success=False)
        return None, None

def run_story_2_returning_user(email, password):
    print("\n" + "="*50)
    print("📖 STORY 2: The Returning User")
    print("="*50)
    
    if not email:
        print("⚠️ Skipping Story 2 (No user created in Story 1)")
        return

    print_step(f"Alice returns the next day and tries to login.")
    
    # Step 1: Wrong Password
    print_step("Alice types the wrong password 'WrongPass'.")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": "WrongPass"
        }, verify=False)
        
        if resp.status_code == 401:
            print_system("Incorrect email or password.", success=True)
        else:
            print_system(f"Unexpected response: {resp.status_code}", success=False)
    except:
        pass

    # Step 2: Success
    print_step("Alice types the correct password.")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        }, verify=False)
        
        if resp.status_code == 200:
            print_system("Login successful! Redirecting to Dashboard...", success=True)
        else:
            print_system(f"Login failed: {resp.text}", success=False)
    except:
        pass

def main():
    print("🚀 Starting User Journey Simulation...")
    print(f"Target: {BASE_URL}")
    
    # Disable SSL warnings for cleaner output
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    email, password = run_story_1_new_user()
    run_story_2_returning_user(email, password)
    
    print("\n" + "="*50)
    print("🏁 Simulation Complete")
    print("="*50)

if __name__ == "__main__":
    main()
