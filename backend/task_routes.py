from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Optional
from task_models import Task, TaskCreate, TaskUpdate, TaskComment, TaskStats
from auth_utils import get_current_user
from sanitization import sanitize_dict

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
    """Create a new task (requires task.create.organization permission)"""
    user = await get_current_user(request, db)
    
    # SECURITY: Check permission before allowing creation
    from permission_routes import check_permission
    has_permission = await check_permission(db, user["id"], "task", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create tasks")
    
    # Sanitize user inputs to prevent XSS
    task_dict = task_data.model_dump()
    sanitized_data = sanitize_dict(task_dict, ['title', 'description'])
    
    # Get assigned user name if provided
    assigned_to_name = None
    if task_data.assigned_to:
        assigned_user = await db.users.find_one({"id": task_data.assigned_to}, {"name": 1})
        if assigned_user:
            assigned_to_name = assigned_user["name"]
    
    task = Task(
        organization_id=user["organization_id"],
        title=sanitized_data['title'],
        description=sanitized_data['description'],
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


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_task_template(
    template_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create recurring task template"""
    from task_models import TaskTemplate
    user = await get_current_user(request, db)
    
    template = TaskTemplate(
        organization_id=user["organization_id"],
        name=template_data.get("name"),
        description=template_data.get("description"),
        task_type="recurring",
        priority=template_data.get("priority", "medium"),
        assigned_to=template_data.get("assigned_to"),
        unit_id=template_data.get("unit_id"),
        estimated_hours=template_data.get("estimated_hours"),
        recurrence_rule=template_data.get("recurrence_rule", "daily"),
        created_by=user["id"],
    )
    
    template_dict = template.model_dump()
    template_dict["created_at"] = template_dict["created_at"].isoformat()
    template_dict["updated_at"] = template_dict["updated_at"].isoformat()
    
    await db.task_templates.insert_one(template_dict.copy())
    return template_dict



@router.get("/templates")
async def get_task_templates(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task templates"""
    user = await get_current_user(request, db)
    
    templates = await db.task_templates.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(1000)
    
    return templates



@router.post("/from-template")
async def create_task_from_template(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create task from template"""
    user = await get_current_user(request, db)
    
    template = await db.task_templates.find_one(
        {"id": template_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Create task from template
    task_data = TaskCreate(
        title=template["name"],
        description=template.get("description"),
        priority=template.get("priority", "medium"),
        assigned_to=template.get("assigned_to"),
        unit_id=template.get("unit_id"),
        task_type="recurring",
        template_id=template_id,
        estimated_hours=template.get("estimated_hours"),
    )
    
    # Use existing create_task logic
    return await create_task(task_data, request, db)



@router.get("/analytics/overview")
async def get_task_analytics(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task analytics"""
    from task_models import TaskAnalytics
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(tasks)
    completed = [t for t in tasks if t.get("status") == "completed"]
    in_progress = [t for t in tasks if t.get("status") == "in_progress"]
    todo = [t for t in tasks if t.get("status") == "todo"]
    blocked = [t for t in tasks if t.get("status") == "blocked"]
    
    # Calculate overdue
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue = len([t for t in tasks if t.get("due_date") and t.get("due_date") < today and t.get("status") != "completed"])
    
    # Average completion hours
    hours = [t.get("actual_hours") for t in completed if t.get("actual_hours")]
    avg_hours = sum(hours) / len(hours) if hours else None
    
    # On-time percentage
    completed_on_time = len([t for t in completed if t.get("due_date") and t.get("completed_at") and t.get("completed_at")[:10] <= t.get("due_date")])
    on_time_pct = (completed_on_time / len(completed) * 100) if completed else 0.0
    
    # Completion trend
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent = [t for t in completed if t.get("completed_at") and datetime.fromisoformat(t["completed_at"]) >= thirty_days_ago]
    
    trend = {}
    for t in recent:
        date_str = t.get("completed_at", "")[:10]
        trend[date_str] = trend.get(date_str, 0) + 1
    
    completion_trend = [{"date": d, "count": c} for d, c in sorted(trend.items())]
    
    analytics = TaskAnalytics(
        total_tasks=total,
        completed_tasks=len(completed),
        in_progress_tasks=len(in_progress),
        todo_tasks=len(todo),
        blocked_tasks=len(blocked),
        overdue_tasks=overdue,
        average_completion_hours=round(avg_hours, 2) if avg_hours else None,
        on_time_percentage=round(on_time_pct, 2),
        completion_trend=completion_trend
    )
    
    return analytics.model_dump()

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
    
    # Sanitize user inputs to prevent XSS
    if 'title' in update_data or 'description' in update_data:
        update_data = sanitize_dict(update_data, ['title', 'description'])
    
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


@router.post("/{task_id}/subtasks")
async def create_subtask(
    task_id: str,
    subtask_data: TaskCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create subtask"""
    user = await get_current_user(request, db)
    
    # Verify parent task exists
    parent = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found",
        )
    
    # Create subtask with parent_task_id
    subtask_data.parent_task_id = task_id
    task = await create_task(subtask_data, request, db)
    
    # Update parent's subtask count
    await db.tasks.update_one(
        {"id": task_id},
        {"$inc": {"subtask_count": 1}}
    )
    
    return task


@router.get("/{task_id}/subtasks")
async def get_subtasks(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get subtasks for a task"""
    user = await get_current_user(request, db)
    
    subtasks = await db.tasks.find(
        {"parent_task_id": task_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    return subtasks


@router.post("/{task_id}/log-time")
async def log_time_entry(
    task_id: str,
    time_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Log work hours for task"""
    from task_models import LaborEntry
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Create labor entry
    entry = LaborEntry(
        task_id=task_id,
        user_id=user["id"],
        user_name=user["name"],
        hours=time_data.get("hours"),
        hourly_rate=time_data.get("hourly_rate"),
        cost=time_data.get("hours", 0) * time_data.get("hourly_rate", 0) if time_data.get("hourly_rate") else None,
        description=time_data.get("description"),
        entry_date=time_data.get("entry_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
    )
    
    entry_dict = entry.model_dump()
    entry_dict["created_at"] = entry_dict["created_at"].isoformat()
    
    await db.labor_entries.insert_one(entry_dict.copy())
    
    # Update task totals
    total_hours = (task.get("actual_hours") or 0.0) + time_data.get("hours", 0)
    total_cost = (task.get("labor_cost") or 0.0) + (entry_dict.get("cost") or 0)
    
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": {
            "actual_hours": total_hours,
            "labor_cost": total_cost,
            "has_time_entries": True,
        }}
    )
    
    return entry_dict


@router.post("/{task_id}/log-parts")
async def log_parts_usage(
    task_id: str,
    parts_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Log parts used for task"""
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Add parts to task
    parts_used = task.get("parts_used", [])
    parts_used.append(parts_data)
    
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": {"parts_used": parts_used}}
    )
    
    return {"message": "Parts logged successfully", "parts": parts_data}


@router.get("/{task_id}/dependencies")
async def get_task_dependencies(
    task_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task dependency chain"""
    user = await get_current_user(request, db)
    
    task = await db.tasks.find_one(
        {"id": task_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Get predecessor tasks
    predecessors = []
    if task.get("predecessor_task_ids"):
        predecessors = await db.tasks.find(
            {"id": {"$in": task["predecessor_task_ids"]}},
            {"_id": 0}
        ).to_list(100)
    
    # Get subtasks
    subtasks = await db.tasks.find(
        {"parent_task_id": task_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get parent if exists
    parent = None
    if task.get("parent_task_id"):
        parent = await db.tasks.find_one(
            {"id": task["parent_task_id"]},
            {"_id": 0}
        )
    
    return {
        "task": task,
        "predecessors": predecessors,
        "subtasks": subtasks,
        "parent": parent,
    }


