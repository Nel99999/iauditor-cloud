from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid


class Webhook(BaseModel):
    """Webhook configuration model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    url: HttpUrl
    secret: str  # For signature verification
    events: List[str] = []  # List of event types to subscribe to
    is_active: bool = True
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    
    # Statistics
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery_at: Optional[datetime] = None
    last_delivery_status: Optional[str] = None
    
    # Metadata
    created_by: str
    created_by_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookCreate(BaseModel):
    """Create webhook"""
    name: str
    url: HttpUrl
    events: List[str]


class WebhookUpdate(BaseModel):
    """Update webhook"""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookDelivery(BaseModel):
    """Webhook delivery log"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    webhook_id: str
    organization_id: str
    event_type: str
    payload: Dict
    status: str  # pending, success, failed
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int = 0
    next_retry_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Available webhook events
WEBHOOK_EVENTS = [
    # User events
    "user.created",
    "user.updated",
    "user.deleted",
    "user.invited",
    
    # Task events
    "task.created",
    "task.updated",
    "task.completed",
    "task.deleted",
    
    # Inspection events
    "inspection.created",
    "inspection.completed",
    "inspection.updated",
    
    # Checklist events
    "checklist.created",
    "checklist.completed",
    
    # Workflow events
    "workflow.started",
    "workflow.approved",
    "workflow.rejected",
    "workflow.completed",
    
    # Group events
    "group.created",
    "group.updated",
    "group.member_added",
    "group.member_removed",
]
