from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class Role(BaseModel):
    """Role model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []
    is_system_role: bool = False
    level: int = 0
    color: Optional[str] = None
    organization_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RoleCreate(BaseModel):
    """Create role model"""
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []
    level: int = 0
    color: Optional[str] = None


class RoleUpdate(BaseModel):
    """Update role model"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    level: Optional[int] = None
    color: Optional[str] = None


class ExtendedRole(Role):
    """Extended role model"""
    pass


class ExtendedRoleCreate(RoleCreate):
    """Extended role creation model"""
    pass
