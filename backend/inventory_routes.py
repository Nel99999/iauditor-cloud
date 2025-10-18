from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional
import uuid

from inventory_models import InventoryItem, InventoryItemCreate, InventoryItemUpdate, InventoryStats
from auth_utils import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create inventory item"""
    user = await get_current_user(request, db)
    
    # Check if part number exists
    existing = await db.inventory_items.find_one({
        "part_number": item_data.part_number,
        "organization_id": user["organization_id"]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Part number '{item_data.part_number}' already exists"
        )
    
    item = InventoryItem(
        organization_id=user["organization_id"],
        part_number=item_data.part_number,
        description=item_data.description,
        category=item_data.category,
        unit_of_measure=item_data.unit_of_measure,
        quantity_on_hand=item_data.quantity_on_hand,
        quantity_available=item_data.quantity_on_hand,
        reorder_point=item_data.reorder_point,
        reorder_quantity=item_data.reorder_quantity,
        unit_cost=item_data.unit_cost,
        total_value=item_data.quantity_on_hand * item_data.unit_cost,
        created_by=user["id"],
    )
    
    item_dict = item.model_dump()
    item_dict["created_at"] = item_dict["created_at"].isoformat()
    item_dict["updated_at"] = item_dict["updated_at"].isoformat()
    
    await db.inventory_items.insert_one(item_dict.copy())
    return item_dict


@router.get("/stats")
async def get_inventory_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inventory statistics"""
    user = await get_current_user(request, db)
    
    items = await db.inventory_items.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(items)
    total_value = sum(i.get("total_value", 0) for i in items)
    below_reorder = len([i for i in items if i.get("quantity_available", 0) <= i.get("reorder_point", 0)])
    out_of_stock = len([i for i in items if i.get("quantity_available", 0) == 0])
    
    stats = InventoryStats(
        total_items=total,
        total_value=round(total_value, 2),
        items_below_reorder=below_reorder,
        out_of_stock=out_of_stock
    )
    
    return stats.model_dump()


@router.get("/items/reorder")
async def get_reorder_items(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get items below reorder point"""
    user = await get_current_user(request, db)
    
    items = await db.inventory_items.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    reorder_items = [i for i in items if i.get("quantity_available", 0) <= i.get("reorder_point", 0)]
    
    return reorder_items


@router.get("/items")
async def list_inventory_items(
    request: Request,
    category: Optional[str] = None,
    below_reorder: bool = False,
    search: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List inventory items"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"part_number": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    
    items = await db.inventory_items.find(query, {"_id": 0}).sort("part_number", 1).limit(limit).to_list(limit)
    
    if below_reorder:
        items = [i for i in items if i.get("quantity_available", 0) <= i.get("reorder_point", 0)]
    
    return items


@router.get("/items/{item_id}")
async def get_inventory_item(
    item_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get inventory item"""
    user = await get_current_user(request, db)
    
    item = await db.inventory_items.find_one(
        {"id": item_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return item


@router.put("/items/{item_id}")
async def update_inventory_item(
    item_id: str,
    item_data: InventoryItemUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update inventory item"""
    user = await get_current_user(request, db)
    
    item = await db.inventory_items.find_one({"id": item_id, "organization_id": user["organization_id"]})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    update_data = item_data.model_dump(exclude_unset=True)
    
    # Recalculate totals
    if "quantity_on_hand" in update_data or "unit_cost" in update_data:
        qty = update_data.get("quantity_on_hand", item.get("quantity_on_hand", 0))
        cost = update_data.get("unit_cost", item.get("unit_cost", 0))
        update_data["total_value"] = qty * cost
        update_data["quantity_available"] = qty - item.get("quantity_reserved", 0)
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.inventory_items.update_one({"id": item_id}, {"$set": update_data})
    
    return await db.inventory_items.find_one({"id": item_id}, {"_id": 0})


@router.post("/items/{item_id}/adjust")
async def adjust_stock(
    item_id: str,
    adjustment_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Adjust stock levels"""
    user = await get_current_user(request, db)
    
    item = await db.inventory_items.find_one({"id": item_id, "organization_id": user["organization_id"]})
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    adjustment = adjustment_data.get("adjustment", 0)
    new_qty = item.get("quantity_on_hand", 0) + adjustment
    new_available = new_qty - item.get("quantity_reserved", 0)
    new_value = new_qty * item.get("unit_cost", 0)
    
    await db.inventory_items.update_one(
        {"id": item_id},
        {"$set": {
            "quantity_on_hand": new_qty,
            "quantity_available": new_available,
            "total_value": new_value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.inventory_items.find_one({"id": item_id}, {"_id": 0})


