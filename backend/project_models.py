from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class Project(BaseModel):
    """Project model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    project_code: str  # Auto-generated
    name: str
    description: Optional[str] = None
    
    # Classification
    project_type: str = "improvement"  # capital, improvement, maintenance, strategic
    status: str = "planning"  # planning, active, on_hold, completed, cancelled
    priority: str = "normal"
    
    # Ownership
    project_manager_id: str
    project_manager_name: str
    sponsor_id: Optional[str] = None
    unit_id: Optional[str] = None
    stakeholder_ids: List[str] = []
    
    # Timeline
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    
    # Financial
    budget: float = 0.0
    actual_cost: float = 0.0
    currency: str = "USD"
    
    # Progress
    completion_percentage: float = 0.0
    milestone_count: int = 0
    completed_milestones: int = 0
    task_count: int = 0
    completed_tasks: int = 0
    
    # Assets
    related_asset_ids: List[str] = []
    
    # Metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Milestone(BaseModel):
    """Project milestone"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    due_date: str
    status: str = "pending"  # pending, in_progress, completed, missed
    completion_percentage: float = 0.0
    order: int
    completed_at: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "improvement"
    priority: str = "normal"
    unit_id: Optional[str] = None
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    budget: float = 0.0


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    budget: Optional[float] = None


class ProjectStats(BaseModel):
    total_projects: int
    by_status: Dict[str, int]
    total_budget: float
    total_actual_cost: float
