from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class OrganizationUnit(BaseModel):
    """Organization unit model (can be any level in hierarchy)"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    name: str
    description: Optional[str] = None
    level: int  # 1-5 (1=Company, 2=Region, 3=Location, 4=Department, 5=Team)
    parent_id: Optional[str] = None  # Parent unit ID
    path: str = ""  # Hierarchical path like /org/region/location
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationUnitCreate(BaseModel):
    """Create organization unit"""
    name: str
    description: Optional[str] = None
    level: int = Field(ge=1, le=5)  # Must be between 1 and 5
    parent_id: Optional[str] = None


class OrganizationUnitUpdate(BaseModel):
    """Update organization unit"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UserOrgAssignment(BaseModel):
    """User assignment to organization unit with role"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    organization_id: str
    unit_id: str  # Specific unit they belong to
    role: str  # admin, manager, inspector, viewer
    assigned_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserOrgAssignmentCreate(BaseModel):
    """Assign user to organization unit"""
    user_id: str
    unit_id: str
    role: str  # admin, manager, inspector, viewer


class UserInvitation(BaseModel):
    """User invitation model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    organization_id: str
    unit_id: str
    role: str
    invited_by: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending, accepted, expired
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserInvitationCreate(BaseModel):
    """Create user invitation"""
    email: str
    unit_id: str
    role: str


class OrganizationHierarchy(BaseModel):
    """Organization hierarchy tree structure"""
    id: str
    name: str
    description: Optional[str]
    level: int
    parent_id: Optional[str]
    children: List['OrganizationHierarchy'] = []
    user_count: int = 0


class PermissionCheck(BaseModel):
    """Permission check result"""
    has_permission: bool
    user_role: str
    unit_id: str



# ============================================================================
# ENHANCED OPTION B - ORGANIZATIONAL ENTITIES WITH RICH METADATA
# ============================================================================

class OrganizationalEntity(BaseModel):
    """Rich organizational entity (Profile, Organization, Company, Branch, Brand)"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    entity_type: str  # "profile", "organisation", "company", "branch", "brand"
    level: int  # 1-5
    
    # Core fields
    name: str
    description: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    
    # Contact & Location
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Business Details
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    established_date: Optional[str] = None
    industry: Optional[str] = None
    
    # Financial
    cost_center: Optional[str] = None
    budget_code: Optional[str] = None
    currency: Optional[str] = "USD"
    
    # Management
    default_manager_id: Optional[str] = None
    
    # Custom fields (metadata for flexibility)
    custom_fields: Optional[dict] = Field(default_factory=dict)
    
    # Hierarchy (managed separately in tree)
    parent_id: Optional[str] = None  # Set via tree linking
    
    # Status
    is_active: bool = True
    status: Optional[str] = "active"  # active, inactive, archived
    
    # Audit
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrganizationalEntityCreate(BaseModel):
    """Create organizational entity"""
    entity_type: str  # "profile", "organisation", "company", "branch", "brand"
    level: int = Field(ge=1, le=5)
    name: str
    description: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    
    # Contact & Location
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Business
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    industry: Optional[str] = None
    
    # Financial
    cost_center: Optional[str] = None
    budget_code: Optional[str] = None
    
    # Custom fields
    custom_fields: Optional[dict] = Field(default_factory=dict)


class OrganizationalEntityUpdate(BaseModel):
    """Update organizational entity"""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    industry: Optional[str] = None
    cost_center: Optional[str] = None
    budget_code: Optional[str] = None
    default_manager_id: Optional[str] = None
    custom_fields: Optional[dict] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class CustomFieldDefinition(BaseModel):
    """Custom field definition for extending entity types"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str  # Org-specific custom fields
    entity_type: str  # Which entity type this field applies to
    
    field_id: str  # Unique identifier for the field
    field_label: str  # Display label
    field_type: str  # text, number, date, select, multi_select, file, image, etc.
    field_group: str  # Which tab/section it belongs to
    
    required: bool = False
    default_value: Optional[str] = None
    options: Optional[List[str]] = None  # For select/multi_select types
    validation_rules: Optional[dict] = None  # Min, max, regex, etc.
    
    visible_to_roles: Optional[List[str]] = None  # Which roles can see this field
    editable_by_roles: Optional[List[str]] = None  # Which roles can edit
    
    order: int = 0  # Display order within group
    help_text: Optional[str] = None
    placeholder: Optional[str] = None
    
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CustomFieldDefinitionCreate(BaseModel):
    """Create custom field definition"""
    entity_type: str
    field_id: str
    field_label: str
    field_type: str
    field_group: str = "additional_info"
    required: bool = False
    default_value: Optional[str] = None
    options: Optional[List[str]] = None
    validation_rules: Optional[dict] = None
    visible_to_roles: Optional[List[str]] = None
    order: int = 0
    help_text: Optional[str] = None

    reason: Optional[str] = None