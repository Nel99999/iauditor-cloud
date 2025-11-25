from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Optional

from .auth_utils import get_current_user

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/executive")
async def get_executive_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Executive dashboard with org-wide KPIs"""
    user = await get_current_user(request, db)
    
    # Get counts from all modules
    tasks = await db.tasks.count_documents({"organization_id": user["organization_id"]})
    assets = await db.assets.count_documents({"organization_id": user["organization_id"], "is_active": True})
    work_orders = await db.work_orders.count_documents({"organization_id": user["organization_id"], "is_active": True})
    incidents = await db.incidents.count_documents({"organization_id": user["organization_id"]})
    projects = await db.projects.count_documents({"organization_id": user["organization_id"], "is_active": True})
    
    # Get recent activity
    recent_inspections = await db.inspection_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    recent_checklists = await db.checklist_executions.count_documents({
        "organization_id": user["organization_id"],
        "status": "completed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()}
    })
    
    return {
        "overview": {
            "total_tasks": tasks,
            "total_assets": assets,
            "total_work_orders": work_orders,
            "total_incidents": incidents,
            "total_projects": projects,
        },
        "recent_activity": {
            "inspections_last_7_days": recent_inspections,
            "checklists_last_7_days": recent_checklists,
        }
    }


@router.get("/safety")
async def get_safety_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Safety dashboard metrics"""
    user = await get_current_user(request, db)
    
    incidents = await db.incidents.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    # Calculate metrics
    total = len(incidents)
    this_month = len([i for i in incidents if i.get("created_at", "")[:7] == datetime.now(timezone.utc).strftime("%Y-%m")])
    injuries = len([i for i in incidents if i.get("incident_type") == "injury"])
    near_misses = len([i for i in incidents if i.get("incident_type") == "near_miss"])
    
    return {
        "total_incidents": total,
        "this_month": this_month,
        "injuries": injuries,
        "near_misses": near_misses,
        "incident_rate": round((total / max(1, total)) * 100, 2)
    }


@router.get("/maintenance")
async def get_maintenance_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Maintenance dashboard metrics"""
    user = await get_current_user(request, db)
    
    work_orders = await db.work_orders.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    backlog = len([w for w in work_orders if w.get("status") in ["pending", "approved", "scheduled"]])
    in_progress = len([w for w in work_orders if w.get("status") == "in_progress"])
    completed = len([w for w in work_orders if w.get("status") == "completed"])
    
    # PM compliance (preventive vs total)
    preventive = len([w for w in work_orders if w.get("work_type") == "preventive"])
    pm_compliance = round((preventive / max(1, len(work_orders))) * 100, 2)
    
    return {
        "work_order_backlog": backlog,
        "in_progress": in_progress,
        "completed": completed,
        "pm_compliance_percentage": pm_compliance
    }
