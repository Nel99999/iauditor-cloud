from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from permission_models import (
    UserInvitation, UserInvitationCreate, UserInvitationAccept
)
from auth_utils import get_current_user
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
import secrets

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
    """Send user invitation"""
    current_user = await get_current_user(request, db)
    
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
    
    # TODO: Send email with invitation link
    # invitation_link = f"{FRONTEND_URL}/accept-invitation?token={invite.token}"
    # send_invitation_email(invitation.email, invitation_link, current_user["name"])
    
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
    
    # Populate role details
    for invite in invitations:
        role = await db.roles.find_one({"id": invite["role_id"]}, {"_id": 0})
        if role:
            invite["role"] = role
    
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
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": invitation["email"],
        "name": acceptance.name,
        "password": hashed_password,
        "organization_id": invitation["organization_id"],
        "role": invitation["role_id"],
        "status": "active",
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
    
    user_dict.pop("password")
    user_dict.pop("_id")
    
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
    """Resend invitation email"""
    current_user = await get_current_user(request, db)
    
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
