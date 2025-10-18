from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


class CapexRequest(BaseModel):
    """CAPEX request model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capex_number: str
    organization_id: str
    unit_id: str
    title: str
    description: str
    justification: str
    request_type: str  # new_asset, replacement, expansion, upgrade
    estimated_cost: float
    actual_cost: float = 0.0
    budget_year: int
    requested_by: str
    requested_by_name: str
    approval_status: str = "draft"  # draft, pending, approved, rejected
    status: str = "requested"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OpexTransaction(BaseModel):
    """OPEX transaction model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    unit_id: str
    category: str  # labor, materials, utilities, services, repairs
    amount: float
    transaction_date: str
    description: str
    work_order_id: Optional[str] = None
    project_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Budget(BaseModel):
    """Budget model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    unit_id: str
    fiscal_year: int
    category: str
    planned_amount: float
    actual_amount: float = 0.0
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
