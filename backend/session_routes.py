from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import get_current_user
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/auth", tags=["Session Management"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/sessions")
async def get_active_sessions(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all active sessions for current user"""
    current_user = await get_current_user(request, db)
    
    # Get current session token from header
    auth_header = request.headers.get("Authorization", "")
    current_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    
    # Find all active sessions for this user
    sessions = await db.sessions.find({
        "user_id": current_user["id"]
    }).sort("created_at", -1).to_list(length=None)
    
    # Format sessions with device/location info (if available)
    formatted_sessions = []
    for session in sessions:
        is_current = session.get("session_token") == current_token
        
        formatted_sessions.append({
            "id": session.get("id"),
            "device": session.get("device", "Unknown Device"),
            "location": session.get("location", "Unknown Location"),
            "ip_address": session.get("ip_address", "Unknown"),
            "last_active": session.get("last_active", session.get("created_at")),
            "created_at": session.get("created_at"),
            "is_current": is_current
        })
    
    return formatted_sessions


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Revoke a specific session"""
    current_user = await get_current_user(request, db)
    
    # Find the session
    session = await db.sessions.find_one({"id": session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to current user
    if session.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot revoke another user's session")
    
    # Delete session
    await db.sessions.delete_one({"id": session_id})
    
    # Log audit event
    await db.audit_logs.insert_one({
        "organization_id": current_user.get("organization_id"),
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        "user_name": current_user["name"],
        "action": "session.revoked",
        "resource_type": "session",
        "resource_id": session_id,
        "result": "success",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Session revoked successfully"}


@router.delete("/sessions/all")
async def revoke_all_sessions(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Revoke all sessions except current one"""
    current_user = await get_current_user(request, db)
    
    # Get current session token
    auth_header = request.headers.get("Authorization", "")
    current_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    
    # Delete all sessions for this user except current
    result = await db.sessions.delete_many({
        "user_id": current_user["id"],
        "session_token": {"$ne": current_token}
    })
    
    # Log audit event
    await db.audit_logs.insert_one({
        "organization_id": current_user.get("organization_id"),
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        "user_name": current_user["name"],
        "action": "sessions.revoked_all",
        "resource_type": "session",
        "resource_id": "all",
        "result": "success",
        "context": {"sessions_revoked": result.deleted_count},
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": f"{result.deleted_count} session(s) revoked successfully",
        "sessions_revoked": result.deleted_count
    }
