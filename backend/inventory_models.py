from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class InventoryItem(BaseModel):
    """Inventory/spare parts model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    part_number: str
    description: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    unit_of_measure: str = "EA"  # EA, KG, L, M, etc.
    
    # Stock
    quantity_on_hand: float = 0.0
    quantity_reserved: float = 0.0
    quantity_available: float = 0.0
    
    # Reorder
    reorder_point: float = 0.0
    reorder_quantity: float = 0.0
    lead_time_days: int = 0
    
    # Storage
    warehouse_id: Optional[str] = None
    bin_location: Optional[str] = None
    
    # Financial
    unit_cost: float = 0.0
    total_value: float = 0.0
    
    # Asset linking
    compatible_asset_ids: List[str] = []
    
    # Metadata
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InventoryItemCreate(BaseModel):
    part_number: str
    description: str
    category: Optional[str] = None
    unit_of_measure: str = "EA"
    quantity_on_hand: float = 0.0
    reorder_point: float = 0.0
    reorder_quantity: float = 0.0
    unit_cost: float = 0.0


class InventoryItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity_on_hand: Optional[float] = None
    reorder_point: Optional[float] = None
    unit_cost: Optional[float] = None


class InventoryStats(BaseModel):
    total_items: int
    total_value: float
    items_below_reorder: int
    out_of_stock: int
