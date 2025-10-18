from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta, timezone, date
from typing import List, Optional
from checklist_models import (
    ChecklistTemplate,
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistExecution,
    ChecklistExecutionUpdate,
    ChecklistExecutionComplete,
    ChecklistItem,
    ChecklistItemCompletion,
    ChecklistStats,
)
from auth_utils import get_current_user

router = APIRouter(prefix="/checklists", tags=["Checklists"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


def calculate_completion_percentage(items: List[dict]) -> float:
    """Calculate completion percentage for checklist"""
    if not items:
        return 0.0
    
    completed = sum(1 for item in items if item.get("completed", False))
    return round((completed / len(items)) * 100, 2)


def calculate_checklist_score(template: dict, items: List[dict]) -> tuple:
    """Calculate score and pass/fail status for a checklist"""
    if not template.get("scoring_enabled"):
        return None, None
    
    total_score = 0.0
    max_score = 0.0
    
    # Create item map for quick lookup
    item_map = {item["item_id"]: item for item in items}
    
    for template_item in template.get("items", []):
        if not template_item.get("scoring_enabled"):
            continue
        
        max_score += 100.0  # Each item worth 100 points
        
        completion = item_map.get(template_item["id"])
        if completion and completion.get("completed"):
            # Item completed = full score
            total_score += 100.0
    
    if max_score == 0:
        return None, None
    
    percentage = (total_score / max_score) * 100.0
    passed = percentage >= template.get("pass_percentage", 80.0)
    
    return round(percentage, 2), passed


# ==================== TEMPLATE ENDPOINTS ====================

@router.get("/templates")
async def get_checklist_templates(
    request: Request,
    category: Optional[str] = None,
    show_inactive: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all checklist templates for organization
    
    Args:
        category: Filter by category (optional)
        show_inactive: If True, includes inactive templates. Default False (active only)
    """
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    query = {"organization_id": user["organization_id"]}
    if not show_inactive:
        query["is_active"] = True
    if category:
        query["category"] = category
    
    templates = await db.checklist_templates.find(query, {"_id": 0}).to_list(1000)
    return templates


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_checklist_template(
    template_data: ChecklistTemplateCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new checklist template"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Convert items to proper format
    items = []
    for idx, item in enumerate(template_data.items):
        checklist_item = ChecklistItem(
            text=item.text,
            required=item.required,
            order=idx,
            # V1 Enhancement fields
            photo_required=getattr(item, 'photo_required', False),
            min_photos=getattr(item, 'min_photos', 0),
            max_photos=getattr(item, 'max_photos', 10),
            signature_required=getattr(item, 'signature_required', False),
            conditional_logic=getattr(item, 'conditional_logic', None),
            help_text=getattr(item, 'help_text', None),
            scoring_enabled=getattr(item, 'scoring_enabled', False),
            pass_score=getattr(item, 'pass_score', None),
        )
        items.append(checklist_item.model_dump())
    
    template = ChecklistTemplate(
        organization_id=user["organization_id"],
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        items=items,
        frequency=template_data.frequency,
        scheduled_time=template_data.scheduled_time,
        assigned_to=template_data.assigned_to,
        created_by=user["id"],
    )
    
    template_dict = template.model_dump()
    template_dict["created_at"] = template_dict["created_at"].isoformat()
    template_dict["updated_at"] = template_dict["updated_at"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = template_dict.copy()
    await db.checklist_templates.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return template_dict


@router.get("/templates/{template_id}")
async def get_checklist_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific checklist template"""
    user = await get_current_user(request, db)
    
    template = await db.checklist_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    return template


@router.put("/templates/{template_id}")
async def update_checklist_template(
    template_id: str,
    template_data: ChecklistTemplateUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a checklist template"""
    user = await get_current_user(request, db)
    
    template = await db.checklist_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    
    # Handle items update
    if "items" in update_data and update_data["items"]:
        items = []
        for idx, item in enumerate(update_data["items"]):
            checklist_item = ChecklistItem(
                text=item["text"],
                required=item.get("required", True),
                order=idx,
                # V1 Enhancement fields
                photo_required=item.get("photo_required", False),
                min_photos=item.get("min_photos", 0),
                max_photos=item.get("max_photos", 10),
                signature_required=item.get("signature_required", False),
                conditional_logic=item.get("conditional_logic"),
                help_text=item.get("help_text"),
                scoring_enabled=item.get("scoring_enabled", False),
                pass_score=item.get("pass_score"),
            )
            items.append(checklist_item.model_dump())
        update_data["items"] = items
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.checklist_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )
    
    updated_template = await db.checklist_templates.find_one({"id": template_id}, {"_id": 0})
    return updated_template


@router.delete("/templates/{template_id}")
async def delete_checklist_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Soft delete a checklist template"""
    user = await get_current_user(request, db)
    
    template = await db.checklist_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    await db.checklist_templates.update_one(
        {"id": template_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Template deleted successfully"}


# ==================== EXECUTION ENDPOINTS ====================

@router.post("/executions", status_code=status.HTTP_201_CREATED)
async def start_checklist(
    template_id: str,
    date_str: Optional[str] = None,
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a new checklist for a specific date"""
    user = await get_current_user(request, db)
    
    # Get template
    template = await db.checklist_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Use provided date or today
    checklist_date = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Check if checklist already exists for this date
    existing = await db.checklist_executions.find_one({
        "template_id": template_id,
        "date": checklist_date,
        "organization_id": user["organization_id"]
    })
    
    if existing:
        # Return existing checklist
        return existing
    
    # Initialize items
    items = []
    for item in template["items"]:
        items.append({
            "item_id": item["id"],
            "completed": False,
            "notes": None,
            "completed_at": None,
        })
    
    execution = ChecklistExecution(
        organization_id=user["organization_id"],
        template_id=template["id"],
        template_name=template["name"],
        date=checklist_date,
        items=items,
        started_at=datetime.now(timezone.utc),
    )
    
    execution_dict = execution.model_dump()
    execution_dict["created_at"] = execution_dict["created_at"].isoformat()
    if execution_dict["started_at"]:
        execution_dict["started_at"] = execution_dict["started_at"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = execution_dict.copy()
    await db.checklist_executions.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return execution_dict


@router.get("/executions")
async def get_checklists(
    request: Request,
    date_str: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get checklist executions"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if date_str:
        query["date"] = date_str
    
    if status_filter:
        query["status"] = status_filter
    
    executions = await db.checklist_executions.find(
        query,
        {"_id": 0}
    ).sort("date", -1).limit(limit).to_list(limit)
    
    return executions


@router.get("/executions/today")
async def get_todays_checklists(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get today's checklists"""
    user = await get_current_user(request, db)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    executions = await db.checklist_executions.find(
        {
            "organization_id": user["organization_id"],
            "date": today
        },
        {"_id": 0}
    ).to_list(100)
    
    # Also get templates to create pending checklists
    templates = await db.checklist_templates.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(100)
    
    # Check which templates don't have executions today
    existing_template_ids = {e["template_id"] for e in executions}
    
    result = {
        "executions": executions,
        "pending_templates": [
            {"id": t["id"], "name": t["name"], "category": t.get("category")}
            for t in templates
            if t["id"] not in existing_template_ids
        ]
    }
    
    return result


@router.get("/executions/{execution_id}")
async def get_checklist(
    execution_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific checklist execution"""
    user = await get_current_user(request, db)
    
    execution = await db.checklist_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    
    return execution


@router.put("/executions/{execution_id}")
async def update_checklist(
    execution_id: str,
    execution_data: ChecklistExecutionUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a checklist"""
    user = await get_current_user(request, db)
    
    execution = await db.checklist_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    
    if execution.get("status") == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed checklist",
        )
    
    update_data = execution_data.model_dump(exclude_unset=True)
    
    # Convert items to dict format
    if "items" in update_data:
        items_dict = []
        for item in update_data["items"]:
            item_dict = item.dict() if hasattr(item, 'dict') else item
            if item_dict.get("completed") and not item_dict.get("completed_at"):
                item_dict["completed_at"] = datetime.now(timezone.utc).isoformat()
            items_dict.append(item_dict)
        
        update_data["items"] = items_dict
        update_data["completion_percentage"] = calculate_completion_percentage(items_dict)
        update_data["status"] = "in_progress"
    
    if update_data:
        await db.checklist_executions.update_one(
            {"id": execution_id},
            {"$set": update_data}
        )
    
    updated_execution = await db.checklist_executions.find_one({"id": execution_id}, {"_id": 0})
    return updated_execution


@router.post("/executions/{execution_id}/complete")
async def complete_checklist(
    execution_id: str,
    completion_data: ChecklistExecutionComplete,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Complete a checklist"""
    user = await get_current_user(request, db)
    
    execution = await db.checklist_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    
    # Get template to check for workflow requirements and scoring
    template = await db.checklist_templates.find_one(
        {"id": execution["template_id"], "organization_id": user["organization_id"]}
    )
    
    requires_approval = template.get("requires_approval", False) if template else False
    workflow_template_id = template.get("workflow_template_id") if template else None
    
    # Convert items
    items_dict = []
    for item in completion_data.items:
        item_dict = item.dict() if hasattr(item, 'dict') else item
        if item_dict.get("completed") and not item_dict.get("completed_at"):
            item_dict["completed_at"] = datetime.now(timezone.utc).isoformat()
        items_dict.append(item_dict)
    
    # Calculate score if scoring enabled
    score, passed = calculate_checklist_score(template, items_dict)
    
    # Calculate duration
    time_taken = None
    if execution.get("started_at"):
        started_at = datetime.fromisoformat(execution["started_at"])
        completed_at = datetime.now(timezone.utc)
        time_taken = int((completed_at - started_at).total_seconds() / 60)
    
    update_data = {
        "status": "completed",
        "items": items_dict,
        "notes": completion_data.notes,
        "completion_percentage": calculate_completion_percentage(items_dict),
        "completed_by": user["id"],
        "completed_by_name": user["name"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "time_taken_minutes": time_taken,
        "score": score,
        "passed": passed,
    }
    
    await db.checklist_executions.update_one(
        {"id": execution_id},
        {"$set": update_data}
    )
    
    completed_execution = await db.checklist_executions.find_one({"id": execution_id}, {"_id": 0})
    
    # Auto-create work order if failed and template requires it
    if template.get("auto_create_work_order_on_fail") and passed == False:
        work_order = {
            "id": str(uuid.uuid4()),
            "organization_id": user["organization_id"],
            "title": f"Corrective Action: {template['name']}",
            "description": f"Checklist failed. Score: {score}%\nNotes: {completion_data.notes or 'No notes'}",
            "priority": template.get("work_order_priority", "normal"),
            "status": "pending",
            "source_checklist_id": execution_id,
            "asset_id": execution.get("asset_id"),
            "unit_id": execution.get("unit_id"),
            "created_by": user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.work_orders.insert_one(work_order.copy())
    
    # Auto-start workflow if required
    if requires_approval and workflow_template_id:
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine(db)
        
        try:
            # Check for duplicate workflow
            existing_workflow = await db.workflow_instances.find_one({
                "resource_type": "checklist",
                "resource_id": execution_id,
                "status": {"$in": ["pending", "in_progress", "escalated"]}
            })
            
            if not existing_workflow:
                workflow = await engine.start_workflow(
                    template_id=workflow_template_id,
                    resource_type="checklist",
                    resource_id=execution_id,
                    resource_name=f"{template.get('name', 'Checklist')} - {execution.get('date', '')}",
                    created_by=user["id"],
                    created_by_name=user["name"],
                    organization_id=user["organization_id"]
                )
                
                # Link workflow to checklist
                await db.checklist_executions.update_one(
                    {"id": execution_id},
                    {"$set": {
                        "workflow_id": workflow["id"],
                        "workflow_status": "pending",
                        "workflow_template_id": workflow_template_id,
                        "requires_approval": requires_approval
                    }}
                )
                
                completed_execution["workflow_id"] = workflow["id"]
                completed_execution["workflow_status"] = "pending"
        except Exception as e:
            # Log error but don't fail checklist completion
            import logging
            logging.error(f"Failed to start workflow for checklist {execution_id}: {str(e)}")
    
    return completed_execution


@router.get("/stats")
async def get_checklist_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get checklist statistics"""
    user = await get_current_user(request, db)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Get all checklists
    all_checklists = await db.checklist_executions.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(all_checklists)
    
    # Count completed today
    completed_today = len([
        c for c in all_checklists
        if c.get("date") == today and c.get("status") == "completed"
    ])
    
    # Count pending today
    pending_today = len([
        c for c in all_checklists
        if c.get("date") == today and c.get("status") != "completed"
    ])
    
    # Calculate completion rate
    completed_all = len([c for c in all_checklists if c.get("status") == "completed"])
    completion_rate = (completed_all / total * 100) if total > 0 else 0.0
    
    # Count overdue (pending before today)
    overdue = len([
        c for c in all_checklists
        if c.get("date") < today and c.get("status") != "completed"
    ])
    
    return ChecklistStats(
        total_checklists=total,
        completed_today=completed_today,
        pending_today=pending_today,
        completion_rate=round(completion_rate, 2),
        overdue=overdue,
    )