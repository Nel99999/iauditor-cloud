from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from .auth_utils import get_current_user
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# Notification types
NOTIFICATION_TYPES = [
    "mention",           # User mentioned you
    "assignment",        # Task/inspection assigned to you
    "comment",           # New comment on your item
    "approval_request",  # Workflow approval needed
    "approval_decision", # Your approval was approved/rejected
    "due_soon",          # Task/inspection due soon
    "overdue",           # Task/inspection overdue
    "status_change",     # Status changed on watched item
    "group_added",       # Added to group
    "system"             # System notifications
]


# ==================== HELPER FUNCTIONS ====================

async def create_notification(
    db: AsyncIOMotorDatabase,
    user_id: str,
    organization_id: str,
    notification_type: str,
    title: str,
    message: str,
    link: Optional[str] = None,
    metadata: dict = None
):
    """Helper to create notification"""
    notification = {
        "id": str(uuid.uuid4()),
        "organization_id": organization_id,
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "link": link,
        "metadata": metadata or {},
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = notification.copy()
    await db.notifications.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return notification


# ==================== ENDPOINTS ====================

@router.get("")
async def get_notifications(
    request: Request,
    unread_only: bool = False,
    type_filter: Optional[str] = None,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get notifications for current user"""
    user = await get_current_user(request, db)
    
    query = {
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    }
    
    if unread_only:
        query["is_read"] = False
    
    if type_filter and type_filter in NOTIFICATION_TYPES:
        query["type"] = type_filter
    
    notifications = await db.notifications.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {
        "notifications": notifications,
        "total": len(notifications),
        "unread_count": len([n for n in notifications if not n.get("is_read")])
    }


@router.get("/stats")
async def get_notification_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get notification statistics"""
    user = await get_current_user(request, db)
    
    # Total notifications
    total = await db.notifications.count_documents({
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    })
    
    # Unread notifications
    unread = await db.notifications.count_documents({
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "is_read": False
    })
    
    # By type
    by_type = {}
    for notif_type in NOTIFICATION_TYPES:
        count = await db.notifications.count_documents({
            "user_id": user["id"],
            "organization_id": user["organization_id"],
            "type": notif_type
        })
        if count > 0:
            by_type[notif_type] = count
    
    return {
        "total_notifications": total,
        "unread_notifications": unread,
        "read_notifications": total - unread,
        "by_type": by_type
    }


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark notification as read"""
    user = await get_current_user(request, db)
    
    notification = await db.notifications.find_one({
        "id": notification_id,
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    })
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    
    return {"message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    request: Request,
    notification_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark all notifications as read"""
    user = await get_current_user(request, db)
    
    query = {
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "is_read": False
    }
    
    if notification_type and notification_type in NOTIFICATION_TYPES:
        query["type"] = notification_type
    
    result = await db.notifications.update_many(
        query,
        {"$set": {"is_read": True}}
    )
    
    return {
        "message": f"Marked {result.modified_count} notifications as read",
        "count": result.modified_count
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete notification"""
    user = await get_current_user(request, db)
    
    notification = await db.notifications.find_one({
        "id": notification_id,
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    })
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.notifications.delete_one({"id": notification_id})
    
    return {"message": "Notification deleted"}


@router.delete("/clear-all")
async def clear_all_notifications(
    request: Request,
    read_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Clear all notifications (read only by default)"""
    user = await get_current_user(request, db)
    
    query = {
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    }
    
    if read_only:
        query["is_read"] = True
    
    result = await db.notifications.delete_many(query)
    
    return {
        "message": f"Cleared {result.deleted_count} notifications",
        "count": result.deleted_count
    }


@router.get("/preferences")
async def get_notification_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get notification preferences for user"""
    user = await get_current_user(request, db)
    
    prefs = await db.notification_preferences.find_one({
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    if not prefs:
        # Return defaults
        prefs = {
            "user_id": user["id"],
            "organization_id": user["organization_id"],
            "email_notifications": True,
            "push_notifications": True,
            "notification_types": {
                notif_type: True for notif_type in NOTIFICATION_TYPES
            }
        }
    
    return prefs


@router.put("/preferences")
async def update_notification_preferences(
    preferences: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update notification preferences"""
    user = await get_current_user(request, db)
    
    prefs_data = {
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "email_notifications": preferences.get("email_notifications", True),
        "push_notifications": preferences.get("push_notifications", True),
        "notification_types": preferences.get("notification_types", {}),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notification_preferences.update_one(
        {
            "user_id": user["id"],
            "organization_id": user["organization_id"]
        },
        {"$set": prefs_data},
        upsert=True
    )
    
    return {"message": "Notification preferences updated"}
