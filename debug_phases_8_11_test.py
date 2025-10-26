#!/usr/bin/env python3
"""
Debug Test for Phases 8-11 - Simplified version to identify issues
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "https://rbacmaster-1.preview.emergentagent.com/api"

class DebugTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, data=None, headers=None):
        """Make HTTP request"""
        if headers is None:
            headers = {}
        if self.auth_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
        try:
            async with self.session.request(method, f"{BASE_URL}{endpoint}", 
                                          json=data, headers=headers) as resp:
                try:
                    response_data = await resp.json()
                except:
                    response_data = await resp.text()
                
                return {
                    'status': resp.status,
                    'data': response_data,
                    'headers': dict(resp.headers)
                }
        except Exception as e:
            return {
                'status': 0,
                'data': {'error': str(e)},
                'headers': {}
            }
    
    async def test_basic_auth(self):
        """Test basic authentication flow"""
        print("🔐 Testing Basic Authentication...")
        
        # Create a test user
        self.test_user_email = f"debugtest.{int(time.time())}@example.com"
        user_data = {
            "name": "Debug Test User",
            "email": self.test_user_email,
            "password": "SecureTestPass123!",
            "organization_name": f"Debug Test Org {int(time.time())}"
        }
        
        # Register user
        resp = await self.make_request("POST", "/auth/register", user_data, headers={})
        print(f"Registration: {resp['status']} - {resp['data']}")
        
        if resp['status'] == 200:
            self.auth_token = resp['data'].get('access_token')
            print(f"✅ Auth token obtained: {self.auth_token[:50]}...")
            
            # Test protected endpoint
            me_resp = await self.make_request("GET", "/users/me")
            print(f"Profile access: {me_resp['status']} - {me_resp['data']}")
            
            return True
        else:
            print(f"❌ Registration failed: {resp['status']}")
            return False
    
    async def test_task_operations(self):
        """Test task CRUD operations"""
        print("\n📋 Testing Task Operations...")
        
        # Create task
        task_data = {
            "title": "Debug Test Task",
            "description": "Testing task creation",
            "priority": "medium",
            "status": "todo"
        }
        
        create_resp = await self.make_request("POST", "/tasks", task_data)
        print(f"Task creation: {create_resp['status']} - {create_resp['data']}")
        
        # List tasks
        list_resp = await self.make_request("GET", "/tasks")
        print(f"Task list: {list_resp['status']} - Found {len(list_resp['data']) if isinstance(list_resp['data'], list) else 'N/A'} tasks")
        
        return create_resp['status'] in [200, 201]
    
    async def test_workflow_operations(self):
        """Test workflow operations"""
        print("\n🔄 Testing Workflow Operations...")
        
        workflow_data = {
            "name": "Debug Test Workflow",
            "resource_type": "task",
            "steps": [
                {
                    "step_number": 1,
                    "approver_role": "supervisor",
                    "description": "Test step"
                }
            ]
        }
        
        create_resp = await self.make_request("POST", "/workflows/templates", workflow_data)
        print(f"Workflow creation: {create_resp['status']} - {create_resp['data']}")
        
        # List workflows
        list_resp = await self.make_request("GET", "/workflows/templates")
        print(f"Workflow list: {list_resp['status']} - Found {len(list_resp['data']) if isinstance(list_resp['data'], list) else 'N/A'} workflows")
        
        return create_resp['status'] in [200, 201]
    
    async def test_organization_operations(self):
        """Test organization operations"""
        print("\n🏢 Testing Organization Operations...")
        
        org_data = {
            "name": "Debug Test Unit",
            "type": "department",
            "level": 4,
            "parent_id": None
        }
        
        create_resp = await self.make_request("POST", "/org_units", org_data)
        print(f"Org unit creation: {create_resp['status']} - {create_resp['data']}")
        
        # List org units
        list_resp = await self.make_request("GET", "/org_units")
        print(f"Org unit list: {list_resp['status']} - {list_resp['data']}")
        
        return create_resp['status'] in [200, 201]
    
    async def test_role_operations(self):
        """Test role operations"""
        print("\n👥 Testing Role Operations...")
        
        role_data = {
            "name": "Debug Test Role",
            "code": "DEBUG_TEST",
            "level": 8,
            "color": "#FF5733",
            "description": "Test role"
        }
        
        create_resp = await self.make_request("POST", "/roles", role_data)
        print(f"Role creation: {create_resp['status']} - {create_resp['data']}")
        
        # List roles
        list_resp = await self.make_request("GET", "/roles")
        print(f"Role list: {list_resp['status']} - Found {len(list_resp['data']) if isinstance(list_resp['data'], list) else 'N/A'} roles")
        
        return create_resp['status'] in [200, 201]
    
    async def test_error_handling(self):
        """Test basic error handling"""
        print("\n🚨 Testing Error Handling...")
        
        # Test unauthorized access
        no_auth_resp = await self.make_request("GET", "/users/me", headers={})
        print(f"No auth access: {no_auth_resp['status']} - {no_auth_resp['data']}")
        
        # Test invalid endpoint
        invalid_resp = await self.make_request("GET", "/nonexistent")
        print(f"Invalid endpoint: {invalid_resp['status']} - {invalid_resp['data']}")
        
        # Test malformed data
        malformed_resp = await self.make_request("POST", "/tasks", {"invalid": "data"})
        print(f"Malformed data: {malformed_resp['status']} - {malformed_resp['data']}")
        
        return True
    
    async def test_performance(self):
        """Test basic performance"""
        print("\n⚡ Testing Performance...")
        
        start_time = time.time()
        resp = await self.make_request("GET", "/dashboard/stats")
        response_time = (time.time() - start_time) * 1000
        
        print(f"Dashboard stats: {resp['status']} - {response_time:.0f}ms")
        
        return response_time < 1000  # 1 second threshold
    
    async def test_security_basics(self):
        """Test basic security"""
        print("\n🔒 Testing Security Basics...")
        
        # Check if password is exposed in profile
        profile_resp = await self.make_request("GET", "/users/me")
        if profile_resp['status'] == 200:
            profile = profile_resp['data']
            password_secure = 'password' not in profile and 'password_hash' not in profile
            print(f"Password security: {'✅ SECURE' if password_secure else '❌ EXPOSED'}")
        
        # Test token validation
        invalid_token_resp = await self.make_request("GET", "/users/me", 
                                                   headers={"Authorization": "Bearer invalid_token"})
        token_validation = invalid_token_resp['status'] == 401
        print(f"Token validation: {'✅ WORKING' if token_validation else '❌ BROKEN'}")
        
        return True
    
    async def run_debug_tests(self):
        """Run all debug tests"""
        print("🚀 STARTING DEBUG TESTS FOR PHASES 8-11")
        print("=" * 60)
        
        try:
            await self.setup_session()
            
            # Test authentication first
            auth_success = await self.test_basic_auth()
            if not auth_success:
                print("❌ Authentication failed - cannot proceed with other tests")
                return
            
            # Test core operations
            await self.test_task_operations()
            await self.test_workflow_operations()
            await self.test_organization_operations()
            await self.test_role_operations()
            
            # Test other aspects
            await self.test_error_handling()
            await self.test_performance()
            await self.test_security_basics()
            
            print("\n" + "=" * 60)
            print("🎯 DEBUG TESTS COMPLETED")
            
        except Exception as e:
            print(f"❌ Debug test execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup_session()

async def main():
    """Main debug test execution"""
    suite = DebugTestSuite()
    await suite.run_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())