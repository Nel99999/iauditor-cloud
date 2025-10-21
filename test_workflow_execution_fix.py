#!/usr/bin/env python3
"""
Workflow Execution Test - Fixed Version
Tests the complete inspection workflow with correct payload structures
"""

import requests
import json
import time
from datetime import datetime, timezone

# Get backend URL from environment
import os
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

# Production user credentials
USER_EMAIL = "llewellyn@bluedawncapital.co.za"
USER_PASSWORD = "Test@1234"

def authenticate():
    """Authenticate and get token"""
    print("\n🔐 AUTHENTICATING...")
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Authentication successful")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_workflow_execution(token):
    """Test complete inspection workflow"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # STEP 1: Create inspection template
    print("\n" + "="*80)
    print("STEP 1: CREATE INSPECTION TEMPLATE")
    print("="*80)
    
    template_payload = {
        "name": f"Workflow Test Template {int(time.time())}",
        "description": "Test template for workflow execution",
        "category": "testing",
        "questions": [
            {
                "question_text": "Is the equipment in good condition?",
                "question_type": "yes_no",
                "required": True,
                "order": 1
            },
            {
                "question_text": "Take a photo of the equipment",
                "question_type": "photo",
                "required": True,
                "photo_required": True,
                "min_photos": 1,
                "max_photos": 5,
                "order": 2
            },
            {
                "question_text": "Inspector signature",
                "question_type": "signature",
                "required": True,
                "signature_required": True,
                "order": 3
            }
        ],
        "scoring_enabled": False,
        "require_gps": False,
        "require_photos": True,
        "auto_create_work_order_on_fail": False
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/inspections/templates",
        headers=headers,
        json=template_payload
    )
    
    if response.status_code == 201:
        template = response.json()
        template_id = template["id"]
        print(f"✅ Template created successfully")
        print(f"   Template ID: {template_id}")
        print(f"   Questions: {len(template.get('questions', []))}")
        results["passed"] += 1
        results["details"].append({
            "test": "Create Template",
            "status": "PASSED",
            "template_id": template_id
        })
    else:
        print(f"❌ Template creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        results["failed"] += 1
        results["details"].append({
            "test": "Create Template",
            "status": "FAILED",
            "error": response.text
        })
        return results
    
    # STEP 2: Start inspection execution (THIS IS THE FIX)
    print("\n" + "="*80)
    print("STEP 2: START INSPECTION EXECUTION (FIXED PAYLOAD)")
    print("="*80)
    
    # CORRECT PAYLOAD - matches InspectionExecutionCreate model
    execution_payload = {
        "template_id": template_id,
        "unit_id": None,  # Optional
        "location": {  # Optional
            "lat": -33.9249,
            "lng": 18.4241
        },
        "asset_id": None,  # Optional
        "scheduled_date": None  # Optional
    }
    
    print(f"Payload: {json.dumps(execution_payload, indent=2)}")
    
    response = requests.post(
        f"{BACKEND_URL}/api/inspections/executions",
        headers=headers,
        json=execution_payload
    )
    
    if response.status_code == 201:
        execution = response.json()
        execution_id = execution["id"]
        print(f"✅ Inspection execution started successfully")
        print(f"   Execution ID: {execution_id}")
        print(f"   Status: {execution.get('status')}")
        print(f"   Inspector: {execution.get('inspector_name')}")
        results["passed"] += 1
        results["details"].append({
            "test": "Start Execution",
            "status": "PASSED",
            "execution_id": execution_id
        })
    else:
        print(f"❌ Execution start failed: {response.status_code}")
        print(f"   Response: {response.text}")
        results["failed"] += 1
        results["details"].append({
            "test": "Start Execution",
            "status": "FAILED",
            "error": response.text
        })
        return results
    
    # STEP 3: Get question IDs from template
    print("\n" + "="*80)
    print("STEP 3: GET QUESTION IDs FOR ANSWERS")
    print("="*80)
    
    response = requests.get(
        f"{BACKEND_URL}/api/inspections/templates/{template_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        template_data = response.json()
        questions = template_data.get("questions", [])
        question_ids = [q["id"] for q in questions]
        print(f"✅ Retrieved {len(question_ids)} question IDs")
        for i, qid in enumerate(question_ids, 1):
            print(f"   Question {i} ID: {qid}")
        results["passed"] += 1
    else:
        print(f"❌ Failed to get question IDs: {response.status_code}")
        results["failed"] += 1
        return results
    
    # STEP 4: Submit answers
    print("\n" + "="*80)
    print("STEP 4: SUBMIT ANSWERS")
    print("="*80)
    
    # Create answers for each question
    answers = [
        {
            "question_id": question_ids[0],
            "answer": "yes",
            "notes": "Equipment looks good",
            "photo_ids": [],
            "signature_data": None
        },
        {
            "question_id": question_ids[1],
            "answer": "photo_taken",
            "notes": "Photo captured",
            "photo_ids": ["dummy_photo_id"],  # In real scenario, this would be from photo upload
            "signature_data": None
        },
        {
            "question_id": question_ids[2],
            "answer": "signed",
            "notes": "Inspector signed",
            "photo_ids": [],
            "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }
    ]
    
    response = requests.put(
        f"{BACKEND_URL}/api/inspections/executions/{execution_id}",
        headers=headers,
        json={"answers": answers}
    )
    
    if response.status_code == 200:
        print(f"✅ Answers submitted successfully")
        print(f"   Total answers: {len(answers)}")
        results["passed"] += 1
        results["details"].append({
            "test": "Submit Answers",
            "status": "PASSED"
        })
    else:
        print(f"❌ Answer submission failed: {response.status_code}")
        print(f"   Response: {response.text}")
        results["failed"] += 1
        results["details"].append({
            "test": "Submit Answers",
            "status": "FAILED",
            "error": response.text
        })
    
    # STEP 5: Complete inspection
    print("\n" + "="*80)
    print("STEP 5: COMPLETE INSPECTION")
    print("="*80)
    
    complete_payload = {
        "answers": answers,
        "findings": ["Equipment in good condition"],
        "notes": "Inspection completed successfully"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/inspections/executions/{execution_id}/complete",
        headers=headers,
        json=complete_payload
    )
    
    if response.status_code == 200:
        completed = response.json()
        print(f"✅ Inspection completed successfully")
        print(f"   Status: {completed.get('status')}")
        print(f"   Passed: {completed.get('passed')}")
        results["passed"] += 1
        results["details"].append({
            "test": "Complete Inspection",
            "status": "PASSED"
        })
    else:
        print(f"❌ Inspection completion failed: {response.status_code}")
        print(f"   Response: {response.text}")
        results["failed"] += 1
        results["details"].append({
            "test": "Complete Inspection",
            "status": "FAILED",
            "error": response.text
        })
    
    # STEP 6: Generate PDF report
    print("\n" + "="*80)
    print("STEP 6: GENERATE PDF REPORT")
    print("="*80)
    
    response = requests.get(
        f"{BACKEND_URL}/api/inspections/executions/{execution_id}/pdf",
        headers=headers
    )
    
    if response.status_code == 200:
        pdf_size = len(response.content)
        print(f"✅ PDF generated successfully")
        print(f"   PDF size: {pdf_size} bytes")
        results["passed"] += 1
        results["details"].append({
            "test": "Generate PDF",
            "status": "PASSED",
            "pdf_size": pdf_size
        })
    else:
        print(f"❌ PDF generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        results["failed"] += 1
        results["details"].append({
            "test": "Generate PDF",
            "status": "FAILED",
            "error": response.text
        })
    
    # STEP 7: Verify execution in database
    print("\n" + "="*80)
    print("STEP 7: VERIFY EXECUTION IN DATABASE")
    print("="*80)
    
    response = requests.get(
        f"{BACKEND_URL}/api/inspections/executions/{execution_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        execution_data = response.json()
        print(f"✅ Execution retrieved from database")
        print(f"   Status: {execution_data.get('status')}")
        print(f"   Answers: {len(execution_data.get('answers', []))}")
        print(f"   Completed at: {execution_data.get('completed_at')}")
        results["passed"] += 1
        results["details"].append({
            "test": "Verify in Database",
            "status": "PASSED"
        })
    else:
        print(f"❌ Database verification failed: {response.status_code}")
        results["failed"] += 1
        results["details"].append({
            "test": "Verify in Database",
            "status": "FAILED",
            "error": response.text
        })
    
    return results

def main():
    print("🚀 WORKFLOW EXECUTION TEST - FIXED VERSION")
    print("="*80)
    print("Testing complete inspection workflow with corrected payloads")
    print("="*80)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("\n❌ FAILED: Could not authenticate")
        return
    
    # Run workflow test
    results = test_workflow_execution(token)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    total = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print("\n📋 DETAILED RESULTS:")
    for detail in results["details"]:
        status_icon = "✅" if detail["status"] == "PASSED" else "❌"
        print(f"{status_icon} {detail['test']}: {detail['status']}")
        if detail.get("error"):
            print(f"   Error: {detail['error']}")
    
    print("\n" + "="*80)
    if results["failed"] == 0:
        print("🎉 ALL WORKFLOW TESTS PASSED!")
        print("Backend inspection workflow is 100% operational")
    else:
        print(f"⚠️ {results['failed']} test(s) failed")
        print("Review errors above for details")
    print("="*80)

if __name__ == "__main__":
    main()
