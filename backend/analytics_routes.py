from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from auth_utils import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

def get_date_range(period: str) -> tuple:
    """Get date range based on period"""
    now = datetime.now(timezone.utc)
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "week":
        start = now - timedelta(days=7)
        end = now
    elif period == "month":
        start = now - timedelta(days=30)
        end = now
    elif period == "quarter":
        start = now - timedelta(days=90)
        end = now
    elif period == "year":
        start = now - timedelta(days=365)
        end = now
    else:
        start = now - timedelta(days=7)
        end = now
    
    return start.isoformat(), end.isoformat()


# ==================== ENDPOINTS ====================

@router.get("/overview")
async def get_analytics_overview(
    request: Request,
    period: str = "week",  # today, week, month, quarter, year
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get analytics overview with key metrics"""
    user = await get_current_user(request, db)
    start_date, end_date = get_date_range(period)
    
    # Tasks metrics
    total_tasks = await db.tasks.count_documents({
        "organization_id": user["organization_id"]
    })
    
    completed_tasks = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    })
    
    # Inspections metrics
    total_inspections = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"]
    })
    
    completed_inspections = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    })
    
    # Users metrics
    active_users = await db.users.count_documents({
        "organization_id": user["organization_id"],
        "is_active": True
    })
    
    # Groups metrics
    total_groups = await db.user_groups.count_documents({
        "organization_id": user["organization_id"],
        "is_active": True
    })
    
    # Time tracking metrics
    time_entries = await db.time_entries.find({
        "organization_id": user["organization_id"],
        "started_at": {"$gte": start_date, "$lte": end_date}
    }).to_list(10000)
    
    total_hours = sum(e.get("duration_minutes", 0) for e in time_entries if not e.get("is_running")) / 60
    
    # Workflow metrics
    workflows_completed = await db.workflow_instances.count_documents({
        "organization_id": user["organization_id"],
        "status": "approved",
        "updated_at": {"$gte": start_date, "$lte": end_date}
    })
    
    return {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "metrics": {
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            },
            "inspections": {
                "total": total_inspections,
                "completed": completed_inspections,
                "completion_rate": round((completed_inspections / total_inspections * 100) if total_inspections > 0 else 0, 2)
            },
            "users": {
                "active": active_users
            },
            "groups": {
                "total": total_groups
            },
            "time_tracking": {
                "total_hours": round(total_hours, 2),
                "entries": len(time_entries)
            },
            "workflows": {
                "completed": workflows_completed
            }
        }
    }


@router.get("/tasks/trends")
async def get_task_trends(
    request: Request,
    period: str = "week",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task trends over time"""
    user = await get_current_user(request, db)
    start_date, end_date = get_date_range(period)
    
    # Get tasks created in period
    tasks = await db.tasks.find({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date, "$lte": end_date}
    }, {"created_at": 1, "status": 1, "priority": 1, "_id": 0}).to_list(10000)
    
    # Group by date
    trends = {}
    for task in tasks:
        date = task["created_at"][:10]  # YYYY-MM-DD
        if date not in trends:
            trends[date] = {"created": 0, "todo": 0, "in_progress": 0, "completed": 0}
        
        trends[date]["created"] += 1
        status = task.get("status", "todo")
        if status in trends[date]:
            trends[date][status] += 1
    
    # Convert to array format
    trend_data = [
        {"date": date, **values}
        for date, values in sorted(trends.items())
    ]
    
    return {
        "period": period,
        "trends": trend_data
    }


@router.get("/tasks/by-status")
async def get_tasks_by_status(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task distribution by status"""
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find({
        "organization_id": user["organization_id"]
    }, {"status": 1, "_id": 0}).to_list(10000)
    
    status_counts = {}
    for task in tasks:
        status = task.get("status", "todo")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total": len(tasks),
        "by_status": status_counts,
        "chart_data": [
            {"status": status, "count": count}
            for status, count in status_counts.items()
        ]
    }


@router.get("/tasks/by-priority")
async def get_tasks_by_priority(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task distribution by priority"""
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find({
        "organization_id": user["organization_id"]
    }, {"priority": 1, "_id": 0}).to_list(10000)
    
    priority_counts = {}
    for task in tasks:
        priority = task.get("priority", "medium")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    return {
        "total": len(tasks),
        "by_priority": priority_counts,
        "chart_data": [
            {"priority": priority, "count": count}
            for priority, count in priority_counts.items()
        ]
    }


@router.get("/tasks/by-user")
async def get_tasks_by_user(
    request: Request,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get task distribution by assigned user"""
    user = await get_current_user(request, db)
    
    tasks = await db.tasks.find({
        "organization_id": user["organization_id"],
        "assigned_to": {"$ne": None}
    }, {"assigned_to": 1, "assigned_to_name": 1, "_id": 0}).to_list(10000)
    
    user_counts = {}
    for task in tasks:
        user_id = task.get("assigned_to")
        user_name = task.get("assigned_to_name", "Unknown")
        if user_id not in user_counts:
            user_counts[user_id] = {"name": user_name, "count": 0}
        user_counts[user_id]["count"] += 1
    
    # Sort by count and limit
    sorted_users = sorted(user_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:limit]
    
    return {
        "total": len(tasks),
        "chart_data": [
            {"user_id": user_id, "name": data["name"], "count": data["count"]}
            for user_id, data in sorted_users
        ]
    }


@router.get("/time-tracking/trends")
async def get_time_tracking_trends(
    request: Request,
    period: str = "week",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get time tracking trends"""
    user = await get_current_user(request, db)
    start_date, end_date = get_date_range(period)
    
    entries = await db.time_entries.find({
        "organization_id": user["organization_id"],
        "started_at": {"$gte": start_date, "$lte": end_date}
    }, {"started_at": 1, "duration_minutes": 1, "billable": 1, "_id": 0}).to_list(10000)
    
    # Group by date
    daily_hours = {}
    for entry in entries:
        if entry.get("is_running"):
            continue
        
        date = entry["started_at"][:10]
        if date not in daily_hours:
            daily_hours[date] = {"total": 0, "billable": 0}
        
        minutes = entry.get("duration_minutes", 0)
        daily_hours[date]["total"] += minutes
        
        if entry.get("billable"):
            daily_hours[date]["billable"] += minutes
    
    # Convert to hours and array format
    trend_data = [
        {
            "date": date,
            "total_hours": round(values["total"] / 60, 2),
            "billable_hours": round(values["billable"] / 60, 2)
        }
        for date, values in sorted(daily_hours.items())
    ]
    
    return {
        "period": period,
        "trends": trend_data
    }


@router.get("/inspections/scores")
async def get_inspection_scores(
    request: Request,
    period: str = "month",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inspection score trends"""
    user = await get_current_user(request, db)
    start_date, end_date = get_date_range(period)
    
    inspections = await db.inspection_executions.find({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": start_date, "$lte": end_date}
    }, {"completed_at": 1, "score": 1, "template_name": 1, "_id": 0}).to_list(10000)
    
    # Calculate average scores by date
    daily_scores = {}
    for inspection in inspections:
        date = inspection["completed_at"][:10]
        score = inspection.get("score", 0)
        
        if date not in daily_scores:
            daily_scores[date] = {"scores": [], "count": 0}
        
        daily_scores[date]["scores"].append(score)
        daily_scores[date]["count"] += 1
    
    # Calculate averages
    trend_data = [
        {
            "date": date,
            "average_score": round(sum(data["scores"]) / len(data["scores"]), 2) if data["scores"] else 0,
            "count": data["count"]
        }
        for date, data in sorted(daily_scores.items())
    ]
    
    return {
        "period": period,
        "trends": trend_data
    }


@router.get("/workflows/completion-time")
async def get_workflow_completion_time(
    request: Request,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflow completion time statistics"""
    user = await get_current_user(request, db)
    
    workflows = await db.workflow_instances.find({
        "organization_id": user["organization_id"],
        "status": {"$in": ["approved", "rejected", "completed"]}
    }, {"workflow_name": 1, "created_at": 1, "updated_at": 1, "_id": 0}).limit(limit).to_list(limit)
    
    completion_times = []
    for workflow in workflows:
        try:
            created = datetime.fromisoformat(workflow["created_at"].replace('Z', '+00:00'))
            updated = datetime.fromisoformat(workflow["updated_at"].replace('Z', '+00:00'))
            duration_hours = (updated - created).total_seconds() / 3600
            
            completion_times.append({
                "workflow": workflow.get("workflow_name", "Unknown"),
                "duration_hours": round(duration_hours, 2)
            })
        except:
            continue
    
    # Calculate statistics
    if completion_times:
        durations = [ct["duration_hours"] for ct in completion_times]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
    else:
        avg_duration = min_duration = max_duration = 0
    
    return {
        "average_hours": round(avg_duration, 2),
        "min_hours": round(min_duration, 2),
        "max_hours": round(max_duration, 2),
        "completion_times": completion_times
    }


@router.get("/user-activity")
async def get_user_activity(
    request: Request,
    period: str = "week",
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user activity statistics"""
    user = await get_current_user(request, db)
    start_date, end_date = get_date_range(period)
    
    # Get audit logs for activity
    logs = await db.audit_logs.find({
        "organization_id": user["organization_id"],
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }, {"user_id": 1, "user_name": 1, "action": 1, "_id": 0}).to_list(10000)
    
    # Count actions per user
    user_activity = {}
    for log in logs:
        user_id = log.get("user_id")
        user_name = log.get("user_name", "Unknown")
        
        if user_id not in user_activity:
            user_activity[user_id] = {"name": user_name, "actions": 0}
        
        user_activity[user_id]["actions"] += 1
    
    # Sort and limit
    sorted_activity = sorted(user_activity.items(), key=lambda x: x[1]["actions"], reverse=True)[:limit]
    
    return {
        "period": period,
        "most_active_users": [
            {
                "user_id": user_id, 
                "user_name": data["name"], 
                "actions": data["actions"],
                "tasks_completed": 0,  # TODO: Calculate from tasks collection
                "hours_logged": 0.0,   # TODO: Calculate from time_entries collection
                "last_activity": None  # TODO: Get from audit logs
            }
            for user_id, data in sorted_activity
        ]
    }
