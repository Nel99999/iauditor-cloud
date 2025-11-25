"""
SMS and WhatsApp API Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import Optional, List
from .auth_utils import get_current_user
from .sms_service import SMSService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS & WhatsApp"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# ==================== MODELS ====================

class TwilioSettingsCreate(BaseModel):
    account_sid: str
    auth_token: str
    phone_number: str
    whatsapp_number: Optional[str] = None


class SendSMSRequest(BaseModel):
    to_number: str
    message: str
    from_number: Optional[str] = None


class SendWhatsAppRequest(BaseModel):
    to_number: str
    message: str
    from_number: Optional[str] = None
    media_url: Optional[str] = None


class BulkSMSRequest(BaseModel):
    phone_numbers: List[str]
    message: str


class BulkWhatsAppRequest(BaseModel):
    phone_numbers: List[str]
    message: str
    media_url: Optional[str] = None


class NotificationPreferencesUpdate(BaseModel):
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    phone_number: Optional[str] = None


# ==================== CONFIGURATION ENDPOINTS ====================

@router.get("/settings")
async def get_twilio_settings(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get Twilio configuration (only for Master and Developer roles)"""
    user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Master and Developer)
    if user.get("role") not in ["master", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can access Twilio settings"
        )
    
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not settings:
        return {
            "twilio_configured": False,
            "account_sid": "",
            "phone_number": "",
            "whatsapp_number": ""
        }
    
    # Mask sensitive data
    account_sid = settings.get("twilio_account_sid", "")
    auth_token = settings.get("twilio_auth_token", "")
    
    masked_sid = account_sid[:10] + "..." + account_sid[-4:] if len(account_sid) > 14 else account_sid
    
    return {
        "twilio_configured": bool(account_sid and auth_token),
        "account_sid": masked_sid,
        "phone_number": settings.get("twilio_phone_number", ""),
        "whatsapp_number": settings.get("twilio_whatsapp_number", "")
    }


@router.post("/settings")
async def save_twilio_settings(
    settings: TwilioSettingsCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Save Twilio configuration (only for Master and Developer roles)"""
    user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Master and Developer)
    if user.get("role") not in ["master", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can configure Twilio"
        )
    
    # Update or create settings
    await db.organization_settings.update_one(
        {"organization_id": user["organization_id"]},
        {
            "$set": {
                "organization_id": user["organization_id"],
                "twilio_account_sid": settings.account_sid,
                "twilio_auth_token": settings.auth_token,
                "twilio_phone_number": settings.phone_number,
                "twilio_whatsapp_number": settings.whatsapp_number,
                "updated_by": user["id"],
                "updated_at": user.get("updated_at")
            }
        },
        upsert=True
    )
    
    return {"message": "Twilio settings saved successfully"}


@router.post("/test-connection")
async def test_twilio_connection(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Test Twilio connection (only for Master and Developer roles)"""
    user = await get_current_user(request, db)
    
    # Check if user has permission (ONLY Master and Developer)
    if user.get("role") not in ["master", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can test Twilio connection"
        )
    
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.test_connection()
    
    if result.get("success"):
        return {"success": True, "message": "Twilio connection successful", "data": result}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Twilio connection failed: {result.get('error')}"
        )


# ==================== SENDING ENDPOINTS ====================

@router.post("/send")
async def send_sms(
    sms_request: SendSMSRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send SMS message"""
    user = await get_current_user(request, db)
    
    # Get organization Twilio settings
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured for this organization"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.send_sms(
        to_number=sms_request.to_number,
        message=sms_request.message,
        from_number=sms_request.from_number
    )
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send SMS")
        )


@router.post("/whatsapp/send")
async def send_whatsapp(
    whatsapp_request: SendWhatsAppRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send WhatsApp message"""
    user = await get_current_user(request, db)
    
    # Get organization Twilio settings
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured for this organization"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.send_whatsapp(
        to_number=whatsapp_request.to_number,
        message=whatsapp_request.message,
        from_number=whatsapp_request.from_number,
        media_url=whatsapp_request.media_url
    )
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send WhatsApp")
        )


@router.post("/send-bulk")
async def send_bulk_sms(
    bulk_request: BulkSMSRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send SMS to multiple recipients"""
    user = await get_current_user(request, db)
    
    # Get organization Twilio settings
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured for this organization"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.send_bulk_sms(
        phone_numbers=bulk_request.phone_numbers,
        message=bulk_request.message
    )
    
    return result


@router.post("/whatsapp/send-bulk")
async def send_bulk_whatsapp(
    bulk_request: BulkWhatsAppRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send WhatsApp to multiple recipients"""
    user = await get_current_user(request, db)
    
    # Get organization Twilio settings
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured for this organization"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.send_bulk_whatsapp(
        phone_numbers=bulk_request.phone_numbers,
        message=bulk_request.message,
        media_url=bulk_request.media_url
    )
    
    return result


@router.get("/message-status/{message_sid}")
async def get_message_status(
    message_sid: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get status of a sent message"""
    user = await get_current_user(request, db)
    
    # Get organization Twilio settings
    settings = await db.organization_settings.find_one(
        {"organization_id": user["organization_id"]}
    )
    
    if not settings or not settings.get("twilio_account_sid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Twilio not configured for this organization"
        )
    
    sms_service = SMSService(
        account_sid=settings["twilio_account_sid"],
        auth_token=settings["twilio_auth_token"],
        phone_number=settings.get("twilio_phone_number"),
        whatsapp_number=settings.get("twilio_whatsapp_number")
    )
    
    result = sms_service.get_message_status(message_sid)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Message not found")
        )


# ==================== USER PREFERENCES ====================

@router.get("/preferences")
async def get_notification_preferences(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's SMS/WhatsApp notification preferences"""
    user = await get_current_user(request, db)
    
    prefs = await db.user_preferences.find_one(
        {"user_id": user["id"]},
        {"_id": 0}
    )
    
    if not prefs:
        return {
            "sms_enabled": False,
            "whatsapp_enabled": False,
            "phone_number": user.get("phone", "")
        }
    
    return {
        "sms_enabled": prefs.get("sms_enabled", False),
        "whatsapp_enabled": prefs.get("whatsapp_enabled", False),
        "phone_number": prefs.get("phone_number", user.get("phone", ""))
    }


@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferencesUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user's SMS/WhatsApp notification preferences"""
    user = await get_current_user(request, db)
    
    # Update preferences
    await db.user_preferences.update_one(
        {"user_id": user["id"]},
        {
            "$set": {
                "user_id": user["id"],
                "organization_id": user["organization_id"],
                "sms_enabled": preferences.sms_enabled,
                "whatsapp_enabled": preferences.whatsapp_enabled,
                "phone_number": preferences.phone_number
            }
        },
        upsert=True
    )
    
    # Also update user's phone number if provided
    if preferences.phone_number:
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"phone": preferences.phone_number}}
        )
    
    return {"message": "Notification preferences updated successfully"}
