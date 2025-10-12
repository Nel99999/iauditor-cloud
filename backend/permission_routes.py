from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from permission_models import (
    Permission, PermissionCreate,
    RolePermission, RolePermissionCreate,
    UserFunctionOverride, UserFunctionOverrideCreate,
    ExtendedRole, ExtendedRoleCreate
)
from auth_utils import get_current_user
from datetime import datetime, timezone
from typing import Optional
import hashlib
import json

router = APIRouter(prefix="/permissions", tags=["permissions"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# =====================================
# PERMISSION CACHE (3-layer system)
# =====================================

permission_cache = {}  # In-memory cache
CACHE_TTL = 300  # 5 minutes


def cache_key(user_id: str, resource: str, action: str, scope: str) -> str:
    """Generate cache key for permission check"""
    return hashlib.md5(f"{user_id}:{resource}:{action}:{scope}".encode()).hexdigest()


async def check_permission(
    db: AsyncIOMotorDatabase,
    user_id: str,
    resource_type: str,
    action: str,
    scope: str,
    scope_id: Optional[str] = None
) -> bool:
    """
    Check if user has permission (3-layer resolution)
    1. User-specific overrides (highest priority)
    2. Role-based permissions
    3. Inherited from parent scope
    """
    
    # Layer 1: Check cache
    key = cache_key(user_id, resource_type, action, scope)
    if key in permission_cache:
        cached_result, cache_time = permission_cache[key]
        if (datetime.now(timezone.utc).timestamp() - cache_time) < CACHE_TTL:
            return cached_result
    
    # Layer 2: Check user function overrides
    user_override = await db.user_function_overrides.find_one({
        "user_id": user_id,
        "permission_id": {"$exists": True}
    })
    
    if user_override:
        permission = await db.permissions.find_one({
            "id": user_override["permission_id"],
            "resource_type": resource_type,
            "action": action,
            "scope": scope
        })
        if permission:
            result = user_override["granted"]
            permission_cache[key] = (result, datetime.now(timezone.utc).timestamp())
            return result
    
    # Layer 3: Check role permissions
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    role_id = user.get("role_id") or user.get("role")
    
    # Find permission
    permission = await db.permissions.find_one({
        "resource_type": resource_type,
        "action": action,
        "scope": scope
    })
    
    if not permission:
        return False
    
    # Check role has this permission
    role_perm = await db.role_permissions.find_one({
        "role_id": role_id,
        "permission_id": permission["id"],
        "granted": True
    })
    
    result = role_perm is not None
    
    # Cache result
    permission_cache[key] = (result, datetime.now(timezone.utc).timestamp())
    
    return result


# =====================================
# PERMISSION CRUD
# =====================================

@router.get("")
async def list_permissions(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all permissions"""
    user = await get_current_user(request, db)
    
    permissions = await db.permissions.find({}, {"_id": 0}).to_list(length=None)
    return permissions


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create new permission"""
    user = await get_current_user(request, db)
    
    # Check if permission already exists
    existing = await db.permissions.find_one({
        "resource_type": permission.resource_type,
        "action": permission.action,
        "scope": permission.scope
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    perm = Permission(**permission.dict())
    perm_dict = perm.dict()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = perm_dict.copy()
    await db.permissions.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return perm_dict


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete permission"""
    user = await get_current_user(request, db)
    
    result = await db.permissions.delete_one({"id": permission_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    # Clear cache
    permission_cache.clear()
    
    return {"message": "Permission deleted successfully"}


# =====================================
# ROLE PERMISSIONS
# =====================================

@router.get("/roles/{role_id}")
async def get_role_permissions(
    role_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all permissions for a role"""
    user = await get_current_user(request, db)
    
    role_perms = await db.role_permissions.find(
        {"role_id": role_id},
        {"_id": 0}
    ).to_list(length=None)
    
    # Populate permission details
    for rp in role_perms:
        perm = await db.permissions.find_one({"id": rp["permission_id"]}, {"_id": 0})
        if perm:
            rp["permission"] = perm
    
    return role_perms


@router.post("/roles/{role_id}")
async def assign_permission_to_role(
    role_id: str,
    role_perm: RolePermissionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Assign permission to role"""
    user = await get_current_user(request, db)
    
    # Check if already assigned
    existing = await db.role_permissions.find_one({
        "role_id": role_id,
        "permission_id": role_perm.permission_id
    })
    
    if existing:
        # Update granted status
        await db.role_permissions.update_one(
            {"id": existing["id"]},
            {"$set": {"granted": role_perm.granted}}
        )
        return {"message": "Role permission updated"}
    
    rp = RolePermission(role_id=role_id, **role_perm.dict())
    await db.role_permissions.insert_one(rp.dict())
    
    # Clear cache
    permission_cache.clear()
    
    return rp


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Remove permission from role"""
    user = await get_current_user(request, db)
    
    result = await db.role_permissions.delete_one({
        "role_id": role_id,
        "permission_id": permission_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission not found"
        )
    
    # Clear cache
    permission_cache.clear()
    
    return {"message": "Permission removed from role"}


# =====================================
# USER FUNCTION OVERRIDES
# =====================================

@router.get("/users/{user_id}/overrides")
async def get_user_overrides(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all function overrides for a user"""
    current_user = await get_current_user(request, db)
    
    overrides = await db.user_function_overrides.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(length=None)
    
    # Populate permission details
    for override in overrides:
        perm = await db.permissions.find_one({"id": override["permission_id"]}, {"_id": 0})
        if perm:
            override["permission"] = perm
    
    return overrides


@router.post("/users/{user_id}/overrides")
async def create_user_override(
    user_id: str,
    override: UserFunctionOverrideCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create function override for user"""
    current_user = await get_current_user(request, db)
    
    ufo = UserFunctionOverride(
        **override.dict(),
        created_by=current_user["id"]
    )
    
    await db.user_function_overrides.insert_one(ufo.dict())
    
    # Clear cache
    permission_cache.clear()
    
    return ufo


@router.delete("/users/{user_id}/overrides/{override_id}")
async def delete_user_override(
    user_id: str,
    override_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete user function override"""
    current_user = await get_current_user(request, db)
    
    result = await db.user_function_overrides.delete_one({
        "id": override_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Override not found"
        )
    
    # Clear cache
    permission_cache.clear()
    
    return {"message": "Override deleted successfully"}


# =====================================
# PERMISSION CHECK ENDPOINT
# =====================================

@router.post("/check")
async def check_user_permission(
    resource_type: str,
    action: str,
    scope: str,
    scope_id: Optional[str] = None,
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if current user has specific permission"""
    user = await get_current_user(request, db)
    
    has_permission = await check_permission(
        db, user["id"], resource_type, action, scope, scope_id
    )
    
    return {
        "has_permission": has_permission,
        "user_id": user["id"],
        "resource_type": resource_type,
        "action": action,
        "scope": scope
    }


# =====================================
# INITIALIZE DEFAULT PERMISSIONS
# =====================================

async def initialize_permissions(db: AsyncIOMotorDatabase):
    """Initialize default permission set"""
    
    default_permissions = [
        # Inspection permissions
        {"resource_type": "inspection", "action": "create", "scope": "own", "description": "Create own inspections"},
        {"resource_type": "inspection", "action": "create", "scope": "team", "description": "Create team inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "own", "description": "View own inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "team", "description": "View team inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "all", "description": "View all inspections"},
        {"resource_type": "inspection", "action": "update", "scope": "own", "description": "Edit own inspections"},
        {"resource_type": "inspection", "action": "delete", "scope": "own", "description": "Delete own inspections"},
        {"resource_type": "inspection", "action": "approve", "scope": "team", "description": "Approve team inspections"},
        
        # Task permissions
        {"resource_type": "task", "action": "create", "scope": "own", "description": "Create tasks"},
        {"resource_type": "task", "action": "read", "scope": "own", "description": "View own tasks"},
        {"resource_type": "task", "action": "read", "scope": "team", "description": "View team tasks"},
        {"resource_type": "task", "action": "update", "scope": "own", "description": "Update own tasks"},
        {"resource_type": "task", "action": "assign", "scope": "team", "description": "Assign tasks to team"},
        {"resource_type": "task", "action": "delete", "scope": "own", "description": "Delete own tasks"},
        
        # User permissions
        {"resource_type": "user", "action": "create", "scope": "organization", "description": "Create users"},
        {"resource_type": "user", "action": "read", "scope": "organization", "description": "View users"},
        {"resource_type": "user", "action": "update", "scope": "organization", "description": "Update users"},
        {"resource_type": "user", "action": "delete", "scope": "organization", "description": "Delete users"},
        
        # Report permissions
        {"resource_type": "report", "action": "read", "scope": "own", "description": "View own reports"},
        {"resource_type": "report", "action": "read", "scope": "all", "description": "View all reports"},
        {"resource_type": "report", "action": "export", "scope": "all", "description": "Export reports"},
        
        # API permissions (for developer role)
        {"resource_type": "api", "action": "manage", "scope": "all", "description": "Manage API keys"},
        {"resource_type": "webhook", "action": "manage", "scope": "all", "description": "Manage webhooks"},
    ]
    
    # Insert permissions if they don't exist
    for perm_data in default_permissions:
        existing = await db.permissions.find_one({
            "resource_type": perm_data["resource_type"],
            "action": perm_data["action"],
            "scope": perm_data["scope"]
        })
        
        if not existing:
            perm = Permission(**perm_data)
            await db.permissions.insert_one(perm.dict())
            print(f"✅ Created permission: {perm_data['resource_type']}.{perm_data['action']} ({perm_data['scope']})")
