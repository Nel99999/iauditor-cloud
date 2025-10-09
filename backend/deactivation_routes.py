from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from permission_models import (
    UserDeactivation, UserDeactivationCreate, UserReactivation
)
from auth_utils import get_current_user
from datetime import datetime, timezone
from typing import Optional

router = APIRouter(prefix="/users", tags=["user-lifecycle"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# =====================================
# USER DEACTIVATION
# =====================================

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    deactivation: UserDeactivationCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Deactivate user with optional reassignment"""
    current_user = await get_current_user(request, db)
    
    # Cannot deactivate self
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Check user exists and is in same organization
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target_user.get("status") == "deactivated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already deactivated"
        )
    
    # Reassignment logic
    tasks_reassigned = 0
    inspections_reassigned = 0
    checklists_reassigned = 0
    
    if deactivation.reassign_to:
        # Verify reassign_to user exists
        reassign_user = await db.users.find_one({
            "id": deactivation.reassign_to,
            "organization_id": current_user["organization_id"],
            "status": "active"
        })
        
        if not reassign_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reassignment target user not found or inactive"
            )
        
        # Reassign tasks
        task_result = await db.tasks.update_many(
            {"assigned_to": user_id, "status": {"$in": ["todo", "in_progress"]}},
            {"$set": {"assigned_to": deactivation.reassign_to}}
        )
        tasks_reassigned = task_result.modified_count
        
        # Reassign inspections
        inspection_result = await db.inspections.update_many(
            {"assigned_to": user_id, "workflow_status": {"$in": ["draft", "in_progress"]}},
            {"$set": {"assigned_to": deactivation.reassign_to}}
        )
        inspections_reassigned = inspection_result.modified_count
        
        # Reassign checklists
        checklist_result = await db.checklist_instances.update_many(
            {"assigned_to": user_id, "status": "pending"},
            {"$set": {"assigned_to": deactivation.reassign_to}}
        )
        checklists_reassigned = checklist_result.modified_count
    
    # Create deactivation record
    deactivation_record = UserDeactivation(
        user_id=user_id,
        deactivated_by=current_user["id"],
        reason=deactivation.reason,
        reassign_to=deactivation.reassign_to,
        reassignment_completed=bool(deactivation.reassign_to),
        tasks_reassigned=tasks_reassigned,
        inspections_reassigned=inspections_reassigned,
        checklists_reassigned=checklists_reassigned
    )
    
    await db.user_deactivations.insert_one(deactivation_record.dict())
    
    # Update user status
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "deactivated",
            "deactivated_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Revoke all active sessions
    await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"revoked": True}}
    )
    
    return {
        "message": "User deactivated successfully",
        "deactivation": deactivation_record.dict(),
        "reassignments": {
            "tasks": tasks_reassigned,
            "inspections": inspections_reassigned,
            "checklists": checklists_reassigned
        }
    }


@router.post("/{user_id}/reactivate")
async def reactivate_user(
    user_id: str,
    reactivation: UserReactivation,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reactivate deactivated user"""
    current_user = await get_current_user(request, db)
    
    # Check user exists
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target_user.get("status") != "deactivated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not deactivated"
        )
    
    # Update user status
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "active",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update deactivation record
    await db.user_deactivations.update_one(
        {"user_id": user_id, "reactivated_at": None},
        {"$set": {
            "reactivated_at": datetime.now(timezone.utc).isoformat(),
            "reactivated_by": current_user["id"]
        }}
    )
    
    return {"message": "User reactivated successfully"}


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Temporarily suspend user"""
    current_user = await get_current_user(request, db)
    
    # Cannot suspend self
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account"
        )
    
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "suspended",
            "suspended_at": datetime.now(timezone.utc).isoformat(),
            "suspension_reason": reason,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Revoke active sessions
    await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"revoked": True}}
    )
    
    return {"message": "User suspended successfully"}


@router.post("/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Remove suspension from user"""
    current_user = await get_current_user(request, db)
    
    target_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target_user.get("status") != "suspended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not suspended"
        )
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "status": "active",
            "unsuspended_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "User unsuspended successfully"}


@router.get("/{user_id}/assignments")
async def get_user_assignments(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all assignments for a user (for reassignment planning)"""
    current_user = await get_current_user(request, db)
    
    # Get counts of active assignments
    active_tasks = await db.tasks.count_documents({
        "assigned_to": user_id,
        "status": {"$in": ["todo", "in_progress"]}
    })
    
    active_inspections = await db.inspections.count_documents({
        "assigned_to": user_id,
        "workflow_status": {"$in": ["draft", "in_progress"]}
    })
    
    active_checklists = await db.checklist_instances.count_documents({
        "assigned_to": user_id,
        "status": "pending"
    })
    
    # Get actual items
    tasks = await db.tasks.find(
        {"assigned_to": user_id, "status": {"$in": ["todo", "in_progress"]}},
        {"_id": 0, "id": 1, "title": 1, "status": 1, "due_date": 1}
    ).to_list(length=100)
    
    inspections = await db.inspections.find(
        {"assigned_to": user_id, "workflow_status": {"$in": ["draft", "in_progress"]}},
        {"_id": 0, "id": 1, "location": 1, "workflow_status": 1, "scheduled_date": 1}
    ).to_list(length=100)
    
    checklists = await db.checklist_instances.find(
        {"assigned_to": user_id, "status": "pending"},
        {"_id": 0, "id": 1, "checklist_date": 1, "status": 1}
    ).to_list(length=100)
    
    return {
        "user_id": user_id,
        "summary": {
            "active_tasks": active_tasks,
            "active_inspections": active_inspections,
            "active_checklists": active_checklists,
            "total": active_tasks + active_inspections + active_checklists
        },
        "assignments": {
            "tasks": tasks,
            "inspections": inspections,
            "checklists": checklists
        }
    }


@router.post("/{user_id}/reassign")
async def bulk_reassign_assignments(
    user_id: str,
    reassign_to: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk reassign all active assignments to another user"""
    current_user = await get_current_user(request, db)
    
    # Verify both users exist
    source_user = await db.users.find_one({
        "id": user_id,
        "organization_id": current_user["organization_id"]
    })
    
    target_user = await db.users.find_one({
        "id": reassign_to,
        "organization_id": current_user["organization_id"],
        "status": "active"
    })
    
    if not source_user or not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source or target user not found"
        )
    
    # Reassign all active items
    tasks_updated = await db.tasks.update_many(
        {"assigned_to": user_id, "status": {"$in": ["todo", "in_progress"]}},
        {"$set": {"assigned_to": reassign_to, "reassigned_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    inspections_updated = await db.inspections.update_many(
        {"assigned_to": user_id, "workflow_status": {"$in": ["draft", "in_progress"]}},
        {"$set": {"assigned_to": reassign_to, "reassigned_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    checklists_updated = await db.checklist_instances.update_many(
        {"assigned_to": user_id, "status": "pending"},
        {"$set": {"assigned_to": reassign_to, "reassigned_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": "Assignments reassigned successfully",
        "reassigned": {
            "tasks": tasks_updated.modified_count,
            "inspections": inspections_updated.modified_count,
            "checklists": checklists_updated.modified_count,
            "total": tasks_updated.modified_count + inspections_updated.modified_count + checklists_updated.modified_count
        }
    }


@router.get("/{user_id}/deactivation-history")
async def get_deactivation_history(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get deactivation history for a user"""
    current_user = await get_current_user(request, db)
    
    history = await db.user_deactivations.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("deactivated_at", -1).to_list(length=None)
    
    return history
