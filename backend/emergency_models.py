from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Emergency(BaseModel):
    """Emergency event model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emergency_number: str
    organization_id: str
    unit_id: Optional[str] = None
    emergency_type: str  # fire, medical, chemical_spill, evacuation, natural_disaster
    severity: str  # low, moderate, high, critical
    occurred_at: str
    location: Optional[str] = None
    reported_by: str
    reporter_name: str
    status: str = "active"  # active, contained, resolved, closed
    description: str
    actions_taken: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[str] = None
