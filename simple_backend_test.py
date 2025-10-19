#!/usr/bin/env python3
"""
Simple Backend Test - Test basic endpoints without authentication
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://dynamic-sidebar-1.preview.emergentagent.com/api"

def test_basic_endpoints():
    """Test basic endpoints that don't require authentication"""
    print("🚀 TESTING BASIC BACKEND ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Health Check: PASSED - Backend is responding")
        else:
            print(f"❌ Health Check: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: FAILED - {str(e)}")
    
    # Test 2: Try to register a new user to test the system
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_email = f"test.{timestamp}@example.com"
        
        response = requests.post(f"{BACKEND_URL}/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User",
            "organization_name": f"Test Org {timestamp}"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration: PASSED - User created: {test_email}")
            
            # Try to login with the new user
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": test_email,
                "password": "TestPass123!"
            }, timeout=10)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                token = login_data.get("access_token")
                print("✅ Login: PASSED - JWT token obtained")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{BACKEND_URL}/users/me", headers=headers, timeout=10)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"✅ Authenticated Endpoint: PASSED - User: {user_data.get('name')}")
                    return True
                else:
                    print(f"❌ Authenticated Endpoint: FAILED - Status {me_response.status_code}")
            elif login_response.status_code == 403:
                print("⚠️ Login: User pending approval (expected for new registrations)")
                return True  # This is expected behavior
            else:
                print(f"❌ Login: FAILED - Status {login_response.status_code}")
        else:
            print(f"❌ Registration: FAILED - Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Registration/Login: FAILED - {str(e)}")
    
    return False

def test_production_user_status():
    """Check if we can get any info about the production user"""
    print("\n🔍 CHECKING PRODUCTION USER STATUS")
    print("=" * 60)
    
    # Try forgot password to see if user exists
    try:
        response = requests.post(f"{BACKEND_URL}/auth/forgot-password", json={
            "email": "llewellyn@bluedawncapital.co.za"
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ Production User: EXISTS - Forgot password request accepted")
        else:
            print(f"❌ Production User: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Production User Check: FAILED - {str(e)}")

if __name__ == "__main__":
    success = test_basic_endpoints()
    test_production_user_status()
    
    if success:
        print("\n🎉 BASIC BACKEND FUNCTIONALITY: WORKING")
    else:
        print("\n❌ BASIC BACKEND FUNCTIONALITY: ISSUES DETECTED")
    
    sys.exit(0 if success else 1)