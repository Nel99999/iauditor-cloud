from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class WorkOrder(BaseModel):
    """Work order model for CMMS"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wo_number: str  # Auto-generated
    organization_id: str
    title: str
    description: Optional[str] = None
    
    # Classification
    work_type: str = "corrective"  # corrective, preventive, predictive, project, emergency
    priority: str = "normal"  # low, normal, high, critical
    
    # Asset
    asset_id: Optional[str] = None
    asset_tag: Optional[str] = None
    asset_name: Optional[str] = None
    
    # Assignment
    requested_by: str
    requested_by_name: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    approved_by: Optional[str] = None
    completed_by: Optional[str] = None
    
    # Organization
    unit_id: Optional[str] = None
    location: Optional[str] = None
    
    # Status
    status: str = "pending"  # pending, approved, scheduled, in_progress, completed, cancelled
    
    # Scheduling
    scheduled_date: Optional[str] = None
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    
    # Costs
    labor_cost: float = 0.0
    parts_cost: float = 0.0
    total_cost: float = 0.0
    
    # Downtime
    causes_downtime: bool = False
    downtime_hours: Optional[float] = None
    
    # Workflow
    requires_approval: bool = False
    approval_status: Optional[str] = None
    
    # Linking
    source_inspection_id: Optional[str] = None
    source_incident_id: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None
    photo_ids: List[str] = []
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class WorkOrderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    work_type: str = "corrective"
    priority: str = "normal"
    asset_id: Optional[str] = None
    assigned_to: Optional[str] = None
    unit_id: Optional[str] = None
    estimated_hours: Optional[float] = None
    causes_downtime: bool = False


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    scheduled_date: Optional[str] = None
    actual_hours: Optional[float] = None
    notes: Optional[str] = None


class WorkOrderStats(BaseModel):
    total_work_orders: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    backlog_count: int
    completed_this_month: int
    average_completion_hours: Optional[float] = None
