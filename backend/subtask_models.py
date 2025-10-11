from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Subtask(BaseModel):
    """Subtask model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: str
    organization_id: str
    title: str
    description: Optional[str] = None
    status: str = "todo"  # todo, in_progress, completed
    priority: str = "medium"  # low, medium, high, urgent
    assigned_to: Optional[str] = None  # user_id
    assigned_to_name: Optional[str] = None
    due_date: Optional[str] = None  # ISO date string
    order: int = 0  # For ordering subtasks
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    created_by: str
    created_by_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Nested subtasks support
    parent_subtask_id: Optional[str] = None  # For sub-subtasks
    level: int = 1  # Nesting level (1 = direct child of task, 2 = child of subtask, etc.)


class SubtaskCreate(BaseModel):
    """Create subtask"""
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    parent_subtask_id: Optional[str] = None  # For nested subtasks


class SubtaskUpdate(BaseModel):
    """Update subtask"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    order: Optional[int] = None


class SubtaskStats(BaseModel):
    """Subtask statistics"""
    total: int
    completed: int
    in_progress: int
    todo: int
    completion_percentage: float
