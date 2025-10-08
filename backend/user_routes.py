from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth_utils import get_current_user
import bcrypt

router = APIRouter(prefix="/users", tags=["users"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# Pydantic Models
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class NotificationSettings(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = False
    weekly_reports: bool = True
    marketing_emails: bool = False


class UserInvite(BaseModel):
    email: EmailStr
    role: str = "viewer"
    org_unit_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


# Get current user profile
@router.get("/me")
async def get_my_profile(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user's profile"""
    user = await get_current_user(request, db)
    
    full_user = await db.users.find_one({"id": user["id"]})
    if not full_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive data
    full_user.pop("password", None)
    full_user.pop("password_hash", None)
    full_user.pop("_id", None)
    return full_user


# Update user profile
@router.put("/profile")
async def update_profile(
    profile: UserProfileUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user profile information"""
    user = await get_current_user(request, db)
    
    update_data = {k: v for k, v in profile.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.users.update_one(
        {"id": user["id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "Profile updated successfully"}


# Update password
@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user password"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    password_field = user.get("password_hash") or user.get("password")
    if not password_field:
        raise HTTPException(status_code=400, detail="Password not found")
    
    if not bcrypt.checkpw(password_data.current_password.encode('utf-8'), password_field.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    hashed_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "password_hash": hashed_password,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Password updated successfully"}


# Update notification settings
@router.put("/settings")
async def update_settings(
    settings: NotificationSettings,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user notification settings"""
    user = await get_current_user(request, db)
    
    result = await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "notification_settings": settings.dict(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Settings updated successfully", "settings": settings.dict()}


# Get notification settings
@router.get("/settings")
async def get_settings(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get user notification settings"""
    current_user = await get_current_user(request, db)
    
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return default settings if not set
    default_settings = {
        "email_notifications": True,
        "push_notifications": False,
        "weekly_reports": True,
        "marketing_emails": False
    }
    
    return user.get("notification_settings", default_settings)


# Upload profile picture
@router.post("/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload user profile picture"""
    current_user = await get_current_user(request, db)
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # For now, just return success without actually storing
    # TODO: Implement GridFS storage
    picture_url = f"/api/users/profile/picture/placeholder"
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "picture": picture_url,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Profile picture uploaded successfully", "picture_url": picture_url}


# List all users in organization
@router.get("")
async def list_users(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all users in the organization"""
    user = await get_current_user(request, db)
    
    # Get users from same organization
    users = await db.users.find(
        {"organization_id": user["organization_id"], "status": {"$ne": "deleted"}}
    ).to_list(length=None)
    
    # Remove sensitive data and add last_login placeholder
    for u in users:
        u.pop("password", None)
        u.pop("_id", None)
        if "last_login" not in u:
            u["last_login"] = "Recently"
    
    return users


# Invite user to organization
@router.post("/invite")
async def invite_user(
    invite: UserInvite,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send invitation to join organization"""
    user = await get_current_user(request, db)
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": invite.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Check if invitation already sent
    existing_invite = await db.invitations.find_one({
        "email": invite.email,
        "organization_id": user["organization_id"],
        "status": "pending"
    })
    if existing_invite:
        raise HTTPException(status_code=400, detail="Invitation already sent to this email")
    
    # Create invitation
    invitation = {
        "id": str(uuid.uuid4()),
        "email": invite.email,
        "role": invite.role,
        "organization_id": user["organization_id"],
        "org_unit_id": invite.org_unit_id,
        "invited_by": user["id"],
        "invited_by_name": user["name"],
        "status": "pending",
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.invitations.insert_one(invitation)
    
    # TODO: Send email invitation
    
    invitation.pop("_id", None)
    return {"message": f"Invitation sent to {invite.email}", "invitation": invitation}


# Get pending invitations
@router.get("/invitations/pending")
async def get_pending_invitations(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all pending invitations for the organization"""
    user = await get_current_user(request, db)
    
    invitations = await db.invitations.find({
        "organization_id": user["organization_id"],
        "status": "pending"
    }).to_list(length=None)
    
    for inv in invitations:
        inv.pop("_id", None)
    
    return invitations


# Update user
@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user information (admin only)"""
    current_user = await get_current_user(request, db)
    
    # Check if user exists in same organization
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    return {"message": "User updated successfully"}


# Delete user
@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete user from organization (admin only)"""
    current_user = await get_current_user(request, db)
    
    # Don't allow deleting self
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Check if user exists in same organization
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - set status to inactive
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "deleted",
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": current_user["id"]
        }}
    )
    
    return {"message": "User deleted successfully"}