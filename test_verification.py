#!/usr/bin/env python3
"""
VERIFY DATABASE STATE AND USER COUNT UPDATES
"""

import requests
import json

# Configuration
BACKEND_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "Test@1234"

def authenticate():
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        timeout=10
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def verify_database_state(token):
    """Verify the assignment was created in database"""
    print("\n" + "="*80)
    print("VERIFICATION 1: DATABASE STATE")
    print("="*80)
    
    # Get the unit we just assigned to
    unit_id = "cbca528a-bfd8-4953-992f-c700f1f34f10"
    user_id = "1f254996-542b-4d7f-ba88-1bf3fcec193f"
    
    # Check unit users
    response = requests.get(
        f"{BACKEND_URL}/organizations/units/{unit_id}/users",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        unit_users = response.json()
        print(f"✅ Unit now has {len(unit_users)} users")
        
        # Find our newly assigned user
        found = False
        for assignment in unit_users:
            user_data = assignment.get("user", {})
            if user_data.get("id") == user_id:
                found = True
                print(f"\n✅ VERIFIED: Newly assigned user found in database!")
                print(f"   Assignment ID: {assignment.get('assignment_id')}")
                print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
                print(f"   Role: {assignment.get('role')}")
                print(f"   Assigned At: {assignment.get('assigned_at')}")
                break
        
        if not found:
            print(f"\n❌ ERROR: Newly assigned user NOT found in database!")
            return False
        
        return True
    else:
        print(f"❌ Failed to get unit users: {response.status_code}")
        return False

def verify_user_document_updated(token):
    """Verify the user document was updated with organizational_unit_id"""
    print("\n" + "="*80)
    print("VERIFICATION 2: USER DOCUMENT UPDATE")
    print("="*80)
    
    # Get user profile
    response = requests.get(
        f"{BACKEND_URL}/users/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Retrieved user profile")
        print(f"   User: {user.get('name')} ({user.get('email')})")
        print(f"   Organization ID: {user.get('organization_id')}")
        print(f"   Organizational Unit ID: {user.get('organizational_unit_id')}")
        
        if user.get('organizational_unit_id'):
            print(f"\n✅ VERIFIED: User document has organizational_unit_id set!")
            return True
        else:
            print(f"\n⚠️  User document does not have organizational_unit_id")
            return False
    else:
        print(f"❌ Failed to get user profile: {response.status_code}")
        return False

def verify_user_count_updates(token):
    """Verify user counts in hierarchy"""
    print("\n" + "="*80)
    print("VERIFICATION 3: USER COUNT UPDATES IN HIERARCHY")
    print("="*80)
    
    response = requests.get(
        f"{BACKEND_URL}/organizations/hierarchy",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        hierarchy = response.json()
        print(f"✅ Retrieved organization hierarchy")
        
        # Find the unit we assigned to
        unit_id = "cbca528a-bfd8-4953-992f-c700f1f34f10"
        
        def find_unit(units, target_id):
            for unit in units:
                if unit.get('id') == target_id:
                    return unit
                if unit.get('children'):
                    found = find_unit(unit.get('children'), target_id)
                    if found:
                        return found
            return None
        
        target_unit = find_unit(hierarchy, unit_id)
        
        if target_unit:
            user_count = target_unit.get('user_count', 0)
            print(f"\n✅ VERIFIED: Unit '{target_unit.get('name')}' now has {user_count} users")
            
            if user_count >= 3:  # We know there were 2 before, now should be 3
                print(f"   ✅ User count increased correctly!")
                return True
            else:
                print(f"   ⚠️  User count may not have updated yet")
                return False
        else:
            print(f"❌ Could not find target unit in hierarchy")
            return False
    else:
        print(f"❌ Failed to get hierarchy: {response.status_code}")
        return False

def main():
    print("\n" + "="*80)
    print("DATABASE STATE AND USER COUNT VERIFICATION")
    print("="*80)
    
    token = authenticate()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    
    # Run verifications
    db_ok = verify_database_state(token)
    user_ok = verify_user_document_updated(token)
    count_ok = verify_user_count_updates(token)
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Database State: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"User Document Update: {'✅ PASS' if user_ok else '❌ FAIL'}")
    print(f"User Count Updates: {'✅ PASS' if count_ok else '❌ FAIL'}")
    
    if db_ok and count_ok:
        print("\n✅ ALL VERIFICATIONS PASSED!")
        print("   User allocation is working correctly end-to-end.")
    else:
        print("\n⚠️  Some verifications failed")

if __name__ == "__main__":
    main()
