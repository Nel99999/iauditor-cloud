from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime, timezone
from mention_models import Mention, MentionCreate
from auth_utils import get_current_user
import uuid
import re

router = APIRouter(prefix="/mentions", tags=["Mentions"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text (returns user IDs or names)"""
    # Pattern: @username or @[User Name]
    pattern = r'@\[([^\]]+)\]|@(\w+)'
    matches = re.findall(pattern, text)
    
    mentions = []
    for match in matches:
        # match is tuple (bracketed, non-bracketed)
        mention = match[0] if match[0] else match[1]
        mentions.append(mention)
    
    return mentions


async def create_mention_notifications(
    db: AsyncIOMotorDatabase,
    mention_data: dict
):
    """Create notifications for mentioned users"""
    # This will integrate with notifications system
    for user_id in mention_data.get("mentioned_user_ids", []):
        notification = {
            "id": str(uuid.uuid4()),
            "organization_id": mention_data["organization_id"],
            "user_id": user_id,
            "type": "mention",
            "title": f"{mention_data['mentioned_by_name']} mentioned you",
            "message": mention_data["comment_text"][:200],
            "link": f"/{mention_data['resource_type']}/{mention_data['resource_id']}",
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)


# ==================== ENDPOINTS ====================

@router.post("")
async def create_mentions(
    mention_data: MentionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create mentions for users"""
    user = await get_current_user(request, db)
    
    # Get resource details
    resource_map = {
        "task": "tasks",
        "inspection": "inspection_executions",
        "checklist": "checklist_executions"
    }
    
    collection_name = resource_map.get(mention_data.resource_type)
    if not collection_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type"
        )
    
    resource = await db[collection_name].find_one({
        "id": mention_data.resource_id,
        "organization_id": user["organization_id"]
    })
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{mention_data.resource_type.capitalize()} not found"
        )
    
    resource_title = resource.get("title") or resource.get("template_name", "Untitled")
    
    # Create mention for each user
    created_mentions = []
    for mentioned_user_id in mention_data.mentioned_user_ids:
        # Verify user exists
        mentioned_user = await db.users.find_one({
            "id": mentioned_user_id,
            "organization_id": user["organization_id"]
        })
        
        if not mentioned_user:
            continue
        
        mention = Mention(
            organization_id=user["organization_id"],
            mentioned_by_id=user["id"],
            mentioned_by_name=user["name"],
            mentioned_user_id=mentioned_user_id,
            mentioned_user_name=mentioned_user["name"],
            resource_type=mention_data.resource_type,
            resource_id=mention_data.resource_id,
            resource_title=resource_title,
            comment_id=mention_data.comment_id,
            comment_text=mention_data.comment_text[:200]
        )
        
        mention_dict = mention.model_dump()
        mention_dict["created_at"] = mention_dict["created_at"].isoformat()
        
        await db.mentions.insert_one(mention_dict)
        created_mentions.append(mention_dict)
    
    # Create notifications
    await create_mention_notifications(db, {
        "organization_id": user["organization_id"],
        "mentioned_by_name": user["name"],
        "mentioned_user_ids": mention_data.mentioned_user_ids,
        "resource_type": mention_data.resource_type,
        "resource_id": mention_data.resource_id,
        "comment_text": mention_data.comment_text
    })
    
    return {
        "message": f"Created {len(created_mentions)} mentions",
        "mentions": created_mentions
    }


@router.get("/me")
async def get_my_mentions(
    request: Request,
    unread_only: bool = False,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get mentions for current user"""
    user = await get_current_user(request, db)
    
    query = {
        "organization_id": user["organization_id"],
        "mentioned_user_id": user["id"]
    }
    
    if unread_only:
        query["is_read"] = False
    
    mentions = await db.mentions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {
        "mentions": mentions,
        "total": len(mentions),
        "unread_count": len([m for m in mentions if not m.get("is_read")])
    }


@router.put("/{mention_id}/read")
async def mark_mention_read(
    mention_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark mention as read"""
    user = await get_current_user(request, db)
    
    mention = await db.mentions.find_one({
        "id": mention_id,
        "mentioned_user_id": user["id"],
        "organization_id": user["organization_id"]
    })
    
    if not mention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mention not found"
        )
    
    await db.mentions.update_one(
        {"id": mention_id},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "Mention marked as read"}


@router.post("/mark-all-read")
async def mark_all_mentions_read(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark all mentions as read for current user"""
    user = await get_current_user(request, db)
    
    result = await db.mentions.update_many(
        {
            "mentioned_user_id": user["id"],
            "organization_id": user["organization_id"],
            "is_read": False
        },
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": f"Marked {result.modified_count} mentions as read",
        "count": result.modified_count
    }


@router.get("/stats")
async def get_mention_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get mention statistics for current user"""
    user = await get_current_user(request, db)
    
    # Total mentions
    total = await db.mentions.count_documents({
        "mentioned_user_id": user["id"],
        "organization_id": user["organization_id"]
    })
    
    # Unread mentions
    unread = await db.mentions.count_documents({
        "mentioned_user_id": user["id"],
        "organization_id": user["organization_id"],
        "is_read": False
    })
    
    return {
        "total_mentions": total,
        "unread_mentions": unread,
        "read_mentions": total - unread
    }
