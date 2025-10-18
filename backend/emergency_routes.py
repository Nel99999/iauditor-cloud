from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import uuid

from emergency_models import Emergency
from auth_utils import get_current_user

router = APIRouter(prefix="/emergencies", tags=["Emergencies"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("", status_code=status.HTTP_201_CREATED)
async def declare_emergency(
    emergency_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Declare emergency"""
    user = await get_current_user(request, db)
    
    emergency = Emergency(
        emergency_number=f"EMG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        organization_id=user["organization_id"],
        unit_id=emergency_data.get("unit_id"),
        emergency_type=emergency_data.get("emergency_type"),
        severity=emergency_data.get("severity"),
        occurred_at=emergency_data.get("occurred_at"),
        location=emergency_data.get("location"),
        description=emergency_data.get("description"),
        reported_by=user["id"],
        reporter_name=user["name"],
    )
    
    emergency_dict = emergency.model_dump()
    emergency_dict["created_at"] = emergency_dict["created_at"].isoformat()
    
    await db.emergencies.insert_one(emergency_dict.copy())
    return emergency_dict


@router.get("")
async def list_emergencies(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List emergencies"""
    user = await get_current_user(request, db)
    
    emergencies = await db.emergencies.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return emergencies


@router.put("/{emergency_id}/resolve")
async def resolve_emergency(
    emergency_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Resolve emergency"""
    user = await get_current_user(request, db)
    
    await db.emergencies.update_one(
        {"id": emergency_id},
        {"$set": {
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.emergencies.find_one({"id": emergency_id}, {"_id": 0})
