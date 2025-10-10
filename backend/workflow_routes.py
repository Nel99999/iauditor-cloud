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
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


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
    await db.workflow_templates.insert_one(template_dict)
    
    logger.info(f"Created workflow template {template.id} by {user['name']}")
    
    return template


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
