from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone, time
import uuid


class ChecklistItem(BaseModel):
    """Individual item in a checklist"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    required: bool = True
    order: int = 0


class ChecklistItemCreate(BaseModel):
    """Create checklist item"""
    text: str
    required: bool = True
    order: int = 0


class ChecklistTemplate(BaseModel):
    """Checklist template model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None  # opening, closing, daily, weekly, monthly
    items: List[ChecklistItem] = []
    frequency: str = "daily"  # daily, weekly, monthly, custom
    scheduled_time: Optional[str] = None  # HH:MM format
    assigned_to: Optional[str] = None  # user_id or unit_id
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChecklistTemplateCreate(BaseModel):
    """Create checklist template"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    items: List[ChecklistItemCreate] = []
    frequency: str = "daily"
    scheduled_time: Optional[str] = None
    assigned_to: Optional[str] = None


class ChecklistTemplateUpdate(BaseModel):
    """Update checklist template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    items: Optional[List[ChecklistItemCreate]] = None
    frequency: Optional[str] = None
    scheduled_time: Optional[str] = None
    assigned_to: Optional[str] = None
    is_active: Optional[bool] = None


class ChecklistItemCompletion(BaseModel):
    """Completion status of a checklist item"""
    item_id: str
    completed: bool
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class ChecklistExecution(BaseModel):
    """Checklist execution/instance model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    template_id: str
    template_name: str  # Denormalized
    date: str  # YYYY-MM-DD format
    completed_by: Optional[str] = None  # user_id
    completed_by_name: Optional[str] = None  # Denormalized
    status: str = "pending"  # pending, in_progress, completed
    items: List[ChecklistItemCompletion] = []
    completion_percentage: float = 0.0
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Workflow integration fields
    workflow_id: Optional[str] = None
    workflow_status: Optional[str] = None  # pending, in_progress, approved, rejected, cancelled
    workflow_template_id: Optional[str] = None
    requires_approval: bool = False


class ChecklistExecutionUpdate(BaseModel):
    """Update checklist execution"""
    items: Optional[List[ChecklistItemCompletion]] = None
    notes: Optional[str] = None


class ChecklistExecutionComplete(BaseModel):
    """Complete a checklist"""
    items: List[ChecklistItemCompletion]
    notes: Optional[str] = None


class ChecklistStats(BaseModel):
    """Checklist statistics"""
    total_checklists: int
    completed_today: int
    pending_today: int
    completion_rate: float
    overdue: int