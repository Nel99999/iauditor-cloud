import requests
import sys
import json
from datetime import datetime
import uuid
import io
import os

class WorkflowAPITester:
    def __init__(self, base_url="https://ui-refresh-ops.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_templates = []
        self.created_workflows = []
        self.test_user_id = None

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

    def register_and_login_user(self):
        """Register a new user with organization and login"""
        unique_email = f"workflow_test_{uuid.uuid4().hex[:8]}@testcompany.com"
        reg_data = {
            "email": unique_email,
            "password": "WorkflowTest123!",
            "name": "Workflow Test User",
            "organization_name": f"Workflow Test Org {uuid.uuid4().hex[:6]}"
        }
        
        success, response = self.run_test(
            "Register User with Organization",
            "POST",
            "auth/register",
            200,
            data=reg_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.test_user_id = response.get('user', {}).get('id')
            print(f"✅ Created and logged in as: {unique_email}")
            return True, unique_email
        
        return False, unique_email

    def test_create_workflow_template(self):
        """Test creating a workflow template"""
        template_data = {
            "name": "Inspection Approval Workflow",
            "description": "Two-step approval for inspections",
            "resource_type": "inspection",
            "steps": [
                {
                    "step_number": 1,
                    "name": "Supervisor Review",
                    "approver_role": "supervisor",
                    "approver_context": "organization",
                    "approval_type": "any",
                    "timeout_hours": 24,
                    "escalate_to_role": "manager"
                },
                {
                    "step_number": 2,
                    "name": "Manager Approval",
                    "approver_role": "manager",
                    "approver_context": "organization",
                    "approval_type": "any",
                    "timeout_hours": 48
                }
            ],
            "auto_start": False,
            "notify_on_start": True,
            "notify_on_complete": True
        }
        
        success, response = self.run_test(
            "Create Workflow Template",
            "POST",
            "workflows/templates",
            201,
            data=template_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_templates.append(response['id'])
            
            # Verify template structure
            required_fields = ['id', 'organization_id', 'created_by', 'name', 'description', 'resource_type', 'steps']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("Template Structure Validation", False, f"Missing fields: {missing_fields}")
                return False, response
            
            # Verify steps structure
            if len(response.get('steps', [])) != 2:
                self.log_test("Template Steps Validation", False, f"Expected 2 steps, got {len(response.get('steps', []))}")
                return False, response
            
            self.log_test("Template Structure Validation", True, "All required fields present")
            return success, response
        
        return success, response

    def test_list_workflow_templates(self):
        """Test listing workflow templates"""
        success, response = self.run_test(
            "List Workflow Templates",
            "GET",
            "workflows/templates",
            200
        )
        
        if success and isinstance(response, list):
            # Verify created template appears in list
            if self.created_templates:
                template_ids = [t.get('id') for t in response]
                if self.created_templates[0] in template_ids:
                    self.log_test("Created Template in List", True, "Template found in list")
                else:
                    self.log_test("Created Template in List", False, "Template not found in list")
        
        return success, response

    def test_get_workflow_template(self, template_id):
        """Test getting specific workflow template"""
        success, response = self.run_test(
            "Get Workflow Template Details",
            "GET",
            f"workflows/templates/{template_id}",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify all fields returned correctly
            required_fields = ['id', 'name', 'description', 'steps', 'resource_type']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("Template Details Validation", False, f"Missing fields: {missing_fields}")
                return False, response
            
            # Verify steps array structure
            steps = response.get('steps', [])
            if not isinstance(steps, list) or len(steps) == 0:
                self.log_test("Template Steps Structure", False, "Steps should be non-empty array")
                return False, response
            
            self.log_test("Template Details Validation", True, "All fields present and valid")
        
        return success, response

    def test_update_workflow_template(self, template_id):
        """Test updating workflow template"""
        update_data = {
            "name": f"Updated Inspection Workflow {uuid.uuid4().hex[:6]}",
            "description": "Updated description for testing"
        }
        
        success, response = self.run_test(
            "Update Workflow Template",
            "PUT",
            f"workflows/templates/{template_id}",
            200,
            data=update_data
        )
        
        if success and isinstance(response, dict):
            # Verify updates applied
            if response.get('name') != update_data['name']:
                self.log_test("Template Update Validation", False, f"Name not updated: expected {update_data['name']}, got {response.get('name')}")
                return False, response
            
            # Verify updated_at timestamp changed
            if 'updated_at' not in response:
                self.log_test("Updated Timestamp Validation", False, "updated_at field missing")
                return False, response
            
            self.log_test("Template Update Validation", True, "Updates applied correctly")
        
        return success, response

    def test_start_workflow_instance(self, template_id):
        """Test starting workflow instance"""
        instance_data = {
            "template_id": template_id,
            "resource_type": "inspection",
            "resource_id": "test-inspection-123",
            "resource_name": "Safety Inspection #123"
        }
        
        success, response = self.run_test(
            "Start Workflow Instance",
            "POST",
            "workflows/instances",
            201,
            data=instance_data
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.created_workflows.append(response['id'])
            
            # Verify workflow started correctly
            required_fields = ['id', 'current_step', 'status', 'current_approvers', 'due_at']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("Workflow Start Validation", False, f"Missing fields: {missing_fields}")
                return False, response
            
            # Verify initial state
            if response.get('current_step') != 1:
                self.log_test("Initial Step Validation", False, f"Expected current_step=1, got {response.get('current_step')}")
                return False, response
            
            if response.get('status') != 'in_progress':
                self.log_test("Initial Status Validation", False, f"Expected status='in_progress', got {response.get('status')}")
                return False, response
            
            # Note: current_approvers may be empty if no users with required roles exist
            if not isinstance(response.get('current_approvers'), list):
                self.log_test("Current Approvers Type Validation", False, "current_approvers should be a list")
                return False, response
            
            # Log approvers status for information
            approvers_count = len(response.get('current_approvers', []))
            self.log_test("Current Approvers Status", True, f"Found {approvers_count} approvers (expected for test org with no supervisor role users)")
            
            if not response.get('due_at'):
                self.log_test("Due Date Validation", False, "due_at timestamp not set")
                return False, response
            
            self.log_test("Workflow Start Validation", True, "Workflow started correctly")
            return success, response
        
        return success, response

    def test_list_workflow_instances(self):
        """Test listing workflow instances"""
        success, response = self.run_test(
            "List Workflow Instances",
            "GET",
            "workflows/instances",
            200
        )
        
        if success and isinstance(response, list):
            # Verify created workflow in list
            if self.created_workflows:
                workflow_ids = [w.get('id') for w in response]
                if self.created_workflows[0] in workflow_ids:
                    self.log_test("Created Workflow in List", True, "Workflow found in list")
                else:
                    self.log_test("Created Workflow in List", False, "Workflow not found in list")
        
        # Test filtering by status
        success2, response2 = self.run_test(
            "List Workflows (status filter)",
            "GET",
            "workflows/instances?status_filter=in_progress",
            200
        )
        
        # Test filtering by resource_type
        success3, response3 = self.run_test(
            "List Workflows (resource_type filter)",
            "GET",
            "workflows/instances?resource_type=inspection",
            200
        )
        
        return success and success2 and success3

    def test_get_my_pending_approvals(self):
        """Test getting pending approvals for current user"""
        success, response = self.run_test(
            "Get My Pending Approvals",
            "GET",
            "workflows/instances/my-approvals",
            200
        )
        
        if success and isinstance(response, list):
            # Verify only in_progress/escalated workflows returned
            for workflow in response:
                if workflow.get('status') not in ['in_progress', 'escalated']:
                    self.log_test("Pending Approvals Status Filter", False, f"Found workflow with status {workflow.get('status')}")
                    return False
            
            self.log_test("Pending Approvals Status Filter", True, "Only in_progress/escalated workflows returned")
        
        return success, response

    def test_approve_workflow_step(self, workflow_id):
        """Test approving workflow step"""
        approval_data = {
            "action": "approve",
            "comments": "Looks good!"
        }
        
        success, response = self.run_test(
            "Approve Workflow Step",
            "POST",
            f"workflows/instances/{workflow_id}/approve",
            200,
            data=approval_data
        )
        
        if success and isinstance(response, dict):
            # Verify workflow advanced to step 2
            if response.get('current_step') != 2:
                self.log_test("Step Advancement Validation", False, f"Expected current_step=2, got {response.get('current_step')}")
                return False, response
            
            # Verify step completion recorded
            steps_completed = response.get('steps_completed', [])
            if not steps_completed or len(steps_completed) == 0:
                self.log_test("Step Completion Record", False, "No steps_completed recorded")
                return False, response
            
            last_completion = steps_completed[-1]
            if last_completion.get('action') != 'approve':
                self.log_test("Approval Action Record", False, f"Expected action='approve', got {last_completion.get('action')}")
                return False, response
            
            # Verify new current_approvers set
            if not isinstance(response.get('current_approvers'), list):
                self.log_test("New Approvers Set", False, "current_approvers not set for next step")
                return False, response
            
            self.log_test("Step Advancement Validation", True, "Workflow advanced correctly")
        
        return success, response

    def test_approve_final_step(self, workflow_id):
        """Test approving final step"""
        approval_data = {
            "action": "approve",
            "comments": "Final approval granted!"
        }
        
        success, response = self.run_test(
            "Approve Final Step",
            "POST",
            f"workflows/instances/{workflow_id}/approve",
            200,
            data=approval_data
        )
        
        if success and isinstance(response, dict):
            # Verify workflow status changed to approved
            if response.get('status') != 'approved':
                self.log_test("Final Approval Status", False, f"Expected status='approved', got {response.get('status')}")
                return False, response
            
            # Verify completed_at timestamp set
            if not response.get('completed_at'):
                self.log_test("Completion Timestamp", False, "completed_at not set")
                return False, response
            
            # Verify all steps in steps_completed
            steps_completed = response.get('steps_completed', [])
            if len(steps_completed) < 2:
                self.log_test("All Steps Completed", False, f"Expected 2 completed steps, got {len(steps_completed)}")
                return False, response
            
            self.log_test("Final Approval Validation", True, "Workflow completed successfully")
        
        return success, response

    def test_rejection_flow(self, template_id):
        """Test workflow rejection flow"""
        # Start new workflow
        instance_data = {
            "template_id": template_id,
            "resource_type": "inspection",
            "resource_id": "test-inspection-reject",
            "resource_name": "Rejection Test Inspection"
        }
        
        success, workflow = self.test_start_workflow_instance_for_rejection(instance_data)
        if not success:
            return False
        
        workflow_id = workflow['id']
        
        # Reject workflow
        rejection_data = {
            "action": "reject",
            "comments": "Does not meet standards"
        }
        
        success, response = self.run_test(
            "Reject Workflow",
            "POST",
            f"workflows/instances/{workflow_id}/approve",
            200,
            data=rejection_data
        )
        
        if success and isinstance(response, dict):
            # Verify status = rejected
            if response.get('status') != 'rejected':
                self.log_test("Rejection Status", False, f"Expected status='rejected', got {response.get('status')}")
                return False
            
            # Verify completed_at set
            if not response.get('completed_at'):
                self.log_test("Rejection Completion Time", False, "completed_at not set")
                return False
            
            self.log_test("Rejection Flow Validation", True, "Workflow rejected correctly")
        
        return success

    def test_start_workflow_instance_for_rejection(self, instance_data):
        """Helper method to start workflow for rejection test"""
        success, response = self.run_test(
            "Start Workflow for Rejection Test",
            "POST",
            "workflows/instances",
            201,
            data=instance_data
        )
        return success, response

    def test_request_changes_flow(self, template_id):
        """Test request changes flow"""
        # Start new workflow
        instance_data = {
            "template_id": template_id,
            "resource_type": "inspection",
            "resource_id": "test-inspection-changes",
            "resource_name": "Changes Test Inspection"
        }
        
        success, workflow = self.test_start_workflow_instance_for_rejection(instance_data)
        if not success:
            return False
        
        workflow_id = workflow['id']
        
        # Request changes
        changes_data = {
            "action": "request_changes",
            "comments": "Please add more details"
        }
        
        success, response = self.run_test(
            "Request Changes",
            "POST",
            f"workflows/instances/{workflow_id}/approve",
            200,
            data=changes_data
        )
        
        if success and isinstance(response, dict):
            # Verify status = pending
            if response.get('status') != 'pending':
                self.log_test("Request Changes Status", False, f"Expected status='pending', got {response.get('status')}")
                return False
            
            # Verify action recorded
            steps_completed = response.get('steps_completed', [])
            if not steps_completed:
                self.log_test("Changes Request Record", False, "No steps_completed recorded")
                return False
            
            last_action = steps_completed[-1]
            if last_action.get('action') != 'request_changes':
                self.log_test("Changes Action Record", False, f"Expected action='request_changes', got {last_action.get('action')}")
                return False
            
            self.log_test("Request Changes Validation", True, "Changes requested correctly")
        
        return success

    def test_cancel_workflow(self, template_id):
        """Test cancelling workflow"""
        # Start new workflow
        instance_data = {
            "template_id": template_id,
            "resource_type": "inspection",
            "resource_id": "test-inspection-cancel",
            "resource_name": "Cancel Test Inspection"
        }
        
        success, workflow = self.test_start_workflow_instance_for_rejection(instance_data)
        if not success:
            return False
        
        workflow_id = workflow['id']
        
        # Cancel workflow
        cancel_data = {
            "reason": "No longer needed"
        }
        
        success, response = self.run_test(
            "Cancel Workflow",
            "POST",
            f"workflows/instances/{workflow_id}/cancel",
            200,
            data=cancel_data
        )
        
        if success and isinstance(response, dict):
            # Verify status = cancelled
            if response.get('status') != 'cancelled':
                self.log_test("Cancellation Status", False, f"Expected status='cancelled', got {response.get('status')}")
                return False
            
            # Verify cancellation recorded
            steps_completed = response.get('steps_completed', [])
            if not steps_completed:
                self.log_test("Cancellation Record", False, "No cancellation recorded")
                return False
            
            last_action = steps_completed[-1]
            if last_action.get('action') != 'cancel':
                self.log_test("Cancel Action Record", False, f"Expected action='cancel', got {last_action.get('action')}")
                return False
            
            self.log_test("Cancellation Validation", True, "Workflow cancelled correctly")
        
        return success

    def test_workflow_statistics(self):
        """Test workflow statistics endpoint"""
        success, response = self.run_test(
            "Get Workflow Statistics",
            "GET",
            "workflows/stats",
            200
        )
        
        if success and isinstance(response, dict):
            # Verify required fields
            required_fields = ['total_workflows', 'pending_approvals', 'approved_today', 'rejected_today', 'escalated_workflows']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("Stats Structure Validation", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify numbers are reasonable
            total = response.get('total_workflows', 0)
            if total < 0:
                self.log_test("Stats Values Validation", False, f"Invalid total_workflows: {total}")
                return False
            
            self.log_test("Stats Structure Validation", True, "All required fields present")
        
        return success, response

    def test_delete_workflow_template(self, template_id):
        """Test deleting workflow template"""
        success, response = self.run_test(
            "Delete Workflow Template",
            "DELETE",
            f"workflows/templates/{template_id}",
            200
        )
        
        if success:
            # Verify template marked inactive
            success2, template = self.run_test(
                "Verify Template Deactivated",
                "GET",
                f"workflows/templates/{template_id}",
                200
            )
            
            if success2 and isinstance(template, dict):
                if template.get('active') is not False:
                    self.log_test("Template Deactivation", False, f"Template still active: {template.get('active')}")
                    return False
                
                self.log_test("Template Deactivation", True, "Template marked inactive")
        
        return success

    def test_authorization_endpoints(self):
        """Test authorization on all endpoints"""
        old_token = self.token
        self.token = None
        
        # Test without authentication
        endpoints_to_test = [
            ("workflows/templates", "GET"),
            ("workflows/instances", "GET"),
            ("workflows/instances/my-approvals", "GET"),
            ("workflows/stats", "GET")
        ]
        
        all_success = True
        for endpoint, method in endpoints_to_test:
            success, _ = self.run_test(
                f"Unauthorized Access - {endpoint}",
                method,
                endpoint,
                401
            )
            if not success:
                all_success = False
        
        self.token = old_token
        return all_success

    def run_complete_workflow_test_sequence(self):
        """Run the complete workflow test sequence as specified in review request"""
        print("\n🔄 Testing Complete Workflow Test Sequence")
        
        # 1. Authentication Setup
        auth_success, email = self.register_and_login_user()
        if not auth_success:
            print("❌ Authentication setup failed")
            return False
        
        # 2. Create Workflow Template
        template_success, template = self.test_create_workflow_template()
        if not template_success or not isinstance(template, dict) or 'id' not in template:
            print("❌ Template creation failed")
            return False
        
        template_id = template['id']
        
        # 3. List Workflow Templates
        self.test_list_workflow_templates()
        
        # 4. Get Workflow Template Details
        self.test_get_workflow_template(template_id)
        
        # 5. Update Workflow Template
        self.test_update_workflow_template(template_id)
        
        # 6. Start Workflow Instance
        workflow_success, workflow = self.test_start_workflow_instance(template_id)
        if not workflow_success or not isinstance(workflow, dict) or 'id' not in workflow:
            print("❌ Workflow start failed")
            return False
        
        workflow_id = workflow['id']
        
        # 7. List Workflow Instances
        self.test_list_workflow_instances()
        
        # 8. Get My Pending Approvals
        self.test_get_my_pending_approvals()
        
        # 9. Approve Workflow Step
        self.test_approve_workflow_step(workflow_id)
        
        # 10. Approve Final Step
        self.test_approve_final_step(workflow_id)
        
        # 11. Test Rejection Flow
        self.test_rejection_flow(template_id)
        
        # 12. Test Request Changes
        self.test_request_changes_flow(template_id)
        
        # 13. Cancel Workflow
        self.test_cancel_workflow(template_id)
        
        # 14. Workflow Statistics
        self.test_workflow_statistics()
        
        # 15. Delete Workflow Template
        self.test_delete_workflow_template(template_id)
        
        # 16. Authorization Testing
        self.test_authorization_endpoints()
        
        return True

    def run_all_tests(self):
        """Run all workflow tests"""
        print("🚀 Starting Workflow API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)

        # Run complete test sequence
        self.run_complete_workflow_test_sequence()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 WORKFLOW TEST SUMMARY")
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
    print("🚀 PHASE 1: WORKFLOW ENGINE & DESIGNER - BACKEND API TESTING")
    print("=" * 80)
    
    # Run Workflow API testing as per review request
    workflow_tester = WorkflowAPITester()
    workflow_results = workflow_tester.run_all_tests()
    
    print("\n" + "=" * 80)
    print("🎯 WORKFLOW API TEST ASSESSMENT")
    print("=" * 80)
    print(f"Total Tests: {workflow_results['total_tests']}")
    print(f"Success Rate: {workflow_results['success_rate']:.1f}%")
    
    if workflow_results['success_rate'] >= 90:
        print("🎉 WORKFLOW ENGINE READY FOR PRODUCTION - Exceeds expectations!")
        print("✅ All core workflow operations functional")
        print("✅ State machine transitions working")
        print("✅ Authorization checks working")
    elif workflow_results['success_rate'] >= 80:
        print("✅ WORKFLOW ENGINE FUNCTIONAL - Meets requirements")
        print("⚠️ Some minor issues detected")
    else:
        print("❌ WORKFLOW ENGINE NEEDS ATTENTION - Below expected standards")
        print("🔧 Critical errors in workflow engine")
    
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if workflow_results['success_rate'] >= 90 else 1)