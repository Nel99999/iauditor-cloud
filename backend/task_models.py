from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
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