from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import gridfs
from bson import ObjectId
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
    
    await db.inspection_templates.insert_one(template_dict)
    
    return template


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
    
    execution = InspectionExecution(
        organization_id=user["organization_id"],
        template_id=template["id"],
        template_name=template["name"],
        template_version=template.get("version", 1),
        unit_id=execution_data.unit_id,
        inspector_id=user["id"],
        inspector_name=user["name"],
        location=execution_data.location,
    )
    
    execution_dict = execution.model_dump()
    execution_dict["started_at"] = execution_dict["started_at"].isoformat()
    execution_dict["created_at"] = execution_dict["created_at"].isoformat()
    
    await db.inspection_executions.insert_one(execution_dict)
    
    return execution


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
    
    update_data = {
        "status": "completed",
        "answers": answers_dict,
        "findings": completion_data.findings or [],
        "notes": completion_data.notes,
        "score": score,
        "passed": passed,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.inspection_executions.update_one(
        {"id": execution_id},
        {"$set": update_data}
    )
    
    completed_execution = await db.inspection_executions.find_one({"id": execution_id}, {"_id": 0})
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