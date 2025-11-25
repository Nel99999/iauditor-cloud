from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class UserRole(BaseModel):
    """User role within an organization"""
    role_name: str  # admin, manager, inspector, viewer
    permissions: List[str] = []  # list of permission codes


class User(BaseModel):
    """User model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    picture: Optional[str] = None
    password_hash: Optional[str] = None  # Only for JWT auth
    auth_provider: str = "local"  # "local" or "google"
    organization_id: Optional[str] = None
    role: str = "viewer"  # admin, manager, inspector, viewer
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # MFA fields
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    mfa_backup_codes: List[str] = []
    mfa_setup_pending: bool = False
    mfa_enabled_at: Optional[datetime] = None
    
    # Security fields
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_sent_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    password_history: List[str] = []  # Store hashed passwords
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    
    # User Approval fields
    approval_status: str = "pending"  # "pending", "approved", "rejected"
    approved_by: Optional[str] = None  # user_id who approved/rejected
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    registration_ip: Optional[str] = None
    invited: bool = False  # True if created via invitation (auto-approved)


class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    organization_name: str  # Required - users must create organization or use invitation


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    remember_me: bool = False


class Session(BaseModel):
    """Session model for authentication"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class Organization(BaseModel):
    """Organization model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    owner_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationCreate(BaseModel):
    """Organization creation model"""
    name: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[str] = None
    org_unit_id: Optional[str] = None


class UserInvite(BaseModel):
    """User invitation model"""
    email: EmailStr
    role: str = "viewer"
    org_unit_id: Optional[str] = None


class NotificationSettings(BaseModel):
    """Notification settings"""
    email_notifications: bool = True
    push_notifications: bool = False
    weekly_reports: bool = True
    marketing_emails: bool = False


class ThemePreferences(BaseModel):
    """Theme preferences"""
    theme: Optional[str] = "system"  # light, dark, system
    accent_color: Optional[str] = "blue"
    view_density: Optional[str] = "comfortable"  # compact, comfortable, spacious
    font_size: Optional[str] = "medium"  # small, medium, large


class RegionalPreferences(BaseModel):
    """Regional preferences"""
    language: Optional[str] = "en-US"
    timezone: Optional[str] = "UTC"
    date_format: Optional[str] = "YYYY-MM-DD"
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class UserRole(BaseModel):
    """User role within an organization"""
    role_name: str  # admin, manager, inspector, viewer
    permissions: List[str] = []  # list of permission codes


class User(BaseModel):
    """User model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    picture: Optional[str] = None
    password_hash: Optional[str] = None  # Only for JWT auth
    auth_provider: str = "local"  # "local" or "google"
    organization_id: Optional[str] = None
    role: str = "viewer"  # admin, manager, inspector, viewer
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # MFA fields
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    mfa_backup_codes: List[str] = []
    mfa_setup_pending: bool = False
    mfa_enabled_at: Optional[datetime] = None
    
    # Security fields
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_sent_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    password_history: List[str] = []  # Store hashed passwords
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    
    # User Approval fields
    approval_status: str = "pending"  # "pending", "approved", "rejected"
    approved_by: Optional[str] = None  # user_id who approved/rejected
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    registration_ip: Optional[str] = None
    invited: bool = False  # True if created via invitation (auto-approved)


class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    organization_name: str  # Required - users must create organization or use invitation


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    remember_me: bool = False


class Session(BaseModel):
    """Session model for authentication"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class Organization(BaseModel):
    """Organization model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    owner_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationCreate(BaseModel):
    """Organization creation model"""
    name: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[str] = None
    org_unit_id: Optional[str] = None


class UserInvite(BaseModel):
    """User invitation model"""
    email: EmailStr
    role: str = "viewer"
    org_unit_id: Optional[str] = None


class NotificationSettings(BaseModel):
    """Notification settings"""
    email_notifications: bool = True
    push_notifications: bool = False
    weekly_reports: bool = True
    marketing_emails: bool = False


class ThemePreferences(BaseModel):
    """Theme preferences"""
    theme: Optional[str] = "system"  # light, dark, system
    accent_color: Optional[str] = "blue"
    view_density: Optional[str] = "comfortable"  # compact, comfortable, spacious
    font_size: Optional[str] = "medium"  # small, medium, large


class RegionalPreferences(BaseModel):
    """Regional preferences"""
    language: Optional[str] = "en-US"
    timezone: Optional[str] = "UTC"
    date_format: Optional[str] = "YYYY-MM-DD"
    time_format: Optional[str] = "24h"
    currency: Optional[str] = "USD"


class PrivacyPreferences(BaseModel):
    """Privacy preferences"""
    profile_visibility: Optional[str] = "organization"  # public, organization, private
    show_activity_status: Optional[bool] = True
    show_last_seen: Optional[bool] = True


class SecurityPreferences(BaseModel):
    """Security preferences"""
    mfa_enabled: Optional[bool] = None
    session_timeout: Optional[int] = None