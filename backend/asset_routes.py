"""
Asset Register Routes
10 endpoints for comprehensive asset management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import uuid
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

from asset_models import Asset, AssetCreate, AssetUpdate, AssetStats, AssetHistory
from auth_utils import get_current_user

router = APIRouter(prefix="/assets", tags=["Assets"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new asset"""
    user = await get_current_user(request, db)
    
    # Check if asset_tag already exists
    existing = await db.assets.find_one({
        "asset_tag": asset_data.asset_tag,
        "organization_id": user["organization_id"]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset tag '{asset_data.asset_tag}' already exists",
        )
    
    # Get unit name if provided
    unit_name = None
    if asset_data.unit_id:
        unit = await db.organization_units.find_one(
            {"id": asset_data.unit_id},
            {"_id": 0, "name": 1}
        )
        unit_name = unit.get("name") if unit else None
    
    # Create asset
    asset = Asset(
        organization_id=user["organization_id"],
        asset_tag=asset_data.asset_tag,
        name=asset_data.name,
        description=asset_data.description,
        asset_type=asset_data.asset_type,
        category=asset_data.category,
        criticality=asset_data.criticality,
        unit_id=asset_data.unit_id,
        unit_name=unit_name,
        location_details=asset_data.location_details,
        gps_coordinates=asset_data.gps_coordinates,
        parent_asset_id=asset_data.parent_asset_id,
        make=asset_data.make,
        model=asset_data.model,
        serial_number=asset_data.serial_number,
        manufacturer=asset_data.manufacturer,
        specifications=asset_data.specifications,
        purchase_date=asset_data.purchase_date,
        purchase_cost=asset_data.purchase_cost,
        current_value=asset_data.current_value or asset_data.purchase_cost,
        depreciation_rate=asset_data.depreciation_rate,
        status=asset_data.status,
        installation_date=asset_data.installation_date,
        expected_life_years=asset_data.expected_life_years,
        maintenance_schedule=asset_data.maintenance_schedule,
        requires_calibration=asset_data.requires_calibration,
        calibration_frequency=asset_data.calibration_frequency,
        tags=asset_data.tags,
        custom_fields=asset_data.custom_fields,
        created_by=user["id"],
    )
    
    asset_dict = asset.model_dump()
    asset_dict["created_at"] = asset_dict["created_at"].isoformat()
    asset_dict["updated_at"] = asset_dict["updated_at"].isoformat()
    
    # Update parent if this is a child asset
    if asset_data.parent_asset_id:
        await db.assets.update_one(
            {"id": asset_data.parent_asset_id},
            {"$set": {"has_children": True}}
        )
    
    await db.assets.insert_one(asset_dict.copy())
    return asset_dict


@router.get("")
async def list_assets(
    request: Request,
    asset_type: Optional[str] = None,
    criticality: Optional[str] = None,
    status_filter: Optional[str] = None,
    unit_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List assets with filters"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    
    if asset_type:
        query["asset_type"] = asset_type
    if criticality:
        query["criticality"] = criticality
    if status_filter:
        query["status"] = status_filter
    if unit_id:
        query["unit_id"] = unit_id
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"asset_tag": {"$regex": search, "$options": "i"}},
            {"serial_number": {"$regex": search, "$options": "i"}},
        ]
    
    assets = await db.assets.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return assets


@router.get("/types/catalog")
async def get_asset_types(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get asset type catalog"""
    user = await get_current_user(request, db)
    
    # Get unique asset types from existing assets
    pipeline = [
        {"$match": {"organization_id": user["organization_id"]}},
        {"$group": {
            "_id": "$asset_type",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    types = await db.assets.aggregate(pipeline).to_list(100)
    
    # Standard asset types
    standard_types = [
        {"value": "equipment", "label": "Equipment"},
        {"value": "vehicle", "label": "Vehicle"},
        {"value": "building", "label": "Building"},
        {"value": "infrastructure", "label": "Infrastructure"},
        {"value": "machinery", "label": "Machinery"},
        {"value": "tools", "label": "Tools"},
        {"value": "ict", "label": "ICT/Electronics"},
        {"value": "furniture", "label": "Furniture"},
        {"value": "safety", "label": "Safety Equipment"},
    ]
    
    # Merge with existing types
    existing_types = [{"value": t["_id"], "label": t["_id"].title(), "count": t["count"]} for t in types if t["_id"]]
    
    return {
        "standard_types": standard_types,
        "organization_types": existing_types
    }


@router.get("/stats")
async def get_asset_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get asset statistics"""
    user = await get_current_user(request, db)
    
    assets = await db.assets.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).to_list(10000)
    
    total = len(assets)
    
    # By type
    by_type = {}
    for a in assets:
        t = a.get("asset_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    
    # By criticality
    by_criticality = {"A": 0, "B": 0, "C": 0}
    for a in assets:
        c = a.get("criticality", "C")
        by_criticality[c] = by_criticality.get(c, 0) + 1
    
    # By status
    by_status = {}
    for a in assets:
        s = a.get("status", "active")
        by_status[s] = by_status.get(s, 0) + 1
    
    # Total value
    total_value = sum(a.get("current_value", 0) or 0 for a in assets)
    
    # Maintenance due
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    maintenance_due = len([
        a for a in assets
        if a.get("next_maintenance") and a.get("next_maintenance") <= today
    ])
    
    # Calibration due
    calibration_due = len([
        a for a in assets
        if a.get("requires_calibration") and a.get("next_calibration") and a.get("next_calibration") <= today
    ])
    
    stats = AssetStats(
        total_assets=total,
        by_type=by_type,
        by_criticality=by_criticality,
        by_status=by_status,
        total_value=round(total_value, 2),
        maintenance_due_count=maintenance_due,
        calibration_due_count=calibration_due
    )
    
    return stats.model_dump()


@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get asset details"""
    user = await get_current_user(request, db)
    
    asset = await db.assets.find_one(
        {"id": asset_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    return asset


@router.put("/{asset_id}")
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an asset"""
    user = await get_current_user(request, db)
    
    asset = await db.assets.find_one(
        {"id": asset_id, "organization_id": user["organization_id"]}
    )
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    update_data = asset_data.model_dump(exclude_unset=True)
    
    # Update unit name if unit changed
    if "unit_id" in update_data and update_data["unit_id"]:
        unit = await db.organization_units.find_one(
            {"id": update_data["unit_id"]},
            {"_id": 0, "name": 1}
        )
        update_data["unit_name"] = unit.get("name") if unit else None
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.assets.update_one(
            {"id": asset_id},
            {"$set": update_data}
        )
    
    updated = await db.assets.find_one({"id": asset_id}, {"_id": 0})
    return updated


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Soft delete an asset"""
    user = await get_current_user(request, db)
    
    asset = await db.assets.find_one(
        {"id": asset_id, "organization_id": user["organization_id"]}
    )
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    await db.assets.update_one(
        {"id": asset_id},
        {"$set": {
            "is_active": False,
            "status": "retired",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Asset deleted successfully"}


@router.get("/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get complete asset history (inspections, tasks, work orders, etc.)"""
    user = await get_current_user(request, db)
    
    # Verify asset exists
    asset = await db.assets.find_one(
        {"id": asset_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    history = []
    
    # Get inspections
    inspections = await db.inspection_executions.find(
        {"asset_id": asset_id},
        {"_id": 0}
    ).to_list(1000)
    
    for insp in inspections:
        history.append({
            "entry_type": "inspection",
            "entry_id": insp["id"],
            "entry_name": insp["template_name"],
            "timestamp": insp.get("completed_at") or insp.get("started_at"),
            "performed_by": insp.get("inspector_name"),
            "notes": f"Score: {insp.get('score', 'N/A')}%, Status: {insp.get('status')}"
        })
    
    # Get tasks
    tasks = await db.tasks.find(
        {"asset_id": asset_id},
        {"_id": 0}
    ).to_list(1000)
    
    for task in tasks:
        history.append({
            "entry_type": "task",
            "entry_id": task["id"],
            "entry_name": task["title"],
            "timestamp": task.get("completed_at") or task.get("created_at"),
            "performed_by": task.get("assigned_to_name"),
            "notes": f"Status: {task.get('status')}"
        })
    
    # Get work orders (when CMMS is built)
    work_orders = await db.work_orders.find(
        {"asset_id": asset_id},
        {"_id": 0}
    ).to_list(1000)
    
    for wo in work_orders:
        history.append({
            "entry_type": "work_order",
            "entry_id": wo.get("id"),
            "entry_name": wo.get("title", "Work Order"),
            "timestamp": wo.get("created_at"),
            "performed_by": None,
            "notes": f"Status: {wo.get('status')}"
        })
    
    # Sort by timestamp descending
    history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {
        "asset": asset,
        "history": history,
        "total_entries": len(history)
    }


@router.post("/{asset_id}/qr-code")
async def generate_qr_code(
    asset_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Generate QR code for asset"""
    user = await get_current_user(request, db)
    
    asset = await db.assets.find_one(
        {"id": asset_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_data = f"ASSET:{asset['asset_tag']}:{asset_id}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Update asset with QR code status
    await db.assets.update_one(
        {"id": asset_id},
        {"$set": {
            "qr_code_generated": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return StreamingResponse(buffer, media_type="image/png")


@router.post("/import")
async def bulk_import_assets(
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk import assets from CSV"""
    user = await get_current_user(request, db)
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )
    
    # Read CSV content
    content = await file.read()
    import csv
    from io import StringIO
    
    csv_data = StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    imported = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            # Create asset from row
            asset_data = AssetCreate(
                asset_tag=row.get('asset_tag', ''),
                name=row.get('name', ''),
                description=row.get('description'),
                asset_type=row.get('asset_type', 'equipment'),
                criticality=row.get('criticality', 'C'),
                make=row.get('make'),
                model=row.get('model'),
                serial_number=row.get('serial_number'),
            )
            
            # Create using existing endpoint logic
            await create_asset(asset_data, request, db)
            imported += 1
            
        except Exception as e:
            errors.append({
                "row": row_num,
                "error": str(e)
            })
    
    return {
        "imported": imported,
        "failed": len(errors),
        "errors": errors
    }
