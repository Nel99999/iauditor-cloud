from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


# =====================================
# PERMISSION SYSTEM MODELS
# =====================================

class Permission(BaseModel):
    """Granular permission definition"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: str  # 'inspection', 'task', 'report', 'user', etc.
    action: str  # 'create', 'read', 'update', 'delete', 'approve', 'assign'
    scope: str  # 'own', 'team', 'branch', 'organization', 'all'
    description: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PermissionCreate(BaseModel):
    resource_type: str
    action: str
    scope: str
    description: str


class RolePermission(BaseModel):
    """Mapping between roles and permissions"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role_id: str
    permission_id: str
    granted: bool = True  # True = grant, False = deny
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RolePermissionCreate(BaseModel):
    role_id: str
    permission_id: str
    granted: bool = True


class UserFunctionOverride(BaseModel):
    """User-specific permission overrides"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    permission_id: str
    scope_type: str  # 'organization', 'company', 'branch', 'brand', 'team'
    scope_id: str
    granted: bool  # True = grant, False = deny
    reason: Optional[str] = None
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserFunctionOverrideCreate(BaseModel):
    user_id: str
    permission_id: str
    scope_type: str
    scope_id: str
    granted: bool
    reason: Optional[str] = None


# =====================================
# EXTENDED ROLE MODELS
# =====================================

class ExtendedRole(BaseModel):
    """Extended role definition with hierarchy"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str  # 'master', 'admin', 'developer', 'team_lead', etc.
    color: str  # Hex color code
    level: int  # Hierarchy level (1=highest)
    description: str
    organization_id: str
    parent_role_id: Optional[str] = None  # For role inheritance
    is_system_role: bool = False  # Cannot be deleted
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExtendedRoleCreate(BaseModel):
    name: str
    code: str
    color: str
    level: int
    description: str
    parent_role_id: Optional[str] = None


# =====================================
# INVITATION MODELS
# =====================================

class UserInvitation(BaseModel):
    """User invitation tracking"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invited_by: str
    invited_by_name: str
    organization_id: str
    role_id: str
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    function_overrides: Optional[dict] = None
    status: str = "pending"  # 'pending', 'accepted', 'expired', 'cancelled'
    expires_at: str  # 7 days from creation
    accepted_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserInvitationCreate(BaseModel):
    email: str
    role_id: str
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    function_overrides: Optional[dict] = None


class UserInvitationAccept(BaseModel):
    token: str
    name: str
    password: str


# =====================================
# DEACTIVATION MODELS
# =====================================

class UserDeactivation(BaseModel):
    """User deactivation tracking"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    deactivated_by: str
    reason: str
    reassign_to: Optional[str] = None
    reassignment_completed: bool = False
    tasks_reassigned: int = 0
    inspections_reassigned: int = 0
    checklists_reassigned: int = 0
    deactivated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reactivated_at: Optional[str] = None
    reactivated_by: Optional[str] = None


class UserDeactivationCreate(BaseModel):
    user_id: str
    reason: str
    reassign_to: Optional[str] = None


class UserReactivation(BaseModel):
    user_id: str
    reason: str


# =====================================
# APPROVAL WORKFLOW MODELS
# =====================================

class ApprovalChain(BaseModel):
    """Multi-level approval workflow"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approvable_type: str  # 'inspection', 'task', 'finding'
    approvable_id: str
    organization_id: str
    steps: List[dict]  # Array of approval steps
    current_step: int = 1
    status: str = "pending"  # 'pending', 'in_progress', 'approved', 'rejected', 'cancelled'
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class ApprovalChainCreate(BaseModel):
    approvable_type: str
    approvable_id: str
    steps: List[dict]


class Approval(BaseModel):
    """Individual approval action"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approval_chain_id: str
    step_number: int
    user_id: str
    user_name: str
    action: str  # 'approve', 'reject', 'request_changes'
    comments: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApprovalAction(BaseModel):
    action: str  # 'approve', 'reject', 'request_changes'
    comments: Optional[str] = None


# =====================================
# API KEY & WEBHOOK MODELS (Developer Portal)
# =====================================

class APIKey(BaseModel):
    """API key for developer access"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    key_prefix: str  # First 8 chars of key (for display)
    key_hash: str  # Hashed full key
    permissions: List[str]  # ['inspection.read', 'task.create', etc.]
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    rate_limit_per_hour: int = 1000
    last_used_at: Optional[str] = None
    expires_at: Optional[str] = None
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revoked_at: Optional[str] = None


class APIKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    rate_limit_per_hour: int = 1000
    expires_at: Optional[str] = None


class Webhook(BaseModel):
    """Webhook configuration"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    url: str
    secret: str  # For signature verification
    events: List[str]  # ['inspection.completed', 'task.created', etc.]
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    active: bool = True
    retry_config: dict = {"max_retries": 3, "retry_delay": 60}
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[str]
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    retry_config: Optional[dict] = None


# =====================================
# AUDIT LOG MODELS
# =====================================

class AuditLog(BaseModel):
    """Global audit log entry"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    organization_id: str
    action: str
    resource_type: str
    resource_id: str
    changes: Optional[dict] = None  # Before/after values
    metadata: Optional[dict] = None  # IP, user agent, etc.
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLogCreate(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    changes: Optional[dict] = None
    metadata: Optional[dict] = None
    scope_type: Optional[str] = None
    scope_id: Optional[str] = None
