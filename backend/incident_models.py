"""
Incident Management Models
Safety incident reporting and tracking
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class Incident(BaseModel):
    """Incident model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    incident_number: str  # Auto-generated unique number
    
    # Basic info
    title: str
    description: str
    incident_type: str = "safety"  # Default value
    severity: str = "low"  # Default value
    
    # Location
    location: Optional[str] = None
    unit_id: Optional[str] = None
    asset_id: Optional[str] = None
    
    # People involved
    reported_by: str
    reported_by_name: Optional[str] = None
    involved_persons: List[Dict[str, Any]] = []
    witnesses: List[str] = []
    
    # Dates
    occurred_at: str
    reported_at: str
    
    # Status
    status: str = "open"
    priority: str = "medium"
    
    # Investigation
    root_cause: Optional[str] = None
    corrective_actions: List[Dict[str, Any]] = []
    assigned_to: Optional[str] = None
    
    # Tracking
    tags: List[str] = []
    attachments: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IncidentCreate(BaseModel):
    """Create incident - only requires minimum fields"""
    title: str
    description: str
    incident_type: str = "safety"  # Default
    severity: str = "low"  # Default
    location: Optional[str] = None
    unit_id: Optional[str] = None
    asset_id: Optional[str] = None
    occurred_at: Optional[str] = None  # Make optional with default
    involved_persons: List[Dict[str, Any]] = []
    witnesses: List[str] = []
    priority: str = "medium"
    tags: List[str] = []


class IncidentUpdate(BaseModel):
    """Update incident"""
    title: Optional[str] = None
    description: Optional[str] = None
    incident_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    root_cause: Optional[str] = None
    assigned_to: Optional[str] = None
    corrective_actions: Optional[List[Dict[str, Any]]] = None
