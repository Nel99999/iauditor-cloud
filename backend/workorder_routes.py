from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from workorder_models import WorkOrder, WorkOrderCreate, WorkOrderUpdate, WorkOrderStats
from auth_utils import get_current_user

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def generate_wo_number(org_id: str) -> str:
    """Generate work order number"""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
    random_suffix = str(uuid.uuid4())[:6].upper()
    return f"WO-{timestamp}-{random_suffix}"


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_work_order(
    wo_data: WorkOrderCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create work order"""
    user = await get_current_user(request, db)
    
    # Get asset details if provided
    asset_tag, asset_name = None, None
    if wo_data.asset_id:
        asset = await db.assets.find_one({"id": wo_data.asset_id}, {"_id": 0})
        if asset:
            asset_tag = asset.get("asset_tag")
            asset_name = asset.get("name")
    
    # Get assigned user name
    assigned_name = None
    if wo_data.assigned_to:
        assigned_user = await db.users.find_one({"id": wo_data.assigned_to}, {"name": 1})
        if assigned_user:
            assigned_name = assigned_user["name"]
    
    wo = WorkOrder(
        wo_number=generate_wo_number(user["organization_id"]),
        organization_id=user["organization_id"],
        title=wo_data.title,
        description=wo_data.description,
        work_type=wo_data.work_type,
        priority=wo_data.priority,
        asset_id=wo_data.asset_id,
        asset_tag=asset_tag,
        asset_name=asset_name,
        requested_by=user["id"],
        requested_by_name=user["name"],
        assigned_to=wo_data.assigned_to,
        assigned_to_name=assigned_name,
        unit_id=wo_data.unit_id,
        estimated_hours=wo_data.estimated_hours,
        causes_downtime=wo_data.causes_downtime,
        created_by=user["id"],
    )
    
    wo_dict = wo.model_dump()
    wo_dict["created_at"] = wo_dict["created_at"].isoformat()
    wo_dict["updated_at"] = wo_dict["updated_at"].isoformat()
    
    await db.work_orders.insert_one(wo_dict.copy())
    return wo_dict


@router.get("/stats/overview")
async def get_work_order_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get work order statistics"""
    user = await get_current_user(request, db)
    
    wos = await db.work_orders.find({"organization_id": user["organization_id"], "is_active": True}, {"_id": 0}).to_list(10000)
    
    by_status = {}
    by_type = {}
    for wo in wos:
        s = wo.get("status", "pending")
        by_status[s] = by_status.get(s, 0) + 1
        t = wo.get("work_type", "corrective")
        by_type[t] = by_type.get(t, 0) + 1
    
    backlog = len([w for w in wos if w.get("status") in ["pending", "approved", "scheduled"]])
    
    # Completed this month
    month_start = datetime.now(timezone.utc).replace(day=1).isoformat()
    completed_month = len([w for w in wos if w.get("completed_at") and w.get("completed_at") >= month_start])
    
    # Average hours
    hours = [w.get("actual_hours") for w in wos if w.get("actual_hours")]
    avg_hours = sum(hours) / len(hours) if hours else None
    
    stats = WorkOrderStats(
        total_work_orders=len(wos),
        by_status=by_status,
        by_type=by_type,
        backlog_count=backlog,
        completed_this_month=completed_month,
        average_completion_hours=round(avg_hours, 2) if avg_hours else None
    )
    
    return stats.model_dump()


@router.get("/backlog")
async def get_work_order_backlog(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get work order backlog"""
    user = await get_current_user(request, db)
    
    backlog = await db.work_orders.find(
        {
            "organization_id": user["organization_id"],
            "status": {"$in": ["pending", "approved", "scheduled"]},
            "is_active": True
        },
        {"_id": 0}
    ).sort("priority", -1).to_list(1000)
    
    return backlog


@router.get("")
async def list_work_orders(
    request: Request,
    status_filter: Optional[str] = None,
    work_type: Optional[str] = None,
    asset_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List work orders"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    if status_filter:
        query["status"] = status_filter
    if work_type:
        query["work_type"] = work_type
    if asset_id:
        query["asset_id"] = asset_id
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    work_orders = await db.work_orders.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return work_orders


@router.get("/{wo_id}")
async def get_work_order(
    wo_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get work order details"""
    user = await get_current_user(request, db)
    
    wo = await db.work_orders.find_one(
        {"id": wo_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not wo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    
    return wo


@router.put("/{wo_id}")
async def update_work_order(
    wo_id: str,
    wo_data: WorkOrderUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update work order"""
    user = await get_current_user(request, db)
    
    wo = await db.work_orders.find_one({"id": wo_id, "organization_id": user["organization_id"]})
    if not wo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    
    update_data = wo_data.model_dump(exclude_unset=True)
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.work_orders.update_one({"id": wo_id}, {"$set": update_data})
    
    updated = await db.work_orders.find_one({"id": wo_id}, {"_id": 0})
    return updated


@router.put("/{wo_id}/status")
async def change_status(
    wo_id: str,
    status_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Change work order status"""
    user = await get_current_user(request, db)
    
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status required")
    
    update_data = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
    
    if new_status == "in_progress" and not await db.work_orders.find_one({"id": wo_id, "actual_start": {"$ne": None}}):
        update_data["actual_start"] = datetime.now(timezone.utc).isoformat()
    elif new_status == "completed":
        update_data["actual_end"] = datetime.now(timezone.utc).isoformat()
        update_data["completed_by"] = user["id"]
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.work_orders.update_one({"id": wo_id}, {"$set": update_data})
    return await db.work_orders.find_one({"id": wo_id}, {"_id": 0})


@router.post("/{wo_id}/assign")
async def assign_work_order(
    wo_id: str,
    assign_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Assign work order to technician"""
    user = await get_current_user(request, db)
    
    assigned_to = assign_data.get("assigned_to")
    assigned_user = await db.users.find_one({"id": assigned_to}, {"name": 1})
    
    await db.work_orders.update_one(
        {"id": wo_id},
        {"$set": {
            "assigned_to": assigned_to,
            "assigned_to_name": assigned_user.get("name") if assigned_user else None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.work_orders.find_one({"id": wo_id}, {"_id": 0})


@router.post("/{wo_id}/add-labor")
async def add_labor_to_work_order(
    wo_id: str,
    labor_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add labor hours to work order"""
    user = await get_current_user(request, db)
    
    wo = await db.work_orders.find_one({"id": wo_id})
    hours = labor_data.get("hours", 0)
    rate = labor_data.get("hourly_rate", 0)
    cost = hours * rate
    
    # Handle None values properly
    current_labor_cost = wo.get("labor_cost") or 0
    current_actual_hours = wo.get("actual_hours") or 0
    current_parts_cost = wo.get("parts_cost") or 0
    
    new_labor_cost = current_labor_cost + cost
    new_actual_hours = current_actual_hours + hours
    new_total_cost = new_labor_cost + current_parts_cost
    
    await db.work_orders.update_one(
        {"id": wo_id},
        {"$set": {
            "labor_cost": new_labor_cost,
            "actual_hours": new_actual_hours,
            "total_cost": new_total_cost,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.work_orders.find_one({"id": wo_id}, {"_id": 0})


@router.post("/{wo_id}/add-parts")
async def add_parts_to_work_order(
    wo_id: str,
    parts_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add parts to work order"""
    user = await get_current_user(request, db)
    
    wo = await db.work_orders.find_one({"id": wo_id})
    parts_cost = parts_data.get("cost", 0)
    
    # Handle None values properly
    current_parts_cost = wo.get("parts_cost") or 0
    current_labor_cost = wo.get("labor_cost") or 0
    
    new_parts_cost = current_parts_cost + parts_cost
    new_total_cost = new_parts_cost + current_labor_cost
    
    await db.work_orders.update_one(
        {"id": wo_id},
        {"$set": {
            "parts_cost": new_parts_cost,
            "total_cost": new_total_cost,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.work_orders.find_one({"id": wo_id}, {"_id": 0})


@router.get("/{wo_id}/timeline")
async def get_work_order_timeline(
    wo_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get work order activity timeline"""
    user = await get_current_user(request, db)
    
    wo = await db.work_orders.find_one({"id": wo_id, "organization_id": user["organization_id"]}, {"_id": 0})
    if not wo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    
    # Get audit logs
    audit_logs = await db.audit_logs.find(
        {"resource_type": "work_order", "resource_id": wo_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"work_order": wo, "timeline": audit_logs}


