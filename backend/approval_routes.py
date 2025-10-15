"""
User Approval System Routes
Handles approval and rejection of pending user registrations
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timezone
from auth_utils import get_current_user
from typing import Optional

router = APIRouter(prefix="/users", tags=["user-approval"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


class ApprovalAction(BaseModel):
    """Model for approval/rejection action"""
    approval_notes: Optional[str] = None


# =====================================
# PENDING APPROVALS
# =====================================

@router.get("/pending-approvals")
async def get_pending_approvals(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get all pending user registrations
    Requires: user.approve.organization permission
    """
    current_user = await get_current_user(request, db)
    
    # Check permission
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        current_user["id"],
        "user",
        "approve",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view pending user approvals"
        )
    
    # Get pending users from same organization
    pending_users = await db.users.find({
        "organization_id": current_user["organization_id"],
        "approval_status": "pending",
        "invited": False  # Only show self-registrations, not pending invitations
    }, {"_id": 0, "password_hash": 0}).to_list(length=None)
    
    return pending_users


# =====================================
# APPROVE USER
# =====================================

@router.post("/{user_id}/approve")
async def approve_user(
    user_id: str,
    action: ApprovalAction,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Approve a pending user registration
    Requires: user.approve.organization permission
    """
    current_user = await get_current_user(request, db)
    
    # Check permission
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        current_user["id"],
        "user",
        "approve",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve user registrations"
        )
    
    # Find the user
    user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not in your organization"
        )
    
    # Check if user is pending
    if user.get("approval_status") != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not pending approval (current status: {user.get('approval_status')})"
        )
    
    # Approve user
    now = datetime.now(timezone.utc).isoformat()
    approval_notes = action.approval_notes or f"Approved by {current_user.get('name', 'admin')}"
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "approval_status": "approved",
            "is_active": True,
            "approved_by": current_user["id"],
            "approved_at": now,
            "approval_notes": approval_notes,
            "updated_at": now
        }}
    )
    
    # Log in audit trail
    await db.audit_logs.insert_one({
        "id": str(__import__('uuid').uuid4()),
        "action": "user_approved",
        "actor_id": current_user["id"],
        "actor_email": current_user["email"],
        "actor_name": current_user.get("name", "Unknown"),
        "target_id": user_id,
        "target_email": user["email"],
        "organization_id": current_user["organization_id"],
        "details": {
            "approval_notes": approval_notes,
            "approved_user": user["email"]
        },
        "timestamp": now,
        "ip_address": None
    })
    
    # TODO: Send approval email to user
    
    return {
        "message": f"User {user['email']} has been approved",
        "user_id": user_id,
        "approved_by": current_user["email"],
        "approved_at": now
    }


# =====================================
# REJECT USER
# =====================================

@router.post("/{user_id}/reject")
async def reject_user(
    user_id: str,
    action: ApprovalAction,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Reject a pending user registration
    Requires: user.reject.organization permission
    """
    current_user = await get_current_user(request, db)
    
    # Check permission
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        current_user["id"],
        "user",
        "reject",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reject user registrations"
        )
    
    # Find the user
    user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not in your organization"
        )
    
    # Check if user is pending
    if user.get("approval_status") != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is not pending approval (current status: {user.get('approval_status')})"
        )
    
    # Reject user
    now = datetime.now(timezone.utc).isoformat()
    rejection_notes = action.approval_notes or f"Rejected by {current_user.get('name', 'admin')}"
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "approval_status": "rejected",
            "is_active": False,
            "approved_by": current_user["id"],
            "approved_at": now,
            "approval_notes": rejection_notes,
            "updated_at": now
        }}
    )
    
    # Log in audit trail
    await db.audit_logs.insert_one({
        "id": str(__import__('uuid').uuid4()),
        "action": "user_rejected",
        "actor_id": current_user["id"],
        "actor_email": current_user["email"],
        "actor_name": current_user.get("name", "Unknown"),
        "target_id": user_id,
        "target_email": user["email"],
        "organization_id": current_user["organization_id"],
        "details": {
            "rejection_notes": rejection_notes,
            "rejected_user": user["email"]
        },
        "timestamp": now,
        "ip_address": None
    })
    
    # TODO: Send rejection email to user
    
    return {
        "message": f"User {user['email']} has been rejected",
        "user_id": user_id,
        "rejected_by": current_user["email"],
        "rejected_at": now
    }
