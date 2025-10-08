from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from auth_utils import get_current_user
import bcrypt

router = APIRouter(prefix="/users", tags=["users"])


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


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    role: str
    status: str = "active"
    created_at: str
    last_login: Optional[str] = None
    picture: Optional[str] = None
    organization_id: str


class InvitationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    role: str
    status: str
    invited_by: str
    invited_at: str
    expires_at: str


# Get current user profile
@router.get("/me", response_model=UserResponse)
async def get_my_profile(request: Request, current_user=Depends(get_current_user)):
    """Get current user's profile"""
    user = await request.app.state.db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive data
    user.pop("password", None)
    user.pop("_id", None)
    return user


# Update user profile
@router.put("/profile")
async def update_profile(
    request: Request,
    profile: UserProfileUpdate,
    current_user=Depends(get_current_user)
):
    """Update user profile information"""
    update_data = {k: v for k, v in profile.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await request.app.state.db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "Profile updated successfully"}


# Update password
@router.put("/password")
async def update_password(
    request: Request,
    password_data: PasswordUpdate,
    current_user=Depends(get_current_user)
):
    """Update user password"""
    user = await request.app.state.db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not bcrypt.checkpw(password_data.current_password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    hashed_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    await request.app.state.db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "password": hashed_password,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Password updated successfully"}


# Update notification settings
@router.put("/settings")
async def update_settings(
    request: Request,
    settings: NotificationSettings,
    current_user=Depends(get_current_user)
):
    """Update user notification settings"""
    result = await request.app.state.db.users.update_one(
        {"id": current_user["id"]},
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
async def get_settings(request: Request, current_user=Depends(get_current_user)):
    """Get user notification settings"""
    user = await request.app.state.db.users.find_one({"id": current_user["id"]})
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
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload user profile picture"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    content = await file.read()
    
    # Store in GridFS
    from gridfs import GridFS
    import pymongo
    
    mongo_url = request.app.state.db.client.address[0] + ":" + str(request.app.state.db.client.address[1])
    sync_client = pymongo.MongoClient(f"mongodb://{mongo_url}")
    sync_db = sync_client[request.app.state.db.name]
    fs = GridFS(sync_db)
    
    # Delete old profile picture if exists
    user = await request.app.state.db.users.find_one({"id": current_user["id"]})
    if user.get("picture_file_id"):
        try:
            fs.delete(user["picture_file_id"])
        except:
            pass
    
    # Store new picture
    file_id = fs.put(content, filename=file.filename, content_type=file.content_type)
    
    # Update user record
    picture_url = f"/api/users/profile/picture/{str(file_id)}"
    await request.app.state.db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "picture": picture_url,
            "picture_file_id": str(file_id),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Profile picture uploaded successfully", "picture_url": picture_url}


# List all users in organization (admin only)
@router.get("", response_model=List[UserResponse])
async def list_users(request: Request, current_user=Depends(get_current_user)):
    """Get all users in the organization"""
    # Get users from same organization
    users = await request.app.state.db.users.find(
        {"organization_id": current_user["organization_id"]}
    ).to_list(length=None)
    
    # Remove sensitive data and add last_login placeholder
    for user in users:
        user.pop("password", None)
        user.pop("_id", None)
        if "last_login" not in user:
            user["last_login"] = "Recently"
    
    return users


# Invite user to organization
@router.post("/invite")
async def invite_user(
    request: Request,
    invite: UserInvite,
    current_user=Depends(get_current_user)
):
    """Send invitation to join organization"""
    # Check if user already exists
    existing_user = await request.app.state.db.users.find_one({"email": invite.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Check if invitation already sent
    existing_invite = await request.app.state.db.invitations.find_one({
        "email": invite.email,
        "organization_id": current_user["organization_id"],
        "status": "pending"
    })
    if existing_invite:
        raise HTTPException(status_code=400, detail="Invitation already sent to this email")
    
    # Create invitation
    invitation = {
        "id": str(uuid.uuid4()),
        "email": invite.email,
        "role": invite.role,
        "organization_id": current_user["organization_id"],
        "org_unit_id": invite.org_unit_id,
        "invited_by": current_user["id"],
        "invited_by_name": current_user["name"],
        "status": "pending",
        "invited_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat(),  # TODO: Add 7 days expiry
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await request.app.state.db.invitations.insert_one(invitation)
    
    # TODO: Send email invitation
    # For now, just return success
    
    invitation.pop("_id", None)
    return {"message": f"Invitation sent to {invite.email}", "invitation": invitation}


# Get pending invitations
@router.get("/invitations/pending", response_model=List[InvitationResponse])
async def get_pending_invitations(request: Request, current_user=Depends(get_current_user)):
    """Get all pending invitations for the organization"""
    invitations = await request.app.state.db.invitations.find({
        "organization_id": current_user["organization_id"],
        "status": "pending"
    }).to_list(length=None)
    
    for inv in invitations:
        inv.pop("_id", None)
    
    return invitations


# Update user (admin only)
@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: str,
    user_update: UserUpdate,
    current_user=Depends(get_current_user)
):
    """Update user information (admin only)"""
    # Check if user exists in same organization
    target_user = await request.app.state.db.users.find_one({
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
    
    await request.app.state.db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    return {"message": "User updated successfully"}


# Delete user (admin only)
@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    current_user=Depends(get_current_user)
):
    """Delete user from organization (admin only)"""
    # Don't allow deleting self
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Check if user exists in same organization
    target_user = await request.app.state.db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - set status to inactive
    await request.app.state.db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "deleted",
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": current_user["id"]
        }}
    )
    
    return {"message": "User deleted successfully"}
