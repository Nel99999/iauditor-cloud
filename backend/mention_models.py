from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Mention(BaseModel):
    """Mention model - tracks @mentions in comments"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    
    # Who mentioned
    mentioned_by_id: str
    mentioned_by_name: str
    
    # Who was mentioned
    mentioned_user_id: str
    mentioned_user_name: str
    
    # Where the mention occurred
    resource_type: str  # task, inspection, checklist, workflow
    resource_id: str
    resource_title: str
    
    # Comment context
    comment_id: str
    comment_text: str  # Store first 200 chars
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MentionCreate(BaseModel):
    """Create mention"""
    mentioned_user_ids: List[str]  # Support multiple mentions
    resource_type: str
    resource_id: str
    comment_id: str
    comment_text: str
