from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional
from task_models import Task, TaskCreate, TaskUpdate, TaskComment, TaskStats
from auth_utils import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("")
async def get_tasks(
    request: Request,
    status_filter: Optional[str] = None,
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,  # Default limit
    skip: int = 0,  # Default skip for pagination
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get tasks with filters and pagination"""
    user = await get_current_user(request, db)
    
    # Enforce maximum limit
    limit = min(limit, 100)  # Max 100 tasks per request
    
    query = {"organization_id": user["organization_id"]}
    if status_filter:
        query["status"] = status_filter
    if assigned_to:
        query["assigned_to"] = assigned_to
    if priority:
        query["priority"] = priority
    
    tasks = await db.tasks.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return tasks


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new task"""
    user = await get_current_user(request, db)
    
    # Get assigned user name if provided
    assigned_to_name = None
    if task_data.assigned_to:
        assigned_user = await db.users.find_one({"id": task_data.assigned_to}, {"name": 1})
        if assigned_user:
            assigned_to_name = assigned_user["name"]
    
    task = Task(
        organization_id=user["organization_id"],
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        assigned_to=task_data.assigned_to,
        assigned_to_name=assigned_to_name,
        created_by=user["id"],
        created_by_name=user["name"],
        due_date=task_data.due_date,
        unit_id=task_data.unit_id,
        tags=task_data.tags,
    )
    
    task_dict = task.model_dump()
    task_dict["created_at"] = task_dict["created_at"].isoformat()
    task_dict["updated_at"] = task_dict["updated_at"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = task_dict.copy()
    await db.tasks.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return task_dict


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific task"""
    user = await get_current_user(request, db)
    
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.put("/{task_id}")
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a task"""
    user = await get_current_user(request, db)
    
    task = await db.tasks.find_one({"id": task_id, "organization_id": user["organization_id"]})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_data = task_data.model_dump(exclude_unset=True)
    
    # Update assigned user name if changed
    if "assigned_to" in update_data and update_data["assigned_to"]:
        assigned_user = await db.users.find_one({"id": update_data["assigned_to"]}, {"name": 1})
        if assigned_user:
            update_data["assigned_to_name"] = assigned_user["name"]
    
    # Handle status change to completed
    if update_data.get("status") == "completed" and task.get("status") != "completed":
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Check if task requires approval
        if task.get("requires_approval") and task.get("workflow_template_id"):
            update_data["status"] = "pending_approval"
            
            # Auto-start workflow
            from workflow_engine import WorkflowEngine
            engine = WorkflowEngine(db)
            
            try:
                # Check for duplicate workflow
                existing_workflow = await db.workflow_instances.find_one({
                    "resource_type": "task",
                    "resource_id": task_id,
                    "status": {"$in": ["pending", "in_progress", "escalated"]}
                })
                
                if not existing_workflow:
                    workflow = await engine.start_workflow(
                        template_id=task["workflow_template_id"],
                        resource_type="task",
                        resource_id=task_id,
                        resource_name=task.get("title", "Task"),
                        created_by=user["id"],
                        created_by_name=user["name"],
                        organization_id=user["organization_id"]
                    )
                    
                    update_data["workflow_id"] = workflow["id"]
            except Exception as e:
                import logging
                logging.error(f"Failed to start workflow for task {task_id}: {str(e)}")
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.tasks.update_one({"id": task_id}, {"$set": update_data})
    
    updated_task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    return updated_task


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a task"""
    user = await get_current_user(request, db)
    
    result = await db.tasks.delete_one({"id": task_id, "organization_id": user["organization_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/comments")
async def add_comment(
    task_id: str,
    comment: TaskComment,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add a comment to a task"""
    user = await get_current_user(request, db)
    
    task = await db.tasks.find_one({"id": task_id, "organization_id": user["organization_id"]})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    new_comment = {
        "user": user["name"],
        "text": comment.text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.tasks.update_one(
        {"id": task_id},
        {"$push": {"comments": new_comment}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Comment added successfully", "comment": new_comment}


@router.get("/stats/overview")
async def get_task_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task statistics"""
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find({"organization_id": user["organization_id"]}, {"_id": 0}).to_list(10000)
    
    total = len(tasks)
    todo = len([t for t in tasks if t.get("status") == "todo"])
    in_progress = len([t for t in tasks if t.get("status") == "in_progress"])
    completed = len([t for t in tasks if t.get("status") == "completed"])
    
    # Count overdue tasks
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue = len([t for t in tasks if t.get("due_date") and t.get("due_date") < today and t.get("status") != "completed"])
    
    completion_rate = (completed / total * 100) if total > 0 else 0.0
    
    return TaskStats(
        total_tasks=total,
        todo=todo,
        in_progress=in_progress,
        completed=completed,
        overdue=overdue,
        completion_rate=round(completion_rate, 2),
    )