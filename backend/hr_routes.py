from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import uuid

from hr_models import Employee, Announcement
from auth_utils import get_current_user

router = APIRouter(prefix="/hr", tags=["HR"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("/employees", status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create employee profile"""
    user = await get_current_user(request, db)
    
    employee = Employee(
        user_id=employee_data.get("user_id"),
        organization_id=user["organization_id"],
        unit_id=employee_data.get("unit_id"),
        employee_number=employee_data.get("employee_number"),
        first_name=employee_data.get("first_name"),
        last_name=employee_data.get("last_name"),
        email=employee_data.get("email"),
        position=employee_data.get("position"),
        department=employee_data.get("department"),
        hire_date=employee_data.get("hire_date"),
    )
    
    employee_dict = employee.model_dump()
    employee_dict["created_at"] = employee_dict["created_at"].isoformat()
    
    await db.employees.insert_one(employee_dict.copy())
    return employee_dict


@router.get("/employees")
async def list_employees(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List employees"""
    user = await get_current_user(request, db)
    
    employees = await db.employees.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    return employees


@router.post("/announcements", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create announcement"""
    user = await get_current_user(request, db)
    
    announcement = Announcement(
        organization_id=user["organization_id"],
        title=announcement_data.get("title"),
        content=announcement_data.get("content"),
        priority=announcement_data.get("priority", "normal"),
        target_audience=announcement_data.get("target_audience", "all"),
        unit_ids=announcement_data.get("unit_ids", []),
        created_by=user["id"],
    )
    
    announcement_dict = announcement.model_dump()
    announcement_dict["created_at"] = announcement_dict["created_at"].isoformat()
    
    await db.announcements.insert_one(announcement_dict.copy())
    return announcement_dict


@router.get("/announcements")
async def list_announcements(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List announcements"""
    user = await get_current_user(request, db)
    
    announcements = await db.announcements.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return announcements


@router.post("/announcements/{announcement_id}/publish")
async def publish_announcement(
    announcement_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Publish announcement"""
    user = await get_current_user(request, db)
    
    await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": {
            "published": True,
            "published_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.announcements.find_one({"id": announcement_id}, {"_id": 0})
