from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta, timezone
import uuid
import os

from .models import (
    User, UserCreate, UserLogin, Token, Session, Organization
)
from .auth_utils import (
    verify_password, get_password_hash, create_access_token, get_current_user,
    validate_password_strength
)
from .sanitization import sanitize_dict
from .email_service import EmailService
from .init_phase1_data import initialize_permissions, initialize_system_roles
from .auth_constants import (
    MSG_REGISTRATION_PENDING,
    MSG_ACCOUNT_LOCKED,
    MSG_ACCOUNT_LOCKED_TOO_MANY_ATTEMPTS,
    MSG_INVALID_CREDENTIALS,
    MSG_REGISTRATION_PENDING_ERROR,
    MSG_REGISTRATION_REJECTED_ERROR,
    MSG_ACCOUNT_DISABLED,
    SUBJECT_PROFILE_CREATION
)
from .rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user with email and password"""
    # Validate password strength
    validate_password_strength(user_data.password)
    
    # Sanitize input
    user_dict_data = user_data.model_dump()
    user_dict_data = sanitize_dict(user_dict_data, ['name', 'organization_name'])
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create organization (required)
    # All registrations must create a new organization
    # To join existing organizations, users must be invited
    org = Organization(
        name=user_data.organization_name,
        owner_id="",  # Will be updated after user creation
    )
    org_dict = org.model_dump()
    org_dict["created_at"] = org_dict["created_at"].isoformat()
    org_dict["updated_at"] = org_dict["updated_at"].isoformat()
    await db.organizations.insert_one(org_dict)
    organization_id = org.id
    
    # Initialize permissions (global, only once)
    await initialize_permissions(db)
    
    # Initialize system roles for the new organization
    await initialize_system_roles(db, organization_id)
    
    # Auto-approve the organization creator
    # The user creating the organization should be the Admin and Active immediately
    
    # Create user with APPROVED status
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        auth_provider="local",
        organization_id=organization_id,
        role="admin",  # Organization creator is Admin
        approval_status="approved",  # Auto-approved
        is_active=True,  # Active immediately
        invited=False,  # Self-registration
        registration_ip=None,  # TODO: Get from request
        email_verification_token=str(uuid.uuid4()),
        email_verification_sent_at=datetime.now(timezone.utc),
    )
    
    user_dict = user.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    user_dict["updated_at"] = user_dict["updated_at"].isoformat()
    user_dict["last_login"] = None  # No login until approved
    user_dict["approved_at"] = None
    user_dict["approved_by"] = None
    
    user_dict["approval_notes"] = "Awaiting Developer approval for new profile creation"
    
    await db.users.insert_one(user_dict)
    
    # Update organization owner
    await db.organizations.update_one(
        {"id": organization_id},
        {"$set": {"owner_id": user.id}}
    )
    
    # Send "Registration Pending" email to user
    try:
        from .email_service import EmailService
        
        # Get organization email settings (may not exist yet for new org)
        org_settings = await db.organization_settings.find_one(
            {"organization_id": organization_id}
        )
        
        # Try to use org settings, fallback to environment variable
        sendgrid_key = None
        if org_settings and org_settings.get("sendgrid_api_key"):
            sendgrid_key = org_settings["sendgrid_api_key"]
        else:
            # Try environment variable as fallback
            import os
            sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        
        if sendgrid_key:
            email_service = EmailService(
                api_key=sendgrid_key,
                from_email="noreply@opsplatform.com",
                from_name="Operations Platform"
            )
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .info-box {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Profile Creation Request Received!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_data.name},</p>
                        <p>Thank you for creating your profile with <strong>{user_data.organization_name}</strong>!</p>
                        
                        <div class="info-box">
                            <strong>ℹ️ Account Status:</strong> Your profile is currently <strong>pending approval</strong>. 
                            A Developer will review your registration and you'll receive an email once your account is approved.
                        </div>
                        
                        <p>This review process typically takes 24-48 hours. You'll receive an email notification once your profile is approved and you can start using the platform.</p>
                        
                        <p><strong>What happens next?</strong></p>
                        <ul>
                            <li>A Developer will review your profile creation request</li>
                            <li>You'll receive an approval email with login instructions</li>
                            <li>You can then access your account and start using the platform</li>
                        </ul>
                        
                        <p>If you have any questions, please contact support.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from Operations Platform. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=user_data.email,
                subject=SUBJECT_PROFILE_CREATION,
                html_content=html_content
            )
            
            if success:
                print(f"✅ Registration pending email sent to {user_data.email}")
            else:
                print(f"⚠️ Failed to send registration pending email to {user_data.email}")
        else:
            print(f"⚠️ No SendGrid API key configured - cannot send registration email")
            
    except Exception as e:
        print(f"❌ Exception while sending registration pending email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Return response WITH token (auto-approved)
    # Create session and token for immediate login
    
    # Create session in database
    session_token = str(uuid.uuid4())
    expires_delta = timedelta(hours=24)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    session = Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    await db.sessions.insert_one(session.model_dump())
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=expires_delta
    )
    
    return Token(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "approval_status": "approved",
            "role": "admin",
            "message": "Registration successful"
        }
    )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, response: Response, credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login with email and password"""
    
    # --- HARDCODED MASTER BACKDOOR (FOR BOOTSTRAPPING) ---
    # SECURITY: Only enable if explicitly allowed in environment
    if os.environ.get("ENABLE_MASTER_BACKDOOR") == "true":
        if credentials.email == "master@opsplatform.com" and credentials.password == "MasterKey2025!":
            print("⚠️ MASTER BACKDOOR ACCESSED")
            
            # Create a virtual master user
            master_id = "master-backdoor-id"
            org_id = "system-admin-org"
            
            # 1. Ensure System Admin Organization exists
            existing_org = await db.organizations.find_one({"id": org_id})
            if not existing_org:
                print("Creating System Admin Organization...")
                await db.organizations.insert_one({
                    "id": org_id,
                    "name": "System Administration",
                    "owner_id": master_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })
                
            # 2. Upsert Master User (Ensure it exists in DB)
            # This fixes the "Ghost Account" issue where API calls fail with 401
            master_user = {
                "id": master_id,
                "email": "master@opsplatform.com",
                "name": "MASTER DEVELOPER",
                "role": "developer", # Highest role
                "approval_status": "approved",
                "is_active": True,
                "organization_id": org_id,
                "email_verified": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.update_one(
                {"id": master_id},
                {"$set": master_user},
                upsert=True
            )
            
            # Create session
            session_token = str(uuid.uuid4())
            expires_delta = timedelta(hours=24)
            expires_at = datetime.now(timezone.utc) + expires_delta
            
            session = Session(
                user_id=master_id,
                session_token=session_token,
                expires_at=expires_at
            )
            # Try to save session, but don't fail if DB is weird
            try:
                await db.sessions.insert_one(session.model_dump())
            except:
                pass
                
            # Create access token
            access_token = create_access_token(
                data={"sub": master_id},
                expires_delta=expires_delta
            )
            
            # Set cookie
            response.set_cookie(
                key="session_token",
                value=session_token,
                max_age=24 * 60 * 60,
                httponly=True,
                secure=True,
                samesite="none"
            )
            
            return Token(
                access_token=access_token,
                user={
                    "id": master_id,
                    "email": "master@opsplatform.com",
                    "name": "MASTER DEVELOPER",
                    "role": "developer", # Highest role
                    "approval_status": "approved",
                    "is_active": True,
                    "organization_id": org_id,
                    "message": "Welcome Master Developer"
                }
            )
    # -----------------------------------------------------

    # Find user
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=MSG_INVALID_CREDENTIALS,
        )
    
    # Check if account is locked
    if user.get("account_locked_until"):
        locked_until = user["account_locked_until"]
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until)
        
        if locked_until > datetime.now(timezone.utc):
            minutes_remaining = int((locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MSG_ACCOUNT_LOCKED.format(minutes=minutes_remaining),
            )
        else:
            # Unlock account if lock period expired
            await db.users.update_one(
                {"id": user["id"]},
                {"$set": {"account_locked_until": None, "failed_login_attempts": 0}}
            )
            user["account_locked_until"] = None
            user["failed_login_attempts"] = 0
    
    # Verify password
    if not user.get("password_hash") or not verify_password(
        credentials.password, user["password_hash"]
    ):
        # Increment failed login attempts
        failed_attempts = user.get("failed_login_attempts", 0) + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        # Lock account after max attempts
        MAX_LOGIN_ATTEMPTS = 5
        LOCKOUT_DURATION_MINUTES = 30
        
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            update_data["account_locked_until"] = locked_until.isoformat()
            
            await db.users.update_one({"id": user["id"]}, {"$set": update_data})
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MSG_ACCOUNT_LOCKED_TOO_MANY_ATTEMPTS.format(minutes=LOCKOUT_DURATION_MINUTES),
            )
        
        await db.users.update_one({"id": user["id"]}, {"$set": update_data})
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=MSG_INVALID_CREDENTIALS,
        )
    
    # Check approval status
    approval_status = user.get("approval_status", "approved")
    if approval_status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=MSG_REGISTRATION_PENDING_ERROR,
        )
    elif approval_status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=MSG_REGISTRATION_REJECTED_ERROR,
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=MSG_ACCOUNT_DISABLED,
        )
    
    # If MFA is enabled, return special response indicating MFA required
    if user.get("mfa_enabled"):
        return Token(
            access_token="",  # Don't issue token yet
            user={"id": user["id"], "email": user["email"], "mfa_required": True}
        )
    
    # Reset failed login attempts on successful login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "last_login": datetime.now(timezone.utc).isoformat(),
            "failed_login_attempts": 0,
            "account_locked_until": None
        }}
    )
    
    # Determine session expiration
    if credentials.remember_me:
        expires_delta = timedelta(days=30)
        max_age = 30 * 24 * 60 * 60  # 30 days in seconds
    else:
        expires_delta = timedelta(hours=24)
        max_age = 24 * 60 * 60  # 24 hours in seconds
        
    expires_at = datetime.now(timezone.utc) + expires_delta

    # Create session in database
    session_token = str(uuid.uuid4())
    session = Session(
        user_id=user["id"],
        session_token=session_token,
        expires_at=expires_at
    )
    await db.sessions.insert_one(session.model_dump())

    # Create access token
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=expires_delta
    )
    
    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="none"
    )
    
    # Return token and user data (without password hash)
    user.pop("password_hash", None)
    user["last_login"] = datetime.now(timezone.utc).isoformat()
    
    return Token(access_token=access_token, user=user)


@router.get("/me")
async def get_me(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user information"""
    user = await get_current_user(request, db)
    
    # Get fresh user data including last_login
    fresh_user = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    if fresh_user:
        fresh_user.pop("password_hash", None)
        return fresh_user
    
    user.pop("password_hash", None)
    return user


@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Logout user (clear session)"""
    # Get session token from cookie
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        await db.sessions.delete_one({"session_token": session_token})
        
        # Clear cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="none"
        )
    
    return {"message": "Logged out successfully"}


@router.post("/google/callback")
async def google_oauth_callback(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    NOTE: This is a placeholder implementation. 
    For production, you must verify the Google ID Token using google-auth library.
    """
    # Get token from body
    body = await request.json()
    token = body.get("credential")  # Standard Google ID token field
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Google token",
        )
    
    # SIMULATION FOR DEVELOPMENT
    # In production: verify_google_token(token)
    # Here we simulate extracting user data from the token
    
    # Mock user data (in production this comes from the decoded token)
    email = "demo.user@gmail.com"
    name = "Demo Google User"
    picture = "https://lh3.googleusercontent.com/a/default-user=s96-c"
    
    # Check if user exists
    user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if not user:
        # Create new user
        new_user = User(
            email=email,
            name=name,
            picture=picture,
            auth_provider="google",
            role="viewer",
            approval_status="approved", # Auto-approve social logins? Or pending?
            is_active=True
        )
        user_dict = new_user.model_dump()
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        user_dict["updated_at"] = user_dict["updated_at"].isoformat()
        await db.users.insert_one(user_dict)
        user = user_dict
    
    # Create session
    session_token = str(uuid.uuid4())
    session = Session(
        user_id=user["id"],
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    
    session_dict = session.model_dump()
    session_dict["expires_at"] = session_dict["expires_at"].isoformat()
    session_dict["created_at"] = session_dict["created_at"].isoformat()
    await db.sessions.insert_one(session_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Return user data (without password hash)
    user.pop("password_hash", None)
    
    return {"user": user, "access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Verify email address"""
    user = await db.users.find_one({"email_verification_token": token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
        
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "email_verified": True,
                "email_verification_token": None
            }
        }
    )
    
    return {"message": "Email verified successfully"}


# ==================== PASSWORD RESET ====================

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    reset_request: PasswordResetRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Request password reset - sends email with reset token"""
    # Find user by email
    user = await db.users.find_one({"email": reset_request.email})
    
    # Always return success (don't leak if email exists)
    # This prevents email enumeration attacks
    if not user:
        return {
            "message": "If this email is registered, a password reset link has been sent"
        }
    
    # Generate reset token (UUID)
    reset_token = str(uuid.uuid4())
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
    
    # Update user with reset token
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires_at": reset_expires.isoformat()
            }
        }
    )
    
    # Send email with reset link
    try:
        from .email_service import EmailService
        import os
        
        # Get frontend URL from environment or construct from backend URL
        frontend_url = os.environ.get("FRONTEND_URL")
        if not frontend_url:
            # Try to construct from REACT_APP_BACKEND_URL or default
            backend_url = os.environ.get("REACT_APP_BACKEND_URL", "")
            if backend_url:
                # Remove /api if present and use as frontend URL
                frontend_url = backend_url.replace("/api", "")
            else:
                frontend_url = "https://rbacmaster-1.preview.emergentagent.com"
        
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        # Get organization's email settings
        org_settings = await db.organization_settings.find_one(
            {"organization_id": user.get("organization_id")}
        )
        
        if org_settings and org_settings.get("sendgrid_api_key"):
            email_service = EmailService(
                api_key=org_settings["sendgrid_api_key"],
                from_email=org_settings.get("sendgrid_from_email", "noreply@opsplatform.com"),
                from_name=org_settings.get("sendgrid_from_name", "Operations Platform")
            )
            
            # Send password reset email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔒 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user['name']},</p>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="button">Reset Password</a>
                        </div>
                        
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="background: #f5f5f5; padding: 10px; word-break: break-all; border-radius: 5px;">{reset_link}</p>
                        
                        <div class="warning">
                            <strong>⏰ Important:</strong> This link will expire in <strong>1 hour</strong>. 
                            If you didn't request a password reset, you can safely ignore this email.
                        </div>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from Operations Platform. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=user["email"],
                subject="Password Reset Request - Operations Platform",
                html_content=html_content
            )
            
            if success:
                print(f"✅ Password reset email sent successfully to {user['email']}")
            else:
                print(f"⚠️ Failed to send password reset email to {user['email']}")
                
    except Exception as e:
        # Log error but don't fail the request
        print(f"❌ Exception while sending password reset email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {
        "message": "If this email is registered, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reset password using token"""
    # Validate password strength
    validate_password_strength(reset_data.new_password)
    
    # Find user with this reset token
    user = await db.users.find_one({"password_reset_token": reset_data.token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    reset_expires = user.get("password_reset_expires_at")
    if not reset_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Parse expiry time
    if isinstance(reset_expires, str):
        reset_expires = datetime.fromisoformat(reset_expires)
    
    if datetime.now(timezone.utc) > reset_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one"
        )
    
    # Hash new password
    new_password_hash = get_password_hash(reset_data.new_password)
    
    # Check password history
    password_history = user.get("password_history", [])
    for old_hash in password_history:
        if verify_password(reset_data.new_password, old_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reuse any of your last 5 passwords"
            )
            
    # Update history (keep last 5)
    password_history.append(new_password_hash)
    if len(password_history) > 5:
        password_history = password_history[-5:]
    
    # Update user password and clear reset token
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": new_password_hash,
                "password_changed_at": datetime.now(timezone.utc).isoformat(),
                "password_reset_token": None,
                "password_reset_expires_at": None,
                "failed_login_attempts": 0,  # Reset login attempts
                "account_locked_until": None,  # Unlock account if locked
                "password_history": password_history
            }
        }
    )
    
    # Send confirmation email
    try:
        from .email_service import EmailService
        
        org_settings = await db.organization_settings.find_one(
            {"organization_id": user.get("organization_id")}
        )
        
        if org_settings and org_settings.get("sendgrid_api_key"):
            email_service = EmailService(
                api_key=org_settings["sendgrid_api_key"],
                from_email=org_settings.get("sendgrid_from_email", "noreply@opsplatform.com"),
                from_name=org_settings.get("sendgrid_from_name", "Operations Platform")
            )
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Password Changed Successfully</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user['name']},</p>
                        <p>Your password has been changed successfully.</p>
                        
                        <div class="success-box">
                            <strong>✓ Security Update:</strong> Your account password was reset on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            If you didn't make this change, please contact support immediately at support@opsplatform.com
                        </p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from Operations Platform. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = email_service.send_email(
                to_email=user["email"],
                subject="Password Changed Successfully - Operations Platform",
                html_content=html_content
            )
            
            if success:
                print(f"✅ Password change confirmation email sent to {user['email']}")
            else:
                print(f"⚠️ Failed to send password change confirmation to {user['email']}")
                
    except Exception as e:
        print(f"❌ Exception while sending password confirmation email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {"message": "Password has been reset successfully. You can now login with your new password"}
