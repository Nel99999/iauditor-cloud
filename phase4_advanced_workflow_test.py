import requests
import sys
import json
from datetime import datetime, timezone, timedelta
import uuid
import io
import os

class AdvancedWorkflowAPITester:
    def __init__(self, base_url="https://opsman-v2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_user_id = None
        self.test_template_id = None
        self.test_permission_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else str(response_data)[:500]}"
            
            self.log_test(name, success, details)
            
            return success, response_data

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_user(self):
        """Register and login test user"""
        user_email = f"advanced_wf_user_{uuid.uuid4().hex[:8]}@testcompany.com"
        reg_data = {
            "email": user_email,
            "password": "AdvancedWF123!",
            "name": "Advanced Workflow Test User",
            "organization_name": f"Advanced WF Test Org {uuid.uuid4().hex[:6]}"
        }
        
        success, response = self.run_test(
            "Register User for Advanced Workflows",
            "POST",
            "auth/register",
            200,
            data=reg_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id')
            print(f"✅ Created Test User: {user_email}")
            return True
        
        return False

    def setup_workflow_template(self):
        """Create a workflow template for testing"""
        template_data = {
            "name": f"Test SLA Workflow {uuid.uuid4().hex[:6]}",
            "description": "Test workflow for SLA tracking",
            "resource_type": "inspection",
            "steps": [
                {
                    "step_number": 1,
                    "name": "Initial Review",
                    "approver_role": "supervisor",
                    "approval_type": "any_one",
                    "timeout_hours": 24
                },
                {
                    "step_number": 2,
                    "name": "Final Approval",
                    "approver_role": "manager",
                    "approval_type": "any_one",
                    "timeout_hours": 48
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Workflow Template for Testing",
            "POST",
            "workflows/templates",
            201,
            data=template_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.test_template_id = response['id']
            print(f"✅ Created Test Template: {self.test_template_id}")
            return True
        
        return False

    def get_permission_id(self):
        """Get a permission ID for testing"""
        success, response = self.run_test(
            "Get Permissions for Testing",
            "GET",
            "permissions",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            self.test_permission_id = response[0]['id']
            print(f"✅ Using Permission ID: {self.test_permission_id}")
            return True
        
        return False

    # =====================================
    # CONDITIONAL ROUTING TESTS
    # =====================================

    def test_conditional_routing_equals(self):
        """Test conditional routing with equals operator"""
        test_data = {
            "resource_data": {"priority": "high", "score": 85},
            "conditions": [
                {"field": "priority", "operator": "equals", "value": "high", "next_step": 2}
            ],
            "default_step": 1
        }
        
        success, response = self.run_test(
            "Conditional Routing - Equals Condition",
            "POST",
            "advanced-workflows/conditional-routing/evaluate",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            if response.get("next_step") != 2 or response.get("condition_met") != True:
                self.log_test("Conditional Routing Equals Validation", False, f"Expected next_step=2, condition_met=True, got {response}")
                return False
        
        return success

    def test_conditional_routing_greater_than(self):
        """Test conditional routing with greater_than operator"""
        test_data = {
            "resource_data": {"score": 85, "priority": "medium"},
            "conditions": [
                {"field": "score", "operator": "greater_than", "value": 80, "next_step": 3}
            ],
            "default_step": 1
        }
        
        success, response = self.run_test(
            "Conditional Routing - Greater Than Condition",
            "POST",
            "advanced-workflows/conditional-routing/evaluate",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            if response.get("next_step") != 3 or response.get("condition_met") != True:
                self.log_test("Conditional Routing Greater Than Validation", False, f"Expected next_step=3, condition_met=True, got {response}")
                return False
        
        return success

    def test_conditional_routing_multiple_conditions(self):
        """Test conditional routing with multiple conditions (first match wins)"""
        test_data = {
            "resource_data": {"priority": "high", "score": 95, "category": "urgent"},
            "conditions": [
                {"field": "priority", "operator": "equals", "value": "high", "next_step": 2},
                {"field": "score", "operator": "greater_than", "value": 90, "next_step": 3},
                {"field": "category", "operator": "equals", "value": "urgent", "next_step": 4}
            ],
            "default_step": 1
        }
        
        success, response = self.run_test(
            "Conditional Routing - Multiple Conditions (First Match)",
            "POST",
            "advanced-workflows/conditional-routing/evaluate",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            # Should match first condition (priority=high -> step 2)
            if response.get("next_step") != 2 or response.get("condition_met") != True:
                self.log_test("Conditional Routing Multiple Conditions Validation", False, f"Expected next_step=2 (first match), got {response}")
                return False
        
        return success

    def test_conditional_routing_no_match(self):
        """Test conditional routing with no matching conditions (use default)"""
        test_data = {
            "resource_data": {"priority": "low", "score": 45},
            "conditions": [
                {"field": "priority", "operator": "equals", "value": "high", "next_step": 2},
                {"field": "score", "operator": "greater_than", "value": 80, "next_step": 3}
            ],
            "default_step": 1
        }
        
        success, response = self.run_test(
            "Conditional Routing - No Match (Default Step)",
            "POST",
            "advanced-workflows/conditional-routing/evaluate",
            200,
            data=test_data
        )
        
        if success and isinstance(response, dict):
            if response.get("next_step") != 1 or response.get("condition_met") != False:
                self.log_test("Conditional Routing No Match Validation", False, f"Expected next_step=1, condition_met=False, got {response}")
                return False
        
        return success

    def test_conditional_routing_all_operators(self):
        """Test all conditional routing operators"""
        operators_tests = [
            {"operator": "equals", "resource_value": "test", "condition_value": "test", "should_match": True},
            {"operator": "not_equals", "resource_value": "test", "condition_value": "other", "should_match": True},
            {"operator": "greater_than", "resource_value": 100, "condition_value": 50, "should_match": True},
            {"operator": "less_than", "resource_value": 30, "condition_value": 50, "should_match": True},
            {"operator": "greater_or_equal", "resource_value": 50, "condition_value": 50, "should_match": True},
            {"operator": "less_or_equal", "resource_value": 50, "condition_value": 50, "should_match": True},
            {"operator": "contains", "resource_value": "hello world", "condition_value": "world", "should_match": True},
            {"operator": "in", "resource_value": "apple", "condition_value": ["apple", "banana"], "should_match": True}
        ]
        
        all_success = True
        for test_case in operators_tests:
            test_data = {
                "resource_data": {"test_field": test_case["resource_value"]},
                "conditions": [
                    {"field": "test_field", "operator": test_case["operator"], "value": test_case["condition_value"], "next_step": 2}
                ],
                "default_step": 1
            }
            
            success, response = self.run_test(
                f"Conditional Routing - {test_case['operator'].title()} Operator",
                "POST",
                "advanced-workflows/conditional-routing/evaluate",
                200,
                data=test_data
            )
            
            if success and isinstance(response, dict):
                expected_step = 2 if test_case["should_match"] else 1
                expected_condition_met = test_case["should_match"]
                
                if response.get("next_step") != expected_step or response.get("condition_met") != expected_condition_met:
                    self.log_test(f"Conditional Routing {test_case['operator']} Validation", False, 
                                f"Expected next_step={expected_step}, condition_met={expected_condition_met}, got {response}")
                    all_success = False
            else:
                all_success = False
        
        return all_success

    # =====================================
    # SLA TRACKING TESTS
    # =====================================

    def test_create_sla_config(self):
        """Test creating SLA configuration"""
        if not self.test_template_id:
            self.log_test("Create SLA Config", False, "No workflow template available for testing")
            return False
        
        sla_data = {
            "workflow_template_id": self.test_template_id,
            "target_hours": 48,
            "warning_hours": 36,
            "escalation_hours": 40
        }
        
        success, response = self.run_test(
            "Create SLA Configuration",
            "POST",
            "advanced-workflows/sla/config",
            200,
            data=sla_data
        )
        
        if success and isinstance(response, dict):
            if "message" not in response or "created" not in response["message"]:
                self.log_test("SLA Config Creation Message Check", False, f"Expected creation message, got: {response}")
                return False
        
        return success

    def test_update_sla_config(self):
        """Test updating existing SLA configuration"""
        if not self.test_template_id:
            self.log_test("Update SLA Config", False, "No workflow template available for testing")
            return False
        
        updated_sla_data = {
            "workflow_template_id": self.test_template_id,
            "target_hours": 72,
            "warning_hours": 60,
            "escalation_hours": 66
        }
        
        success, response = self.run_test(
            "Update SLA Configuration",
            "POST",
            "advanced-workflows/sla/config",
            200,
            data=updated_sla_data
        )
        
        if success and isinstance(response, dict):
            if "message" not in response or "updated" not in response["message"]:
                self.log_test("SLA Config Update Message Check", False, f"Expected update message, got: {response}")
                return False
        
        return success

    def test_get_sla_config(self):
        """Test getting SLA configuration"""
        if not self.test_template_id:
            self.log_test("Get SLA Config", False, "No workflow template available for testing")
            return False
        
        success, response = self.run_test(
            "Get SLA Configuration",
            "GET",
            f"advanced-workflows/sla/config/{self.test_template_id}",
            200
        )
        
        if success and isinstance(response, dict):
            required_fields = ["workflow_template_id", "target_hours", "warning_hours", "escalation_hours"]
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("SLA Config Fields Check", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify updated values
            if response.get("target_hours") != 72:
                self.log_test("SLA Config Update Verification", False, f"Expected target_hours=72, got {response.get('target_hours')}")
                return False
        
        return success

    def test_get_sla_config_not_found(self):
        """Test getting SLA config for non-existent template"""
        fake_template_id = str(uuid.uuid4())
        
        success, response = self.run_test(
            "Get SLA Config (Not Found)",
            "GET",
            f"advanced-workflows/sla/config/{fake_template_id}",
            404
        )
        
        return success

    def test_get_sla_metrics_no_workflows(self):
        """Test SLA metrics with no completed workflows"""
        if not self.test_template_id:
            self.log_test("Get SLA Metrics (No Workflows)", False, "No workflow template available for testing")
            return False
        
        success, response = self.run_test(
            "Get SLA Metrics (No Workflows)",
            "GET",
            f"advanced-workflows/sla/metrics/{self.test_template_id}?days=30",
            200
        )
        
        if success and isinstance(response, dict):
            required_fields = ["total_workflows", "within_sla", "breached_sla", "average_completion_hours", "sla_compliance_rate"]
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("SLA Metrics Fields Check", False, f"Missing fields: {missing_fields}")
                return False
            
            # Should be all zeros for no workflows
            if response.get("total_workflows") != 0:
                self.log_test("SLA Metrics No Workflows Check", False, f"Expected total_workflows=0, got {response.get('total_workflows')}")
                return False
        
        return success

    def test_create_and_complete_workflow_for_sla(self):
        """Create and complete workflow instances for SLA testing"""
        if not self.test_template_id:
            self.log_test("Create Workflow for SLA", False, "No workflow template available for testing")
            return False
        
        # Create workflow instances
        workflow_data = {
            "template_id": self.test_template_id,
            "resource_type": "inspection",
            "resource_id": "test-inspection-001",
            "resource_name": "Test Inspection for SLA"
        }
        
        workflow_ids = []
        
        # Create 2 workflows
        for i in range(2):
            success, response = self.run_test(
                f"Create Workflow Instance {i+1} for SLA",
                "POST",
                "workflows/instances",
                201,
                data=workflow_data
            )
            
            if success and isinstance(response, dict) and 'id' in response:
                workflow_ids.append(response['id'])
        
        return len(workflow_ids) > 0

    def test_get_sla_metrics_with_workflows(self):
        """Test SLA metrics after creating workflows"""
        if not self.test_template_id:
            self.log_test("Get SLA Metrics (With Workflows)", False, "No workflow template available for testing")
            return False
        
        success, response = self.run_test(
            "Get SLA Metrics (With Workflows)",
            "GET",
            f"advanced-workflows/sla/metrics/{self.test_template_id}?days=30",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify structure is correct
            required_fields = ["total_workflows", "within_sla", "breached_sla", "average_completion_hours", "sla_compliance_rate"]
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("SLA Metrics With Workflows Fields Check", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify calculations are reasonable
            total = response.get("total_workflows", 0)
            within_sla = response.get("within_sla", 0)
            breached = response.get("breached_sla", 0)
            
            if total != within_sla + breached:
                self.log_test("SLA Metrics Calculation Check", False, f"Total ({total}) != within_sla ({within_sla}) + breached ({breached})")
                return False
        
        return success

    def test_get_at_risk_workflows(self):
        """Test getting at-risk workflows"""
        success, response = self.run_test(
            "Get At-Risk Workflows",
            "GET",
            "advanced-workflows/sla/at-risk",
            200
        )
        
        if success and isinstance(response, list):
            # Verify structure of at-risk workflows
            for workflow in response:
                required_fields = ["workflow_id", "workflow_name", "resource_type", "elapsed_hours", "target_hours", "at_risk"]
                missing_fields = [field for field in required_fields if field not in workflow]
                if missing_fields:
                    self.log_test("At-Risk Workflow Fields Check", False, f"Missing fields in workflow: {missing_fields}")
                    return False
        
        return success

    # =====================================
    # TIME-BASED PERMISSIONS TESTS
    # =====================================

    def test_create_time_based_permission(self):
        """Test creating time-based permission"""
        if not self.test_user_id or not self.test_permission_id:
            self.log_test("Create Time-Based Permission", False, "Missing user_id or permission_id for testing")
            return False
        
        # Create permission valid for next week, business hours only
        valid_from = datetime.now(timezone.utc).isoformat()
        valid_until = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        permission_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "days_of_week": [0, 1, 2, 3, 4],  # Monday to Friday
            "hours_of_day": [9, 10, 11, 12, 13, 14, 15, 16, 17],  # 9 AM to 5 PM
            "reason": "Business hours only access for testing"
        }
        
        success, response = self.run_test(
            "Create Time-Based Permission",
            "POST",
            "advanced-workflows/time-based-permissions",
            200,
            data=permission_data
        )
        
        if success and isinstance(response, dict):
            if "message" not in response or "created" not in response["message"]:
                self.log_test("Time-Based Permission Creation Message Check", False, f"Expected creation message, got: {response}")
                return False
        
        return success

    def test_list_time_based_permissions(self):
        """Test listing time-based permissions"""
        success, response = self.run_test(
            "List Time-Based Permissions",
            "GET",
            "advanced-workflows/time-based-permissions",
            200
        )
        
        if success and isinstance(response, list):
            # Should have at least one permission from previous test
            if len(response) == 0:
                self.log_test("Time-Based Permissions List Check", False, "Expected at least one permission in list")
                return False
            
            # Verify structure of permissions
            for permission in response:
                required_fields = ["user_id", "permission_id", "valid_from", "valid_until", "reason"]
                missing_fields = [field for field in required_fields if field not in permission]
                if missing_fields:
                    self.log_test("Time-Based Permission Fields Check", False, f"Missing fields: {missing_fields}")
                    return False
        
        return success

    def test_list_time_based_permissions_filtered(self):
        """Test listing time-based permissions with user filter"""
        if not self.test_user_id:
            self.log_test("List Time-Based Permissions (Filtered)", False, "No user_id for filtering")
            return False
        
        success, response = self.run_test(
            "List Time-Based Permissions (User Filter)",
            "GET",
            f"advanced-workflows/time-based-permissions?user_id={self.test_user_id}",
            200
        )
        
        if success and isinstance(response, list):
            # All permissions should be for the specified user
            for permission in response:
                if permission.get("user_id") != self.test_user_id:
                    self.log_test("Time-Based Permissions Filter Check", False, f"Found permission for wrong user: {permission.get('user_id')}")
                    return False
        
        return success

    def test_check_time_based_permission_valid(self):
        """Test checking time-based permission during valid time"""
        if not self.test_user_id or not self.test_permission_id:
            self.log_test("Check Time-Based Permission (Valid)", False, "Missing user_id or permission_id for testing")
            return False
        
        check_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id
        }
        
        success, response = self.run_test(
            "Check Time-Based Permission (Valid Time)",
            "POST",
            "advanced-workflows/time-based-permissions/check",
            200,
            data=check_data
        )
        
        if success and isinstance(response, dict):
            # Note: This might return False if tested outside business hours
            # We'll accept both True and False as valid responses
            if "granted" not in response or "reason" not in response:
                self.log_test("Time-Based Permission Check Structure", False, f"Missing granted or reason fields: {response}")
                return False
        
        return success

    def test_check_time_based_permission_expired(self):
        """Test checking expired time-based permission"""
        if not self.test_user_id or not self.test_permission_id:
            self.log_test("Check Time-Based Permission (Expired)", False, "Missing user_id or permission_id for testing")
            return False
        
        # Create expired permission
        expired_from = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        expired_until = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        
        expired_permission_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id + "_expired",
            "valid_from": expired_from,
            "valid_until": expired_until,
            "days_of_week": [0, 1, 2, 3, 4, 5, 6],  # All days
            "hours_of_day": list(range(24)),  # All hours
            "reason": "Expired permission for testing"
        }
        
        # Create the expired permission
        create_success, _ = self.run_test(
            "Create Expired Time-Based Permission",
            "POST",
            "advanced-workflows/time-based-permissions",
            200,
            data=expired_permission_data
        )
        
        if not create_success:
            return False
        
        # Check the expired permission
        check_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id + "_expired"
        }
        
        success, response = self.run_test(
            "Check Time-Based Permission (Expired)",
            "POST",
            "advanced-workflows/time-based-permissions/check",
            200,
            data=check_data
        )
        
        if success and isinstance(response, dict):
            if response.get("granted") != False or "expired" not in response.get("reason", "").lower():
                self.log_test("Time-Based Permission Expired Check", False, f"Expected granted=False with expired reason, got: {response}")
                return False
        
        return success

    def test_check_time_based_permission_future(self):
        """Test checking future time-based permission"""
        if not self.test_user_id or not self.test_permission_id:
            self.log_test("Check Time-Based Permission (Future)", False, "Missing user_id or permission_id for testing")
            return False
        
        # Create future permission
        future_from = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        future_until = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        
        future_permission_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id + "_future",
            "valid_from": future_from,
            "valid_until": future_until,
            "days_of_week": [0, 1, 2, 3, 4, 5, 6],  # All days
            "hours_of_day": list(range(24)),  # All hours
            "reason": "Future permission for testing"
        }
        
        # Create the future permission
        create_success, _ = self.run_test(
            "Create Future Time-Based Permission",
            "POST",
            "advanced-workflows/time-based-permissions",
            200,
            data=future_permission_data
        )
        
        if not create_success:
            return False
        
        # Check the future permission
        check_data = {
            "user_id": self.test_user_id,
            "permission_id": self.test_permission_id + "_future"
        }
        
        success, response = self.run_test(
            "Check Time-Based Permission (Future)",
            "POST",
            "advanced-workflows/time-based-permissions/check",
            200,
            data=check_data
        )
        
        if success and isinstance(response, dict):
            if response.get("granted") != False or "not yet valid" not in response.get("reason", "").lower():
                self.log_test("Time-Based Permission Future Check", False, f"Expected granted=False with 'not yet valid' reason, got: {response}")
                return False
        
        return success

    def test_delete_time_based_permission(self):
        """Test deleting time-based permission"""
        if not self.test_user_id or not self.test_permission_id:
            self.log_test("Delete Time-Based Permission", False, "Missing user_id or permission_id for testing")
            return False
        
        success, response = self.run_test(
            "Delete Time-Based Permission",
            "DELETE",
            f"advanced-workflows/time-based-permissions/{self.test_user_id}/{self.test_permission_id}",
            200
        )
        
        if success and isinstance(response, dict):
            if "message" not in response or "deleted" not in response["message"]:
                self.log_test("Time-Based Permission Deletion Message Check", False, f"Expected deletion message, got: {response}")
                return False
        
        return success

    def test_delete_time_based_permission_not_found(self):
        """Test deleting non-existent time-based permission"""
        fake_user_id = str(uuid.uuid4())
        fake_permission_id = str(uuid.uuid4())
        
        success, response = self.run_test(
            "Delete Time-Based Permission (Not Found)",
            "DELETE",
            f"advanced-workflows/time-based-permissions/{fake_user_id}/{fake_permission_id}",
            404
        )
        
        return success

    # =====================================
    # AUTHORIZATION TESTS
    # =====================================

    def test_unauthorized_access(self):
        """Test all endpoints without authentication"""
        old_token = self.token
        self.token = None
        
        endpoints_to_test = [
            ("POST", "advanced-workflows/conditional-routing/evaluate", {"resource_data": {}, "conditions": [], "default_step": 1}),
            ("POST", "advanced-workflows/sla/config", {"workflow_template_id": "test", "target_hours": 24, "warning_hours": 20, "escalation_hours": 22}),
            ("GET", "advanced-workflows/sla/config/test-id", None),
            ("GET", "advanced-workflows/sla/metrics/test-id", None),
            ("GET", "advanced-workflows/sla/at-risk", None),
            ("POST", "advanced-workflows/time-based-permissions", {"user_id": "test", "permission_id": "test", "valid_from": "2024-01-01", "valid_until": "2024-12-31", "reason": "test"}),
            ("GET", "advanced-workflows/time-based-permissions", None),
            ("POST", "advanced-workflows/time-based-permissions/check", {"user_id": "test", "permission_id": "test"}),
            ("DELETE", "advanced-workflows/time-based-permissions/test/test", None)
        ]
        
        all_success = True
        for method, endpoint, data in endpoints_to_test:
            success, _ = self.run_test(
                f"Unauthorized Access - {method} {endpoint}",
                method,
                endpoint,
                401,
                data=data
            )
            if not success:
                all_success = False
        
        self.token = old_token
        return all_success

    def run_all_tests(self):
        """Run all advanced workflow tests"""
        print("🚀 Starting Phase 4 Advanced Workflow API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Setup test environment
        if not self.setup_test_user():
            print("❌ User setup failed, stopping tests")
            return self.generate_report()
        
        if not self.setup_workflow_template():
            print("❌ Workflow template setup failed, continuing with limited tests")
        
        if not self.get_permission_id():
            print("❌ Permission ID setup failed, continuing with limited tests")

        # A. CONDITIONAL ROUTING TESTS
        print("\n🔄 Testing Conditional Routing...")
        self.test_conditional_routing_equals()
        self.test_conditional_routing_greater_than()
        self.test_conditional_routing_multiple_conditions()
        self.test_conditional_routing_no_match()
        self.test_conditional_routing_all_operators()

        # B. SLA TRACKING TESTS
        print("\n📊 Testing SLA Tracking...")
        self.test_create_sla_config()
        self.test_update_sla_config()
        self.test_get_sla_config()
        self.test_get_sla_config_not_found()
        self.test_get_sla_metrics_no_workflows()
        self.test_create_and_complete_workflow_for_sla()
        self.test_get_sla_metrics_with_workflows()
        self.test_get_at_risk_workflows()

        # C. TIME-BASED PERMISSIONS TESTS
        print("\n⏰ Testing Time-Based Permissions...")
        self.test_create_time_based_permission()
        self.test_list_time_based_permissions()
        self.test_list_time_based_permissions_filtered()
        self.test_check_time_based_permission_valid()
        self.test_check_time_based_permission_expired()
        self.test_check_time_based_permission_future()
        self.test_delete_time_based_permission()
        self.test_delete_time_based_permission_not_found()

        # D. AUTHORIZATION TESTS
        print("\n🔒 Testing Authorization...")
        self.test_unauthorized_access()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 PHASE 4 ADVANCED WORKFLOW TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": self.tests_run - self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "test_results": self.test_results
        }


if __name__ == "__main__":
    print("🚀 Starting Phase 4 Advanced Workflow Backend API Tests")
    print("=" * 80)
    
    # Run Phase 4 Advanced Workflow tests
    advanced_workflow_tester = AdvancedWorkflowAPITester()
    advanced_workflow_results = advanced_workflow_tester.run_all_tests()
    
    # Generate summary
    print("\n" + "=" * 80)
    print("🎯 PHASE 4 ADVANCED WORKFLOW TEST SUMMARY")
    print("=" * 80)
    
    rate = advanced_workflow_results['success_rate']
    status = "✅" if rate >= 90 else "⚠️" if rate >= 80 else "❌"
    print(f"{status} Advanced Workflows: {advanced_workflow_results['passed_tests']}/{advanced_workflow_results['total_tests']} ({rate:.1f}%)")
    
    if rate >= 90:
        print("\n🎉 EXCELLENT! Phase 4 Advanced Workflow features are operational and ready for production.")
    elif rate >= 80:
        print("\n✅ GOOD! Most Phase 4 features working well with minor issues.")
    else:
        print("\n⚠️ ATTENTION NEEDED! Phase 4 features require fixes before production.")
    
    print("=" * 80)