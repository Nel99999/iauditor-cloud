"""
Sidebar Preferences Routes
Manages user sidebar preferences (mode, hover behavior, auto-collapse settings)
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional
from auth_utils import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/sidebar-preferences", tags=["Sidebar Preferences"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class SidebarPreferences(BaseModel):
    default_mode: str = "expanded"  # expanded, collapsed, mini
    hover_expand_enabled: bool = True  # Desktop only: expand on hover
    auto_collapse_enabled: bool = False  # Auto-collapse after inactivity
    inactivity_timeout: int = 10  # Seconds before auto-collapse
    context_aware_enabled: bool = True  # Adjust based on screen size and route
    collapse_after_navigation: bool = False  # Auto-collapse after clicking menu item


@router.get("")
async def get_sidebar_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's sidebar preferences"""
    user = await get_current_user(request, db)
    
    # Get preferences from user_preferences collection
    prefs = await db.user_preferences.find_one(
        {"user_id": user["id"]},
        {"_id": 0}
    )
    
    if not prefs or "sidebar_preferences" not in prefs:
        # Return defaults
        return {
            "default_mode": "expanded",
            "hover_expand_enabled": True,
            "auto_collapse_enabled": False,
            "inactivity_timeout": 10,
            "context_aware_enabled": True,
            "collapse_after_navigation": False
        }
    
    return prefs.get("sidebar_preferences", {})


@router.put("")
async def update_sidebar_preferences(
    preferences: SidebarPreferences,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user's sidebar preferences"""
    try:
        logger.info(f"🔍 PUT sidebar preferences called with data: {preferences.dict()}")
        user = await get_current_user(request, db)
        logger.info(f"🔍 User retrieved successfully: {user['id']}")
    except Exception as e:
        logger.error(f"❌ Error in get_current_user: {str(e)}")
        raise
    
    # Validate timeout value
    if preferences.inactivity_timeout < 5 or preferences.inactivity_timeout > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactivity timeout must be between 5 and 60 seconds"
        )
    
    # Validate mode
    valid_modes = ["expanded", "collapsed", "mini"]
    if preferences.default_mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    # Update preferences in database
    await db.user_preferences.update_one(
        {"user_id": user["id"]},
        {
            "$set": {
                "user_id": user["id"],
                "organization_id": user["organization_id"],
                "sidebar_preferences": preferences.dict()
            }
        },
        upsert=True
    )
    
    logger.info(f"✅ Sidebar preferences updated for user {user['id']}")
    
    return {"message": "Sidebar preferences updated successfully", "preferences": preferences.dict()}
