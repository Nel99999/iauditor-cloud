from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from contractor_models import Contractor
from auth_utils import get_current_user

router = APIRouter(prefix="/contractors", tags=["Contractors"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class ContractorCreate(BaseModel):
    """Create contractor"""
    name: str
    company_name: Optional[str] = None
    contractor_type: str = "service_provider"
    specialization: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    certification_number: Optional[str] = None
    certifications: List[str] = []
    insurance_details: Optional[Dict[str, Any]] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    hourly_rate: Optional[float] = None
    payment_terms: Optional[str] = None
    tags: List[str] = []


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contractor(
    contractor_data: ContractorCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create contractor"""
    user = await get_current_user(request, db)
    
    contractor = Contractor(
        organization_id=user["organization_id"],
        name=contractor_data.name,
        company_name=contractor_data.company_name,
        contractor_type=contractor_data.contractor_type,
        specialization=contractor_data.specialization,
        contact_person=contractor_data.contact_person,
        email=contractor_data.email,
        phone=contractor_data.phone,
        address=contractor_data.address,
        certification_number=contractor_data.certification_number,
        certifications=contractor_data.certifications,
        insurance_details=contractor_data.insurance_details,
        contract_start_date=contractor_data.contract_start_date,
        contract_end_date=contractor_data.contract_end_date,
        hourly_rate=contractor_data.hourly_rate,
        payment_terms=contractor_data.payment_terms,
        tags=contractor_data.tags,
        created_by=user["id"],
        onboarded_at=datetime.now(timezone.utc).isoformat(),
    )
    
    contractor_dict = contractor.model_dump()
    contractor_dict["created_at"] = contractor_dict["created_at"].isoformat()
    
    await db.contractors.insert_one(contractor_dict.copy())
    return contractor_dict


@router.get("")
async def list_contractors(
    request: Request,
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List contractors"""
    user = await get_current_user(request, db)
    
    filter_query = {"organization_id": user["organization_id"]}
    if status_filter:
        filter_query["status"] = status_filter
    
    contractors = await db.contractors.find(
        filter_query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return contractors


@router.get("/{contractor_id}")
async def get_contractor(
    contractor_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get contractor detail"""
    user = await get_current_user(request, db)
    
    contractor = await db.contractors.find_one(
        {"id": contractor_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    return contractor


@router.put("/{contractor_id}")
async def update_contractor(
    contractor_id: str,
    update_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update contractor"""
    user = await get_current_user(request, db)
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.contractors.update_one(
        {"id": contractor_id, "organization_id": user["organization_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    return await db.contractors.find_one({"id": contractor_id}, {"_id": 0})


@router.delete("/{contractor_id}")
async def delete_contractor(
    contractor_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete contractor"""
    user = await get_current_user(request, db)
    
    result = await db.contractors.delete_one(
        {"id": contractor_id, "organization_id": user["organization_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor not found"
        )
    
    return {"message": "Contractor deleted successfully"}
