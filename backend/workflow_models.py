from pydantic import BaseModel, Field, ConfigDict, field_validator, constr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


# =====================================
# WORKFLOW TEMPLATE MODELS
# =====================================

class WorkflowStep(BaseModel):
    """Individual step in workflow"""
    step_number: int
    name: str
    approver_role: str  # Role code that can approve this step
    approver_context: str = "organization"  # 'own', 'team', 'branch', 'region', 'organization'
    approval_type: str = "any"  # 'any' (any one approver) or 'all' (all must approve)
    timeout_hours: Optional[int] = 24
    escalate_to_role: Optional[str] = None  # Role to escalate to if timeout
    required_permissions: List[str] = []  # Additional permissions required
    conditions: Optional[Dict[str, Any]] = None  # Conditional logic
    
    @field_validator('approver_role', 'approver_context', 'approval_type')
    @classmethod
    def validate_non_empty(cls, v, info):
        if not v or (isinstance(v, str) and not v.strip()):
            field_name = info.field_name
            raise ValueError(f'{field_name} cannot be empty')
        return v


class WorkflowTemplate(BaseModel):
    """Reusable workflow template"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: str
    resource_type: str  # 'inspection', 'task', 'report', 'user_role_change', etc.
    trigger_conditions: Dict[str, Any] = {}  # When to start this workflow
    steps: List[Dict[str, Any]] = []  # Array of WorkflowStep dicts
    active: bool = True
    auto_start: bool = False  # Automatically start workflow when conditions met
    notify_on_start: bool = True
    notify_on_complete: bool = True
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorkflowTemplateCreate(BaseModel):
    name: str
    description: str
    resource_type: str
    trigger_conditions: Dict[str, Any] = {}
    steps: List[Dict[str, Any]]
    auto_start: bool = False
    notify_on_start: bool = True
    notify_on_complete: bool = True


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    active: Optional[bool] = None
    auto_start: Optional[bool] = None
    notify_on_start: Optional[bool] = None
    notify_on_complete: Optional[bool] = None


# =====================================
# WORKFLOW INSTANCE MODELS
# =====================================

class WorkflowStepCompletion(BaseModel):
    """Record of completed workflow step"""
    step_number: int
    step_name: str
    approved_by: str
    approved_by_name: str
    action: str  # 'approve', 'reject', 'request_changes'
    comments: Optional[str] = None
    approved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorkflowInstance(BaseModel):
    """Active workflow execution"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    template_id: str
    template_name: str
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None
    current_step: int = 1
    status: str = "pending"  # 'pending', 'in_progress', 'approved', 'rejected', 'cancelled', 'escalated'
    steps_completed: List[Dict[str, Any]] = []
    current_approvers: List[str] = []  # User IDs who can currently approve
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    due_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_by: str
    created_by_name: str


class WorkflowInstanceCreate(BaseModel):
    template_id: str
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None


class WorkflowApprovalAction(BaseModel):
    """Action taken on workflow step"""
    action: str  # 'approve', 'reject', 'request_changes', 'delegate'
    comments: Optional[str] = None
    delegate_to: Optional[str] = None  # User ID for delegation


# =====================================
# WORKFLOW STATISTICS
# =====================================

class WorkflowStats(BaseModel):
    """Workflow statistics"""
    total_workflows: int = 0
    pending_approvals: int = 0
    approved_today: int = 0
    rejected_today: int = 0
    average_approval_time_hours: Optional[float] = None
    escalated_workflows: int = 0


# =====================================
# DELEGATION MODELS
# =====================================

class Delegation(BaseModel):
    """Temporary authority delegation"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    delegator_id: str
    delegator_name: str
    delegate_id: str
    delegate_name: str
    workflow_types: List[str] = []  # Empty = all workflows
    resource_types: List[str] = []  # Empty = all resources
    valid_from: str
    valid_until: str
    reason: str
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DelegationCreate(BaseModel):
    delegate_id: str
    workflow_types: List[str] = []
    resource_types: List[str] = []
    valid_from: str
    valid_until: str
    reason: str


# =====================================
# CONTEXT PERMISSION MODELS
# =====================================

class PermissionContext(BaseModel):
    """Context-aware permission"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    user_id: str
    permission_id: str
    context_type: str  # 'own', 'team', 'branch', 'region', 'organization'
    context_id: Optional[str] = None  # ID of team/branch/region
    granted: bool = True
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    reason: Optional[str] = None
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PermissionContextCreate(BaseModel):
    user_id: str
    permission_id: str
    context_type: str
    context_id: Optional[str] = None
    granted: bool = True
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    reason: Optional[str] = None


# =====================================
# AUDIT TRAIL MODELS
# =====================================

class AuditLog(BaseModel):
    """Comprehensive audit log"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    user_id: str
    user_email: str
    user_name: str
    action: str  # 'workflow.start', 'workflow.approve', 'permission.check', etc.
    resource_type: str
    resource_id: str
    permission_checked: Optional[str] = None
    result: str  # 'granted', 'denied', 'success', 'failure'
    context: Dict[str, Any] = {}  # IP, user agent, branch_id, etc.
    changes: Optional[Dict[str, Any]] = None  # Before/after values
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLogCreate(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    permission_checked: Optional[str] = None
    result: str
    context: Dict[str, Any] = {}
    changes: Optional[Dict[str, Any]] = None
