from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class InspectionQuestion(BaseModel):
    """Individual question in an inspection template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str  # text, number, yes_no, multiple_choice, photo, signature
    required: bool = True
    options: Optional[List[str]] = None  # For multiple_choice
    scoring_enabled: bool = False
    pass_score: Optional[float] = None  # If scoring enabled
    order: int = 0
    # Enhanced fields
    photo_required: bool = False  # NEW: Require photo for this question
    min_photos: int = 0  # NEW: Minimum photos required
    max_photos: int = 10  # NEW: Maximum photos allowed
    signature_required: bool = False  # NEW: Require signature
    conditional_logic: Optional[Dict[str, Any]] = None  # NEW: {show_if: {question_id: value}}
    help_text: Optional[str] = None  # NEW: Helper text for inspectors


class InspectionQuestionCreate(BaseModel):
    """Create inspection question"""
    question_text: str
    question_type: str
    required: bool = True
    options: Optional[List[str]] = None
    scoring_enabled: bool = False
    pass_score: Optional[float] = None
    order: int = 0
    # Enhanced fields
    photo_required: bool = False
    min_photos: int = 0
    max_photos: int = 10
    signature_required: bool = False
    conditional_logic: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None


class InspectionTemplate(BaseModel):
    """Inspection template model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None  # safety, quality, maintenance, etc.
    questions: List[InspectionQuestion] = []
    scoring_enabled: bool = False
    pass_percentage: Optional[float] = None  # Minimum to pass (e.g., 80.0)
    require_gps: bool = False
    require_photos: bool = False
    requires_approval: bool = False  # Requires workflow approval
    workflow_template_id: Optional[str] = None  # Workflow template to use
    # Enhanced fields for V1
    unit_ids: List[str] = []  # NEW: Which units use this template
    asset_type_ids: List[str] = []  # NEW: Which asset types this applies to
    recurrence_rule: Optional[str] = None  # NEW: "daily", "weekly", "monthly", cron
    auto_assign_logic: Optional[str] = None  # NEW: "round_robin", "least_loaded", "specific_users"
    assigned_inspector_ids: List[str] = []  # NEW: Pre-assigned inspectors
    requires_competency: Optional[str] = None  # NEW: Competency required to perform
    estimated_duration_minutes: Optional[int] = None  # NEW: Expected duration
    auto_create_work_order_on_fail: bool = False  # NEW: Auto-create WO if fails
    work_order_priority: Optional[str] = None  # NEW: Priority for auto-created WO
    version: int = 1
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InspectionTemplateCreate(BaseModel):
    """Create inspection template"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    questions: List[InspectionQuestionCreate] = []
    scoring_enabled: bool = False
    pass_percentage: Optional[float] = None
    require_gps: bool = False
    require_photos: bool = False
    auto_create_work_order_on_fail: bool = False
    work_order_priority: Optional[str] = None


class InspectionTemplateUpdate(BaseModel):
    """Update inspection template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    questions: Optional[List[InspectionQuestionCreate]] = None
    scoring_enabled: Optional[bool] = None
    pass_percentage: Optional[float] = None
    require_gps: Optional[bool] = None
    require_photos: Optional[bool] = None
    is_active: Optional[bool] = None
    # V1 Enhancement fields
    unit_ids: Optional[List[str]] = None
    asset_type_ids: Optional[List[str]] = None
    recurrence_rule: Optional[str] = None
    auto_assign_logic: Optional[str] = None
    assigned_inspector_ids: Optional[List[str]] = None
    requires_competency: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    auto_create_work_order_on_fail: Optional[bool] = None
    work_order_priority: Optional[str] = None


class InspectionAnswer(BaseModel):
    """Answer to an inspection question"""
    question_id: str
    answer: Any  # Can be string, number, boolean, list
    photo_ids: Optional[List[str]] = []  # GridFS file IDs
    notes: Optional[str] = None
    score: Optional[float] = None
    signature_data: Optional[str] = None  # NEW: Base64 encoded signature image
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # NEW: When answered


class InspectionExecution(BaseModel):
    """Inspection execution/instance model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    template_id: str
    template_name: str  # Denormalized for reporting
    template_version: int
    unit_id: Optional[str] = None  # Which org unit was inspected
    unit_name: Optional[str] = None  # NEW: Denormalized unit name
    inspector_id: str  # User who performed inspection
    inspector_name: str  # Denormalized
    status: str = "in_progress"  # in_progress, completed, pending_approval, approved, rejected, failed
    answers: List[InspectionAnswer] = []
    location: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    score: Optional[float] = None  # Overall score if scoring enabled
    passed: Optional[bool] = None  # Pass/fail status
    findings: List[str] = []  # List of issues found
    notes: Optional[str] = None
    workflow_id: Optional[str] = None  # Linked workflow instance
    # Enhanced fields for V1
    asset_id: Optional[str] = None  # NEW: Asset being inspected
    asset_name: Optional[str] = None  # NEW: Denormalized asset name
    due_date: Optional[datetime] = None  # NEW: When inspection is due
    scheduled_date: Optional[datetime] = None  # NEW: Scheduled date/time
    auto_created_wo_id: Optional[str] = None  # NEW: Link to work order if created
    follow_up_inspection_id: Optional[str] = None  # NEW: Follow-up inspection if required
    parent_inspection_id: Optional[str] = None  # NEW: If this is a follow-up
    rectification_required: bool = False  # NEW: Whether issues need fixing
    rectified: bool = False  # NEW: Whether issues have been fixed
    duration_minutes: Optional[int] = None  # NEW: Actual time taken
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InspectionExecutionCreate(BaseModel):
    """Start an inspection"""
    template_id: str
    unit_id: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    asset_id: Optional[str] = None  # NEW: Asset being inspected
    scheduled_date: Optional[datetime] = None  # NEW: Scheduled date/time


class InspectionExecutionUpdate(BaseModel):
    """Update inspection execution"""
    answers: Optional[List[InspectionAnswer]] = None
    location: Optional[Dict[str, float]] = None
    notes: Optional[str] = None


class InspectionExecutionComplete(BaseModel):
    """Complete an inspection"""
    answers: List[InspectionAnswer]
    findings: Optional[List[str]] = []
    notes: Optional[str] = None


class InspectionStats(BaseModel):
    """Inspection statistics"""
    total_inspections: int
    completed_today: int
    pending: int
    pass_rate: float
    average_score: Optional[float] = None


class InspectionSchedule(BaseModel):
    """Recurring inspection schedule"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    template_id: str
    template_name: str
    unit_ids: List[str] = []  # Units to schedule for
    recurrence_rule: str  # "daily", "weekly", "monthly", "custom_cron"
    recurrence_details: Optional[Dict[str, Any]] = None  # {day_of_week: 1, time: "09:00"}
    assigned_inspector_ids: List[str] = []  # Auto-assign to these inspectors
    auto_assign_logic: str = "round_robin"  # "round_robin", "least_loaded", "specific"
    next_due_date: Optional[datetime] = None
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateAnalytics(BaseModel):
    """Analytics for inspection template"""
    template_id: str
    template_name: str
    total_executions: int
    completed_executions: int
    in_progress_executions: int
    average_score: Optional[float] = None
    pass_rate: float
    average_duration_minutes: Optional[int] = None
    most_common_findings: List[Dict[str, Any]] = []  # [{finding: str, count: int}]
    completion_trend: List[Dict[str, Any]] = []  # [{date: str, count: int}]


class InspectionCalendarItem(BaseModel):
    """Calendar view item"""
    id: str
    template_id: str
    template_name: str
    due_date: datetime
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    status: str  # "scheduled", "in_progress", "completed", "overdue"
    unit_id: Optional[str] = None
    unit_name: Optional[str] = None
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None