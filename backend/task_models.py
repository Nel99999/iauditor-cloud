from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, date
import uuid


class Task(BaseModel):
    """Task model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    title: str
    description: Optional[str] = None
    status: str = "todo"  # todo, in_progress, completed, blocked
    priority: str = "medium"  # low, medium, high, urgent
    assigned_to: Optional[str] = None  # user_id
    assigned_to_name: Optional[str] = None  # Denormalized
    created_by: str
    created_by_name: str
    due_date: Optional[str] = None  # YYYY-MM-DD
    unit_id: Optional[str] = None  # Organization unit
    tags: List[str] = []
    comments: List[dict] = []  # [{"user": "name", "text": "...", "created_at": "..."}]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Subtask tracking
    subtask_count: int = 0
    subtasks_completed: int = 0
    completion_percentage: float = 0.0
    
    # File attachments
    attachments: List[dict] = []  # [{"id": "...", "filename": "...", "url": "...", "uploaded_at": "..."}]
    
    # Dependencies
    depends_on: List[str] = []  # List of task IDs this task depends on
    blocked_by: List[str] = []  # List of task IDs blocking this task
    
    # Time tracking
    has_time_entries: bool = False
    total_time_minutes: int = 0
    estimated_time_minutes: Optional[int] = None
    
    # V1 Enhancement fields
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None
    task_type: str = "standard"  # "standard", "corrective_action", "project_task", "recurring"
    template_id: Optional[str] = None  # If created from template
    parent_task_id: Optional[str] = None  # For subtasks
    predecessor_task_ids: List[str] = []  # Dependencies
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    labor_cost: Optional[float] = None
    parts_used: List[Dict[str, Any]] = []  # [{part_id, quantity, cost}]
    requires_checklist: Optional[str] = None  # Checklist template ID
    linked_inspection_id: Optional[str] = None  # If created from inspection
    linked_incident_id: Optional[str] = None  # If corrective action
    photo_ids: List[str] = []  # GridFS file IDs
    signature_data: Optional[str] = None


class TaskCreate(BaseModel):
    """Create task"""
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    unit_id: Optional[str] = None
    tags: List[str] = []


class TaskUpdate(BaseModel):
    """Update task"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None



class TaskTemplate(BaseModel):
    """Recurring task template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    task_type: str = "recurring"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    unit_id: Optional[str] = None
    estimated_hours: Optional[float] = None
    recurrence_rule: str = "daily"  # daily, weekly, monthly
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskAnalytics(BaseModel):
    """Task analytics"""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    todo_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    average_completion_hours: Optional[float] = None
    on_time_percentage: float
    completion_trend: List[Dict[str, Any]] = []


class LaborEntry(BaseModel):
    """Labor time entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    user_id: str
    user_name: str
    hours: float
    hourly_rate: Optional[float] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    entry_date: str  # YYYY-MM-DD
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PartsUsage(BaseModel):
    """Parts used in task"""
    part_id: str
    part_name: str
    quantity: float
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    notes: Optional[str] = None

    unit_id: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskComment(BaseModel):
    """Add comment to task"""
    text: str


class TaskStats(BaseModel):
    """Task statistics"""
    total_tasks: int
    todo: int
    in_progress: int
    completed: int
    overdue: int
    completion_rate: float