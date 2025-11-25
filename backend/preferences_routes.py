from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from .auth_utils import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["preferences"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class ThemePreferences(BaseModel):
    theme: Optional[str] = None
    accent_color: Optional[str] = None
    view_density: Optional[str] = None
    font_size: Optional[str] = None


class RegionalPreferences(BaseModel):
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    currency: Optional[str] = None


class PrivacyPreferences(BaseModel):
    profile_visibility: Optional[str] = None
    show_activity_status: Optional[bool] = None
    show_last_seen: Optional[bool] = None


class SecurityPreferences(BaseModel):
    two_factor_enabled: Optional[bool] = None
    session_timeout: Optional[int] = None


@router.get("/theme")
async def get_theme_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user theme preferences"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    
    return {
        "theme": user.get("theme", "light"),
        "accent_color": user.get("accent_color", "#6366f1"),
        "view_density": user.get("view_density", "comfortable"),
        "font_size": user.get("font_size", "medium")
    }


@router.put("/theme")
async def update_theme_preferences(
    preferences: ThemePreferences,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user theme preferences"""
    current_user = await get_current_user(request, db)
    
    update_data = {}
    if preferences.theme:
        update_data["theme"] = preferences.theme
    if preferences.accent_color:
        update_data["accent_color"] = preferences.accent_color
    if preferences.view_density:
        update_data["view_density"] = preferences.view_density
    if preferences.font_size:
        update_data["font_size"] = preferences.font_size
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    return {"message": "Theme preferences updated successfully"}


@router.get("/regional")
async def get_regional_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user regional preferences"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    
    return {
        "language": user.get("language", "en"),
        "timezone": user.get("timezone", "UTC"),
        "date_format": user.get("date_format", "MM/DD/YYYY"),
        "time_format": user.get("time_format", "12h"),
        "currency": user.get("currency", "USD")
    }


@router.put("/regional")
async def update_regional_preferences(
    preferences: RegionalPreferences,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user regional preferences"""
    current_user = await get_current_user(request, db)
    
    update_data = {}
    if preferences.language:
        update_data["language"] = preferences.language
    if preferences.timezone:
        update_data["timezone"] = preferences.timezone
    if preferences.date_format:
        update_data["date_format"] = preferences.date_format
    if preferences.time_format:
        update_data["time_format"] = preferences.time_format
    if preferences.currency:
        update_data["currency"] = preferences.currency
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    return {"message": "Regional preferences updated successfully"}


@router.get("/privacy")
async def get_privacy_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user privacy preferences"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    
    return {
        "profile_visibility": user.get("profile_visibility", "organization"),
        "show_activity_status": user.get("show_activity_status", True),
        "show_last_seen": user.get("show_last_seen", True)
    }


@router.put("/privacy")
async def update_privacy_preferences(
    preferences: PrivacyPreferences,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user privacy preferences"""
    current_user = await get_current_user(request, db)
    
    update_data = {}
    if preferences.profile_visibility:
        update_data["profile_visibility"] = preferences.profile_visibility
    if preferences.show_activity_status is not None:
        update_data["show_activity_status"] = preferences.show_activity_status
    if preferences.show_last_seen is not None:
        update_data["show_last_seen"] = preferences.show_last_seen
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    return {"message": "Privacy preferences updated successfully"}


@router.get("/security-prefs")
async def get_security_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user security preferences"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    
    return {
        "two_factor_enabled": user.get("two_factor_enabled", False),
        "session_timeout": user.get("session_timeout", 3600)
    }


@router.put("/security-prefs")
async def update_security_preferences(
    preferences: SecurityPreferences,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user security preferences"""
    current_user = await get_current_user(request, db)
    
    update_data = {}
    if preferences.two_factor_enabled is not None:
        update_data["two_factor_enabled"] = preferences.two_factor_enabled
    if preferences.session_timeout:
        update_data["session_timeout"] = preferences.session_timeout
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    return {"message": "Security preferences updated successfully"}
