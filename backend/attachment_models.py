"""
Universal Attachment Service for All Modules
Provides file upload/management for inspections, checklists, tasks, etc.
Uses GridFS for storage
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Attachment(BaseModel):
    """Universal attachment model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    file_id: str  # GridFS file ID
    filename: str
    file_size: int  # Bytes
    content_type: str
    
    # Linking
    resource_type: str  # "inspection", "checklist", "task", "project", "asset", "incident", etc.
    resource_id: str  # ID of the linked resource
    
    # Metadata
    uploaded_by: str  # User ID
    uploaded_by_name: str  # Denormalized
    description: Optional[str] = None
    tags: List[str] = []
    
    # Organization
    is_public: bool = False  # Public to organization or private
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttachmentCreate(BaseModel):
    """Create attachment"""
    resource_type: str
    resource_id: str
    description: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False


class AttachmentStats(BaseModel):
    """Attachment statistics"""
    total_attachments: int
    total_size_bytes: int
    by_resource_type: dict
    recent_uploads: int  # Last 7 days
