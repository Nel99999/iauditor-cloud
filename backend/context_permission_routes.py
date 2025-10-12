from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from workflow_models import PermissionContext, PermissionContextCreate, Delegation, DelegationCreate
from auth_utils import get_current_user
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context-permissions", tags=["Context Permissions"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# =====================================
# CONTEXT PERMISSION ENDPOINTS
# =====================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_context_permission(
    permission_data: PermissionContextCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a context-aware permission for a user"""
    user = await get_current_user(request, db)
    
    # Verify permission exists
    permission = await db.permissions.find_one({"id": permission_data.permission_id})
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    # Verify target user exists
    target_user = await db.users.find_one({"id": permission_data.user_id})
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if permission already exists
    existing = await db.permission_contexts.find_one({
        "user_id": permission_data.user_id,
        "permission_id": permission_data.permission_id,
        "context_type": permission_data.context_type,
        "context_id": permission_data.context_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Context permission already exists"
        )
    
    context_permission = PermissionContext(
        organization_id=user["organization_id"],
        created_by=user["id"],
        **permission_data.model_dump()
    )
    
    context_dict = context_permission.model_dump()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = context_dict.copy()
    await db.permission_contexts.insert_one(insert_dict)
    
    logger.info(f"Created context permission {context_permission.id} by {user['name']}")
    
    # Return clean dict without MongoDB _id
    return context_dict


@router.get("")
async def list_context_permissions(
    request: Request,
    user_id: str = None,
    context_type: str = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all context permissions"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if user_id:
        query["user_id"] = user_id
    
    if context_type:
        query["context_type"] = context_type
    
    permissions = await db.permission_contexts.find(query, {"_id": 0}).to_list(1000)
    return permissions


@router.get("/{permission_context_id}")
async def get_context_permission(
    permission_context_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific context permission"""
    user = await get_current_user(request, db)
    
    permission = await db.permission_contexts.find_one(
        {"id": permission_context_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context permission not found"
        )
    
    return permission


@router.delete("/{permission_context_id}")
async def delete_context_permission(
    permission_context_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a context permission"""
    user = await get_current_user(request, db)
    
    result = await db.permission_contexts.delete_one({
        "id": permission_context_id,
        "organization_id": user["organization_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context permission not found"
        )
    
    return {"message": "Context permission deleted successfully"}


@router.post("/check")
async def check_context_permission(
    request: Request,
    user_id: str,
    permission_id: str,
    context_type: str,
    context_id: str = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if user has permission in specific context"""
    current_user = await get_current_user(request, db)
    
    # Check for context permission
    query = {
        "user_id": user_id,
        "permission_id": permission_id,
        "context_type": context_type,
        "granted": True
    }
    
    if context_id:
        query["context_id"] = context_id
    
    # Check if permission is still valid (time-based)
    now = datetime.now(timezone.utc).isoformat()
    
    context_perm = await db.permission_contexts.find_one(query)
    
    if context_perm:
        # Check validity period
        valid_from = context_perm.get("valid_from")
        valid_until = context_perm.get("valid_until")
        
        if valid_from and valid_from > now:
            return {"granted": False, "reason": "Permission not yet valid"}
        
        if valid_until and valid_until < now:
            return {"granted": False, "reason": "Permission expired"}
        
        return {"granted": True, "context": context_type, "context_id": context_id}
    
    return {"granted": False, "reason": "No context permission found"}


# =====================================
# DELEGATION ENDPOINTS
# =====================================

@router.post("/delegations", status_code=status.HTTP_201_CREATED)
async def create_delegation(
    delegation_data: DelegationCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a delegation (temporary authority transfer)"""
    user = await get_current_user(request, db)
    
    # Verify delegate exists
    delegate = await db.users.find_one({"id": delegation_data.delegate_id})
    if not delegate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delegate user not found"
        )
    
    # Cannot delegate to self
    if delegation_data.delegate_id == user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delegate to yourself"
        )
    
    delegation = Delegation(
        organization_id=user["organization_id"],
        delegator_id=user["id"],
        delegator_name=user["name"],
        delegate_name=delegate["name"],
        **delegation_data.model_dump()
    )
    
    delegation_dict = delegation.model_dump()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = delegation_dict.copy()
    await db.delegations.insert_one(insert_dict)
    
    logger.info(f"Created delegation {delegation.id}: {user['name']} → {delegate['name']}")
    
    # Return clean dict without MongoDB _id
    return delegation_dict


@router.get("/delegations")
async def list_delegations(
    request: Request,
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get delegations (both as delegator and delegate)"""
    user = await get_current_user(request, db)
    
    query = {
        "organization_id": user["organization_id"],
        "$or": [
            {"delegator_id": user["id"]},
            {"delegate_id": user["id"]}
        ]
    }
    
    if active_only:
        now = datetime.now(timezone.utc).isoformat()
        query["active"] = True
        query["valid_from"] = {"$lte": now}
        query["valid_until"] = {"$gte": now}
    
    delegations = await db.delegations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return delegations


@router.get("/delegations/{delegation_id}")
async def get_delegation(
    delegation_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific delegation"""
    user = await get_current_user(request, db)
    
    delegation = await db.delegations.find_one(
        {"id": delegation_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not delegation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delegation not found"
        )
    
    return delegation


@router.post("/delegations/{delegation_id}/revoke")
async def revoke_delegation(
    delegation_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Revoke a delegation"""
    user = await get_current_user(request, db)
    
    # Only delegator can revoke
    delegation = await db.delegations.find_one({
        "id": delegation_id,
        "delegator_id": user["id"]
    })
    
    if not delegation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delegation not found or you don't have permission to revoke it"
        )
    
    await db.delegations.update_one(
        {"id": delegation_id},
        {"$set": {"active": False}}
    )
    
    logger.info(f"Revoked delegation {delegation_id} by {user['name']}")
    
    return {"message": "Delegation revoked successfully"}


@router.post("/delegations/check")
async def check_delegation(
    request: Request,
    delegate_id: str,
    workflow_type: str = None,
    resource_type: str = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if user has active delegations"""
    current_user = await get_current_user(request, db)
    
    now = datetime.now(timezone.utc).isoformat()
    
    query = {
        "delegate_id": delegate_id,
        "active": True,
        "valid_from": {"$lte": now},
        "valid_until": {"$gte": now}
    }
    
    if workflow_type:
        query["$or"] = [
            {"workflow_types": {"$size": 0}},  # Empty = all workflows
            {"workflow_types": workflow_type}
        ]
    
    if resource_type:
        query["$or"] = [
            {"resource_types": {"$size": 0}},  # Empty = all resources
            {"resource_types": resource_type}
        ]
    
    delegations = await db.delegations.find(query, {"_id": 0}).to_list(100)
    
    return {
        "has_delegation": len(delegations) > 0,
        "delegations": delegations
    }
