from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from workflow_models import (
    WorkflowTemplate, WorkflowTemplateCreate, WorkflowTemplateUpdate,
    WorkflowInstance, WorkflowInstanceCreate,
    WorkflowApprovalAction, WorkflowStats
)
from workflow_engine import WorkflowEngine
from auth_utils import get_current_user
from datetime import datetime, timezone
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


async def check_user_permission(
    db: AsyncIOMotorDatabase,
    user_id: str,
    permission_code: str,
    organization_id: str
) -> bool:
    """Check if user has specific permission"""
    # Get permission
    permission = await db.permissions.find_one({"code": permission_code})
    if not permission:
        return False
    
    # Check user override
    user_perm = await db.user_permissions.find_one({
        "user_id": user_id,
        "permission_id": permission["id"]
    })
    if user_perm:
        return user_perm.get("granted", False)
    
    # Check role permission
    user_doc = await db.users.find_one({"id": user_id}, {"role_id": 1})
    if not user_doc:
        return False
    
    role_perm = await db.role_permissions.find_one({
        "role_id": user_doc["role_id"],
        "permission_id": permission["id"]
    })
    
    return role_perm.get("granted", False) if role_perm else False


# =====================================
# WORKFLOW TEMPLATE ENDPOINTS
# =====================================

@router.get("/templates")
async def list_workflow_templates(
    request: Request,
    resource_type: Optional[str] = None,
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all workflow templates for organization"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if resource_type:
        query["resource_type"] = resource_type
    
    if active_only:
        query["active"] = True
    
    templates = await db.workflow_templates.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return templates


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_workflow_template(
    template_data: WorkflowTemplateCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new workflow template"""
    user = await get_current_user(request, db)
    
    # Validate steps
    if not template_data.steps or len(template_data.steps) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow must have at least one step"
        )
    
    # Validate step numbers are sequential
    for i, step in enumerate(template_data.steps):
        if step.get("step_number") != i + 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Step numbers must be sequential starting from 1"
            )
    
    template = WorkflowTemplate(
        organization_id=user["organization_id"],
        created_by=user["id"],
        **template_data.model_dump()
    )
    
    template_dict = template.model_dump()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = template_dict.copy()
    await db.workflow_templates.insert_one(insert_dict)
    
    logger.info(f"Created workflow template {template.id} by {user['name']}")
    
    # Return clean dict without MongoDB _id
    return template_dict


@router.get("/templates/{template_id}")
async def get_workflow_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific workflow template"""
    user = await get_current_user(request, db)
    
    template = await db.workflow_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    return template


@router.post("/templates/{template_id}/assign-to-resource")
async def assign_workflow_to_resource_type(
    template_id: str,
    request: Request,
    resource_type: str,
    auto_trigger: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Assign a workflow template to a resource type (inspection/task/checklist)"""
    user = await get_current_user(request, db)
    
    template = await db.workflow_templates.find_one({
        "id": template_id,
        "organization_id": user["organization_id"]
    })
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    # Update resource templates to use this workflow
    if resource_type == "inspection":
        # Update all inspection templates
        result = await db.inspection_templates.update_many(
            {"organization_id": user["organization_id"]},
            {
                "$set": {
                    "requires_approval": True,
                    "workflow_template_id": template_id,
                    "auto_trigger_workflow": auto_trigger
                }
            }
        )
        return {
            "message": f"Assigned workflow to {result.modified_count} inspection templates",
            "resource_type": resource_type,
            "workflow_template_id": template_id
        }
    
    elif resource_type == "task":
        # Update all tasks
        result = await db.tasks.update_many(
            {"organization_id": user["organization_id"], "status": {"$ne": "completed"}},
            {
                "$set": {
                    "requires_approval": True,
                    "workflow_template_id": template_id,
                    "auto_trigger_workflow": auto_trigger
                }
            }
        )
        return {
            "message": f"Assigned workflow to {result.modified_count} tasks",
            "resource_type": resource_type,
            "workflow_template_id": template_id
        }
    
    elif resource_type == "checklist":
        result = await db.checklist_templates.update_many(
            {"organization_id": user["organization_id"]},
            {
                "$set": {
                    "requires_approval": True,
                    "workflow_template_id": template_id,
                    "auto_trigger_workflow": auto_trigger
                }
            }
        )
        return {
            "message": f"Assigned workflow to {result.modified_count} checklist templates",
            "resource_type": resource_type,
            "workflow_template_id": template_id
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type. Must be: inspection, task, or checklist"
        )


@router.put("/templates/{template_id}")
async def update_workflow_template(
    template_id: str,
    template_data: WorkflowTemplateUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a workflow template"""
    user = await get_current_user(request, db)
    
    template = await db.workflow_templates.find_one({
        "id": template_id,
        "organization_id": user["organization_id"]
    })
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.workflow_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )
    
    updated = await db.workflow_templates.find_one({"id": template_id}, {"_id": 0})
    return updated


@router.delete("/templates/{template_id}")
async def delete_workflow_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a workflow template (soft delete by setting active=False)"""
    user = await get_current_user(request, db)
    
    # Check if template has active workflows
    active_workflows = await db.workflow_instances.count_documents({
        "template_id": template_id,
        "status": {"$in": ["pending", "in_progress", "escalated"]}
    })
    
    if active_workflows > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete template with {active_workflows} active workflows"
        )
    
    result = await db.workflow_templates.update_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"$set": {"active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    return {"message": "Workflow template deactivated successfully"}


# =====================================
# WORKFLOW INSTANCE ENDPOINTS
# =====================================

@router.post("/instances", status_code=status.HTTP_201_CREATED)
async def start_workflow_instance(
    instance_data: WorkflowInstanceCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a new workflow instance"""
    user = await get_current_user(request, db)
    
    engine = WorkflowEngine(db)
    
    try:
        instance = await engine.start_workflow(
            template_id=instance_data.template_id,
            resource_type=instance_data.resource_type,
            resource_id=instance_data.resource_id,
            resource_name=instance_data.resource_name or instance_data.resource_id,
            created_by=user["id"],
            created_by_name=user["name"],
            organization_id=user["organization_id"]
        )
        
        return instance
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/instances")
async def list_workflow_instances(
    request: Request,
    status_filter: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all workflow instances for organization"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if status_filter:
        query["status"] = status_filter
    
    if resource_type:
        query["resource_type"] = resource_type
    
    instances = await db.workflow_instances.find(query, {"_id": 0}).sort("started_at", -1).to_list(500)
    return instances


@router.get("/instances/my-approvals")
async def get_my_pending_approvals(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflows pending approval by current user"""
    user = await get_current_user(request, db)
    
    # Find workflows where user is in current_approvers list
    workflows = await db.workflow_instances.find(
        {
            "organization_id": user["organization_id"],
            "status": {"$in": ["in_progress", "escalated"]},
            "current_approvers": user["id"]
        },
        {"_id": 0}
    ).sort("started_at", -1).to_list(100)
    
    return workflows


@router.get("/instances/{workflow_id}")
async def get_workflow_instance(
    workflow_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific workflow instance"""
    user = await get_current_user(request, db)
    
    workflow = await db.workflow_instances.find_one(
        {"id": workflow_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow instance not found"
        )
    
    return workflow


@router.post("/instances/{workflow_id}/approve")
async def approve_workflow_step(
    workflow_id: str,
    action_data: WorkflowApprovalAction,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Approve/Reject/Request Changes on workflow step"""
    user = await get_current_user(request, db)
    
    if action_data.action not in ["approve", "reject", "request_changes"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'approve', 'reject', or 'request_changes'"
        )
    
    # Permission check: workflow.approve
    has_permission = await check_user_permission(
        db=db,
        user_id=user["id"],
        permission_code="workflow.approve",
        organization_id=user["organization_id"]
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve workflows"
        )
    
    engine = WorkflowEngine(db)
    
    try:
        updated_workflow = await engine.process_approval_action(
            workflow_id=workflow_id,
            user_id=user["id"],
            user_name=user["name"],
            action=action_data.action,
            comments=action_data.comments
        )
        
        return updated_workflow
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/instances/bulk-approve")
async def bulk_approve_workflows(
    request: Request,
    workflow_ids: List[str],
    comments: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk approve multiple workflows at once"""
    user = await get_current_user(request, db)
    
    # Permission check
    has_permission = await check_user_permission(
        db=db,
        user_id=user["id"],
        permission_code="workflow.approve",
        organization_id=user["organization_id"]
    )
    



@router.get("/escalations")
async def check_workflow_escalations_endpoint(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check for workflows that need escalation (manual trigger)"""
    user = await get_current_user(request, db)
    
    engine = WorkflowEngine(db)
    
    try:
        escalated = await engine.check_escalations()
        return {
            "message": f"Escalated {len(escalated)} workflows",
            "escalated_workflows": escalated
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation check failed: {str(e)}"
        )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve workflows"
        )
    
    engine = WorkflowEngine(db)
    results = []
    
    for workflow_id in workflow_ids:
        try:
            updated_workflow = await engine.process_approval_action(
                workflow_id=workflow_id,
                user_id=user["id"],
                user_name=user["name"],
                action="approve",
                comments=comments
            )
            results.append({"workflow_id": workflow_id, "status": "success", "workflow": updated_workflow})
        except Exception as e:
            results.append({"workflow_id": workflow_id, "status": "error", "error": str(e)})
    
    success_count = len([r for r in results if r["status"] == "success"])
    
    return {
        "message": f"Bulk approve completed: {success_count}/{len(workflow_ids)} successful",
        "results": results
    }


@router.post("/instances/bulk-reject")
async def bulk_reject_workflows(
    request: Request,
    workflow_ids: List[str],
    comments: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk reject multiple workflows at once"""
    user = await get_current_user(request, db)
    
    # Permission check
    has_permission = await check_user_permission(
        db=db,
        user_id=user["id"],
        permission_code="workflow.approve",
        organization_id=user["organization_id"]
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reject workflows"
        )
    
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are required for bulk rejection"
        )
    
    engine = WorkflowEngine(db)
    results = []
    
    for workflow_id in workflow_ids:
        try:
            updated_workflow = await engine.process_approval_action(
                workflow_id=workflow_id,
                user_id=user["id"],
                user_name=user["name"],
                action="reject",
                comments=comments
            )
            results.append({"workflow_id": workflow_id, "status": "success", "workflow": updated_workflow})
        except Exception as e:
            results.append({"workflow_id": workflow_id, "status": "error", "error": str(e)})
    
    success_count = len([r for r in results if r["status"] == "success"])
    
    return {
        "message": f"Bulk reject completed: {success_count}/{len(workflow_ids)} successful",
        "results": results
    }


@router.post("/instances/{workflow_id}/cancel")
async def cancel_workflow_instance(
    workflow_id: str,
    request: Request,
    reason: str = "Cancelled by user",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Cancel an active workflow"""
    user = await get_current_user(request, db)
    
    engine = WorkflowEngine(db)
    
    try:
        updated_workflow = await engine.cancel_workflow(
            workflow_id=workflow_id,
            user_id=user["id"],
            reason=reason
        )
        
        return updated_workflow
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =====================================
# WORKFLOW STATISTICS
# =====================================

@router.get("/stats", response_model=WorkflowStats)
async def get_workflow_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflow statistics"""
    user = await get_current_user(request, db)
    
    org_id = user["organization_id"]
    
    # Total workflows
    total = await db.workflow_instances.count_documents({"organization_id": org_id})
    
    # Pending approvals (for current user)
    pending = await db.workflow_instances.count_documents({
        "organization_id": org_id,
        "status": {"$in": ["in_progress", "escalated"]},
        "current_approvers": user["id"]
    })
    
    # Approved/rejected today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    approved_today = await db.workflow_instances.count_documents({
        "organization_id": org_id,
        "status": "approved",
        "completed_at": {"$gte": today_start}
    })
    
    rejected_today = await db.workflow_instances.count_documents({
        "organization_id": org_id,
        "status": "rejected",
        "completed_at": {"$gte": today_start}
    })
    
    # Escalated workflows
    escalated = await db.workflow_instances.count_documents({
        "organization_id": org_id,
        "status": "escalated"
    })
    
    # Average approval time (simple calculation)
    completed_workflows = await db.workflow_instances.find({
        "organization_id": org_id,
        "status": {"$in": ["approved", "rejected"]},
        "completed_at": {"$exists": True}
    }, {"started_at": 1, "completed_at": 1}).to_list(100)
    
    if completed_workflows:
        total_hours = 0
        for wf in completed_workflows:
            started = datetime.fromisoformat(wf["started_at"])
            completed = datetime.fromisoformat(wf["completed_at"])
            total_hours += (completed - started).total_seconds() / 3600
        
        avg_hours = total_hours / len(completed_workflows)
    else:
        avg_hours = None
    
    return WorkflowStats(
        total_workflows=total,
        pending_approvals=pending,
        approved_today=approved_today,
        rejected_today=rejected_today,
        average_approval_time_hours=round(avg_hours, 2) if avg_hours else None,
        escalated_workflows=escalated
    )
