from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class TrainingCourse(BaseModel):
    """Training course model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    course_code: str
    name: str
    description: Optional[str] = None
    course_type: str  # safety, technical, compliance, soft_skill
    duration_hours: float
    valid_for_years: Optional[int] = None
    required_for_roles: List[str] = []
    pass_score: Optional[float] = None
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmployeeTraining(BaseModel):
    """Employee training record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str
    course_id: str
    course_name: str
    completed_at: str
    score: Optional[float] = None
    passed: bool
    expires_at: Optional[str] = None
    instructor_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingCourseCreate(BaseModel):
    course_code: str
    name: str
    description: Optional[str] = None
    course_type: str
    duration_hours: float
    valid_for_years: Optional[int] = None


class TrainingStats(BaseModel):
    total_courses: int
    total_enrollments: int
    completed_this_month: int
    expired_certifications: int
