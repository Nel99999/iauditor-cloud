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
    
    # Get role_id - handle both UUID and string role codes
    role_id = user.get("role_id") or user.get("role")
    
    # If role_id is a string code (e.g., "master", "admin"), resolve it to UUID
    # Check if it's a UUID format (contains dashes) vs a role code (no dashes)
    if role_id and '-' not in role_id:
        # Looks like a code, not a UUID - resolve it
        role_record = await db.roles.find_one({
            "code": role_id,
            "organization_id": user.get("organization_id")
        })
        if role_record:
            role_id = role_record["id"]
        else:
            # Role not found, try without org filter (for backward compatibility)
            role_record = await db.roles.find_one({"code": role_id})
            if role_record:
                role_id = role_record["id"]
    
    if not role_id:
        return False
    
    # Find permission - check for exact match first
    permission = await db.permissions.find_one({
        "resource_type": resource_type,
        "action": action,
        "scope": scope
    })
    
    # If not found and requesting broader scope, check if user has narrower scopes
    # Scope hierarchy: all > organization > team > own
    scope_hierarchy = {
        "all": ["all"],
        "organization": ["all", "organization", "team", "own"],
        "team": ["all", "team", "own"],
        "own": ["all", "own"]
    }
    
    permission_found = False
    permission_id_to_check = None
    
    if permission:
        permission_id_to_check = permission["id"]
        permission_found = True
    else:
        # Try to find permission with broader or equivalent scopes
        allowed_scopes = scope_hierarchy.get(scope, [scope])
        for check_scope in allowed_scopes:
            permission = await db.permissions.find_one({
                "resource_type": resource_type,
                "action": action,
                "scope": check_scope
            })
            if permission:
                permission_id_to_check = permission["id"]
                # Check if role has THIS permission
                role_perm = await db.role_permissions.find_one({
                    "role_id": role_id,
                    "permission_id": permission["id"],
                    "granted": True
                })
                if role_perm:
                    permission_found = True
                    break
    
    if not permission_found or not permission_id_to_check:
        result = False
    else:
        # Check role has this permission (if not already checked above)
        if not permission_found:
            role_perm = await db.role_permissions.find_one({
                "role_id": role_id,
                "permission_id": permission_id_to_check,
                "granted": True
            })
            result = role_perm is not None
        else:
            result = True
    
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
    rp_dict = rp.dict()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = rp_dict.copy()
    await db.role_permissions.insert_one(insert_dict)
    
    # Clear cache
    permission_cache.clear()
    
    # Return clean dict without MongoDB _id
    return rp_dict


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
    
    ufo_dict = ufo.dict()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = ufo_dict.copy()
    await db.user_function_overrides.insert_one(insert_dict)
    
    # Clear cache
    permission_cache.clear()
    
    # Return clean dict without MongoDB _id
    return ufo_dict


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
        {"resource_type": "inspection", "action": "create", "scope": "organization", "description": "Create inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "own", "description": "View own inspections"},
        {"resource_type": "inspection", "action": "read", "scope": "organization", "description": "View all inspections"},
        {"resource_type": "inspection", "action": "update", "scope": "own", "description": "Edit own inspections"},
        {"resource_type": "inspection", "action": "update", "scope": "organization", "description": "Edit all inspections"},
        {"resource_type": "inspection", "action": "delete", "scope": "own", "description": "Delete own inspections"},
        {"resource_type": "inspection", "action": "delete", "scope": "organization", "description": "Delete all inspections"},
        
        # Checklist permissions
        {"resource_type": "checklist", "action": "create", "scope": "own", "description": "Create checklists"},
        {"resource_type": "checklist", "action": "create", "scope": "organization", "description": "Create all checklists"},
        {"resource_type": "checklist", "action": "read", "scope": "own", "description": "View own checklists"},
        {"resource_type": "checklist", "action": "read", "scope": "organization", "description": "View all checklists"},
        {"resource_type": "checklist", "action": "update", "scope": "own", "description": "Update own checklists"},
        {"resource_type": "checklist", "action": "update", "scope": "organization", "description": "Update all checklists"},
        {"resource_type": "checklist", "action": "delete", "scope": "organization", "description": "Delete checklists"},
        
        # Task permissions
        {"resource_type": "task", "action": "create", "scope": "own", "description": "Create tasks"},
        {"resource_type": "task", "action": "create", "scope": "organization", "description": "Create all tasks"},
        {"resource_type": "task", "action": "read", "scope": "own", "description": "View own tasks"},
        {"resource_type": "task", "action": "read", "scope": "organization", "description": "View all tasks"},
        {"resource_type": "task", "action": "update", "scope": "own", "description": "Update own tasks"},
        {"resource_type": "task", "action": "update", "scope": "organization", "description": "Update all tasks"},
        {"resource_type": "task", "action": "delete", "scope": "own", "description": "Delete own tasks"},
        {"resource_type": "task", "action": "delete", "scope": "organization", "description": "Delete all tasks"},
        
        # Asset permissions
        {"resource_type": "asset", "action": "create", "scope": "organization", "description": "Create assets"},
        {"resource_type": "asset", "action": "read", "scope": "own", "description": "View own assets"},
        {"resource_type": "asset", "action": "read", "scope": "organization", "description": "View all assets"},
        {"resource_type": "asset", "action": "update", "scope": "organization", "description": "Update assets"},
        {"resource_type": "asset", "action": "delete", "scope": "organization", "description": "Delete assets"},
        
        # Work Order permissions
        {"resource_type": "workorder", "action": "create", "scope": "own", "description": "Create work orders"},
        {"resource_type": "workorder", "action": "create", "scope": "organization", "description": "Create all work orders"},
        {"resource_type": "workorder", "action": "read", "scope": "own", "description": "View own work orders"},
        {"resource_type": "workorder", "action": "read", "scope": "organization", "description": "View all work orders"},
        {"resource_type": "workorder", "action": "update", "scope": "own", "description": "Update own work orders"},
        {"resource_type": "workorder", "action": "update", "scope": "organization", "description": "Update all work orders"},
        {"resource_type": "workorder", "action": "delete", "scope": "organization", "description": "Delete work orders"},
        
        # Inventory permissions
        {"resource_type": "inventory", "action": "create", "scope": "organization", "description": "Create inventory items"},
        {"resource_type": "inventory", "action": "read", "scope": "own", "description": "View inventory"},
        {"resource_type": "inventory", "action": "read", "scope": "organization", "description": "View all inventory"},
        {"resource_type": "inventory", "action": "update", "scope": "organization", "description": "Update inventory"},
        {"resource_type": "inventory", "action": "delete", "scope": "organization", "description": "Delete inventory items"},
        
        # Project permissions
        {"resource_type": "project", "action": "create", "scope": "organization", "description": "Create projects"},
        {"resource_type": "project", "action": "read", "scope": "own", "description": "View own projects"},
        {"resource_type": "project", "action": "read", "scope": "organization", "description": "View all projects"},
        {"resource_type": "project", "action": "update", "scope": "own", "description": "Update own projects"},
        {"resource_type": "project", "action": "update", "scope": "organization", "description": "Update all projects"},
        {"resource_type": "project", "action": "delete", "scope": "organization", "description": "Delete projects"},
        
        # Incident permissions
        {"resource_type": "incident", "action": "create", "scope": "organization", "description": "Report incidents"},
        {"resource_type": "incident", "action": "read", "scope": "own", "description": "View own incidents"},
        {"resource_type": "incident", "action": "read", "scope": "organization", "description": "View all incidents"},
        {"resource_type": "incident", "action": "update", "scope": "organization", "description": "Update incidents"},
        {"resource_type": "incident", "action": "investigate", "scope": "organization", "description": "Investigate incidents"},
        
        # Training permissions
        {"resource_type": "training", "action": "create", "scope": "organization", "description": "Create training courses"},
        {"resource_type": "training", "action": "read", "scope": "own", "description": "View own training"},
        {"resource_type": "training", "action": "read", "scope": "organization", "description": "View all training"},
        {"resource_type": "training", "action": "manage", "scope": "organization", "description": "Manage training"},
        
        # Financial permissions
        {"resource_type": "financial", "action": "read", "scope": "organization", "description": "View financial data"},
        {"resource_type": "financial", "action": "create", "scope": "organization", "description": "Create financial entries"},
        {"resource_type": "financial", "action": "manage", "scope": "organization", "description": "Manage finances"},
        
        # Dashboard permissions
        {"resource_type": "dashboard", "action": "read", "scope": "organization", "description": "View dashboards"},
        
        # Contractor permissions
        {"resource_type": "contractor", "action": "create", "scope": "organization", "description": "Create contractors"},
        {"resource_type": "contractor", "action": "read", "scope": "organization", "description": "View contractors"},
        {"resource_type": "contractor", "action": "update", "scope": "organization", "description": "Update contractors"},
        
        # Emergency permissions
        {"resource_type": "emergency", "action": "create", "scope": "organization", "description": "Declare emergencies"},
        {"resource_type": "emergency", "action": "read", "scope": "organization", "description": "View emergencies"},
        {"resource_type": "emergency", "action": "manage", "scope": "organization", "description": "Manage emergencies"},
        
        # Chat permissions
        {"resource_type": "chat", "action": "read", "scope": "organization", "description": "Access team chat"},
        {"resource_type": "chat", "action": "create", "scope": "organization", "description": "Send messages"},
        
        # Announcement permissions
        {"resource_type": "announcement", "action": "create", "scope": "organization", "description": "Create announcements"},
        {"resource_type": "announcement", "action": "read", "scope": "organization", "description": "View announcements"},
        
        # User permissions
        {"resource_type": "user", "action": "create", "scope": "organization", "description": "Create users"},
        {"resource_type": "user", "action": "read", "scope": "organization", "description": "View users"},
        {"resource_type": "user", "action": "update", "scope": "organization", "description": "Update users"},
        {"resource_type": "user", "action": "delete", "scope": "organization", "description": "Delete users"},
        {"resource_type": "user", "action": "invite", "scope": "organization", "description": "Invite users"},
        {"resource_type": "user", "action": "approve", "scope": "organization", "description": "Approve users"},
        
        # Invitation permissions
        {"resource_type": "invitation", "action": "create", "scope": "organization", "description": "Send invitations"},
        {"resource_type": "invitation", "action": "read", "scope": "organization", "description": "View invitations"},
        {"resource_type": "invitation", "action": "cancel", "scope": "organization", "description": "Cancel invitations"},
        {"resource_type": "invitation", "action": "resend", "scope": "organization", "description": "Resend invitations"},
        
        # Role permissions
        {"resource_type": "role", "action": "create", "scope": "organization", "description": "Create roles"},
        {"resource_type": "role", "action": "read", "scope": "organization", "description": "View roles"},
        {"resource_type": "role", "action": "update", "scope": "organization", "description": "Update roles"},
        {"resource_type": "role", "action": "delete", "scope": "organization", "description": "Delete roles"},
        
        # Organization permissions
        {"resource_type": "organization", "action": "create", "scope": "organization", "description": "Create organization units"},
        {"resource_type": "organization", "action": "read", "scope": "organization", "description": "View organization"},
        {"resource_type": "organization", "action": "update", "scope": "organization", "description": "Update organization"},
        {"resource_type": "organization", "action": "delete", "scope": "organization", "description": "Delete organization units"},
        
        # Report permissions
        {"resource_type": "report", "action": "read", "scope": "own", "description": "View own reports"},
        {"resource_type": "report", "action": "read", "scope": "organization", "description": "View all reports"},
        {"resource_type": "report", "action": "create", "scope": "organization", "description": "Create reports"},
        
        # Settings permissions
        {"resource_type": "settings", "action": "read", "scope": "organization", "description": "View settings"},
        {"resource_type": "settings", "action": "update", "scope": "organization", "description": "Update settings"},
        
        # Webhook permissions
        {"resource_type": "webhook", "action": "manage", "scope": "organization", "description": "Manage webhooks"},
        
        # Group permissions
        {"resource_type": "group", "action": "create", "scope": "organization", "description": "Create groups"},
        {"resource_type": "group", "action": "read", "scope": "organization", "description": "View groups"},
        {"resource_type": "group", "action": "update", "scope": "organization", "description": "Update groups"},
        {"resource_type": "group", "action": "delete", "scope": "organization", "description": "Delete groups"},
        
        # Workflow permissions
        {"resource_type": "workflow", "action": "create", "scope": "organization", "description": "Create workflows"},
        {"resource_type": "workflow", "action": "read", "scope": "organization", "description": "View workflows"},
        {"resource_type": "workflow", "action": "update", "scope": "organization", "description": "Update workflows"},
        
        # Analytics permissions
        {"resource_type": "analytics", "action": "read", "scope": "organization", "description": "View analytics"},
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
