from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional
import uuid

from project_models import Project, Milestone, ProjectCreate, ProjectUpdate, ProjectStats
from auth_utils import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def generate_project_code() -> str:
    year = datetime.now(timezone.utc).strftime('%Y')
    random = str(uuid.uuid4())[:6].upper()
    return f"PRJ-{year}-{random}"


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create project"""
    user = await get_current_user(request, db)
    # SECURITY: Check permission before allowing creation
    from permission_routes import check_permission
    has_permission = await check_permission(db, user["id"], "project", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create projects")
    
    
    project = Project(
        organization_id=user["organization_id"],
        project_code=generate_project_code(),
        name=project_data.name,
        description=project_data.description,
        project_type=project_data.project_type,
        priority=project_data.priority,
        project_manager_id=user["id"],
        project_manager_name=user["name"],
        unit_id=project_data.unit_id,
        planned_start=project_data.planned_start,
        planned_end=project_data.planned_end,
        budget=project_data.budget,
        created_by=user["id"],
    )
    
    project_dict = project.model_dump()
    project_dict["created_at"] = project_dict["created_at"].isoformat()
    project_dict["updated_at"] = project_dict["updated_at"].isoformat()
    
    await db.projects.insert_one(project_dict.copy())
    return project_dict


@router.get("/stats/overview")
async def get_project_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get project statistics"""
    user = await get_current_user(request, db)
    
    projects = await db.projects.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    by_status = {}
    for p in projects:
        s = p.get("status", "planning")
        by_status[s] = by_status.get(s, 0) + 1
    
    total_budget = sum(p.get("budget", 0) for p in projects)
    total_cost = sum(p.get("actual_cost", 0) for p in projects)
    
    stats = ProjectStats(
        total_projects=len(projects),
        by_status=by_status,
        total_budget=round(total_budget, 2),
        total_actual_cost=round(total_cost, 2)
    )
    
    return stats.model_dump()


@router.get("/dashboard")
async def get_project_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get project portfolio dashboard"""
    user = await get_current_user(request, db)
    
    projects = await db.projects.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    # Calculate metrics
    active_projects = [p for p in projects if p.get("status") == "active"]
    on_hold = [p for p in projects if p.get("status") == "on_hold"]
    completed = [p for p in projects if p.get("status") == "completed"]
    
    total_budget = sum(p.get("budget", 0) for p in projects)
    total_spent = sum(p.get("actual_cost", 0) for p in projects)
    
    on_time = len([p for p in completed if p.get("actual_end") and p.get("planned_end") and p.get("actual_end") <= p.get("planned_end")])
    on_time_pct = (on_time / len(completed) * 100) if completed else 0
    
    return {
        "total_projects": len(projects),
        "active": len(active_projects),
        "on_hold": len(on_hold),
        "completed": len(completed),
        "total_budget": total_budget,
        "total_spent": total_spent,
        "variance": total_budget - total_spent,
        "on_time_percentage": round(on_time_pct, 2)
    }


@router.get("")
async def list_projects(
    request: Request,
    status_filter: Optional[str] = None,
    pm_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List projects"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    if status_filter:
        query["status"] = status_filter
    if pm_id:
        query["project_manager_id"] = pm_id
    if unit_id:
        query["unit_id"] = unit_id
    
    projects = await db.projects.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return projects


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get project details"""
    user = await get_current_user(request, db)
    
    project = await db.projects.find_one(
        {"id": project_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    return project


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update project"""
    user = await get_current_user(request, db)
    
    project = await db.projects.find_one({"id": project_id, "organization_id": user["organization_id"]})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    update_data = project_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.projects.update_one({"id": project_id}, {"$set": update_data})
    return await db.projects.find_one({"id": project_id}, {"_id": 0})


@router.post("/{project_id}/milestones")
async def create_milestone(
    project_id: str,
    milestone_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create project milestone"""
    user = await get_current_user(request, db)
    
    project = await db.projects.find_one({"id": project_id, "organization_id": user["organization_id"]})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    milestone = Milestone(
        project_id=project_id,
        name=milestone_data.get("name"),
        description=milestone_data.get("description"),
        due_date=milestone_data.get("due_date"),
        order=project.get("milestone_count", 0) + 1,
    )
    
    milestone_dict = milestone.model_dump()
    milestone_dict["created_at"] = milestone_dict["created_at"].isoformat()
    
    await db.milestones.insert_one(milestone_dict.copy())
    await db.projects.update_one({"id": project_id}, {"$inc": {"milestone_count": 1}})
    
    return milestone_dict


@router.get("/{project_id}/milestones")
async def list_milestones(
    project_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List project milestones"""
    user = await get_current_user(request, db)
    
    milestones = await db.milestones.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    return milestones


@router.post("/{project_id}/tasks")
async def create_project_task(
    project_id: str,
    task_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create task for project"""
    user = await get_current_user(request, db)
    
    # Verify project exists
    project = await db.projects.find_one({"id": project_id, "organization_id": user["organization_id"]})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Create task linked to project
    task = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "title": task_data.get("title"),
        "description": task_data.get("description"),
        "task_type": "project_task",
        "project_id": project_id,
        "status": "todo",
        "priority": task_data.get("priority", "normal"),
        "assigned_to": task_data.get("assigned_to"),
        "due_date": task_data.get("due_date"),
        "created_by": user["id"],
        "created_by_name": user["name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tasks.insert_one(task.copy())
    await db.projects.update_one({"id": project_id}, {"$inc": {"task_count": 1}})
    
    return task


@router.get("/{project_id}/tasks")
async def list_project_tasks(
    project_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List project tasks"""
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find(
        {"project_id": project_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    return tasks

