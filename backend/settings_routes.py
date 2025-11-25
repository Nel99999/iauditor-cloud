from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from .auth_utils import get_current_user
from .email_service import EmailService
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/settings", tags=["settings"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class EmailSettings(BaseModel):
    sendgrid_api_key: str
    sendgrid_from_email: str = ""
    sendgrid_from_name: str = ""


@router.get("/email")
async def get_email_settings(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get email settings (only for Master and Developer roles)"""
    current_user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Developer and Master)
    allowed_roles = ['developer', 'master']
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can access email settings"
        )
    
    settings = await db.organization_settings.find_one({
        "organization_id": current_user["organization_id"]
    }, {"_id": 0})
    
    if not settings:
        return {
            "sendgrid_configured": False, 
            "sendgrid_api_key": "",
            "sendgrid_from_email": "",
            "sendgrid_from_name": ""
        }
    
    # Mask API key for security
    api_key = settings.get("sendgrid_api_key", "")
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else ""
    
    return {
        "sendgrid_configured": bool(api_key),
        "sendgrid_api_key": masked_key,
        "sendgrid_from_email": settings.get("sendgrid_from_email", ""),
        "sendgrid_from_name": settings.get("sendgrid_from_name", "")
    }


@router.post("/email")
async def update_email_settings(
    settings: EmailSettings,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update email settings (only for Master and Developer roles)"""
    current_user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Developer and Master)
    allowed_roles = ['developer', 'master']
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can update email settings"
        )
    
    # Check if API key is masked (contains "...") - if so, don't update it
    is_masked_key = "..." in settings.sendgrid_api_key
    
    # Prepare update data
    update_data = {
        "sendgrid_from_email": settings.sendgrid_from_email or "",
        "sendgrid_from_name": settings.sendgrid_from_name or "",
        "updated_by": current_user["id"],
        "updated_at": uuid.uuid4().hex
    }
    
    # Only update API key if it's not masked (user actually changed it)
    if not is_masked_key and settings.sendgrid_api_key:
        update_data["sendgrid_api_key"] = settings.sendgrid_api_key
    
    # Upsert settings
    await db.organization_settings.update_one(
        {"organization_id": current_user["organization_id"]},
        {
            "$set": update_data,
            "$setOnInsert": {
                "id": str(uuid.uuid4()),
                "organization_id": current_user["organization_id"]
            }
        },
        upsert=True
    )
    
    return {"message": "Email settings updated successfully"}


@router.post("/email/test")
async def test_email_settings(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Test email configuration (only for Master and Developer roles)"""
    current_user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Developer and Master)
    allowed_roles = ['developer', 'master']
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can test email settings"
        )
    
    settings = await db.organization_settings.find_one({
        "organization_id": current_user["organization_id"]
    })
    
    if not settings or not settings.get("sendgrid_api_key"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SendGrid API key not configured"
        )
    
    if not settings.get("sendgrid_from_email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SendGrid sender email not configured. Please add a verified sender email address."
        )
    
    # Initialize email service with configured sender
    email_service = EmailService(
        api_key=settings["sendgrid_api_key"],
        from_email=settings.get("sendgrid_from_email", "noreply@opsplatform.com"),
        from_name=settings.get("sendgrid_from_name", "Operations Platform")
    )
    
    # Send test email
    success = email_service.send_email(
        to_email=current_user["email"],
        subject="✅ SendGrid Test Email - Configuration Successful",
        html_content=f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #10b981;">🎉 SendGrid Configuration Test Successful!</h2>
            <p>Hi {current_user.get('name', 'there')},</p>
            <p>Your SendGrid configuration is working correctly!</p>
            <ul>
                <li><strong>Sender Email:</strong> {settings.get("sendgrid_from_email")}</li>
                <li><strong>Sender Name:</strong> {settings.get("sendgrid_from_name", "Operations Platform")}</li>
            </ul>
            <p>All email notifications are now operational and ready to use.</p>
        </div>
        """
    )
    
    if success:
        return {"success": True, "message": f"Test email sent successfully to {current_user['email']}"}
    else:
        return {"success": False, "message": "Failed to send test email. Check your SendGrid sender verification."}
