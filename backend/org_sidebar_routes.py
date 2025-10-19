"""
Organization Sidebar Settings Routes
Master/Developer only: Set organization-wide sidebar defaults
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from auth_utils import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organization/sidebar-settings", tags=["Organization Sidebar Settings"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class OrganizationSidebarSettings(BaseModel):
    default_mode: str = "collapsed"  # expanded, collapsed, mini
    hover_expand_enabled: bool = False  # Desktop only: expand on hover
    auto_collapse_enabled: bool = False  # Auto-collapse after inactivity
    inactivity_timeout: int = 10  # Seconds before auto-collapse
    context_aware_enabled: bool = False  # Adjust based on screen size and route
    collapse_after_navigation: bool = False  # Auto-collapse after clicking menu item


@router.get("")
async def get_organization_sidebar_settings(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get organization-wide sidebar settings"""
    user = await get_current_user(request, db)
    
    # Get organization settings
    org_settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]},
        {"_id": 0, "sidebar_settings": 1}
    )
    
    if not org_settings or "sidebar_settings" not in org_settings:
        # Return system defaults
        return {
            "default_mode": "collapsed",
            "hover_expand_enabled": False,
            "auto_collapse_enabled": False,
            "inactivity_timeout": 10,
            "context_aware_enabled": False,
            "collapse_after_navigation": False
        }
    
    return org_settings.get("sidebar_settings", {})


@router.put("")
async def update_organization_sidebar_settings(
    settings: OrganizationSidebarSettings,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update organization-wide sidebar settings (Master & Developer only)"""
    user = await get_current_user(request, db)
    
    # RBAC: Only Master and Developer can update organization settings
    user_role = await db.roles.find_one({"name": user["role"], "organization_id": user["organization_id"]})
    
    if not user_role or user_role.get("level", 10) > 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can update organization sidebar settings"
        )
    
    # Validate timeout value
    if settings.inactivity_timeout < 5 or settings.inactivity_timeout > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactivity timeout must be between 5 and 60 seconds"
        )
    
    # Validate mode
    valid_modes = ["expanded", "collapsed", "mini"]
    if settings.default_mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    # Update organization settings
    await db.organization_settings.update_one(
        {"organization_id": user["organization_id"]},
        {
            "$set": {
                "sidebar_settings": settings.dict()
            }
        },
        upsert=True
    )
    
    logger.info(f"✅ Organization sidebar settings updated by {user['email']} (role: {user['role']})")
    
    return {
        "message": "Organization sidebar settings updated successfully",
        "settings": settings.dict()
    }
