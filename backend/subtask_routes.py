from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
from .subtask_models import Subtask, SubtaskCreate, SubtaskUpdate, SubtaskStats
from .auth_utils import get_current_user
import uuid

router = APIRouter(prefix="/subtasks", tags=["Subtasks"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

async def calculate_task_progress(db: AsyncIOMotorDatabase, task_id: str) -> dict:
    """Calculate task progress based on subtasks"""
    subtasks = await db.subtasks.find(
        {"parent_task_id": task_id},
        {"_id": 0}
    ).to_list(1000)
    
    if not subtasks:
        return {"total": 0, "completed": 0, "percentage": 0}
    
    total = len(subtasks)
    completed = len([s for s in subtasks if s.get("status") == "completed"])
    percentage = round((completed / total) * 100, 2) if total > 0 else 0
    
    return {"total": total, "completed": completed, "percentage": percentage}


async def update_parent_task_status(db: AsyncIOMotorDatabase, task_id: str):
    """Update parent task status based on subtask completion"""
    progress = await calculate_task_progress(db, task_id)
    
    # Update task with subtask progress
    update_data = {
        "subtask_count": progress["total"],
        "subtasks_completed": progress["completed"],
        "completion_percentage": progress["percentage"],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Auto-complete task if all subtasks are done
    if progress["total"] > 0 and progress["percentage"] == 100:
        update_data["status"] = "completed"
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )


# ==================== ENDPOINTS ====================

@router.post("/{task_id}", response_model=Subtask)
async def create_subtask(
    task_id: str,
    subtask_data: SubtaskCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a subtask for a task"""
    user = await get_current_user(request, db)
    
    # Verify task exists and user has access
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Determine nesting level
    level = 1
    if subtask_data.parent_subtask_id:
        parent_subtask = await db.subtasks.find_one({"id": subtask_data.parent_subtask_id})
        if parent_subtask:
            level = parent_subtask.get("level", 1) + 1
    
    # Get assigned user name if provided
    assigned_to_name = None
    if subtask_data.assigned_to:
        assigned_user = await db.users.find_one({"id": subtask_data.assigned_to})
        if assigned_user:
            assigned_to_name = assigned_user.get("name")
    
    # Create subtask
    subtask = Subtask(
        parent_task_id=task_id,
        organization_id=user["organization_id"],
        title=subtask_data.title,
        description=subtask_data.description,
        assigned_to=subtask_data.assigned_to,
        assigned_to_name=assigned_to_name,
        priority=subtask_data.priority,
        due_date=subtask_data.due_date,
        parent_subtask_id=subtask_data.parent_subtask_id,
        level=level,
        created_by=user["id"],
        created_by_name=user["name"]
    )
    
    subtask_dict = subtask.model_dump()
    subtask_dict["created_at"] = subtask_dict["created_at"].isoformat()
    subtask_dict["updated_at"] = subtask_dict["updated_at"].isoformat()
    
    await db.subtasks.insert_one(subtask_dict)
    
    # Update parent task progress
    await update_parent_task_status(db, task_id)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "subtask.created",
        "resource_type": "subtask",
        "resource_id": subtask.id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"parent_task_id": task_id, "title": subtask.title}
    })
    
    return Subtask(**subtask_dict)


@router.get("/{task_id}", response_model=List[Subtask])
async def get_subtasks(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all subtasks for a task (hierarchical)"""
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get all subtasks (including nested)
    subtasks = await db.subtasks.find(
        {"parent_task_id": task_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    return [Subtask(**s) for s in subtasks]


@router.get("/{task_id}/stats", response_model=SubtaskStats)
async def get_subtask_stats(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get subtask statistics for a task"""
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get subtasks
    subtasks = await db.subtasks.find(
        {"parent_task_id": task_id},
        {"_id": 0}
    ).to_list(1000)
    
    total = len(subtasks)
    completed = len([s for s in subtasks if s.get("status") == "completed"])
    in_progress = len([s for s in subtasks if s.get("status") == "in_progress"])
    todo = len([s for s in subtasks if s.get("status") == "todo"])
    percentage = round((completed / total) * 100, 2) if total > 0 else 0
    
    return SubtaskStats(
        total=total,
        completed=completed,
        in_progress=in_progress,
        todo=todo,
        completion_percentage=percentage
    )


@router.put("/{subtask_id}", response_model=Subtask)
async def update_subtask(
    subtask_id: str,
    subtask_data: SubtaskUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a subtask"""
    user = await get_current_user(request, db)
    
    # Find subtask
    subtask = await db.subtasks.find_one(
        {"id": subtask_id, "organization_id": user["organization_id"]}
    )
    
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    # Prepare update data
    update_data = subtask_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # If status changed to completed
    if subtask_data.status == "completed" and subtask.get("status") != "completed":
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        update_data["completed_by"] = user["id"]
    
    # If assigned_to changed, update name
    if subtask_data.assigned_to:
        assigned_user = await db.users.find_one({"id": subtask_data.assigned_to})
        if assigned_user:
            update_data["assigned_to_name"] = assigned_user.get("name")
    
    # Update subtask
    await db.subtasks.update_one(
        {"id": subtask_id},
        {"$set": update_data}
    )
    
    # Update parent task progress
    await update_parent_task_status(db, subtask["parent_task_id"])
    
    # Get updated subtask
    updated_subtask = await db.subtasks.find_one({"id": subtask_id}, {"_id": 0})
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "subtask.updated",
        "resource_type": "subtask",
        "resource_id": subtask_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"changes": list(update_data.keys())}
    })
    
    return Subtask(**updated_subtask)


@router.delete("/{subtask_id}")
async def delete_subtask(
    subtask_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a subtask"""
    user = await get_current_user(request, db)
    
    # Find subtask
    subtask = await db.subtasks.find_one(
        {"id": subtask_id, "organization_id": user["organization_id"]}
    )
    
    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found"
        )
    
    # Delete all nested subtasks first
    await db.subtasks.delete_many({"parent_subtask_id": subtask_id})
    
    # Delete subtask
    await db.subtasks.delete_one({"id": subtask_id})
    
    # Update parent task progress
    await update_parent_task_status(db, subtask["parent_task_id"])
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "subtask.deleted",
        "resource_type": "subtask",
        "resource_id": subtask_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Subtask deleted successfully"}


@router.post("/{task_id}/reorder")
async def reorder_subtasks(
    task_id: str,
    subtask_ids: List[str],
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reorder subtasks"""
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update order for each subtask
    for index, subtask_id in enumerate(subtask_ids):
        await db.subtasks.update_one(
            {"id": subtask_id, "parent_task_id": task_id},
            {"$set": {"order": index}}
        )
    
    return {"message": "Subtasks reordered successfully"}
