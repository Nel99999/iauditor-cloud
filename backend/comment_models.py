from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Comment(BaseModel):
    """Universal comment model for threaded discussions"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    
    # Linking
    resource_type: str  # "inspection", "checklist", "task", "project", etc.
    resource_id: str
    
    # Content
    text: str
    
    # Author
    user_id: str
    user_name: str  # Denormalized
    
    # Threading
    parent_comment_id: Optional[str] = None  # For threaded replies
    reply_count: int = 0
    
    # Mentions
    mentions: List[str] = []  # User IDs mentioned with @
    
    # Metadata
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommentCreate(BaseModel):
    """Create comment"""
    resource_type: str
    resource_id: str
    text: str
    parent_comment_id: Optional[str] = None
    mentions: List[str] = []


class CommentUpdate(BaseModel):
    """Update comment"""
    text: str
