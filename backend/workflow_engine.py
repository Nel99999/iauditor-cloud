"""
Workflow Engine - State Machine for Workflow Execution
Handles workflow progression, approval routing, escalation
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Core workflow execution engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        from email_service import EmailService
        import os
        self.email_service = EmailService()
        self.frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000').replace('/api', '')
    
    async def start_workflow(
        self,
        template_id: str,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        created_by: str,
        created_by_name: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Start a new workflow instance
        Returns the created workflow instance
        """
        # Get template
        template = await self.db.workflow_templates.find_one({
            "id": template_id,
            "organization_id": organization_id,
            "active": True
        })
        
        if not template:
            raise ValueError(f"Workflow template {template_id} not found or inactive")
        
        if not template.get("steps") or len(template["steps"]) == 0:
            raise ValueError("Workflow template has no steps defined")
        
        # Calculate due date based on first step timeout
        first_step = template["steps"][0]
        timeout_hours = first_step.get("timeout_hours", 24)
        due_at = (datetime.now(timezone.utc) + timedelta(hours=timeout_hours)).isoformat()
        
        # Find approvers for first step
        approvers = await self._find_approvers_for_step(
            first_step,
            organization_id,
            resource_id,
            created_by
        )
        
        # Create workflow instance
        workflow_instance = {
            "organization_id": organization_id,
            "template_id": template_id,
            "template_name": template["name"],
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_name": resource_name,
            "current_step": 1,
            "status": "in_progress",
            "steps_completed": [],
            "current_approvers": approvers,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "due_at": due_at,
            "completed_at": None,
            "created_by": created_by,
            "created_by_name": created_by_name
        }
        
        from workflow_models import WorkflowInstance
        instance = WorkflowInstance(**workflow_instance)
        
        instance_dict = instance.model_dump()
        await self.db.workflow_instances.insert_one(instance_dict)
        
        logger.info(f"Started workflow {instance.id} for {resource_type}/{resource_id}")
        
        # Send email notifications to approvers
        if template.get("notify_on_start", True) and approvers:
            approver_emails = []
            for approver_id in approvers:
                approver = await self.db.users.find_one({"id": approver_id}, {"email": 1})
                if approver and approver.get("email"):
                    approver_emails.append(approver["email"])
            
            if approver_emails:
                try:
                    self.email_service.send_workflow_started_email(
                        to_emails=approver_emails,
                        workflow_name=template["name"],
                        resource_type=resource_type,
                        resource_name=resource_name,
                        frontend_url=self.frontend_url
                    )
                except Exception as e:
                    logger.error(f"Failed to send workflow start emails: {str(e)}")
        
        return instance_dict
    
    async def process_approval_action(
        self,
        workflow_id: str,
        user_id: str,
        user_name: str,
        action: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process approval action (approve/reject/request_changes)
        Returns updated workflow instance
        """
        # Get workflow instance
        workflow = await self.db.workflow_instances.find_one({"id": workflow_id})
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow["status"] not in ["pending", "in_progress"]:
            raise ValueError(f"Workflow is {workflow['status']}, cannot process action")
        
        # Verify user is an authorized approver
        if user_id not in workflow.get("current_approvers", []):
            raise ValueError("User not authorized to approve this workflow step")
        
        # Get template and current step
        template = await self.db.workflow_templates.find_one({"id": workflow["template_id"]})
        current_step_num = workflow["current_step"]
        current_step = template["steps"][current_step_num - 1]
        
        # Record the approval action
        step_completion = {
            "step_number": current_step_num,
            "step_name": current_step["name"],
            "approved_by": user_id,
            "approved_by_name": user_name,
            "action": action,
            "comments": comments,
            "approved_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update workflow based on action
        if action == "reject":
            # Workflow rejected - end workflow
            await self.db.workflow_instances.update_one(
                {"id": workflow_id},
                {
                    "$set": {
                        "status": "rejected",
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    },
                    "$push": {"steps_completed": step_completion}
                }
            )
            
            # Sync resource status
            await self._sync_resource_status(workflow, "rejected")
            
            logger.info(f"Workflow {workflow_id} rejected by {user_name}")
            
        elif action == "approve":
            # Check if this step requires all approvers
            approval_type = current_step.get("approval_type", "any")
            
            if approval_type == "all":
                # Check if all approvers have approved
                completed_by = [s["approved_by"] for s in workflow.get("steps_completed", []) if s["step_number"] == current_step_num and s["action"] == "approve"]
                completed_by.append(user_id)
                
                all_approved = all(approver in completed_by for approver in workflow["current_approvers"])
                
                if not all_approved:
                    # Not all have approved yet, just record this approval
                    await self.db.workflow_instances.update_one(
                        {"id": workflow_id},
                        {"$push": {"steps_completed": step_completion}}
                    )
                    return await self.db.workflow_instances.find_one({"id": workflow_id}, {"_id": 0})
            
            # Step approved - move to next step
            if current_step_num < len(template["steps"]):
                # More steps remaining
                next_step_num = current_step_num + 1
                next_step = template["steps"][next_step_num - 1]
                
                # Find approvers for next step
                next_approvers = await self._find_approvers_for_step(
                    next_step,
                    workflow["organization_id"],
                    workflow["resource_id"],
                    workflow["created_by"]
                )
                
                # Calculate new due date
                timeout_hours = next_step.get("timeout_hours", 24)
                due_at = (datetime.now(timezone.utc) + timedelta(hours=timeout_hours)).isoformat()
                
                await self.db.workflow_instances.update_one(
                    {"id": workflow_id},
                    {
                        "$set": {
                            "current_step": next_step_num,
                            "current_approvers": next_approvers,
                            "due_at": due_at
                        },
                        "$push": {"steps_completed": step_completion}
                    }
                )
                
                logger.info(f"Workflow {workflow_id} advanced to step {next_step_num}")
                
            else:
                # All steps completed - workflow approved
                await self.db.workflow_instances.update_one(
                    {"id": workflow_id},
                    {
                        "$set": {
                            "status": "approved",
                            "completed_at": datetime.now(timezone.utc).isoformat()
                        },
                        "$push": {"steps_completed": step_completion}
                    }
                )
                
                # Sync resource status
                await self._sync_resource_status(workflow, "approved")
                
                logger.info(f"Workflow {workflow_id} fully approved")
        
        elif action == "request_changes":
            # Request changes - mark as pending
            await self.db.workflow_instances.update_one(
                {"id": workflow_id},
                {
                    "$set": {"status": "pending"},
                    "$push": {"steps_completed": step_completion}
                }
            )
            
            logger.info(f"Changes requested for workflow {workflow_id}")
        
        # Return updated workflow
        return await self.db.workflow_instances.find_one({"id": workflow_id}, {"_id": 0})
    
    async def _find_approvers_for_step(
        self,
        step: Dict[str, Any],
        organization_id: str,
        resource_id: str,
        created_by: str
    ) -> List[str]:
        """
        Find users who can approve this workflow step
        Based on role and context, including delegation routing
        """
        approver_role = step["approver_role"]
        context = step.get("approver_context", "organization")
        
        # Get users with this role
        query = {
            "organization_id": organization_id,
            "status": "active"
        }
        
        # Find role ID from role code
        role = await self.db.roles.find_one({"code": approver_role, "organization_id": organization_id})
        if not role:
            logger.warning(f"Role {approver_role} not found for organization {organization_id}")
            return []
        
        query["role_id"] = role["id"]
        
        # Apply context filtering
        if context == "own":
            # Only the creator can approve
            base_approvers = [created_by]
        
        elif context in ["team", "branch", "region"]:
            # Find users in same team/branch/region as resource
            # For now, return all users with the role (can enhance with org unit filtering)
            users = await self.db.users.find(query, {"id": 1}).to_list(100)
            base_approvers = [u["id"] for u in users]
        
        else:  # organization
            # All users with this role in organization
            users = await self.db.users.find(query, {"id": 1}).to_list(100)
            base_approvers = [u["id"] for u in users]
        
        # Check for active delegations and add delegates
        now = datetime.now(timezone.utc).isoformat()
        final_approvers = set(base_approvers)
        
        for approver_id in base_approvers:
            # Find active delegations from this approver
            delegations = await self.db.delegations.find({
                "delegator_id": approver_id,
                "active": True,
                "valid_from": {"$lte": now},
                "valid_until": {"$gte": now}
            }).to_list(100)
            
            for delegation in delegations:
                # Check if delegation applies to this workflow
                workflow_types = delegation.get("workflow_types", [])
                if len(workflow_types) == 0 or "all" in workflow_types:
                    # Delegation applies to all workflows, add delegate
                    final_approvers.add(delegation["delegate_id"])
        
        return list(final_approvers)
    
    async def check_escalations(self) -> List[Dict[str, Any]]:
        """
        Check for workflows that need escalation
        Called periodically by background task
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Find workflows past due date
        overdue_workflows = await self.db.workflow_instances.find({
            "status": "in_progress",
            "due_at": {"$lt": now}
        }).to_list(1000)
        
        escalated = []
        
        for workflow in overdue_workflows:
            # Get template
            template = await self.db.workflow_templates.find_one({"id": workflow["template_id"]})
            if not template:
                continue
            
            current_step = template["steps"][workflow["current_step"] - 1]
            escalate_to_role = current_step.get("escalate_to_role")
            
            if escalate_to_role:
                # Find users with escalation role
                role = await self.db.roles.find_one({
                    "code": escalate_to_role,
                    "organization_id": workflow["organization_id"]
                })
                
                if role:
                    escalation_users = await self.db.users.find({
                        "role_id": role["id"],
                        "status": "active"
                    }, {"id": 1}).to_list(100)
                    
                    escalation_approvers = [u["id"] for u in escalation_users]
                    
                    # Update workflow with escalated approvers
                    await self.db.workflow_instances.update_one(
                        {"id": workflow["id"]},
                        {
                            "$set": {
                                "current_approvers": escalation_approvers,
                                "status": "escalated"
                            }
                        }
                    )
                    
                    escalated.append(workflow)
                    logger.info(f"Escalated workflow {workflow['id']} to role {escalate_to_role}")
        
        return escalated
    
    async def cancel_workflow(
        self,
        workflow_id: str,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Cancel an active workflow"""
        workflow = await self.db.workflow_instances.find_one({"id": workflow_id})
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow["status"] not in ["pending", "in_progress", "escalated"]:
            raise ValueError(f"Cannot cancel workflow with status {workflow['status']}")
        
        # Record cancellation
        cancellation = {
            "step_number": workflow["current_step"],
            "step_name": "Cancelled",
            "approved_by": user_id,
            "approved_by_name": "System",
            "action": "cancel",
            "comments": reason,
            "approved_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.workflow_instances.update_one(
            {"id": workflow_id},
            {
                "$set": {
                    "status": "cancelled",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"steps_completed": cancellation}
            }
        )
        
        logger.info(f"Workflow {workflow_id} cancelled by user {user_id}")
        
        
        # Sync resource status on cancellation
        await self._sync_resource_status(workflow, "cancelled")


    
    async def _sync_resource_status(
        self,
        workflow: Dict[str, Any],
        workflow_status: str
    ) -> None:
        """
        Synchronize resource status when workflow changes
        """
        resource_type = workflow["resource_type"]
        resource_id = workflow["resource_id"]
        
        # Map workflow status to resource status
        status_map = {
            "approved": "approved",
            "rejected": "rejected",
            "cancelled": "completed"  # Revert to completed if cancelled
        }
        
        new_status = status_map.get(workflow_status)
        if not new_status:
            return
        
        # Update resource based on type
        collection_map = {
            "inspection": "inspection_executions",
            "task": "tasks",
            "checklist": "checklist_executions",
            "report": "reports"
        }
        
        collection_name = collection_map.get(resource_type)
        if not collection_name:
            logger.warning(f"Unknown resource type: {resource_type}")
            return
        
        collection = getattr(self.db, collection_name)
        
        update_data = {
            "status": new_status,
            "workflow_status": workflow_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add approval/rejection timestamp
        if workflow_status == "approved":
            update_data["approved_at"] = datetime.now(timezone.utc).isoformat()
        elif workflow_status == "rejected":
            update_data["rejected_at"] = datetime.now(timezone.utc).isoformat()
        
        await collection.update_one(
            {"id": resource_id},
            {"$set": update_data}
        )
        
        logger.info(f"Synced {resource_type}/{resource_id} status to {new_status}")

        return await self.db.workflow_instances.find_one({"id": workflow_id}, {"_id": 0})
