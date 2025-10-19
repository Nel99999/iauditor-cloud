"""
Announcement Routes
Manages company-wide announcements for all users
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from auth_utils import get_current_user
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/announcements", tags=["Announcements"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"  # low, normal, high, urgent
    target_audience: str = "all"  # all, role, department
    target_roles: Optional[List[str]] = None
    target_departments: Optional[List[str]] = None
    expires_at: Optional[str] = None


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
async def get_announcements(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get announcements list (filtered by user role/department)"""
    user = await get_current_user(request, db)
    
    # Build filter - show all announcements for now (can add role/dept filtering later)
    filter_query = {
        "organization_id": user["organization_id"],
        "is_active": True
    }
    
    announcements = await db.announcements.find(
        filter_query,
        {"_id": 0}
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(length=limit)
    
    return announcements


@router.post("")
async def create_announcement(
    announcement: AnnouncementCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create announcement (Admin+)"""
    user = await get_current_user(request, db)
    
    # Check permission
    user_role = await db.roles.find_one({
        "name": user["role"],
        "organization_id": user["organization_id"]
    })
    
    if not user_role or user_role.get("level", 10) > 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin and above can create announcements"
        )
    
    announcement_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    announcement_doc = {
        "id": announcement_id,
        "organization_id": user["organization_id"],
        "title": announcement.title,
        "content": announcement.content,
        "priority": announcement.priority,
        "target_audience": announcement.target_audience,
        "target_roles": announcement.target_roles or [],
        "target_departments": announcement.target_departments or [],
        "expires_at": announcement.expires_at,
        "created_by": user["id"],
        "created_by_name": user.get("name", user["email"]),
        "created_at": now,
        "updated_at": now,
        "is_active": True,
        "views": 0,
        "acknowledgedments": []
    }
    
    await db.announcements.insert_one(announcement_doc)
    
    logger.info(f"Announcement created: {announcement_id} by {user['email']}")
    
    return {"message": "Announcement created successfully", "id": announcement_id}


@router.get("/{announcement_id}")
async def get_announcement(
    announcement_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get announcement detail"""
    user = await get_current_user(request, db)
    
    announcement = await db.announcements.find_one(
        {
            "id": announcement_id,
            "organization_id": user["organization_id"]
        },
        {"_id": 0}
    )
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Increment view count
    await db.announcements.update_one(
        {"id": announcement_id},
        {"$inc": {"views": 1}}
    )
    
    return announcement


@router.put("/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    update_data: AnnouncementUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update announcement (Admin+)"""
    user = await get_current_user(request, db)
    
    # Check permission
    user_role = await db.roles.find_one({
        "name": user["role"],
        "organization_id": user["organization_id"]
    })
    
    if not user_role or user_role.get("level", 10) > 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin and above can update announcements"
        )
    
    # Build update dict
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.announcements.update_one(
        {
            "id": announcement_id,
            "organization_id": user["organization_id"]
        },
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    return {"message": "Announcement updated successfully"}


@router.delete("/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete announcement (Admin+)"""
    user = await get_current_user(request, db)
    
    # Check permission
    user_role = await db.roles.find_one({
        "name": user["role"],
        "organization_id": user["organization_id"]
    })
    
    if not user_role or user_role.get("level", 10) > 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin and above can delete announcements"
        )
    
    result = await db.announcements.delete_one(
        {
            "id": announcement_id,
            "organization_id": user["organization_id"]
        }
    )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    return {"message": "Announcement deleted successfully"}


@router.post("/{announcement_id}/acknowledge")
async def acknowledge_announcement(
    announcement_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Acknowledge announcement (mark as read)"""
    user = await get_current_user(request, db)
    
    await db.announcements.update_one(
        {"id": announcement_id},
        {
            "$addToSet": {
                "acknowledgedments": {
                    "user_id": user["id"],
                    "user_name": user.get("name", user["email"]),
                    "acknowledged_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    
    return {"message": "Announcement acknowledged"}
