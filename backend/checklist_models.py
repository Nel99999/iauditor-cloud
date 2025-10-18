from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, time
import uuid


class ChecklistItem(BaseModel):
    """Individual item in a checklist"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    required: bool = True
    order: int = 0
    # V1 Enhancement fields
    photo_required: bool = False
    min_photos: int = 0
    max_photos: int = 10
    signature_required: bool = False
    conditional_logic: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None
    scoring_enabled: bool = False
    pass_score: Optional[float] = None


class ChecklistItemCreate(BaseModel):
    """Create checklist item"""
    text: str
    required: bool = True
    order: int = 0
    # V1 Enhancement fields
    photo_required: bool = False
    min_photos: int = 0
    max_photos: int = 10
    signature_required: bool = False
    conditional_logic: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None
    scoring_enabled: bool = False
    pass_score: Optional[float] = None


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
    
    # Workflow integration fields
    requires_approval: bool = False
    workflow_template_id: Optional[str] = None
    
    # V1 Enhancement fields
    unit_ids: List[str] = []
    asset_type_ids: List[str] = []
    shift_based: bool = False  # Auto-create per shift
    time_limit_minutes: Optional[int] = None  # Must complete within X minutes
    requires_supervisor_approval: bool = False
    scoring_enabled: bool = False
    pass_percentage: Optional[float] = None
    auto_create_work_order_on_fail: bool = False
    work_order_priority: Optional[str] = None


class ChecklistTemplateCreate(BaseModel):
    """Create checklist template"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    items: List[ChecklistItemCreate] = []
    frequency: str = "daily"
    scheduled_time: Optional[str] = None
    assigned_to: Optional[str] = None
    requires_approval: bool = False
    workflow_template_id: Optional[str] = None


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
    requires_approval: Optional[bool] = None
    workflow_template_id: Optional[str] = None


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