from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional, List
import uuid

from .emergency_models import Emergency
from .auth_utils import get_current_user

router = APIRouter(prefix="/emergencies", tags=["Emergencies"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class EmergencyCreate(BaseModel):
    """Create emergency"""
    emergency_type: str
    severity: str = "medium"
    location: Optional[str] = None
    description: str
    unit_id: Optional[str] = None
    occurred_at: Optional[str] = None
    affected_areas: List[str] = []


@router.post("", status_code=status.HTTP_201_CREATED)
async def declare_emergency(
    emergency_data: EmergencyCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Declare emergency"""
    user = await get_current_user(request, db)
    
    # Use current time if occurred_at not provided
    occurred_at = emergency_data.occurred_at or datetime.now(timezone.utc).isoformat()
    
    emergency = Emergency(
        emergency_number=f"EMG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        organization_id=user["organization_id"],
        unit_id=emergency_data.unit_id,
        emergency_type=emergency_data.emergency_type,
        severity=emergency_data.severity,
        occurred_at=occurred_at,
        location=emergency_data.location,
        description=emergency_data.description,
        reported_by=user["id"],
        reporter_name=user.get("name", user["email"]),
        affected_areas=emergency_data.affected_areas,
    )
    
    emergency_dict = emergency.model_dump()
    emergency_dict["created_at"] = emergency_dict["created_at"].isoformat()
    
    await db.emergencies.insert_one(emergency_dict.copy())
    return emergency_dict


@router.get("")
async def list_emergencies(
    request: Request,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List emergencies"""
    user = await get_current_user(request, db)
    
    emergencies = await db.emergencies.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return emergencies


@router.get("/{emergency_id}")
async def get_emergency(
    emergency_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get emergency detail"""
    user = await get_current_user(request, db)
    
    emergency = await db.emergencies.find_one(
        {"id": emergency_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not emergency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency not found"
        )
    
    return emergency


@router.put("/{emergency_id}/resolve")
async def resolve_emergency(
    emergency_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Resolve emergency"""
    user = await get_current_user(request, db)
    
    result = await db.emergencies.update_one(
        {"id": emergency_id, "organization_id": user["organization_id"]},
        {"$set": {
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency not found"
        )
    
    return await db.emergencies.find_one({"id": emergency_id}, {"_id": 0})


@router.put("/{emergency_id}/activate")
async def activate_emergency(
    emergency_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Activate emergency response"""
    user = await get_current_user(request, db)
    
    await db.emergencies.update_one(
        {"id": emergency_id},
        {"$set": {
            "status": "active",
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.emergencies.find_one({"id": emergency_id}, {"_id": 0})
