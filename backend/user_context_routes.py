from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/users/me", tags=["User Context"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


@router.get("/org-context")
async def get_organizational_context(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's organizational context - role, manager, team, position"""
    current_user = await get_current_user(request, db)
    
    # Get user's full details
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get organization details
    org = await db.organizations.find_one({"id": user.get("organization_id")})
    
    # Get user's organizational unit
    org_unit = None
    if user.get("organizational_unit_id"):
        org_unit = await db.organizational_units.find_one({"id": user["organizational_unit_id"]})
    
    # Find manager (user in parent org unit or higher-level role in same unit)
    manager = None
    if org_unit and org_unit.get("parent_id"):
        # Find users in parent unit with admin/manager roles
        managers = await db.users.find({
            "organizational_unit_id": org_unit["parent_id"],
            "role": {"$in": ["developer", "master", "admin", "manager", "operations_manager"]},
            "organization_id": user["organization_id"],
            "is_active": True
        }).to_list(length=1)
        
        if managers:
            manager = managers[0]
    
    # Count team members (users in same or child units)
    team_count = 0
    if user.get("organizational_unit_id"):
        # Count users in same unit
        team_count = await db.users.count_documents({
            "organizational_unit_id": user["organizational_unit_id"],
            "organization_id": user["organization_id"],
            "is_active": True,
            "id": {"$ne": user["id"]}  # Exclude self
        })
    
    return {
        "organization_id": user.get("organization_id"),
        "organization_name": org.get("name") if org else None,
        "unit_id": org_unit.get("id") if org_unit else None,
        "unit_name": org_unit.get("name") if org_unit else None,
        "unit_level": org_unit.get("level") if org_unit else None,
        "manager_id": manager.get("id") if manager else None,
        "manager_name": manager.get("name") if manager else None,
        "manager_role": manager.get("role") if manager else None,
        "team_size": team_count,
        "role": user.get("role"),
        "role_level": user.get("role_level"),  # Will need to fetch from roles table
    }


@router.get("/recent-activity")
async def get_recent_activity(
    request: Request,
    limit: int = 5,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's recent activity from audit logs"""
    current_user = await get_current_user(request, db)
    
    # Get recent audit logs for this user
    logs = await db.audit_logs.find({
        "user_id": current_user["id"]
    }, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return logs

