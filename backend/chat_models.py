from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Channel(BaseModel):
    """Chat channel model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    channel_type: str = "team"  # team, project, incident, direct
    description: Optional[str] = None
    member_ids: List[str] = []
    owner_id: str
    entity_type: Optional[str] = None  # project, incident, work_order
    entity_id: Optional[str] = None
    is_private: bool = False
    is_archived: bool = False
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(BaseModel):
    """Chat message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    sender_id: str
    sender_name: str
    content: str
    mentions: List[str] = []  # User IDs
    parent_message_id: Optional[str] = None
    reply_count: int = 0
    attachment_ids: List[str] = []
    is_edited: bool = False
    is_deleted: bool = False
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
