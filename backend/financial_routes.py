from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import uuid

from financial_models import CapexRequest, OpexTransaction, Budget
from auth_utils import get_current_user

router = APIRouter(prefix="/financial", tags=["Financial"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.post("/capex", status_code=status.HTTP_201_CREATED)
async def create_capex_request(
    capex_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create CAPEX request"""
    user = await get_current_user(request, db)
    
    capex = CapexRequest(
        capex_number=f"CAP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        organization_id=user["organization_id"],
        unit_id=capex_data.get("unit_id"),
        title=capex_data.get("title"),
        description=capex_data.get("description"),
        justification=capex_data.get("justification"),
        request_type=capex_data.get("request_type"),
        estimated_cost=capex_data.get("estimated_cost"),
        budget_year=capex_data.get("budget_year", datetime.now(timezone.utc).year),
        requested_by=user["id"],
        requested_by_name=user["name"],
    )
    
    capex_dict = capex.model_dump()
    capex_dict["created_at"] = capex_dict["created_at"].isoformat()
    capex_dict["updated_at"] = capex_dict["updated_at"].isoformat()
    
    await db.capex_requests.insert_one(capex_dict.copy())
    return capex_dict


@router.get("/capex")
async def list_capex(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List CAPEX requests"""
    user = await get_current_user(request, db)
    
    capex_list = await db.capex_requests.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    return capex_list


@router.post("/opex", status_code=status.HTTP_201_CREATED)
async def create_opex_transaction(
    opex_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create OPEX transaction"""
    user = await get_current_user(request, db)
    
    opex = OpexTransaction(
        organization_id=user["organization_id"],
        unit_id=opex_data.get("unit_id"),
        category=opex_data.get("category"),
        amount=opex_data.get("amount"),
        transaction_date=opex_data.get("transaction_date"),
        description=opex_data.get("description"),
        work_order_id=opex_data.get("work_order_id"),
        project_id=opex_data.get("project_id"),
        created_by=user["id"],
    )
    
    opex_dict = opex.model_dump()
    opex_dict["created_at"] = opex_dict["created_at"].isoformat()
    
    await db.opex_transactions.insert_one(opex_dict.copy())
    return opex_dict


@router.get("/opex")
async def list_opex(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List OPEX transactions"""
    user = await get_current_user(request, db)
    
    opex_list = await db.opex_transactions.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).sort("transaction_date", -1).to_list(1000)
    
    return opex_list


@router.post("/budgets", status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create budget"""
    user = await get_current_user(request, db)
    
    budget = Budget(
        organization_id=user["organization_id"],
        unit_id=budget_data.get("unit_id"),
        fiscal_year=budget_data.get("fiscal_year"),
        category=budget_data.get("category"),
        planned_amount=budget_data.get("planned_amount"),
    )
    
    budget_dict = budget.model_dump()
    budget_dict["created_at"] = budget_dict["created_at"].isoformat()
    
    await db.budgets.insert_one(budget_dict.copy())
    return budget_dict


@router.get("/budgets")
async def list_budgets(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List budgets"""
    user = await get_current_user(request, db)
    
    budgets = await db.budgets.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    return budgets


@router.get("/summary")
async def get_financial_summary(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get financial summary"""
    user = await get_current_user(request, db)
    
    # CAPEX
    capex_requests = await db.capex_requests.find({"organization_id": user["organization_id"]}, {"_id": 0}).to_list(10000)
    total_capex = sum(c.get("estimated_cost", 0) for c in capex_requests)
    approved_capex = sum(c.get("estimated_cost", 0) for c in capex_requests if c.get("approval_status") == "approved")
    
    # OPEX
    opex_transactions = await db.opex_transactions.find({"organization_id": user["organization_id"]}, {"_id": 0}).to_list(10000)
    total_opex = sum(o.get("amount", 0) for o in opex_transactions)
    
    # Budgets
    budgets = await db.budgets.find({"organization_id": user["organization_id"]}, {"_id": 0}).to_list(10000)
    total_budget = sum(b.get("planned_amount", 0) for b in budgets)
    total_spent = sum(b.get("actual_amount", 0) for b in budgets)
    
    return {
        "capex": {
            "total_requests": len(capex_requests),
            "total_estimated": total_capex,
            "approved_amount": approved_capex
        },
        "opex": {
            "total_transactions": len(opex_transactions),
            "total_spent": total_opex
        },
        "budgets": {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "variance": total_budget - total_spent
        }
    }
