from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import gridfs
from bson import ObjectId
import uuid
from inspection_models import (
    InspectionTemplate,
    InspectionTemplateCreate,
    InspectionTemplateUpdate,
    InspectionExecution,
    InspectionExecutionCreate,
    InspectionExecutionUpdate,
    InspectionExecutionComplete,
    InspectionQuestion,
    InspectionStats,
)
from auth_utils import get_current_user
import io

router = APIRouter(prefix="/inspections", tags=["Inspections"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


def calculate_inspection_score(template: dict, answers: List[dict]) -> tuple:
    """Calculate score and pass/fail status for an inspection"""
    if not template.get("scoring_enabled"):
        return None, None
    
    total_score = 0.0
    max_score = 0.0
    
    # Create answer map for quick lookup
    answer_map = {ans["question_id"]: ans for ans in answers}
    
    for question in template.get("questions", []):
        if not question.get("scoring_enabled"):
            continue
        
        max_score += 100.0  # Each question worth 100 points
        
        answer = answer_map.get(question["id"])
        if answer and answer.get("answer") is not None:
            # Simple scoring: yes/true = 100, no/false = 0
            if question["question_type"] == "yes_no":
                total_score += 100.0 if answer["answer"] else 0.0
            elif question["question_type"] == "number":
                # Check against pass_score threshold
                if question.get("pass_score") is not None:
                    if float(answer["answer"]) >= question["pass_score"]:
                        total_score += 100.0
            else:
                # For other types, assume answered = full score
                if answer["answer"]:
                    total_score += 100.0
    
    if max_score == 0:
        return None, None
    
    percentage = (total_score / max_score) * 100.0
    passed = percentage >= template.get("pass_percentage", 80.0)
    
    return round(percentage, 2), passed


# ==================== TEMPLATE ENDPOINTS ====================

@router.get("/templates")
async def get_inspection_templates(
    request: Request,
    category: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all inspection templates for organization"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    if category:
        query["category"] = category
    
    templates = await db.inspection_templates.find(query, {"_id": 0}).to_list(1000)
    return templates


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_inspection_template(
    template_data: InspectionTemplateCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new inspection template"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Convert questions to proper format
    questions = []
    for idx, q in enumerate(template_data.questions):
        question = InspectionQuestion(
            question_text=q.question_text,
            question_type=q.question_type,
            required=q.required,
            options=q.options,
            scoring_enabled=q.scoring_enabled,
            pass_score=q.pass_score,
            order=idx,
        )
        questions.append(question.model_dump())
    
    template = InspectionTemplate(
        organization_id=user["organization_id"],
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        questions=questions,
        scoring_enabled=template_data.scoring_enabled,
        pass_percentage=template_data.pass_percentage,
        require_gps=template_data.require_gps,
        require_photos=template_data.require_photos,
        created_by=user["id"],
    )
    
    template_dict = template.model_dump()
    template_dict["created_at"] = template_dict["created_at"].isoformat()
    template_dict["updated_at"] = template_dict["updated_at"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = template_dict.copy()
    await db.inspection_templates.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return template_dict


@router.get("/templates/{template_id}")
async def get_inspection_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific inspection template"""
    user = await get_current_user(request, db)
    
    template = await db.inspection_templates.find_one(
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
async def update_inspection_template(
    template_id: str,
    template_data: InspectionTemplateUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an inspection template"""
    user = await get_current_user(request, db)
    
    template = await db.inspection_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    
    # Handle questions update
    if "questions" in update_data and update_data["questions"]:
        questions = []
        for idx, q in enumerate(update_data["questions"]):
            question = InspectionQuestion(
                question_text=q["question_text"],
                question_type=q["question_type"],
                required=q.get("required", True),
                options=q.get("options"),
                scoring_enabled=q.get("scoring_enabled", False),
                pass_score=q.get("pass_score"),
                order=idx,
            )
            questions.append(question.model_dump())
        update_data["questions"] = questions
        update_data["version"] = template.get("version", 1) + 1
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.inspection_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )
    
    updated_template = await db.inspection_templates.find_one({"id": template_id}, {"_id": 0})
    return updated_template


@router.delete("/templates/{template_id}")
async def delete_inspection_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Soft delete an inspection template"""
    user = await get_current_user(request, db)
    
    template = await db.inspection_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    await db.inspection_templates.update_one(
        {"id": template_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Template deleted successfully"}


# ==================== EXECUTION ENDPOINTS ====================

@router.post("/executions", status_code=status.HTTP_201_CREATED)
async def start_inspection(
    execution_data: InspectionExecutionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Start a new inspection"""
    user = await get_current_user(request, db)
    
    # Get template
    template = await db.inspection_templates.find_one(
        {"id": execution_data.template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Get unit name if unit_id provided
    unit_name = None
    if execution_data.unit_id:
        unit = await db.organization_units.find_one(
            {"id": execution_data.unit_id},
            {"_id": 0, "name": 1}
        )
        unit_name = unit.get("name") if unit else None
    
    # Get asset name if asset_id provided
    asset_name = None
    if execution_data.asset_id:
        asset = await db.assets.find_one(
            {"id": execution_data.asset_id},
            {"_id": 0, "name": 1}
        )
        asset_name = asset.get("name") if asset else None
    
    execution = InspectionExecution(
        organization_id=user["organization_id"],
        template_id=template["id"],
        template_name=template["name"],
        template_version=template.get("version", 1),
        unit_id=execution_data.unit_id,
        unit_name=unit_name,
        inspector_id=user["id"],
        inspector_name=user["name"],
        location=execution_data.location,
        asset_id=execution_data.asset_id,
        asset_name=asset_name,
        scheduled_date=execution_data.scheduled_date,
    )
    
    execution_dict = execution.model_dump()
    execution_dict["started_at"] = execution_dict["started_at"].isoformat()
    execution_dict["created_at"] = execution_dict["created_at"].isoformat()
    if execution_dict.get("scheduled_date"):
        execution_dict["scheduled_date"] = execution_dict["scheduled_date"].isoformat()
    if execution_dict.get("due_date"):
        execution_dict["due_date"] = execution_dict["due_date"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = execution_dict.copy()
    await db.inspection_executions.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return execution_dict


@router.get("/executions")
async def get_inspections(
    request: Request,
    status_filter: Optional[str] = None,
    template_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inspection executions"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    if status_filter:
        query["status"] = status_filter
    if template_id:
        query["template_id"] = template_id
    
    executions = await db.inspection_executions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return executions


@router.get("/executions/{execution_id}")
async def get_inspection(
    execution_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific inspection execution"""
    user = await get_current_user(request, db)
    
    execution = await db.inspection_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )
    
    return execution


@router.put("/executions/{execution_id}")
async def update_inspection(
    execution_id: str,
    execution_data: InspectionExecutionUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an in-progress inspection"""
    user = await get_current_user(request, db)
    
    execution = await db.inspection_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )
    
    if execution.get("status") == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed inspection",
        )
    
    update_data = execution_data.model_dump(exclude_unset=True)
    
    # Convert answers to dict format
    if "answers" in update_data:
        update_data["answers"] = [ans.dict() if hasattr(ans, 'dict') else ans for ans in update_data["answers"]]
    
    if update_data:
        await db.inspection_executions.update_one(
            {"id": execution_id},
            {"$set": update_data}
        )
    
    updated_execution = await db.inspection_executions.find_one({"id": execution_id}, {"_id": 0})
    return updated_execution


@router.post("/executions/{execution_id}/complete")
async def complete_inspection(
    execution_id: str,
    completion_data: InspectionExecutionComplete,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Complete an inspection"""
    user = await get_current_user(request, db)
    
    execution = await db.inspection_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )
    
    # Get template for scoring
    template = await db.inspection_templates.find_one(
        {"id": execution["template_id"]},
        {"_id": 0}
    )
    
    # Calculate score
    answers_dict = [ans.dict() if hasattr(ans, 'dict') else ans for ans in completion_data.answers]
    score, passed = calculate_inspection_score(template, answers_dict)
    
    # Calculate duration
    started_at = datetime.fromisoformat(execution["started_at"])
    completed_at = datetime.now(timezone.utc)
    duration_minutes = int((completed_at - started_at).total_seconds() / 60)
    
    # Check if workflow is required
    requires_approval = template.get("requires_approval", False)
    workflow_template_id = template.get("workflow_template_id")
    
    # Determine initial status based on approval requirement
    if requires_approval and workflow_template_id:
        initial_status = "pending_approval"
    else:
        initial_status = "completed"
    
    update_data = {
        "status": initial_status,
        "answers": answers_dict,
        "findings": completion_data.findings or [],
        "notes": completion_data.notes,
        "score": score,
        "passed": passed,
        "completed_at": completed_at.isoformat(),
        "duration_minutes": duration_minutes,
        "rectification_required": bool(completion_data.findings),
    }
    
    await db.inspection_executions.update_one(
        {"id": execution_id},
        {"$set": update_data}
    )
    
    completed_execution = await db.inspection_executions.find_one({"id": execution_id}, {"_id": 0})
    
    # Auto-create work order if inspection failed and template requires it
    if template.get("auto_create_work_order_on_fail") and not passed and completion_data.findings:
        work_order = {
            "id": str(uuid.uuid4()),
            "organization_id": user["organization_id"],
            "title": f"Corrective Action: {template['name']}",
            "description": f"Inspection failed with findings:\n" + "\n".join(completion_data.findings),
            "priority": template.get("work_order_priority", "normal"),
            "status": "pending",
            "source_inspection_id": execution_id,
            "asset_id": execution.get("asset_id"),
            "unit_id": execution.get("unit_id"),
            "created_by": user["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.work_orders.insert_one(work_order.copy())
        
        # Link work order to inspection
        await db.inspection_executions.update_one(
            {"id": execution_id},
            {"$set": {"auto_created_wo_id": work_order["id"]}}
        )
        
        completed_execution["auto_created_wo_id"] = work_order["id"]
    
    # Auto-start workflow if required
    if requires_approval and workflow_template_id:
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine(db)
        
        try:
            # Check for duplicate workflow
            existing_workflow = await db.workflow_instances.find_one({
                "resource_type": "inspection",
                "resource_id": execution_id,
                "status": {"$in": ["pending", "in_progress", "escalated"]}
            })
            
            if not existing_workflow:
                workflow = await engine.start_workflow(
                    template_id=workflow_template_id,
                    resource_type="inspection",
                    resource_id=execution_id,
                    resource_name=f"{template.get('name', 'Inspection')} - {execution.get('unit_name', '')}",
                    created_by=user["id"],
                    created_by_name=user["name"],
                    organization_id=user["organization_id"]
                )
                
                # Link workflow to inspection
                await db.inspection_executions.update_one(
                    {"id": execution_id},
                    {"$set": {"workflow_id": workflow["id"]}}
                )
                
                completed_execution["workflow_id"] = workflow["id"]
        except Exception as e:
            # Log error but don't fail inspection completion
            import logging
            logging.error(f"Failed to start workflow for inspection {execution_id}: {str(e)}")
    
    return completed_execution


@router.get("/stats")
async def get_inspection_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inspection statistics"""
    user = await get_current_user(request, db)
    
    # Get all inspections
    all_inspections = await db.inspection_executions.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(all_inspections)
    
    # Count completed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = len([
        i for i in all_inspections
        if i.get("status") == "completed" and 
        i.get("completed_at") and
        datetime.fromisoformat(i["completed_at"]) >= today_start
    ])
    
    # Count pending
    pending = len([i for i in all_inspections if i.get("status") == "in_progress"])
    
    # Calculate pass rate
    completed = [i for i in all_inspections if i.get("status") == "completed" and i.get("passed") is not None]
    pass_rate = (len([i for i in completed if i.get("passed")]) / len(completed) * 100.0) if completed else 0.0
    
    # Average score
    scores = [i.get("score") for i in completed if i.get("score") is not None]
    average_score = sum(scores) / len(scores) if scores else None
    
    return InspectionStats(
        total_inspections=total,
        completed_today=completed_today,
        pending=pending,
        pass_rate=round(pass_rate, 2),
        average_score=round(average_score, 2) if average_score else None,
    )


@router.post("/upload-photo")
async def upload_inspection_photo(
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload a photo for an inspection using GridFS"""
    user = await get_current_user(request, db)
    
    # Read file content
    content = await file.read()
    
    # Create GridFS bucket
    fs = AsyncIOMotorGridFSBucket(db)
    
    # Upload to GridFS
    file_id = await fs.upload_from_stream(
        file.filename,
        io.BytesIO(content),
        metadata={
            "content_type": file.content_type,
            "uploaded_by": user["id"],
            "organization_id": user["organization_id"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    
    return {"file_id": str(file_id), "filename": file.filename}


@router.get("/photos/{file_id}")
async def get_inspection_photo(
    file_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a photo from GridFS"""
    from fastapi.responses import StreamingResponse
    
    user = await get_current_user(request, db)
    
    try:
        fs = AsyncIOMotorGridFSBucket(db)
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        
        # Read file content
        content = await grid_out.read()
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=grid_out.metadata.get("content_type", "image/jpeg")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )


# ==================== NEW ENHANCED ENDPOINTS ====================

@router.post("/templates/{template_id}/schedule")
async def set_inspection_schedule(
    template_id: str,
    schedule_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Set recurring schedule for an inspection template"""
    from inspection_models import InspectionSchedule
    
    user = await get_current_user(request, db)
    
    # Verify template exists and belongs to organization
    template = await db.inspection_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Create schedule
    schedule = InspectionSchedule(
        organization_id=user["organization_id"],
        template_id=template["id"],
        template_name=template["name"],
        unit_ids=schedule_data.get("unit_ids", []),
        recurrence_rule=schedule_data.get("recurrence_rule", "monthly"),
        recurrence_details=schedule_data.get("recurrence_details"),
        assigned_inspector_ids=schedule_data.get("assigned_inspector_ids", []),
        auto_assign_logic=schedule_data.get("auto_assign_logic", "round_robin"),
        created_by=user["id"],
    )
    
    schedule_dict = schedule.model_dump()
    schedule_dict["created_at"] = schedule_dict["created_at"].isoformat()
    schedule_dict["updated_at"] = schedule_dict["updated_at"].isoformat()
    if schedule_dict.get("next_due_date"):
        schedule_dict["next_due_date"] = schedule_dict["next_due_date"].isoformat()
    
    # Save schedule
    insert_dict = schedule_dict.copy()
    await db.inspection_schedules.insert_one(insert_dict)
    
    # Update template with schedule info
    await db.inspection_templates.update_one(
        {"id": template_id},
        {"$set": {
            "recurrence_rule": schedule_data.get("recurrence_rule"),
            "auto_assign_logic": schedule_data.get("auto_assign_logic"),
            "assigned_inspector_ids": schedule_data.get("assigned_inspector_ids", []),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return schedule_dict


@router.post("/templates/{template_id}/assign-units")
async def assign_template_to_units(
    template_id: str,
    unit_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Assign inspection template to specific units"""
    user = await get_current_user(request, db)
    
    # Verify template exists
    template = await db.inspection_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    unit_ids = unit_data.get("unit_ids", [])
    
    # Update template
    await db.inspection_templates.update_one(
        {"id": template_id},
        {"$set": {
            "unit_ids": unit_ids,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Units assigned successfully", "unit_ids": unit_ids}


@router.get("/due")
async def get_due_inspections(
    request: Request,
    days_ahead: int = 7,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inspections due in the next X days"""
    user = await get_current_user(request, db)
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days_ahead)
    
    # Find due inspections (scheduled but not completed)
    due_inspections = await db.inspection_executions.find(
        {
            "organization_id": user["organization_id"],
            "status": {"$in": ["in_progress", "scheduled"]},
            "due_date": {
                "$gte": now.isoformat(),
                "$lte": end_date.isoformat()
            }
        },
        {"_id": 0}
    ).sort("due_date", 1).to_list(1000)
    
    # Also check for recurring schedules that need new instances
    schedules = await db.inspection_schedules.find(
        {
            "organization_id": user["organization_id"],
            "is_active": True
        },
        {"_id": 0}
    ).to_list(1000)
    
    return {
        "due_inspections": due_inspections,
        "active_schedules": schedules,
        "date_range": {
            "start": now.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.post("/executions/{execution_id}/create-work-order")
async def create_work_order_from_inspection(
    execution_id: str,
    wo_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Manually create a work order from inspection findings"""
    user = await get_current_user(request, db)
    
    # Get inspection
    execution = await db.inspection_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )
    
    # Create placeholder work order (will be replaced when Work Order module is implemented)
    work_order = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "title": wo_data.get("title", f"Work Order from Inspection: {execution['template_name']}"),
        "description": wo_data.get("description", "\n".join(execution.get("findings", []))),
        "priority": wo_data.get("priority", "normal"),
        "status": "pending",
        "source_inspection_id": execution_id,
        "asset_id": execution.get("asset_id"),
        "unit_id": execution.get("unit_id"),
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Save work order (placeholder collection)
    await db.work_orders.insert_one(work_order.copy())
    
    # Update inspection with work order reference
    await db.inspection_executions.update_one(
        {"id": execution_id},
        {"$set": {"auto_created_wo_id": work_order["id"]}}
    )
    
    return work_order


@router.get("/templates/{template_id}/analytics")
async def get_template_analytics(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get performance analytics for a template"""
    from inspection_models import TemplateAnalytics
    from collections import Counter
    
    user = await get_current_user(request, db)
    
    # Get template
    template = await db.inspection_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Get all executions for this template
    executions = await db.inspection_executions.find(
        {"template_id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(executions)
    completed = [e for e in executions if e.get("status") == "completed"]
    in_progress = [e for e in executions if e.get("status") == "in_progress"]
    
    # Calculate average score
    scores = [e.get("score") for e in completed if e.get("score") is not None]
    avg_score = sum(scores) / len(scores) if scores else None
    
    # Calculate pass rate
    passed = [e for e in completed if e.get("passed")]
    pass_rate = (len(passed) / len(completed) * 100.0) if completed else 0.0
    
    # Calculate average duration
    durations = [e.get("duration_minutes") for e in completed if e.get("duration_minutes") is not None]
    avg_duration = int(sum(durations) / len(durations)) if durations else None
    
    # Get most common findings
    all_findings = []
    for e in completed:
        all_findings.extend(e.get("findings", []))
    
    finding_counts = Counter(all_findings)
    most_common = [{"finding": f, "count": c} for f, c in finding_counts.most_common(10)]
    
    # Completion trend (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent = [e for e in completed if datetime.fromisoformat(e.get("completed_at", "2000-01-01T00:00:00+00:00")) >= thirty_days_ago]
    
    trend = {}
    for e in recent:
        date_str = e.get("completed_at", "")[:10]
        trend[date_str] = trend.get(date_str, 0) + 1
    
    completion_trend = [{"date": d, "count": c} for d, c in sorted(trend.items())]
    
    analytics = TemplateAnalytics(
        template_id=template_id,
        template_name=template["name"],
        total_executions=total,
        completed_executions=len(completed),
        in_progress_executions=len(in_progress),
        average_score=round(avg_score, 2) if avg_score else None,
        pass_rate=round(pass_rate, 2),
        average_duration_minutes=avg_duration,
        most_common_findings=most_common,
        completion_trend=completion_trend
    )
    
    return analytics.model_dump()


@router.get("/executions/{execution_id}/follow-ups")
async def get_inspection_follow_ups(
    execution_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get follow-up inspection history"""
    user = await get_current_user(request, db)
    
    # Get the inspection
    execution = await db.inspection_executions.find_one(
        {"id": execution_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )
    
    # Find all follow-ups
    follow_ups = await db.inspection_executions.find(
        {"parent_inspection_id": execution_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Find parent if this is a follow-up
    parent = None
    if execution.get("parent_inspection_id"):
        parent = await db.inspection_executions.find_one(
            {"id": execution["parent_inspection_id"]},
            {"_id": 0}
        )
    
    return {
        "inspection": execution,
        "parent": parent,
        "follow_ups": follow_ups,
        "total_follow_ups": len(follow_ups)
    }


@router.post("/templates/bulk-schedule")
async def bulk_schedule_inspections(
    schedule_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Schedule multiple templates at once"""
    user = await get_current_user(request, db)
    
    template_ids = schedule_data.get("template_ids", [])
    unit_ids = schedule_data.get("unit_ids", [])
    recurrence_rule = schedule_data.get("recurrence_rule", "monthly")
    
    if not template_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No templates specified",
        )
    
    results = []
    
    for template_id in template_ids:
        template = await db.inspection_templates.find_one(
            {"id": template_id, "organization_id": user["organization_id"]},
            {"_id": 0}
        )
        
        if not template:
            continue
        
        # Update template
        await db.inspection_templates.update_one(
            {"id": template_id},
            {"$set": {
                "unit_ids": unit_ids,
                "recurrence_rule": recurrence_rule,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        results.append({
            "template_id": template_id,
            "template_name": template["name"],
            "status": "scheduled"
        })
    
    return {
        "message": f"Scheduled {len(results)} templates",
        "results": results
    }


@router.get("/calendar")
async def get_inspection_calendar(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    unit_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get calendar view of scheduled inspections"""
    from inspection_models import InspectionCalendarItem
    
    user = await get_current_user(request, db)
    
    # Parse date range
    if not start_date:
        start = datetime.now(timezone.utc)
    else:
        start = datetime.fromisoformat(start_date)
    
    if not end_date:
        end = start + timedelta(days=30)
    else:
        end = datetime.fromisoformat(end_date)
    
    # Build query
    query = {
        "organization_id": user["organization_id"],
        "due_date": {
            "$gte": start.isoformat(),
            "$lte": end.isoformat()
        }
    }
    
    if unit_id:
        query["unit_id"] = unit_id
    
    # Get scheduled inspections
    executions = await db.inspection_executions.find(query, {"_id": 0}).sort("due_date", 1).to_list(1000)
    
    # Transform to calendar items
    calendar_items = []
    for e in executions:
        item = InspectionCalendarItem(
            id=e["id"],
            template_id=e["template_id"],
            template_name=e["template_name"],
            due_date=datetime.fromisoformat(e["due_date"]),
            assigned_to=e.get("inspector_id"),
            assigned_to_name=e.get("inspector_name"),
            status=e["status"],
            unit_id=e.get("unit_id"),
            unit_name=e.get("unit_name"),
            asset_id=e.get("asset_id"),
            asset_name=e.get("asset_name")
        )
        calendar_items.append(item.model_dump())
    
    return {
        "calendar_items": calendar_items,
        "date_range": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "total_items": len(calendar_items)
    }