from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Employee(BaseModel):
    """Employee model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    organization_id: str
    unit_id: str
    employee_number: str
    first_name: str
    last_name: str
    email: str
    position: str
    department: Optional[str] = None
    manager_id: Optional[str] = None
    hire_date: str
    employment_status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Announcement(BaseModel):
    """Announcement model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    title: str
    content: str
    priority: str = "normal"  # normal, important, urgent
    target_audience: str = "all"  # all, unit, role, custom
    unit_ids: List[str] = []
    published: bool = False
    published_at: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
