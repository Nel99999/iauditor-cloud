"""
Asset Register Models
Comprehensive asset management with 25+ fields
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, date
import uuid


class Asset(BaseModel):
    """Comprehensive asset model"""
    model_config = ConfigDict(extra="ignore")
    
    # Core fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    asset_tag: str  # Unique asset identifier
    name: str
    description: Optional[str] = None
    
    # Classification
    asset_type: str  # "equipment", "vehicle", "building", "infrastructure", etc.
    category: Optional[str] = None  # Sub-category
    criticality: str = "C"  # A (critical), B (important), C (normal)
    
    # Location
    unit_id: Optional[str] = None  # Organizational unit
    unit_name: Optional[str] = None  # Denormalized
    location_details: Optional[str] = None  # Building, floor, room
    gps_coordinates: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    
    # Hierarchy
    parent_asset_id: Optional[str] = None  # Parent asset if part of larger system
    has_children: bool = False
    
    # Technical details
    make: Optional[str] = None  # Manufacturer brand
    model: Optional[str] = None  # Model number
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None  # Technical specs
    
    # Financial
    purchase_date: Optional[str] = None  # YYYY-MM-DD
    purchase_cost: Optional[float] = None
    current_value: Optional[float] = None
    depreciation_rate: Optional[float] = None  # Annual percentage
    
    # Lifecycle
    status: str = "active"  # active, inactive, in_maintenance, retired, disposed
    installation_date: Optional[str] = None  # YYYY-MM-DD
    expected_life_years: Optional[int] = None
    
    # Maintenance
    maintenance_schedule: Optional[str] = None  # "weekly", "monthly", "quarterly", "annual"
    last_maintenance: Optional[str] = None  # YYYY-MM-DD
    next_maintenance: Optional[str] = None  # YYYY-MM-DD
    
    # Calibration
    requires_calibration: bool = False
    calibration_frequency: Optional[str] = None  # "monthly", "quarterly", "annual"
    next_calibration: Optional[str] = None  # YYYY-MM-DD
    
    # Metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    qr_code_generated: bool = False
    qr_code_url: Optional[str] = None
    photo_ids: List[str] = []  # GridFS photo IDs
    
    # Tracking
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssetCreate(BaseModel):
    """Create asset"""
    asset_tag: str
    name: str
    description: Optional[str] = None
    asset_type: str
    category: Optional[str] = None
    criticality: str = "C"
    unit_id: Optional[str] = None
    location_details: Optional[str] = None
    gps_coordinates: Optional[Dict[str, float]] = None
    parent_asset_id: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = None
    current_value: Optional[float] = None
    depreciation_rate: Optional[float] = None
    status: str = "active"
    installation_date: Optional[str] = None
    expected_life_years: Optional[int] = None
    maintenance_schedule: Optional[str] = None
    requires_calibration: bool = False
    calibration_frequency: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}


class AssetUpdate(BaseModel):
    """Update asset"""
    asset_tag: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    asset_type: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[str] = None
    unit_id: Optional[str] = None
    location_details: Optional[str] = None
    gps_coordinates: Optional[Dict[str, float]] = None
    parent_asset_id: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = None
    current_value: Optional[float] = None
    depreciation_rate: Optional[float] = None
    status: Optional[str] = None
    installation_date: Optional[str] = None
    expected_life_years: Optional[int] = None
    maintenance_schedule: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None
    requires_calibration: Optional[bool] = None
    calibration_frequency: Optional[str] = None
    next_calibration: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AssetStats(BaseModel):
    """Asset statistics"""
    total_assets: int
    by_type: Dict[str, int]
    by_criticality: Dict[str, int]
    by_status: Dict[str, int]
    total_value: float
    maintenance_due_count: int
    calibration_due_count: int


class AssetHistory(BaseModel):
    """Asset history entry"""
    entry_type: str  # "inspection", "checklist", "task", "work_order", "maintenance", "update"
    entry_id: str
    entry_name: str
    timestamp: str
    performed_by: Optional[str] = None
    notes: Optional[str] = None
