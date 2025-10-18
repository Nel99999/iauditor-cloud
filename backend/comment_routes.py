from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional

from comment_models import Comment, CommentCreate, CommentUpdate
from auth_utils import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a comment"""
    user = await get_current_user(request, db)
    
    comment = Comment(
        organization_id=user["organization_id"],
        resource_type=comment_data.resource_type,
        resource_id=comment_data.resource_id,
        text=comment_data.text,
        user_id=user["id"],
        user_name=user["name"],
        parent_comment_id=comment_data.parent_comment_id,
        mentions=comment_data.mentions,
    )
    
    comment_dict = comment.model_dump()
    comment_dict["created_at"] = comment_dict["created_at"].isoformat()
    
    await db.comments.insert_one(comment_dict.copy())
    
    # Update parent reply count if threaded
    if comment_data.parent_comment_id:
        await db.comments.update_one(
            {"id": comment_data.parent_comment_id},
            {"$inc": {"reply_count": 1}}
        )
    
    return comment_dict


@router.get("")
async def list_comments(
    request: Request,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    parent_comment_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List comments with filters"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if resource_type:
        query["resource_type"] = resource_type
    if resource_id:
        query["resource_id"] = resource_id
    if parent_comment_id:
        query["parent_comment_id"] = parent_comment_id
    
    comments = await db.comments.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return comments


@router.put("/{comment_id}")
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a comment"""
    user = await get_current_user(request, db)
    
    comment = await db.comments.find_one(
        {"id": comment_id, "organization_id": user["organization_id"]}
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    # Verify user is author
    if comment.get("user_id") != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own comments",
        )
    
    await db.comments.update_one(
        {"id": comment_id},
        {"$set": {
            "text": comment_data.text,
            "is_edited": True,
            "edited_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    updated = await db.comments.find_one({"id": comment_id}, {"_id": 0})
    return updated


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a comment"""
    user = await get_current_user(request, db)
    
    comment = await db.comments.find_one(
        {"id": comment_id, "organization_id": user["organization_id"]}
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    # Verify user is author
    if comment.get("user_id") != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own comments",
        )
    
    await db.comments.delete_one({"id": comment_id})
    
    return {"message": "Comment deleted successfully"}
