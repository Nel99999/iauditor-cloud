"""
PHASE 1 TESTING - DIRECT DATABASE VERIFICATION

This script directly connects to MongoDB to verify migration success
across ALL organizations, not just the test organization.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

# Test results tracking
test_results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    test_results["total_tests"] += 1
    if passed:
        test_results["passed"] += 1
        print(f"✅ PASSED: {test_name}")
    else:
        test_results["failed"] += 1
        print(f"❌ FAILED: {test_name}")
    
    if details:
        print(f"   {details}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })

async def verify_migration():
    """Verify migration success by directly querying MongoDB"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("="*80)
    print("PHASE 1 MIGRATION VERIFICATION - DIRECT DATABASE CHECK")
    print("="*80)
    print(f"Database: {db_name}")
    print(f"MongoDB URL: {mongo_url}")
    
    # ========================================================================
    # TEST 1: VERIFY ALL USERS HAVE APPROVAL FIELDS
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 1: VERIFY ALL USERS HAVE APPROVAL FIELDS")
    print("="*80)
    
    # Get all users
    all_users = await db.users.find({}).to_list(length=None)
    total_users = len(all_users)
    
    print(f"\n📊 Total users in database: {total_users}")
    
    # Analyze approval fields
    with_approval_status = 0
    with_approved_at = 0
    with_approval_notes = 0
    with_invited = 0
    
    for user in all_users:
        if 'approval_status' in user:
            with_approval_status += 1
        if 'approved_at' in user:
            with_approved_at += 1
        if 'approval_notes' in user:
            with_approval_notes += 1
        if 'invited' in user:
            with_invited += 1
    
    print(f"\n📋 Approval Fields Coverage:")
    print(f"   Users with approval_status: {with_approval_status}/{total_users}")
    print(f"   Users with approved_at: {with_approved_at}/{total_users}")
    print(f"   Users with approval_notes: {with_approval_notes}/{total_users}")
    print(f"   Users with invited: {with_invited}/{total_users}")
    
    # Test 1.1: All users have approval_status
    log_test(
        "All users have approval_status field",
        with_approval_status == total_users,
        f"{with_approval_status}/{total_users} users"
    )
    
    # Test 1.2: All users have approved_at
    log_test(
        "All users have approved_at field",
        with_approved_at == total_users,
        f"{with_approved_at}/{total_users} users"
    )
    
    # Test 1.3: All users have approval_notes
    log_test(
        "All users have approval_notes field",
        with_approval_notes == total_users,
        f"{with_approval_notes}/{total_users} users"
    )
    
    # Test 1.4: All users have invited
    log_test(
        "All users have invited field",
        with_invited == total_users,
        f"{with_invited}/{total_users} users"
    )
    
    # ========================================================================
    # TEST 2: VERIFY MIGRATED USERS
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 2: VERIFY MIGRATED USERS")
    print("="*80)
    
    # Count migrated users
    migrated_users = []
    for user in all_users:
        if user.get('approval_notes') == 'Auto-approved during migration':
            migrated_users.append(user)
    
    migrated_count = len(migrated_users)
    print(f"\n📊 Migrated users found: {migrated_count}")
    
    # Test 2.1: Migrated users exist
    log_test(
        "Migrated users found in database",
        migrated_count > 0,
        f"Found {migrated_count} migrated users"
    )
    
    if migrated_count > 0:
        # Analyze migrated users
        approved_count = 0
        invited_false_count = 0
        has_approved_at_count = 0
        
        for user in migrated_users:
            if user.get('approval_status') == 'approved':
                approved_count += 1
            if user.get('invited') == False:
                invited_false_count += 1
            if user.get('approved_at') is not None:
                has_approved_at_count += 1
        
        print(f"\n📋 Migrated Users Analysis:")
        print(f"   Total migrated: {migrated_count}")
        print(f"   With approval_status='approved': {approved_count}")
        print(f"   With invited=False: {invited_false_count}")
        print(f"   With approved_at set: {has_approved_at_count}")
        
        # Test 2.2: All migrated users have approval_status='approved'
        log_test(
            "All migrated users have approval_status='approved'",
            approved_count == migrated_count,
            f"{approved_count}/{migrated_count} migrated users"
        )
        
        # Test 2.3: All migrated users have invited=False
        log_test(
            "All migrated users have invited=False",
            invited_false_count == migrated_count,
            f"{invited_false_count}/{migrated_count} migrated users"
        )
        
        # Test 2.4: All migrated users have approved_at set
        log_test(
            "All migrated users have approved_at set",
            has_approved_at_count == migrated_count,
            f"{has_approved_at_count}/{migrated_count} migrated users"
        )
        
        # Sample migrated users
        print(f"\n📋 Sample Migrated Users (first 5):")
        for i, user in enumerate(migrated_users[:5]):
            print(f"\n   User {i+1}: {user.get('email')}")
            print(f"   - approval_status: {user.get('approval_status')}")
            print(f"   - approved_at: {user.get('approved_at')}")
            print(f"   - approval_notes: {user.get('approval_notes')}")
            print(f"   - invited: {user.get('invited')}")
            
            # Check correctness
            is_correct = (
                user.get('approval_status') == 'approved' and
                user.get('approval_notes') == 'Auto-approved during migration' and
                user.get('invited') == False and
                user.get('approved_at') is not None
            )
            
            if is_correct:
                print(f"   ✅ All fields correct")
            else:
                print(f"   ❌ Some fields incorrect")
    
    # ========================================================================
    # TEST 3: VERIFY NEW USERS (NON-MIGRATED)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 3: VERIFY NEW USERS (NON-MIGRATED)")
    print("="*80)
    
    # Find new users (not migrated)
    new_users = []
    for user in all_users:
        if user.get('approval_notes') != 'Auto-approved during migration':
            new_users.append(user)
    
    new_count = len(new_users)
    print(f"\n📊 New users (non-migrated) found: {new_count}")
    
    if new_count > 0:
        # Analyze new users
        with_approval_status = 0
        pending_count = 0
        
        for user in new_users:
            if 'approval_status' in user:
                with_approval_status += 1
                if user.get('approval_status') == 'pending':
                    pending_count += 1
        
        print(f"\n📋 New Users Analysis:")
        print(f"   Total new users: {new_count}")
        print(f"   With approval_status field: {with_approval_status}")
        print(f"   With approval_status='pending': {pending_count}")
        
        # Test 3.1: New users have approval_status field
        log_test(
            "New users have approval_status field",
            with_approval_status == new_count,
            f"{with_approval_status}/{new_count} new users"
        )
        
        # Sample new users
        print(f"\n📋 Sample New Users (first 3):")
        for i, user in enumerate(new_users[:3]):
            print(f"\n   User {i+1}: {user.get('email')}")
            print(f"   - approval_status: {user.get('approval_status')}")
            print(f"   - approved_at: {user.get('approved_at')}")
            print(f"   - approval_notes: {user.get('approval_notes')}")
            print(f"   - invited: {user.get('invited')}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("🎯 MIGRATION VERIFICATION SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")
    print("="*80)
    
    print("\n📊 DATABASE STATISTICS:")
    print(f"   Total users: {total_users}")
    print(f"   Migrated users: {migrated_count}")
    print(f"   New users: {new_count}")
    print("="*80)
    
    # Print failed tests if any
    if test_results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  • {test['name']}: {test['details']}")
    
    # Close connection
    client.close()
    
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = asyncio.run(verify_migration())
    exit(0 if success else 1)
