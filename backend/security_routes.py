from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import secrets
import uuid
import re
from .auth_utils import get_current_user

router = APIRouter(prefix="/security", tags=["Security"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== PASSWORD POLICY CONFIGURATION ====================

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_EXPIRY_DAYS = 90
PASSWORD_HISTORY_COUNT = 5
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


# ==================== MODELS ====================

class PasswordChangeRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        return validate_password_strength(v)


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        return validate_password_strength(v)


class EmailVerificationRequest(BaseModel):
    """Request email verification"""
    token: str


class PasswordPolicy(BaseModel):
    """Password policy configuration"""
    min_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_numbers: bool
    require_special: bool
    expiry_days: int
    history_count: int


class AccountStatus(BaseModel):
    """Account security status"""
    email_verified: bool
    mfa_enabled: bool
    password_expires_in_days: Optional[int]
    account_locked: bool
    failed_attempts: int


# ==================== HELPER FUNCTIONS ====================

def validate_password_strength(password: str) -> str:
    """Validate password against security policy"""
    errors = []
    
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be no more than {PASSWORD_MAX_LENGTH} characters")
    
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if PASSWORD_REQUIRE_NUMBERS and not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    if errors:
        raise ValueError(". ".join(errors))
    
    return password


def check_password_history(new_password: str, password_history: list) -> bool:
    """Check if password was used before"""
    for old_password in password_history[:PASSWORD_HISTORY_COUNT]:
        if pwd_context.verify(new_password, old_password):
            return True
    return False


def is_account_locked(user: dict) -> bool:
    """Check if account is locked"""
    if user.get("account_locked_until"):
        locked_until = user["account_locked_until"]
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until)
        
        if locked_until > datetime.now(timezone.utc):
            return True
        
    return False


# ==================== ENDPOINTS ====================

@router.get("/password-policy", response_model=PasswordPolicy)
async def get_password_policy():
    """Get password policy configuration"""
    return PasswordPolicy(
        min_length=PASSWORD_MIN_LENGTH,
        require_uppercase=PASSWORD_REQUIRE_UPPERCASE,
        require_lowercase=PASSWORD_REQUIRE_LOWERCASE,
        require_numbers=PASSWORD_REQUIRE_NUMBERS,
        require_special=PASSWORD_REQUIRE_SPECIAL,
        expiry_days=PASSWORD_EXPIRY_DAYS,
        history_count=PASSWORD_HISTORY_COUNT
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Change password for authenticated user"""
    user = await get_current_user(request, db)
    
    # Verify current password
    password_hash = user.get("password_hash") or user.get("password", "")
    if not pwd_context.verify(password_data.current_password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Check if new password matches confirmation
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Check password history
    password_history = user.get("password_history", [])
    if check_password_history(password_data.new_password, password_history):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reuse any of your last {PASSWORD_HISTORY_COUNT} passwords"
        )
    
    # Hash new password
    new_password_hash = pwd_context.hash(password_data.new_password)
    
    # Update password history
    current_hash = user.get("password_hash") or user.get("password", "")
    password_history.insert(0, current_hash)
    password_history = password_history[:PASSWORD_HISTORY_COUNT]
    
    # Update user
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password": new_password_hash,
                "password_history": password_history,
                "password_changed_at": datetime.now(timezone.utc).isoformat(),
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
        "action": "password.changed",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Password changed successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Request password reset via email"""
    # Find user
    user = await db.users.find_one({"email": reset_request.email})
    
    # Don't reveal if user exists for security
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store token
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires_at": expires_at.isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # TODO: Send email with reset link
    # reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    # await send_password_reset_email(user["email"], reset_link)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user.get("organization_id"),
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "password.reset_requested",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reset password using token"""
    # Check passwords match
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Find user by token
    user = await db.users.find_one({"password_reset_token": reset_data.token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check token expiry
    expires_at = user.get("password_reset_expires_at")
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
    
    # Check password history
    password_history = user.get("password_history", [])
    if check_password_history(reset_data.new_password, password_history):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reuse any of your last {PASSWORD_HISTORY_COUNT} passwords"
        )
    
    # Hash new password
    new_password_hash = pwd_context.hash(reset_data.new_password)
    
    # Update password history
    current_hash = user.get("password_hash") or user.get("password", "")
    password_history.insert(0, current_hash)
    password_history = password_history[:PASSWORD_HISTORY_COUNT]
    
    # Update user
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password": new_password_hash,
                "password_history": password_history,
                "password_changed_at": datetime.now(timezone.utc).isoformat(),
                "password_reset_token": None,
                "password_reset_expires_at": None,
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user.get("organization_id"),
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "password.reset_completed",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Password reset successful"}


@router.post("/send-verification-email")
async def send_verification_email(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send email verification link"""
    user = await get_current_user(request, db)
    
    if user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Store token
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "email_verification_token": verification_token,
                "email_verification_sent_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # TODO: Send verification email
    # verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
    # await send_email_verification(user["email"], verification_link)
    
    return {"message": "Verification email sent"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Verify email using token"""
    # Find user by token
    user = await db.users.find_one({"email_verification_token": verification_data.token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Mark as verified
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "email_verified": True,
                "email_verification_token": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user.get("organization_id"),
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "email.verified",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Email verified successfully"}


@router.get("/account-status", response_model=AccountStatus)
async def get_account_status(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get account security status"""
    user = await get_current_user(request, db)
    
    # Calculate password expiry
    password_expires_in_days = None
    if user.get("password_changed_at"):
        password_changed = user["password_changed_at"]
        if isinstance(password_changed, str):
            password_changed = datetime.fromisoformat(password_changed)
        
        expiry_date = password_changed + timedelta(days=PASSWORD_EXPIRY_DAYS)
        days_remaining = (expiry_date - datetime.now(timezone.utc)).days
        password_expires_in_days = max(0, days_remaining)
    
    return AccountStatus(
        email_verified=user.get("email_verified", False),
        mfa_enabled=user.get("mfa_enabled", False),
        password_expires_in_days=password_expires_in_days,
        account_locked=is_account_locked(user),
        failed_attempts=user.get("failed_login_attempts", 0)
    )


@router.post("/unlock-account/{user_id}")
async def unlock_account(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Unlock user account (Admin only)"""
    admin_user = await get_current_user(request, db)
    
    # Check if admin has permission using database-driven RBAC
    from .auth_utils import check_permission
    has_permission = await check_permission(admin_user, "user", "update", "organization", db)
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to unlock accounts"
        )
    
    # Unlock account
    await db.users.update_one(
        {"id": user_id, "organization_id": admin_user["organization_id"]},
        {
            "$set": {
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": admin_user["organization_id"],
        "user_id": admin_user["id"],
        "user_email": admin_user["email"],
        "user_name": admin_user["name"],
        "action": "account.unlocked",
        "resource_type": "user",
        "resource_id": user_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"unlocked_by": admin_user["id"]}
    })
    
    return {"message": "Account unlocked successfully"}
