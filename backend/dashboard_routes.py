from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
from .auth_utils import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


class UserStats(BaseModel):
    total_users: int = 0
    active_users: int = 0
    pending_invitations: int = 0
    recent_logins: int = 0


class InspectionStats(BaseModel):
    total_inspections: int = 0
    pending: int = 0
    completed_today: int = 0
    pass_rate: float = 0.0
    average_score: Optional[float] = None


class TaskStats(BaseModel):
    total_tasks: int = 0
    todo: int = 0
    in_progress: int = 0
    completed: int = 0
    overdue: int = 0


class ChecklistStats(BaseModel):
    total_checklists: int = 0
    completed_today: int = 0
    pending_today: int = 0
    completion_rate: float = 0.0


class OrganizationStats(BaseModel):
    total_units: int = 0
    total_levels: int = 0


class DashboardStats(BaseModel):
    users: UserStats
    inspections: InspectionStats
    tasks: TaskStats
    checklists: ChecklistStats
    organization: OrganizationStats


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    user = await get_current_user(request, db)
    org_id = user["organization_id"]
    
    # === USER STATS ===
    all_users = await db.users.find(
        {"organization_id": org_id, "status": {"$ne": "deleted"}},
        {"_id": 0}
    ).to_list(10000)
    
    total_users = len(all_users)
    active_users = len([u for u in all_users if u.get("status") == "active"])
    
    # Recent logins (last 7 days)
    seven_days_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() - (7 * 24 * 60 * 60)
    recent_logins = 0
    for u in all_users:
        if u.get("last_login"):
            try:
                last_login = datetime.fromisoformat(u["last_login"])
                if last_login.timestamp() >= seven_days_ago:
                    recent_logins += 1
            except:
                pass
    
    # Pending invitations
    pending_invitations = await db.invitations.count_documents({
        "organization_id": org_id,
        "status": "pending"
    })
    
    user_stats = UserStats(
        total_users=total_users,
        active_users=active_users,
        pending_invitations=pending_invitations,
        recent_logins=recent_logins
    )
    
    # === INSPECTION STATS ===
    all_inspections = await db.inspection_executions.find(
        {"organization_id": org_id},
        {"_id": 0}
    ).to_list(10000)
    
    total_inspections = len(all_inspections)
    
    # Count completed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = len([
        i for i in all_inspections
        if i.get("status") == "completed" and 
        i.get("completed_at") and
        datetime.fromisoformat(i["completed_at"]) >= today_start
    ])
    
    # Count pending
    pending_inspections = len([i for i in all_inspections if i.get("status") == "in_progress"])
    
    # Calculate pass rate
    completed_inspections = [i for i in all_inspections if i.get("status") == "completed" and i.get("passed") is not None]
    pass_rate = (len([i for i in completed_inspections if i.get("passed")]) / len(completed_inspections) * 100.0) if completed_inspections else 0.0
    
    # Average score
    scores = [i.get("score") for i in completed_inspections if i.get("score") is not None]
    average_score = sum(scores) / len(scores) if scores else None
    
    inspection_stats = InspectionStats(
        total_inspections=total_inspections,
        completed_today=completed_today,
        pending=pending_inspections,
        pass_rate=round(pass_rate, 2),
        average_score=round(average_score, 2) if average_score else None
    )
    
    # === TASK STATS ===
    all_tasks = await db.tasks.find(
        {"organization_id": org_id},
        {"_id": 0}
    ).to_list(10000)
    
    total_tasks = len(all_tasks)
    todo = len([t for t in all_tasks if t.get("status") == "todo"])
    in_progress = len([t for t in all_tasks if t.get("status") == "in_progress"])
    completed_tasks = len([t for t in all_tasks if t.get("status") == "completed"])
    
    # Count overdue tasks
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue = len([t for t in all_tasks if t.get("due_date") and t.get("due_date") < today_str and t.get("status") != "completed"])
    
    task_stats = TaskStats(
        total_tasks=total_tasks,
        todo=todo,
        in_progress=in_progress,
        completed=completed_tasks,
        overdue=overdue
    )
    
    # === CHECKLIST STATS ===
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    all_checklists = await db.checklist_executions.find(
        {"organization_id": org_id},
        {"_id": 0}
    ).to_list(10000)
    
    total_checklists = len(all_checklists)
    
    # Count completed today
    completed_today_checklists = len([
        c for c in all_checklists
        if c.get("date") == today and c.get("status") == "completed"
    ])
    
    # Count pending today
    pending_today = len([
        c for c in all_checklists
        if c.get("date") == today and c.get("status") != "completed"
    ])
    
    # Calculate completion rate
    completed_all_checklists = len([c for c in all_checklists if c.get("status") == "completed"])
    completion_rate = (completed_all_checklists / total_checklists * 100) if total_checklists > 0 else 0.0
    
    checklist_stats = ChecklistStats(
        total_checklists=total_checklists,
        completed_today=completed_today_checklists,
        pending_today=pending_today,
        completion_rate=round(completion_rate, 2)
    )
    
    # === ORGANIZATION STATS ===
    all_units = await db.organization_units.find(
        {"organization_id": org_id},
        {"_id": 0}
    ).to_list(10000)
    
    total_units = len(all_units)
    
    # Get unique levels
    levels = set([u.get("level", 0) for u in all_units])
    total_levels = len(levels)
    
    org_stats = OrganizationStats(
        total_units=total_units,
        total_levels=total_levels
    )
    
    return DashboardStats(
        users=user_stats,
        inspections=inspection_stats,
        tasks=task_stats,
        checklists=checklist_stats,
        organization=org_stats
    )



@router.get("/financial")
async def get_financial_dashboard(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get financial dashboard metrics"""
    user = await get_current_user(request, db)
    
    transactions = await db.financial_transactions.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(10000)
    
    total_revenue = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "income")
    total_expenses = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "expense")
    net_income = total_revenue - total_expenses
    
    # This month
    from datetime import datetime, timezone
    month_start = datetime.now(timezone.utc).replace(day=1).isoformat()
    month_transactions = [t for t in transactions if t.get("created_at", "") >= month_start]
    month_revenue = sum(t.get("amount", 0) for t in month_transactions if t.get("transaction_type") == "income")
    month_expenses = sum(t.get("amount", 0) for t in month_transactions if t.get("transaction_type") == "expense")
    
    # By category
    by_category = {}
    for t in transactions:
        category = t.get("category", "uncategorized")
        amount = t.get("amount", 0)
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += amount
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_income": round(net_income, 2),
        "month_revenue": round(month_revenue, 2),
        "month_expenses": round(month_expenses, 2),
        "by_category": by_category,
        "transaction_count": len(transactions)
    }
