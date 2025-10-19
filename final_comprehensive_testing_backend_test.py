#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TESTING - ALL 13 FIXED ISSUES
Testing all previously failing endpoints that were reported as 404/422/500 errors.

Target: 100% pass rate (13/13 endpoints)
Test User: llewellyn@bluedawncapital.co.za (developer role)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://workflow-engine-18.preview.emergentagent.com/api"
TEST_USER_EMAIL = "llewellyn@bluedawncapital.co.za"
TEST_USER_PASSWORD = "TestPassword123!"

class ComprehensiveEndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.organization_id = None
        self.test_results = []
        
    def authenticate(self):
        """Authenticate with production user"""
        print("🔐 AUTHENTICATING WITH PRODUCTION USER...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_id = data.get('user', {}).get('id')
                self.organization_id = data.get('user', {}).get('organization_id')
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                })
                
                print(f"✅ Authentication successful!")
                print(f"   User ID: {self.user_id}")
                print(f"   Organization ID: {self.organization_id}")
                print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=None, test_name=""):
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Determine if test passed
            if expected_status:
                passed = response.status_code == expected_status
            else:
                # Success if 200-299 range
                passed = 200 <= response.status_code < 300
            
            result = {
                'test_name': test_name,
                'method': method.upper(),
                'endpoint': endpoint,
                'status_code': response.status_code,
                'passed': passed,
                'response_size': len(response.text) if response.text else 0
            }
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                result['response_type'] = 'json'
                if isinstance(response_data, dict):
                    result['response_keys'] = list(response_data.keys())
                elif isinstance(response_data, list):
                    result['response_count'] = len(response_data)
            except:
                result['response_type'] = 'text'
            
            self.test_results.append(result)
            
            # Print result
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} {test_name}: {method.upper()} {endpoint} -> {response.status_code}")
            
            if not passed:
                print(f"   Response: {response.text[:200]}...")
            
            return passed, response
            
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            self.test_results.append({
                'test_name': test_name,
                'method': method.upper(),
                'endpoint': endpoint,
                'status_code': 'ERROR',
                'passed': False,
                'error': str(e)
            })
            return False, None
    
    def run_phase_1_announcements(self):
        """PHASE 1: Announcements Module (was 404)"""
        print("\n🎯 PHASE 1: ANNOUNCEMENTS MODULE TESTING")
        
        # Test 1: GET /api/announcements
        self.test_endpoint(
            "GET", "/announcements",
            test_name="Test 1 - List Announcements"
        )
        
        # Test 2: POST /api/announcements
        announcement_data = {
            "title": "Test Announcement",
            "content": "This is a test announcement",
            "priority": "normal"
        }
        self.test_endpoint(
            "POST", "/announcements",
            data=announcement_data,
            expected_status=201,
            test_name="Test 2 - Create Announcement"
        )
    
    def run_phase_2_analytics(self):
        """PHASE 2: Analytics Endpoints (were 404)"""
        print("\n🎯 PHASE 2: ANALYTICS ENDPOINTS TESTING")
        
        # Test 3: GET /api/inspections/analytics?period=30d
        self.test_endpoint(
            "GET", "/inspections/analytics?period=30d",
            test_name="Test 3 - Inspections Analytics"
        )
        
        # Test 4: GET /api/checklists/analytics?period=30d
        self.test_endpoint(
            "GET", "/checklists/analytics?period=30d",
            test_name="Test 4 - Checklists Analytics"
        )
        
        # Test 5: GET /api/tasks/analytics?period=30d
        self.test_endpoint(
            "GET", "/tasks/analytics?period=30d",
            test_name="Test 5 - Tasks Analytics"
        )
    
    def run_phase_3_dashboards(self):
        """PHASE 3: Dashboard Endpoints (were 404)"""
        print("\n🎯 PHASE 3: DASHBOARD ENDPOINTS TESTING")
        
        # Test 6: GET /api/dashboard/operations
        self.test_endpoint(
            "GET", "/dashboard/operations",
            test_name="Test 6 - Operations Dashboard"
        )
        
        # Test 7: GET /api/dashboard/safety
        self.test_endpoint(
            "GET", "/dashboard/safety",
            test_name="Test 7 - Safety Dashboard"
        )
    
    def run_phase_4_assets(self):
        """PHASE 4: Asset Creation (was 422)"""
        print("\n🎯 PHASE 4: ASSET CREATION TESTING")
        
        # Test 8: POST /api/assets
        asset_data = {
            "asset_tag": "TEST-001",
            "name": "Test Asset"
        }
        self.test_endpoint(
            "POST", "/assets",
            data=asset_data,
            expected_status=201,
            test_name="Test 8 - Create Asset"
        )
    
    def run_phase_5_incidents(self):
        """PHASE 5: Incident Creation (was 422)"""
        print("\n🎯 PHASE 5: INCIDENT CREATION TESTING")
        
        # Test 9: POST /api/incidents
        incident_data = {
            "title": "Test Incident",
            "description": "Test incident description"
        }
        self.test_endpoint(
            "POST", "/incidents",
            data=incident_data,
            expected_status=201,
            test_name="Test 9 - Create Incident"
        )
    
    def run_phase_6_training(self):
        """PHASE 6: Training Creation (was 422)"""
        print("\n🎯 PHASE 6: TRAINING CREATION TESTING")
        
        # Test 10: POST /api/training/courses
        training_data = {
            "course_code": "TEST-001",
            "name": "Test Training Program",
            "description": "Test training description",
            "course_type": "safety",
            "duration_hours": 8.0,
            "valid_for_years": 2
        }
        self.test_endpoint(
            "POST", "/training/courses",
            data=training_data,
            expected_status=201,
            test_name="Test 10 - Create Training Course"
        )
    
    def run_phase_7_emergencies(self):
        """PHASE 7: Emergency Creation (was 500)"""
        print("\n🎯 PHASE 7: EMERGENCY CREATION TESTING")
        
        # Test 11: POST /api/emergencies
        emergency_data = {
            "emergency_type": "fire",
            "severity": "high",
            "description": "Test emergency",
            "location": "Test Location",
            "unit_id": "test-unit-001"
        }
        self.test_endpoint(
            "POST", "/emergencies",
            data=emergency_data,
            expected_status=201,
            test_name="Test 11 - Create Emergency"
        )
    
    def run_phase_8_contractors(self):
        """PHASE 8: Contractor Creation (was 500)"""
        print("\n🎯 PHASE 8: CONTRACTOR CREATION TESTING")
        
        # Test 12: POST /api/contractors
        contractor_data = {
            "name": "Test Contractor",
            "company_name": "Test Contractor Company",
            "contact_person": "John Doe",
            "email": "john@testcontractor.com",
            "phone": "+1234567890"
        }
        self.test_endpoint(
            "POST", "/contractors",
            data=contractor_data,
            expected_status=201,
            test_name="Test 12 - Create Contractor"
        )
    
    def run_phase_9_financial(self):
        """PHASE 9: Financial Transaction (was 500)"""
        print("\n🎯 PHASE 9: FINANCIAL TRANSACTION TESTING")
        
        # Test 13: POST /api/financial/transactions
        transaction_data = {
            "transaction_type": "expense",
            "category": "supplies",
            "amount": 100.00
        }
        self.test_endpoint(
            "POST", "/financial/transactions",
            data=transaction_data,
            expected_status=201,
            test_name="Test 13 - Create Financial Transaction"
        )
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 FINAL COMPREHENSIVE TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Target: 100% (13/13)")
        
        if success_rate == 100:
            print("\n🎉 SUCCESS: All 13 endpoints are now working correctly!")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: {failed_tests} endpoints still need attention")
        
        # Group results by phase
        print(f"\n📋 DETAILED RESULTS BY PHASE:")
        
        phases = {
            "PHASE 1 - Announcements": [1, 2],
            "PHASE 2 - Analytics": [3, 4, 5], 
            "PHASE 3 - Dashboards": [6, 7],
            "PHASE 4 - Assets": [8],
            "PHASE 5 - Incidents": [9],
            "PHASE 6 - Training": [10],
            "PHASE 7 - Emergencies": [11],
            "PHASE 8 - Contractors": [12],
            "PHASE 9 - Financial": [13]
        }
        
        for phase_name, test_numbers in phases.items():
            phase_results = [r for r in self.test_results if any(f"Test {num}" in r['test_name'] for num in test_numbers)]
            phase_passed = sum(1 for r in phase_results if r['passed'])
            phase_total = len(phase_results)
            phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
            
            status_icon = "✅" if phase_rate == 100 else "❌"
            print(f"   {status_icon} {phase_name}: {phase_passed}/{phase_total} ({phase_rate:.0f}%)")
        
        # Show failed tests details
        failed_results = [r for r in self.test_results if not r['passed']]
        if failed_results:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test_name']}: {result['method']} {result['endpoint']}")
                print(f"     Status: {result['status_code']}")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
        
        return success_rate == 100

def main():
    """Main test execution"""
    print("🚀 STARTING FINAL COMPREHENSIVE TESTING - ALL 13 FIXED ISSUES")
    print("="*80)
    
    tester = ComprehensiveEndpointTester()
    
    # Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with testing.")
        sys.exit(1)
    
    # Run all test phases
    tester.run_phase_1_announcements()
    tester.run_phase_2_analytics()
    tester.run_phase_3_dashboards()
    tester.run_phase_4_assets()
    tester.run_phase_5_incidents()
    tester.run_phase_6_training()
    tester.run_phase_7_emergencies()
    tester.run_phase_8_contractors()
    tester.run_phase_9_financial()
    
    # Print summary
    all_passed = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()