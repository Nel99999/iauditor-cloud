"""
Training & Competency Models
Employee training program management
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class TrainingProgram(BaseModel):
    """Training program model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    
    # Basic info
    title: str
    description: Optional[str] = None
    training_type: str = "safety"  # Default value
    category: Optional[str] = None
    
    # Details
    duration_hours: Optional[float] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    
    # Requirements
    prerequisites: List[str] = []
    required_for_roles: List[str] = []
    certification_provided: bool = False
    certificate_valid_years: Optional[int] = None
    
    # Content
    modules: List[Dict[str, Any]] = []
    materials: List[str] = []
    
    # Scheduling
    is_recurring: bool = False
    frequency: Optional[str] = None
    
    # Status
    status: str = "active"
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingProgramCreate(BaseModel):
    """Create training program - only requires minimum fields"""
    title: str
    description: Optional[str] = None
    training_type: str = "safety"  # Default
    category: Optional[str] = None
    duration_hours: Optional[float] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    prerequisites: List[str] = []
    required_for_roles: List[str] = []
    certification_provided: bool = False
    certificate_valid_years: Optional[int] = None
    modules: List[Dict[str, Any]] = []
    is_recurring: bool = False
    frequency: Optional[str] = None


# Aliases for backward compatibility
TrainingCourse = TrainingProgram
TrainingCourseCreate = TrainingProgramCreate


class TrainingRecord(BaseModel):
    """Training attendance record"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    program_id: str
    user_id: str
    user_name: Optional[str] = None
    
    # Session details
    session_date: str
    completion_date: Optional[str] = None
    score: Optional[float] = None
    status: str = "registered"
    
    # Certification
    certificate_issued: bool = False
    certificate_number: Optional[str] = None
    certificate_expires_at: Optional[str] = None
    
    # Tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Alias for backward compatibility
EmployeeTraining = TrainingRecord


class TrainingStats(BaseModel):
    """Training statistics"""
    total_programs: int
    total_completions: int
    completion_rate: float
    by_type: Dict[str, int]
    by_status: Dict[str, int]
