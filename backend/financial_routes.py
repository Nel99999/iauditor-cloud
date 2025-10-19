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



@router.get("/stats")
async def get_financial_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get financial statistics"""
    user = await get_current_user(request, db)
    
    transactions = await db.financial_transactions.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total_transactions = len(transactions)
    total_revenue = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "income")
    total_expenses = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "expense")
    net_income = total_revenue - total_expenses
    
    # By type
    by_type = {}
    for t in transactions:
        t_type = t.get("transaction_type", "unknown")
        by_type[t_type] = by_type.get(t_type, 0) + 1
    
    # By category
    by_category = {}
    for t in transactions:
        category = t.get("category", "uncategorized")
        by_category[category] = by_category.get(category, 0) + 1
    
    return {
        "total_transactions": total_transactions,
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_income": round(net_income, 2),
        "by_type": by_type,
        "by_category": by_category
    }



# CAPEX endpoints
class CAPEXCreate(BaseModel):
    """Create CAPEX request"""
    title: str
    description: Optional[str] = None
    category: str = "equipment"
    estimated_cost: float
    justification: Optional[str] = None
    budget_year: int
    priority: str = "medium"


@router.post("/capex", status_code=status.HTTP_201_CREATED)
async def create_capex_request(
    capex_data: CAPEXCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create CAPEX request"""
    user = await get_current_user(request, db)
    
    capex = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "request_number": f"CAP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        "title": capex_data.title,
        "description": capex_data.description,
        "category": capex_data.category,
        "estimated_cost": capex_data.estimated_cost,
        "justification": capex_data.justification,
        "budget_year": capex_data.budget_year,
        "priority": capex_data.priority,
        "status": "pending",
        "requested_by": user["id"],
        "requested_by_name": user.get("name", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.financial_capex.insert_one(capex.copy())
    return capex


@router.get("/capex")
async def list_capex_requests(
    request: Request,
    budget_year: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List CAPEX requests"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    if budget_year:
        query["budget_year"] = budget_year
    if status_filter:
        query["status"] = status_filter
    
    capex_requests = await db.financial_capex.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"capex_requests": capex_requests, "total_count": len(capex_requests)}


# OPEX endpoints
class OPEXCreate(BaseModel):
    """Create OPEX transaction"""
    category: str  # utilities, maintenance, salaries, supplies
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[str] = None
    vendor: Optional[str] = None
    cost_center: Optional[str] = None


@router.post("/opex", status_code=status.HTTP_201_CREATED)
async def create_opex_transaction(
    opex_data: OPEXCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create OPEX transaction"""
    user = await get_current_user(request, db)
    
    transaction_date = opex_data.transaction_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    opex = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "transaction_number": f"OPEX-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        "category": opex_data.category,
        "amount": opex_data.amount,
        "description": opex_data.description,
        "transaction_date": transaction_date,
        "vendor": opex_data.vendor,
        "cost_center": opex_data.cost_center,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.financial_opex.insert_one(opex.copy())
    return opex


@router.get("/opex")
async def list_opex_transactions(
    request: Request,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List OPEX transactions"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    if category:
        query["category"] = category
    if start_date and end_date:
        query["transaction_date"] = {"$gte": start_date, "$lte": end_date}
    
    opex_transactions = await db.financial_opex.find(
        query,
        {"_id": 0}
    ).sort("transaction_date", -1).to_list(100)
    
    return {"opex_transactions": opex_transactions, "total_count": len(opex_transactions)}


# Budget endpoints
class BudgetCreate(BaseModel):
    """Create budget"""
    fiscal_year: int
    category: str
    planned_amount: float
    department: Optional[str] = None
    description: Optional[str] = None


@router.post("/budgets", status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create budget"""
    user = await get_current_user(request, db)
    
    budget = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "fiscal_year": budget_data.fiscal_year,
        "category": budget_data.category,
        "planned_amount": budget_data.planned_amount,
        "actual_amount": 0.0,
        "department": budget_data.department,
        "description": budget_data.description,
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.financial_budgets.insert_one(budget.copy())
    return budget


@router.get("/budgets")
async def list_budgets(
    request: Request,
    fiscal_year: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List budgets"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    if fiscal_year:
        query["fiscal_year"] = fiscal_year
    if category:
        query["category"] = category
    
    budgets = await db.financial_budgets.find(
        query,
        {"_id": 0}
    ).sort("fiscal_year", -1).to_list(100)
    
    return {"budgets": budgets, "total_count": len(budgets)}

