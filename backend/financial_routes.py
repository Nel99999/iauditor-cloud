from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import uuid

from financial_models import FinancialTransaction
from auth_utils import get_current_user

router = APIRouter(prefix="/financial", tags=["Financial"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class FinancialTransactionCreate(BaseModel):
    """Create financial transaction"""
    transaction_type: str  # income, expense, budget, invoice
    category: str
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    reference_number: Optional[str] = None
    vendor: Optional[str] = None
    project_id: Optional[str] = None
    cost_center: Optional[str] = None
    transaction_date: Optional[str] = None
    payment_method: Optional[str] = None
    status: str = "pending"


@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: FinancialTransactionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create financial transaction"""
    user = await get_current_user(request, db)
    
    # Use current date if transaction_date not provided
    transaction_date = transaction_data.transaction_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    transaction = FinancialTransaction(
        transaction_number=f"TXN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
        organization_id=user["organization_id"],
        transaction_type=transaction_data.transaction_type,
        category=transaction_data.category,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        description=transaction_data.description,
        reference_number=transaction_data.reference_number,
        vendor=transaction_data.vendor,
        project_id=transaction_data.project_id,
        cost_center=transaction_data.cost_center,
        transaction_date=transaction_date,
        payment_method=transaction_data.payment_method,
        status=transaction_data.status,
        created_by=user["id"],
    )
    
    transaction_dict = transaction.model_dump()
    transaction_dict["created_at"] = transaction_dict["created_at"].isoformat()
    transaction_dict["updated_at"] = transaction_dict["updated_at"].isoformat()
    
    await db.financial_transactions.insert_one(transaction_dict.copy())
    return transaction_dict


@router.get("/transactions")
async def list_transactions(
    request: Request,
    limit: int = 50,
    transaction_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List financial transactions"""
    user = await get_current_user(request, db)
    
    filter_query = {"organization_id": user["organization_id"]}
    if transaction_type:
        filter_query["transaction_type"] = transaction_type
    
    transactions = await db.financial_transactions.find(
        filter_query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return transactions


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get transaction detail"""
    user = await get_current_user(request, db)
    
    transaction = await db.financial_transactions.find_one(
        {"id": transaction_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    update_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update transaction"""
    user = await get_current_user(request, db)
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.financial_transactions.update_one(
        {"id": transaction_id, "organization_id": user["organization_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return await db.financial_transactions.find_one({"id": transaction_id}, {"_id": 0})


@router.get("/summary")
async def get_financial_summary(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get financial summary"""
    user = await get_current_user(request, db)
    
    # Calculate totals
    pipeline = [
        {"$match": {"organization_id": user["organization_id"]}},
        {"$group": {
            "_id": "$transaction_type",
            "total": {"$sum": "$amount"},
            "count": {"$sum": 1}
        }}
    ]
    
    result = await db.financial_transactions.aggregate(pipeline).to_list(100)
    
    summary = {}
    for item in result:
        summary[item["_id"]] = {
            "total": item["total"],
            "count": item["count"]
        }
    
    return summary
