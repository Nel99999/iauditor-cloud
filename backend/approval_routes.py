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
    
    # Send approval email to user
    try:
        from email_service import EmailService
        import os
        
        # Get organization's email settings
        org_settings = await db.organization_settings.find_one(
            {"organization_id": user.get("organization_id")}
        )
        
        # Try to use org settings, fallback to environment variable
        sendgrid_key = None
        if org_settings and org_settings.get("sendgrid_api_key"):
            sendgrid_key = org_settings["sendgrid_api_key"]
        else:
            sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        
        if sendgrid_key:
            email_service = EmailService(
                api_key=sendgrid_key,
                from_email=org_settings.get("sendgrid_from_email", "noreply@opsplatform.com") if org_settings else "noreply@opsplatform.com",
                from_name=org_settings.get("sendgrid_from_name", "Operations Platform") if org_settings else "Operations Platform"
            )
            
            # Get frontend URL
            frontend_url = os.environ.get("FRONTEND_URL")
            if not frontend_url:
                backend_url = os.environ.get("REACT_APP_BACKEND_URL", "")
                if backend_url:
                    frontend_url = backend_url.replace("/api", "")
                else:
                    frontend_url = "https://backendhealer.preview.emergentagent.com"
            
            login_url = f"{frontend_url}/login"
            
            # Get organization name
            org = await db.organizations.find_one({"id": user.get("organization_id")})
            org_name = org.get("name", "Operations Platform") if org else "Operations Platform"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Profile Approved!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user['name']},</p>
                        <p>Great news! Your profile for <strong>{org_name}</strong> has been approved by a Developer.</p>
                        
                        <div class="success-box">
                            <strong>✅ You can now log in and start using the platform!</strong>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{login_url}" class="button">Log In Now</a>
                        </div>
                        
                        <p><strong>Your account details:</strong></p>
                        <ul>
                            <li><strong>Email:</strong> {user['email']}</li>
                            <li><strong>Organization:</strong> {org_name}</li>
                            <li><strong>Approved by:</strong> {current_user.get('name', 'Developer')}</li>
                        </ul>
                        
                        <p>If you have any questions or need assistance getting started, please contact your administrator.</p>
                        
                        <p>Welcome aboard!</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from Operations Platform. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=user["email"],
                subject=f"Profile Approved - Welcome to {org_name}!",
                html_content=html_content
            )
            
            if success:
                print(f"✅ Approval email sent successfully to {user['email']}")
            else:
                print(f"⚠️ Failed to send approval email to {user['email']}")
        else:
            print(f"⚠️ No SendGrid API key configured - cannot send approval email")
            
    except Exception as e:
        print(f"❌ Exception while sending approval email: {str(e)}")
        import traceback
        traceback.print_exc()
    
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
    
    # Send rejection email to user
    try:
        from email_service import EmailService
        import os
        
        # Get organization's email settings
        org_settings = await db.organization_settings.find_one(
            {"organization_id": user.get("organization_id")}
        )
        
        # Try to use org settings, fallback to environment variable
        sendgrid_key = None
        if org_settings and org_settings.get("sendgrid_api_key"):
            sendgrid_key = org_settings["sendgrid_api_key"]
        else:
            sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        
        if sendgrid_key:
            email_service = EmailService(
                api_key=sendgrid_key,
                from_email=org_settings.get("sendgrid_from_email", "noreply@opsplatform.com") if org_settings else "noreply@opsplatform.com",
                from_name=org_settings.get("sendgrid_from_name", "Operations Platform") if org_settings else "Operations Platform"
            )
            
            # Get organization name
            org = await db.organizations.find_one({"id": user.get("organization_id")})
            org_name = org.get("name", "Operations Platform") if org else "Operations Platform"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .warning-box {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Profile Registration Update</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user['name']},</p>
                        <p>We regret to inform you that your profile registration for <strong>{org_name}</strong> was not approved at this time.</p>
                        
                        <div class="warning-box">
                            <strong>Reason:</strong><br>
                            {rejection_notes}
                        </div>
                        
                        <p>If you believe this was a mistake or would like more information, please contact your administrator or support team.</p>
                        
                        <p>You're welcome to register again if your circumstances have changed or if you can address the concerns noted above.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from Operations Platform. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=user["email"],
                subject=f"Profile Registration Update - {org_name}",
                html_content=html_content
            )
            
            if success:
                print(f"✅ Rejection email sent successfully to {user['email']}")
            else:
                print(f"⚠️ Failed to send rejection email to {user['email']}")
        else:
            print(f"⚠️ No SendGrid API key configured - cannot send rejection email")
            
    except Exception as e:
        print(f"❌ Exception while sending rejection email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {
        "message": f"User {user['email']} has been rejected",
        "user_id": user_id,
        "rejected_by": current_user["email"],
        "rejected_at": now
    }
