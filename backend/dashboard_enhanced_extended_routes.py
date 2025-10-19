"""
Extended Dashboard Routes
Provides operations and safety dashboard endpoints
"""
from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import get_current_user
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/dashboard", tags=["Dashboards Extended"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/operations")
async def get_operations_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get operations dashboard data"""
    user = await get_current_user(request, db)
    
    # Get last 30 days data
    start_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    # Inspections data
    inspections_total = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    inspections_completed = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    # Checklists data
    checklists_total = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    checklists_completed = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    # Tasks data
    tasks_total = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    tasks_completed = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    # Work orders data
    workorders_total = await db.workorders.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    workorders_completed = await db.workorders.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "created_at": {"$gte": start_date}
    })
    
    return {
        "period": "30d",
        "inspections": {
            "total": inspections_total,
            "completed": inspections_completed,
            "completion_rate": round((inspections_completed / inspections_total * 100) if inspections_total > 0 else 0, 2)
        },
        "checklists": {
            "total": checklists_total,
            "completed": checklists_completed,
            "completion_rate": round((checklists_completed / checklists_total * 100) if checklists_total > 0 else 0, 2)
        },
        "tasks": {
            "total": tasks_total,
            "completed": tasks_completed,
            "completion_rate": round((tasks_completed / tasks_total * 100) if tasks_total > 0 else 0, 2)
        },
        "workorders": {
            "total": workorders_total,
            "completed": workorders_completed,
            "completion_rate": round((workorders_completed / workorders_total * 100) if workorders_total > 0 else 0, 2)
        }
    }


@router.get("/safety")
async def get_safety_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get safety dashboard data"""
    user = await get_current_user(request, db)
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    # Incidents data
    incidents_total = await db.incidents.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    incidents_critical = await db.incidents.count_documents({
        "organization_id": user["organization_id"],
        "severity": "critical",
        "created_at": {"$gte": start_date}
    })
    
    incidents_closed = await db.incidents.count_documents({
        "organization_id": user["organization_id"],
        "status": "closed",
        "created_at": {"$gte": start_date}
    })
    
    # Safety inspections
    safety_inspections = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "type": "safety",
        "created_at": {"$gte": start_date}
    })
    
    # Training completions
    training_completed = await db.training_records.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": start_date}
    })
    
    # Emergencies
    emergencies_total = await db.emergencies.count_documents({
        "organization_id": user["organization_id"],
        "created_at": {"$gte": start_date}
    })
    
    emergencies_active = await db.emergencies.count_documents({
        "organization_id": user["organization_id"],
        "status": "active",
        "created_at": {"$gte": start_date}
    })
    
    return {
        "period": "30d",
        "incidents": {
            "total": incidents_total,
            "critical": incidents_critical,
            "closed": incidents_closed,
            "open": incidents_total - incidents_closed
        },
        "safety_inspections": safety_inspections,
        "training_completed": training_completed,
        "emergencies": {
            "total": emergencies_total,
            "active": emergencies_active,
            "resolved": emergencies_total - emergencies_active
        },
        "safety_score": round((incidents_closed / incidents_total * 100) if incidents_total > 0 else 100, 2)
    }
