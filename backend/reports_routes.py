from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta, timezone
from typing import Optional
from .auth_utils import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/overview")
async def get_overview_report(
    request: Request,
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get overview report for dashboard"""
    user = await get_current_user(request, db)
    org_id = user["organization_id"]
    
    # Get all data
    inspections = await db.inspection_executions.find({"organization_id": org_id}, {"_id": 0}).to_list(10000)
    checklists = await db.checklist_executions.find({"organization_id": org_id}, {"_id": 0}).to_list(10000)
    tasks = await db.tasks.find({"organization_id": org_id}, {"_id": 0}).to_list(10000)
    
    # Calculate metrics
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    
    inspection_metrics = {
        "total": len(inspections),
        "completed": len([i for i in inspections if i.get("status") == "completed"]),
        "pending": len([i for i in inspections if i.get("status") == "in_progress"]),
        "pass_rate": 0.0,
        "avg_score": 0.0,
    }
    
    completed_inspections = [i for i in inspections if i.get("status") == "completed" and i.get("passed") is not None]
    if completed_inspections:
        passed = len([i for i in completed_inspections if i.get("passed")])
        inspection_metrics["pass_rate"] = round((passed / len(completed_inspections)) * 100, 2)
        
        scores = [i.get("score") for i in completed_inspections if i.get("score")]
        if scores:
            inspection_metrics["avg_score"] = round(sum(scores) / len(scores), 2)
    
    checklist_metrics = {
        "total": len(checklists),
        "completed": len([c for c in checklists if c.get("status") == "completed"]),
        "pending": len([c for c in checklists if c.get("status") != "completed"]),
        "completion_rate": 0.0,
    }
    
    if len(checklists) > 0:
        checklist_metrics["completion_rate"] = round(
            (checklist_metrics["completed"] / len(checklists)) * 100, 2
        )
    
    task_metrics = {
        "total": len(tasks),
        "completed": len([t for t in tasks if t.get("status") == "completed"]),
        "in_progress": len([t for t in tasks if t.get("status") == "in_progress"]),
        "todo": len([t for t in tasks if t.get("status") == "todo"]),
        "overdue": 0,
    }
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    task_metrics["overdue"] = len([
        t for t in tasks
        if t.get("due_date") and t.get("due_date") < today and t.get("status") != "completed"
    ])
    
    return {
        "period_days": days,
        "inspections": inspection_metrics,
        "checklists": checklist_metrics,
        "tasks": task_metrics,
    }


@router.get("/trends")
async def get_trends(
    request: Request,
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get trends data for charts"""
    user = await get_current_user(request, db)
    org_id = user["organization_id"]
    
    # Get data from last N days
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    
    # Inspections trend
    inspections = await db.inspection_executions.find(
        {"organization_id": org_id},
        {"completed_at": 1, "status": 1, "_id": 0}
    ).to_list(10000)
    
    inspection_by_day = {}
    for inspection in inspections:
        if inspection.get("completed_at"):
            date_str = inspection["completed_at"][:10]
            if date_str >= cutoff_str:
                inspection_by_day[date_str] = inspection_by_day.get(date_str, 0) + 1
    
    # Checklists trend
    checklists = await db.checklist_executions.find(
        {"organization_id": org_id, "date": {"$gte": cutoff_str}},
        {"date": 1, "status": 1, "_id": 0}
    ).to_list(10000)
    
    checklist_by_day = {}
    for checklist in checklists:
        date_str = checklist.get("date")
        if date_str and checklist.get("status") == "completed":
            checklist_by_day[date_str] = checklist_by_day.get(date_str, 0) + 1
    
    # Tasks trend
    tasks = await db.tasks.find(
        {"organization_id": org_id},
        {"completed_at": 1, "status": 1, "_id": 0}
    ).to_list(10000)
    
    task_by_day = {}
    for task in tasks:
        if task.get("completed_at"):
            date_str = task["completed_at"][:10]
            if date_str >= cutoff_str:
                task_by_day[date_str] = task_by_day.get(date_str, 0) + 1
    
    return {
        "inspections": inspection_by_day,
        "checklists": checklist_by_day,
        "tasks": task_by_day,
    }