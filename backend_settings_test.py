#!/usr/bin/env python3
"""
Backend Settings Verification Test
Tests ALL settings save functions for the production user
"""

import requests
import json
import io
from datetime import datetime

# Configuration
BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"
PRODUCTION_EMAIL = "llewellyn@bluedawncapital.co.za"
PRODUCTION_PASSWORD = "TestPassword123!"

# Test results tracking
test_results = []

def log_test(test_name, status, details=""):
    """Log test result"""
    symbol = "✅" if status == "PASS" else "❌"
    result = {
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    print(f"{symbol} {test_name}: {status}")
    if details:
        print(f"   Details: {details}")

def login():
    """Login and get JWT token"""
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": PRODUCTION_EMAIL,
                "password": PRODUCTION_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                log_test("Login", "PASS", f"Successfully logged in as {PRODUCTION_EMAIL}")
                return token
            else:
                log_test("Login", "FAIL", "No access token in response")
                return None
        else:
            log_test("Login", "FAIL", f"Status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        log_test("Login", "FAIL", f"Exception: {str(e)}")
        return None

def test_profile_photo_upload(token):
    """Test 1: Profile Photo Upload"""
    print("\n" + "="*80)
    print("TEST 1: PROFILE PHOTO UPLOAD")
    print("="*80)
    
    try:
        # Create a small test image (1x1 pixel PNG)
        test_image = io.BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        test_image.name = 'test_profile.png'
        
        # Upload photo
        response = requests.post(
            f"{BASE_URL}/users/profile/picture",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_profile.png", test_image, "image/png")},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            picture_url = data.get("picture_url")
            
            if picture_url:
                log_test("Profile Photo Upload", "PASS", f"Picture URL: {picture_url}")
                
                # Try to retrieve the photo
                file_id = picture_url.split("/")[-1]
                get_response = requests.get(
                    f"{BASE_URL}/users/profile/picture/{file_id}",
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    log_test("Profile Photo Retrieval", "PASS", f"Successfully retrieved photo ({len(get_response.content)} bytes)")
                    return True
                else:
                    log_test("Profile Photo Retrieval", "FAIL", f"Status {get_response.status_code}")
                    return False
            else:
                log_test("Profile Photo Upload", "FAIL", "No picture_url in response")
                return False
        else:
            log_test("Profile Photo Upload", "FAIL", f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Profile Photo Upload", "FAIL", f"Exception: {str(e)}")
        return False

def test_profile_update(token):
    """Test 2: Profile Update"""
    print("\n" + "="*80)
    print("TEST 2: PROFILE UPDATE")
    print("="*80)
    
    try:
        # Get current profile (use /users/me endpoint)
        get_response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Profile", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_profile = get_response.json()
        log_test("Get Profile", "PASS", f"Retrieved profile for {original_profile.get('name')}")
        
        # Update profile
        test_data = {
            "name": "Llewellyn Nel (Test)",
            "phone": "+27123456789",
            "bio": "Test bio updated at " + datetime.now().isoformat()
        }
        
        update_response = requests.put(
            f"{BASE_URL}/users/profile",
            headers={"Authorization": f"Bearer {token}"},
            json=test_data,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Profile Update", "PASS", "Profile updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_profile = verify_response.json()
                
                if (updated_profile.get("name") == test_data["name"] and
                    updated_profile.get("phone") == test_data["phone"] and
                    updated_profile.get("bio") == test_data["bio"]):
                    log_test("Profile Update Verification", "PASS", "All changes saved correctly")
                    
                    # Restore original values
                    restore_data = {
                        "name": original_profile.get("name", "Llewellyn Nel"),
                        "phone": original_profile.get("phone", ""),
                        "bio": original_profile.get("bio", "")
                    }
                    requests.put(
                        f"{BASE_URL}/users/profile",
                        headers={"Authorization": f"Bearer {token}"},
                        json=restore_data,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Profile Update Verification", "FAIL", "Changes not saved correctly")
                    return False
            else:
                log_test("Profile Update Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Profile Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Profile Update", "FAIL", f"Exception: {str(e)}")
        return False

def test_theme_preferences(token):
    """Test 3: Theme Preferences"""
    print("\n" + "="*80)
    print("TEST 3: THEME PREFERENCES")
    print("="*80)
    
    try:
        # Get current theme
        get_response = requests.get(
            f"{BASE_URL}/users/theme",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Theme", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_theme = get_response.json()
        log_test("Get Theme", "PASS", f"Current theme: {original_theme.get('theme')}")
        
        # Update theme
        test_theme = {
            "theme": "dark",
            "accent_color": "#ff5733",
            "view_density": "compact",
            "font_size": "large"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/users/theme",
            headers={"Authorization": f"Bearer {token}"},
            json=test_theme,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Theme Update", "PASS", "Theme updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/users/theme",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_theme = verify_response.json()
                
                if (updated_theme.get("theme") == test_theme["theme"] and
                    updated_theme.get("accent_color") == test_theme["accent_color"] and
                    updated_theme.get("view_density") == test_theme["view_density"] and
                    updated_theme.get("font_size") == test_theme["font_size"]):
                    log_test("Theme Verification", "PASS", "All theme changes saved correctly")
                    
                    # Restore original
                    requests.put(
                        f"{BASE_URL}/users/theme",
                        headers={"Authorization": f"Bearer {token}"},
                        json=original_theme,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Theme Verification", "FAIL", "Theme changes not saved correctly")
                    return False
            else:
                log_test("Theme Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Theme Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Theme Preferences", "FAIL", f"Exception: {str(e)}")
        return False

def test_regional_preferences(token):
    """Test 4: Regional Preferences"""
    print("\n" + "="*80)
    print("TEST 4: REGIONAL PREFERENCES")
    print("="*80)
    
    try:
        # Get current regional settings
        get_response = requests.get(
            f"{BASE_URL}/users/regional",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Regional", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_regional = get_response.json()
        log_test("Get Regional", "PASS", f"Current timezone: {original_regional.get('timezone')}")
        
        # Update regional settings
        test_regional = {
            "language": "en-ZA",
            "timezone": "Africa/Johannesburg",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "ZAR"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/users/regional",
            headers={"Authorization": f"Bearer {token}"},
            json=test_regional,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Regional Update", "PASS", "Regional settings updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/users/regional",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_regional = verify_response.json()
                
                if (updated_regional.get("timezone") == test_regional["timezone"] and
                    updated_regional.get("currency") == test_regional["currency"]):
                    log_test("Regional Verification", "PASS", "Regional changes saved correctly")
                    
                    # Restore original
                    requests.put(
                        f"{BASE_URL}/users/regional",
                        headers={"Authorization": f"Bearer {token}"},
                        json=original_regional,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Regional Verification", "FAIL", "Regional changes not saved correctly")
                    return False
            else:
                log_test("Regional Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Regional Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Regional Preferences", "FAIL", f"Exception: {str(e)}")
        return False

def test_privacy_preferences(token):
    """Test 5: Privacy Preferences"""
    print("\n" + "="*80)
    print("TEST 5: PRIVACY PREFERENCES")
    print("="*80)
    
    try:
        # Get current privacy settings
        get_response = requests.get(
            f"{BASE_URL}/users/privacy",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Privacy", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_privacy = get_response.json()
        log_test("Get Privacy", "PASS", f"Current visibility: {original_privacy.get('profile_visibility')}")
        
        # Update privacy settings
        test_privacy = {
            "profile_visibility": "private",
            "show_activity_status": False,
            "show_last_seen": False
        }
        
        update_response = requests.put(
            f"{BASE_URL}/users/privacy",
            headers={"Authorization": f"Bearer {token}"},
            json=test_privacy,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Privacy Update", "PASS", "Privacy settings updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/users/privacy",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_privacy = verify_response.json()
                
                if (updated_privacy.get("profile_visibility") == test_privacy["profile_visibility"] and
                    updated_privacy.get("show_activity_status") == test_privacy["show_activity_status"]):
                    log_test("Privacy Verification", "PASS", "Privacy changes saved correctly")
                    
                    # Restore original
                    requests.put(
                        f"{BASE_URL}/users/privacy",
                        headers={"Authorization": f"Bearer {token}"},
                        json=original_privacy,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Privacy Verification", "FAIL", "Privacy changes not saved correctly")
                    return False
            else:
                log_test("Privacy Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Privacy Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Privacy Preferences", "FAIL", f"Exception: {str(e)}")
        return False

def test_security_preferences(token):
    """Test 6: Security Preferences"""
    print("\n" + "="*80)
    print("TEST 6: SECURITY PREFERENCES")
    print("="*80)
    
    try:
        # Get current security settings
        get_response = requests.get(
            f"{BASE_URL}/users/security-prefs",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Security", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_security = get_response.json()
        log_test("Get Security", "PASS", f"2FA enabled: {original_security.get('two_factor_enabled')}")
        
        # Update security settings
        test_security = {
            "two_factor_enabled": True,
            "session_timeout": 7200
        }
        
        update_response = requests.put(
            f"{BASE_URL}/users/security-prefs",
            headers={"Authorization": f"Bearer {token}"},
            json=test_security,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Security Update", "PASS", "Security settings updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/users/security-prefs",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_security = verify_response.json()
                
                if (updated_security.get("two_factor_enabled") == test_security["two_factor_enabled"] and
                    updated_security.get("session_timeout") == test_security["session_timeout"]):
                    log_test("Security Verification", "PASS", "Security changes saved correctly")
                    
                    # Restore original
                    requests.put(
                        f"{BASE_URL}/users/security-prefs",
                        headers={"Authorization": f"Bearer {token}"},
                        json=original_security,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Security Verification", "FAIL", "Security changes not saved correctly")
                    return False
            else:
                log_test("Security Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Security Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Security Preferences", "FAIL", f"Exception: {str(e)}")
        return False

def test_notification_preferences(token):
    """Test 7: Notification Preferences"""
    print("\n" + "="*80)
    print("TEST 7: NOTIFICATION PREFERENCES")
    print("="*80)
    
    try:
        # Get current notification settings
        get_response = requests.get(
            f"{BASE_URL}/notifications/preferences",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_test("Get Notifications", "FAIL", f"Status {get_response.status_code}")
            return False
        
        original_notifications = get_response.json()
        log_test("Get Notifications", "PASS", f"Email notifications: {original_notifications.get('email_notifications')}")
        
        # Update notification settings
        test_notifications = {
            "email_notifications": False,
            "push_notifications": True,
            "notification_types": {
                "task_assigned": True,
                "task_completed": False,
                "inspection_due": True
            }
        }
        
        update_response = requests.put(
            f"{BASE_URL}/notifications/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json=test_notifications,
            timeout=10
        )
        
        if update_response.status_code == 200:
            log_test("Notification Update", "PASS", "Notification settings updated successfully")
            
            # Verify changes
            verify_response = requests.get(
                f"{BASE_URL}/notifications/preferences",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if verify_response.status_code == 200:
                updated_notifications = verify_response.json()
                
                if (updated_notifications.get("email_notifications") == test_notifications["email_notifications"] and
                    updated_notifications.get("push_notifications") == test_notifications["push_notifications"]):
                    log_test("Notification Verification", "PASS", "Notification changes saved correctly")
                    
                    # Restore original
                    requests.put(
                        f"{BASE_URL}/notifications/preferences",
                        headers={"Authorization": f"Bearer {token}"},
                        json=original_notifications,
                        timeout=10
                    )
                    return True
                else:
                    log_test("Notification Verification", "FAIL", "Notification changes not saved correctly")
                    return False
            else:
                log_test("Notification Verification", "FAIL", f"Status {verify_response.status_code}")
                return False
        else:
            log_test("Notification Update", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Notification Preferences", "FAIL", f"Exception: {str(e)}")
        return False

def test_password_change(token):
    """Test 8: Password Change"""
    print("\n" + "="*80)
    print("TEST 8: PASSWORD CHANGE")
    print("="*80)
    
    try:
        # Try to change password
        test_password_data = {
            "current_password": PRODUCTION_PASSWORD,
            "new_password": "NewTestPassword123!"
        }
        
        # First, try the endpoint
        update_response = requests.put(
            f"{BASE_URL}/users/password",
            headers={"Authorization": f"Bearer {token}"},
            json=test_password_data,
            timeout=10
        )
        
        # Also try POST /auth/change-password
        if update_response.status_code != 200:
            update_response = requests.post(
                f"{BASE_URL}/auth/change-password",
                headers={"Authorization": f"Bearer {token}"},
                json=test_password_data,
                timeout=10
            )
        
        if update_response.status_code == 200:
            log_test("Password Change", "PASS", "Password changed successfully")
            
            # Verify by logging in with new password
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": PRODUCTION_EMAIL,
                    "password": "NewTestPassword123!"
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                log_test("Password Change Verification", "PASS", "Login successful with new password")
                
                # Restore original password
                new_token = login_response.json().get("access_token")
                restore_response = requests.put(
                    f"{BASE_URL}/users/password",
                    headers={"Authorization": f"Bearer {new_token}"},
                    json={
                        "current_password": "NewTestPassword123!",
                        "new_password": PRODUCTION_PASSWORD
                    },
                    timeout=10
                )
                
                if restore_response.status_code == 200:
                    log_test("Password Restore", "PASS", "Original password restored")
                    return True
                else:
                    log_test("Password Restore", "FAIL", "Could not restore original password")
                    return False
            else:
                log_test("Password Change Verification", "FAIL", "Could not login with new password")
                return False
        else:
            log_test("Password Change", "FAIL", f"Status {update_response.status_code}: {update_response.text}")
            return False
            
    except Exception as e:
        log_test("Password Change", "FAIL", f"Exception: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")
    
    # Group by function
    functions = {}
    for result in test_results:
        test_name = result["test"]
        # Extract function name (before the first space or dash)
        func_name = test_name.split()[0]
        if func_name not in functions:
            functions[func_name] = {"pass": 0, "fail": 0}
        
        if result["status"] == "PASS":
            functions[func_name]["pass"] += 1
        else:
            functions[func_name]["fail"] += 1
    
    print("FUNCTION STATUS:")
    print("-" * 80)
    
    function_order = [
        "Login",
        "Profile",
        "Theme",
        "Regional",
        "Privacy",
        "Security",
        "Notification",
        "Password"
    ]
    
    for func in function_order:
        for key in functions.keys():
            if key.startswith(func):
                stats = functions[key]
                total_func = stats["pass"] + stats["fail"]
                if stats["fail"] == 0:
                    print(f"✅ {func} Settings: WORKING ({stats['pass']}/{total_func} tests passed)")
                else:
                    print(f"❌ {func} Settings: BROKEN ({stats['pass']}/{total_func} tests passed)")
                break
    
    print("\n" + "="*80)

def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("BACKEND SETTINGS VERIFICATION TEST")
    print("Testing ALL settings save functions")
    print("="*80)
    
    # Login
    token = login()
    if not token:
        print("\n❌ CRITICAL: Cannot proceed without authentication")
        return
    
    # Run all tests
    test_profile_photo_upload(token)
    test_profile_update(token)
    test_theme_preferences(token)
    test_regional_preferences(token)
    test_privacy_preferences(token)
    test_security_preferences(token)
    test_notification_preferences(token)
    test_password_change(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
