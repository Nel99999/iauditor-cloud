from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from permission_models import (
    UserInvitation, UserInvitationCreate, UserInvitationAccept
)
from auth_utils import get_current_user
from email_service import EmailService
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
import secrets
import os

router = APIRouter(prefix="/invitations", tags=["invitations"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def generate_invitation_token() -> str:
    """Generate secure invitation token"""
    return secrets.token_urlsafe(32)


# =====================================
# INVITATION MANAGEMENT
# =====================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation: UserInvitationCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send user invitation - Requires user.invite.organization permission"""
    current_user = await get_current_user(request, db)
    
    # Check if user has permission to invite
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        current_user["id"],
        "user",
        "invite",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite users"
        )
    
    # Validate role hierarchy - can only invite equal or lower level roles
    # Get the role being invited
    invited_role = await db.roles.find_one({"id": invitation.role_id})
    if not invited_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id"
        )
    
    # Get current user's role
    current_user_role_code = current_user.get("role")
    if current_user_role_code:
        # Resolve to role object
        current_role = await db.roles.find_one({
            "code": current_user_role_code,
            "organization_id": current_user["organization_id"]
        })
        
        if current_role and invited_role:
            current_level = current_role.get("level", 999)
            invited_level = invited_role.get("level", 999)
            
            # Can only invite equal or lower level (higher number = lower level)
            if current_level > invited_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You can only invite users with equal or lower role levels. Your level: {current_level}, Invited level: {invited_level}"
                )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": invitation.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if invitation already pending
    existing_invite = await db.invitations.find_one({
        "email": invitation.email,
        "organization_id": current_user["organization_id"],
        "status": "pending"
    })
    
    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already sent to this email"
        )
    
    # Create invitation with 7-day expiry
    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    
    invite = UserInvitation(
        email=invitation.email,
        token=generate_invitation_token(),
        invited_by=current_user["id"],
        invited_by_name=current_user.get("name", "Unknown"),
        organization_id=current_user["organization_id"],
        role_id=invitation.role_id,
        scope_type=invitation.scope_type,
        scope_id=invitation.scope_id,
        function_overrides=invitation.function_overrides,
        expires_at=expires_at
    )
    
    await db.invitations.insert_one(invite.dict())
    
    # Send email with invitation link
    try:
        # Get SendGrid API key from organization settings
        org_settings = await db.organization_settings.find_one({
            "organization_id": current_user["organization_id"]
        })
        sendgrid_key = org_settings.get("sendgrid_api_key") if org_settings else None
        
        if sendgrid_key:
            email_service = EmailService(sendgrid_key)
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            
            # Get organization name
            org = await db.organizations.find_one({"id": current_user["organization_id"]})
            org_name = org.get("name") if org else "Your Organization"
            
            email_sent = email_service.send_invitation_email(
                to_email=invitation.email,
                inviter_name=current_user.get("name", "A team member"),
                organization_name=org_name,
                invitation_token=invite.token,
                frontend_url=frontend_url
            )
            
            if email_sent:
                print(f"✅ Invitation email sent to {invitation.email}")
        else:
            print(f"⚠️ SendGrid not configured. Email not sent to {invitation.email}")
    except Exception as e:
        print(f"❌ Failed to send invitation email: {str(e)}")
    
    invite_dict = invite.dict()
    invite_dict.pop("_id", None)
    
    return {
        "message": f"Invitation sent to {invitation.email}",
        "invitation": invite_dict
    }


@router.get("/pending")
async def get_pending_invitations(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all pending invitations for the organization"""
    current_user = await get_current_user(request, db)
    
    invitations = await db.invitations.find({
        "organization_id": current_user["organization_id"],
        "status": "pending"
    }, {"_id": 0}).to_list(length=None)
    
    # Invitations already have role as string, no need to populate from roles collection
    # Just return the invitations as is
    return invitations


@router.get("/token/{token}")
async def validate_invitation_token(
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Validate invitation token"""
    invitation = await db.invitations.find_one({"token": token}, {"_id": 0})
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )
    
    # Check if expired
    expires_at = datetime.fromisoformat(invitation["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        # Mark as expired
        await db.invitations.update_one(
            {"token": token},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Check if already accepted
    if invitation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation already {invitation['status']}"
        )
    
    # Get role details
    role = await db.roles.find_one({"id": invitation["role_id"]}, {"_id": 0})
    if role:
        invitation["role"] = role
    
    return invitation


@router.post("/accept")
async def accept_invitation(
    acceptance: UserInvitationAccept,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Accept invitation and create user account"""
    import bcrypt
    
    # Validate token
    invitation = await db.invitations.find_one({"token": acceptance.token})
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )
    
    if invitation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation already {invitation['status']}"
        )
    
    # Check expiry
    expires_at = datetime.fromisoformat(invitation["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        await db.invitations.update_one(
            {"token": acceptance.token},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Create user account
    hashed_password = bcrypt.hashpw(acceptance.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Get role details to store role code instead of ID
    role = await db.roles.find_one({"id": invitation["role_id"]})
    role_code = role["code"] if role else invitation["role_id"]
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": invitation["email"],
        "name": acceptance.name,
        "password_hash": hashed_password,
        "organization_id": invitation["organization_id"],
        "role": role_code,  # Store role CODE, not UUID
        "is_active": True,
        "approval_status": "approved",  # Invited users are pre-approved
        "invited": True,  # Mark as invited
        "approved_by": invitation["invited_by"],  # The person who invited
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approval_notes": "Pre-approved via invitation",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_login": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Update invitation status
    await db.invitations.update_one(
        {"token": acceptance.token},
        {"$set": {
            "status": "accepted",
            "accepted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Create JWT token for immediate login
    from auth_utils import create_access_token
    access_token = create_access_token(data={"sub": user_dict["id"]})
    
    user_dict.pop("password_hash", None)
    user_dict.pop("_id", None)
    
    return {
        "message": "Invitation accepted successfully",
        "access_token": access_token,
        "user": user_dict
    }


@router.post("/{invitation_id}/resend")
async def resend_invitation(
    invitation_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Resend invitation email - Requires invitation.resend.organization permission"""
    current_user = await get_current_user(request, db)
    
    # Check permission
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        current_user["id"],
        "invitation",
        "resend",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to resend invitations"
        )
    
    invitation = await db.invitations.find_one({
        "id": invitation_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resend {invitation['status']} invitation"
        )
    
    # Extend expiry by 7 days
    new_expiry = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    
    await db.invitations.update_one(
        {"id": invitation_id},
        {"$set": {"expires_at": new_expiry}}
    )
    
    # Resend email
    try:
        org_settings = await db.organization_settings.find_one({
            "organization_id": current_user["organization_id"]
        })
        sendgrid_key = org_settings.get("sendgrid_api_key") if org_settings else None
        
        if sendgrid_key:
            email_service = EmailService(sendgrid_key)
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            
            org = await db.organizations.find_one({"id": current_user["organization_id"]})
            org_name = org.get("name") if org else "Your Organization"
            
            email_sent = email_service.send_invitation_email(
                to_email=invitation["email"],
                inviter_name=current_user.get("name", "A team member"),
                organization_name=org_name,
                invitation_token=invitation["token"],
                frontend_url=frontend_url
            )
            
            if email_sent:
                print(f"✅ Invitation resent to {invitation['email']}")
    except Exception as e:
        print(f"❌ Failed to resend invitation email: {str(e)}")
    
    # TODO: Resend email
    
    return {"message": "Invitation resent successfully"}


@router.delete("/{invitation_id}")
async def cancel_invitation(
    invitation_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Cancel pending invitation"""
    current_user = await get_current_user(request, db)
    
    result = await db.invitations.update_one(
        {
            "id": invitation_id,
            "organization_id": current_user["organization_id"],
            "status": "pending"
        },
        {"$set": {"status": "cancelled"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already processed"
        )
    
    return {"message": "Invitation cancelled successfully"}


@router.get("")
async def list_all_invitations(
    status_filter: Optional[str] = None,
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all invitations with optional status filter"""
    current_user = await get_current_user(request, db)
    
    query = {"organization_id": current_user["organization_id"]}
    if status_filter:
        query["status"] = status_filter
    
    invitations = await db.invitations.find(query, {"_id": 0}).to_list(length=None)
    
    return invitations
