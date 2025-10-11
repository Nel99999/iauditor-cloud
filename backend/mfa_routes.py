from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import pyotp
import qrcode
import io
import base64
from auth_utils import get_current_user
import secrets
import uuid

router = APIRouter(prefix="/mfa", tags=["Multi-Factor Authentication"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== MODELS ====================

class MFASetupRequest(BaseModel):
    """Request to setup MFA"""
    pass


class MFASetupResponse(BaseModel):
    """Response with QR code and secret"""
    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: List[str]


class MFAVerifyRequest(BaseModel):
    """Verify MFA code"""
    code: str


class MFADisableRequest(BaseModel):
    """Disable MFA"""
    password: str


class MFAStatusResponse(BaseModel):
    """MFA status"""
    enabled: bool
    backup_codes_remaining: int


# ==================== HELPER FUNCTIONS ====================

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for MFA recovery"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def hash_backup_codes(codes: List[str]) -> List[str]:
    """Hash backup codes for storage"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return [pwd_context.hash(code) for code in codes]


def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
    """Verify if backup code is valid"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    for hashed_code in hashed_codes:
        if pwd_context.verify(code, hashed_code):
            return True
    return False


def generate_qr_code(secret: str, email: str, issuer: str = "OpsPlatform") -> str:
    """Generate QR code for MFA setup"""
    # Create provisioning URI
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=issuer)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


# ==================== ENDPOINTS ====================

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Setup MFA for user - generate secret and QR code
    """
    user = await get_current_user(request, db)
    
    # Check if MFA already enabled
    if user.get("mfa_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled. Disable it first to setup again."
        )
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Generate QR code
    qr_code = generate_qr_code(secret, user["email"])
    
    # Generate backup codes
    backup_codes = generate_backup_codes(10)
    hashed_backup_codes = hash_backup_codes(backup_codes)
    
    # Store MFA data (not enabled yet - user must verify first)
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "mfa_secret": secret,
                "mfa_backup_codes": hashed_backup_codes,
                "mfa_setup_pending": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/verify")
async def verify_mfa_setup(
    verify_data: MFAVerifyRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Verify MFA code and enable MFA
    """
    user = await get_current_user(request, db)
    
    # Check if setup is pending
    if not user.get("mfa_setup_pending"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending MFA setup found. Please setup MFA first."
        )
    
    # Get secret
    secret = user.get("mfa_secret")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA secret not found. Please setup MFA again."
        )
    
    # Verify code
    totp = pyotp.TOTP(secret)
    if not totp.verify(verify_data.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    # Enable MFA
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "mfa_enabled": True,
                "mfa_setup_pending": False,
                "mfa_enabled_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "mfa.enabled",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"method": "totp"}
    })
    
    return {"message": "MFA enabled successfully"}


@router.post("/verify-login")
async def verify_mfa_login(
    verify_data: MFAVerifyRequest,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Verify MFA code during login (called after password verification)
    This endpoint doesn't require authentication
    """
    # Get user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if MFA is enabled
    if not user.get("mfa_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this user"
        )
    
    # Get secret
    secret = user.get("mfa_secret")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA secret not found"
        )
    
    # Check if it's a backup code
    backup_codes = user.get("mfa_backup_codes", [])
    if verify_backup_code(verify_data.code, backup_codes):
        # Remove used backup code
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        remaining_codes = [
            code for code in backup_codes 
            if not pwd_context.verify(verify_data.code, code)
        ]
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"mfa_backup_codes": remaining_codes}}
        )
        
        return {"verified": True, "method": "backup_code"}
    
    # Verify TOTP code
    totp = pyotp.TOTP(secret)
    if not totp.verify(verify_data.code, valid_window=1):
        # Log failed attempt
        await db.audit_logs.insert_one({
            "id": str(uuid.uuid4()),
            "organization_id": user["organization_id"],
            "user_id": user["id"],
            "user_email": user["email"],
            "user_name": user["name"],
            "action": "mfa.verify_failed",
            "resource_type": "user",
            "resource_id": user["id"],
            "result": "failure",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    return {"verified": True, "method": "totp"}


@router.post("/disable")
async def disable_mfa(
    disable_data: MFADisableRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Disable MFA for user (requires password confirmation)
    """
    user = await get_current_user(request, db)
    
    # Check if MFA is enabled
    if not user.get("mfa_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify password
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(disable_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Disable MFA
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "mfa_enabled": False,
                "mfa_secret": None,
                "mfa_backup_codes": [],
                "mfa_setup_pending": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "mfa.disabled",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "MFA disabled successfully"}


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get MFA status for current user
    """
    user = await get_current_user(request, db)
    
    return MFAStatusResponse(
        enabled=user.get("mfa_enabled", False),
        backup_codes_remaining=len(user.get("mfa_backup_codes", []))
    )


@router.post("/regenerate-backup-codes", response_model=MFASetupResponse)
async def regenerate_backup_codes(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Regenerate backup codes (requires MFA to be enabled)
    """
    user = await get_current_user(request, db)
    
    # Check if MFA is enabled
    if not user.get("mfa_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA must be enabled to regenerate backup codes"
        )
    
    # Generate new backup codes
    backup_codes = generate_backup_codes(10)
    hashed_backup_codes = hash_backup_codes(backup_codes)
    
    # Update user
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "mfa_backup_codes": hashed_backup_codes,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "mfa.backup_codes_regenerated",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return MFASetupResponse(
        secret=user["mfa_secret"],
        qr_code="",  # Not needed for regeneration
        backup_codes=backup_codes
    )
