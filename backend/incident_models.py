from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class Incident(BaseModel):
    """Incident/safety event model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_number: str
    organization_id: str
    unit_id: str
    
    # Classification
    incident_type: str  # "injury", "near_miss", "property_damage", "environmental"
    severity: str  # "minor", "moderate", "serious", "critical"
    
    # Event
    occurred_at: str
    location: str
    description: str
    
    # People
    reported_by: str
    reporter_name: str
    
    # Investigation
    investigation_status: str = "not_started"
    
    # Corrective Actions
    corrective_action_task_ids: List[str] = []
    
    # Status
    status: str = "reported"
    
    # Metadata
    photo_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IncidentCreate(BaseModel):
    incident_type: str
    severity: str
    occurred_at: str
    location: str
    description: str
    unit_id: Optional[str] = None


class IncidentStats(BaseModel):
    total_incidents: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    this_month: int
