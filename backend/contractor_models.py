from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Contractor(BaseModel):
    """Contractor/vendor model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    company_name: str
    contact_person: str
    email: str
    phone: str
    contractor_type: str  # maintenance, construction, cleaning, security
    trade: Optional[str] = None  # electrical, plumbing, HVAC
    
    # Insurance
    insurance_expiry: Optional[str] = None
    safety_rating: Optional[float] = None
    
    # Performance
    performance_score: float = 0.0
    completed_jobs: int = 0
    on_time_percentage: float = 0.0
    
    # Status
    status: str = "active"  # active, inactive
    onboarded_at: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
