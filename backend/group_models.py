from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class UserGroup(BaseModel):
    """User group/team model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    color: str = "#3b82f6"  # Default blue
    icon: Optional[str] = None
    
    # Group hierarchy
    parent_group_id: Optional[str] = None
    level: int = 1  # Nesting level
    
    # Members
    member_ids: List[str] = []  # List of user IDs
    member_count: int = 0
    
    # Permissions
    role_id: Optional[str] = None  # Default role for group members
    permissions: List[str] = []  # Group-level permissions
    
    # Settings
    is_active: bool = True
    is_system_group: bool = False  # System groups can't be deleted
    
    # Organization unit association
    unit_id: Optional[str] = None
    
    # Metadata
    created_by: str
    created_by_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupCreate(BaseModel):
    """Create user group"""
    name: str
    description: Optional[str] = None
    color: str = "#3b82f6"
    icon: Optional[str] = None
    parent_group_id: Optional[str] = None
    role_id: Optional[str] = None
    unit_id: Optional[str] = None


class GroupUpdate(BaseModel):
    """Update user group"""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[str] = None


class GroupMemberAdd(BaseModel):
    """Add members to group"""
    user_ids: List[str]


class GroupStats(BaseModel):
    """Group statistics"""
    total_groups: int
    active_groups: int
    total_members: int
    groups_by_level: dict
