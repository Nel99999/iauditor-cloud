"""
Module Analytics Routes
Provides analytics endpoints for Inspections, Checklists, and Tasks
"""
from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import get_current_user
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["Module Analytics"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/inspections/analytics")
async def get_inspections_analytics(
    request: Request,
    period: str = "30d",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inspections analytics"""
    user = await get_current_user(request, db)
    
    # Calculate date range
    days = int(period.replace('d', '')) if period.endswith('d') else 30
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    # Get total templates
    total_templates = await db.inspection_templates.count_documents({
        "organization_id": user["organization_id"]
    })
    
    # Get total executions
    total_executions = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    # Get completed executions
    completed = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    # Get pending executions
    pending = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "pending",
        "created_at": {"$gte": start_date}
    })
    
    # Get failed executions
    failed = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "failed",
        "created_at": {"$gte": start_date}
    })
    
    completion_rate = (completed / total_executions * 100) if total_executions > 0 else 0
    
    return {
        "period": period,
        "total_templates": total_templates,
        "total_executions": total_executions,
        "completed": completed,
        "pending": pending,
        "failed": failed,
        "completion_rate": round(completion_rate, 2),
        "avg_per_day": round(total_executions / days, 2) if days > 0 else 0
    }


@router.get("/checklists/analytics")
async def get_checklists_analytics(
    request: Request,
    period: str = "30d",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get checklists analytics"""
    user = await get_current_user(request, db)
    
    days = int(period.replace('d', '')) if period.endswith('d') else 30
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    total_templates = await db.checklist_templates.count_documents({
        "organization_id": user["organization_id"]
    })
    
    total_executions = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    completed = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    pending = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "pending",
        "created_at": {"$gte": start_date}
    })
    
    completion_rate = (completed / total_executions * 100) if total_executions > 0 else 0
    
    return {
        "period": period,
        "total_templates": total_templates,
        "total_executions": total_executions,
        "completed": completed,
        "pending": pending,
        "completion_rate": round(completion_rate, 2),
        "avg_per_day": round(total_executions / days, 2) if days > 0 else 0
    }


@router.get("/tasks/analytics")
async def get_tasks_analytics(
    request: Request,
    period: str = "30d",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get tasks analytics"""
    user = await get_current_user(request, db)
    
    days = int(period.replace('d', '')) if period.endswith('d') else 30
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    total_tasks = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    completed = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    in_progress = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": "in_progress",
        "created_at": {"$gte": start_date}
    })
    
    pending = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": "pending",
        "created_at": {"$gte": start_date}
    })
    
    overdue = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": {"$ne": "completed"},
        "due_date": {"$lt": datetime.now(timezone.utc).isoformat()},
        "created_at": {"$gte": start_date}
    })
    
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "period": period,
        "total_tasks": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": round(completion_rate, 2),
        "avg_per_day": round(total_tasks / days, 2) if days > 0 else 0
    }
