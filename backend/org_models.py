from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class OrganizationUnit(BaseModel):
    """Organization unit model (can be any level in hierarchy)"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    level: int  # 1-5 (1=Company, 2=Region, 3=Location, 4=Department, 5=Team)
    parent_id: Optional[str] = None  # Parent unit ID
    path: str = ""  # Hierarchical path like /org/region/location
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationUnitCreate(BaseModel):
    """Create organization unit"""
    name: str
    description: Optional[str] = None
    level: int = Field(ge=1, le=5)  # Must be between 1 and 5
    parent_id: Optional[str] = None


class OrganizationUnitUpdate(BaseModel):
    """Update organization unit"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UserOrgAssignment(BaseModel):
    """User assignment to organization unit with role"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    organization_id: str
    unit_id: str  # Specific unit they belong to
    role: str  # admin, manager, inspector, viewer
    assigned_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserOrgAssignmentCreate(BaseModel):
    """Assign user to organization unit"""
    user_id: str
    unit_id: str
    role: str  # admin, manager, inspector, viewer


class UserInvitation(BaseModel):
    """User invitation model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    organization_id: str
    unit_id: str
    role: str
    invited_by: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending, accepted, expired
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserInvitationCreate(BaseModel):
    """Create user invitation"""
    email: str
    unit_id: str
    role: str


class OrganizationHierarchy(BaseModel):
    """Organization hierarchy tree structure"""
    id: str
    name: str
    description: Optional[str]
    level: int
    parent_id: Optional[str]
    children: List['OrganizationHierarchy'] = []
    user_count: int = 0


class PermissionCheck(BaseModel):
    """Permission check result"""
    has_permission: bool
    user_role: str
    unit_id: str
    reason: Optional[str] = None