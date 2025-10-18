from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional
import uuid

from incident_models import Incident, IncidentCreate, IncidentStats
from auth_utils import get_current_user

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def generate_incident_number() -> str:
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
    random = str(uuid.uuid4())[:6].upper()
    return f"INC-{timestamp}-{random}"


@router.post("", status_code=status.HTTP_201_CREATED)
async def report_incident(
    incident_data: IncidentCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Report new incident"""
    user = await get_current_user(request, db)
    
    incident = Incident(
        incident_number=generate_incident_number(),
        organization_id=user["organization_id"],
        unit_id=incident_data.unit_id,
        incident_type=incident_data.incident_type,
        severity=incident_data.severity,
        occurred_at=incident_data.occurred_at,
        location=incident_data.location,
        description=incident_data.description,
        reported_by=user["id"],
        reporter_name=user["name"],
    )
    
    incident_dict = incident.model_dump()
    incident_dict["created_at"] = incident_dict["created_at"].isoformat()
    incident_dict["updated_at"] = incident_dict["updated_at"].isoformat()
    
    await db.incidents.insert_one(incident_dict.copy())
    return incident_dict


@router.get("/stats")
async def get_incident_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get incident statistics"""
    user = await get_current_user(request, db)
    
    incidents = await db.incidents.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    by_type = {}
    by_severity = {}
    for inc in incidents:
        t = inc.get("incident_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        s = inc.get("severity", "unknown")
        by_severity[s] = by_severity.get(s, 0) + 1
    
    month_start = datetime.now(timezone.utc).replace(day=1).isoformat()
    this_month = len([i for i in incidents if i.get("created_at") >= month_start])
    
    stats = IncidentStats(
        total_incidents=len(incidents),
        by_type=by_type,
        by_severity=by_severity,
        this_month=this_month
    )
    
    return stats.model_dump()


@router.get("")
async def list_incidents(
    request: Request,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List incidents"""
    user = await get_current_user(request, db)
    
    incidents = await db.incidents.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return incidents


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get incident"""
    user = await get_current_user(request, db)
    
    incident = await db.incidents.find_one(
        {"id": incident_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    
    return incident


@router.post("/{incident_id}/corrective-action")
async def create_corrective_action(
    incident_id: str,
    action_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create corrective action task"""
    user = await get_current_user(request, db)
    
    incident = await db.incidents.find_one({"id": incident_id})
    
    task = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "title": f"CAPA: {incident.get('incident_number')}",
        "description": action_data.get("description"),
        "task_type": "corrective_action",
        "linked_incident_id": incident_id,
        "priority": "high",
        "status": "todo",
        "created_by": user["id"],
        "created_by_name": user["name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tasks.insert_one(task.copy())
    await db.incidents.update_one({"id": incident_id}, {"$push": {"corrective_action_task_ids": task["id"]}})
    
    return task

