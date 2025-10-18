from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

from contractor_models import Contractor
from auth_utils import get_current_user

router = APIRouter(prefix="/contractors", tags=["Contractors"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contractor(
    contractor_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create contractor"""
    user = await get_current_user(request, db)
    
    contractor = Contractor(
        organization_id=user["organization_id"],
        company_name=contractor_data.get("company_name"),
        contact_person=contractor_data.get("contact_person"),
        email=contractor_data.get("email"),
        phone=contractor_data.get("phone"),
        contractor_type=contractor_data.get("contractor_type"),
        trade=contractor_data.get("trade"),
        onboarded_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    
    contractor_dict = contractor.model_dump()
    contractor_dict["created_at"] = contractor_dict["created_at"].isoformat()
    
    await db.contractors.insert_one(contractor_dict.copy())
    return contractor_dict


@router.get("")
async def list_contractors(
    request: Request,
    contractor_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List contractors"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "status": "active"}
    if contractor_type:
        query["contractor_type"] = contractor_type
    
    contractors = await db.contractors.find(query, {"_id": 0}).to_list(1000)
    return contractors


@router.get("/{contractor_id}")
async def get_contractor(
    contractor_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get contractor details"""
    user = await get_current_user(request, db)
    
    contractor = await db.contractors.find_one(
        {"id": contractor_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not contractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contractor not found")
    
    return contractor


@router.get("/{contractor_id}/work-history")
async def get_contractor_work_history(
    contractor_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get contractor work history"""
    user = await get_current_user(request, db)
    
    # Get work orders assigned to this contractor
    work_orders = await db.work_orders.find(
        {"assigned_to": contractor_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    return work_orders
