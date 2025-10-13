from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import get_current_user
from email_service import EmailService
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/settings", tags=["settings"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class EmailSettings(BaseModel):
    sendgrid_api_key: str


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
        return {"sendgrid_configured": False, "sendgrid_api_key": ""}
    
    # Mask API key for security
    api_key = settings.get("sendgrid_api_key", "")
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else ""
    
    return {
        "sendgrid_configured": bool(api_key),
        "sendgrid_api_key": masked_key
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
    
    # Upsert settings
    await db.organization_settings.update_one(
        {"organization_id": current_user["organization_id"]},
        {
            "$set": {
                "sendgrid_api_key": settings.sendgrid_api_key,
                "updated_by": current_user["id"],
                "updated_at": uuid.uuid4().hex
            },
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
    
    email_service = EmailService(settings["sendgrid_api_key"])
    
    # Test connection
    if email_service.test_connection():
        return {"success": True, "message": "SendGrid connection successful"}
    else:
        return {"success": False, "message": "SendGrid connection failed"}
