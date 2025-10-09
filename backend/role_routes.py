from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from permission_models import ExtendedRole, ExtendedRoleCreate
from auth_utils import get_current_user
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/roles", tags=["roles"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# System roles that cannot be deleted
SYSTEM_ROLES = {
    "developer": {
        "name": "Developer",
        "code": "developer",
        "color": "#6366f1",  # Indigo
        "level": 1,
        "description": "Software/Platform OWNER with code access and system control",
        "is_system_role": True
    },
    "master": {
        "name": "Master",
        "code": "master",
        "color": "#9333ea",  # Purple
        "level": 2,
        "description": "Business OWNER with full operational control (no code access)",
        "is_system_role": True
    },
    "admin": {
        "name": "Admin",
        "code": "admin",
        "color": "#ef4444",  # Red
        "level": 3,
        "description": "Organization administrator - admin functions only",
        "is_system_role": True
    },
    "operations_manager": {
        "name": "Operations Manager",
        "code": "operations_manager",
        "color": "#f59e0b",  # Amber
        "level": 4,
        "description": "Manages operational programs and strategic initiatives",
        "is_system_role": True
    },
    "team_lead": {
        "name": "Team Lead",
        "code": "team_lead",
        "color": "#06b6d4",  # Cyan
        "level": 5,
        "description": "Leads teams and manages task assignments",
        "is_system_role": True
    },
    "manager": {
        "name": "Manager",
        "code": "manager",
        "color": "#3b82f6",  # Blue
        "level": 6,
        "description": "Manages branches/departments and approves work",
        "is_system_role": True
    },
    "supervisor": {
        "name": "Supervisor",
        "code": "supervisor",
        "color": "#10b981",  # Emerald
        "level": 7,
        "description": "Supervises field teams and shift assignments",
        "is_system_role": True
    },
    "inspector": {
        "name": "Inspector",
        "code": "inspector",
        "color": "#eab308",  # Yellow
        "level": 8,
        "description": "Executes inspections and operational tasks",
        "is_system_role": True
    },
    "operator": {
        "name": "Operator",
        "code": "operator",
        "color": "#64748b",  # Slate
        "level": 9,
        "description": "Basic operational role for task execution",
        "is_system_role": True
    },
    "viewer": {
        "name": "Viewer",
        "code": "viewer",
        "color": "#22c55e",  # Green
        "level": 10,
        "description": "Read-only access to assigned data",
        "is_system_role": True
    }
}


@router.get("")
async def list_roles(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all roles for the organization"""
    current_user = await get_current_user(request, db)
    
    roles = await db.roles.find(
        {"organization_id": current_user["organization_id"]},
        {"_id": 0}
    ).sort("level", 1).to_list(length=None)
    
    return roles


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_role(
    role: ExtendedRoleCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create custom role"""
    current_user = await get_current_user(request, db)
    
    # Check if role code already exists
    existing = await db.roles.find_one({
        "code": role.code,
        "organization_id": current_user["organization_id"]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this code already exists"
        )
    
    new_role = ExtendedRole(
        **role.dict(),
        organization_id=current_user["organization_id"],
        is_system_role=False
    )
    
    await db.roles.insert_one(new_role.dict())
    
    return new_role


@router.get("/{role_id}")
async def get_role(
    role_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get role details"""
    current_user = await get_current_user(request, db)
    
    role = await db.roles.find_one({
        "id": role_id,
        "organization_id": current_user["organization_id"]
    }, {"_id": 0})
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Get permissions for this role
    permissions = await db.role_permissions.find(
        {"role_id": role_id},
        {"_id": 0}
    ).to_list(length=None)
    
    role["permissions"] = permissions
    
    return role


@router.put("/{role_id}")
async def update_role(
    role_id: str,
    role_update: ExtendedRoleCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update role details"""
    current_user = await get_current_user(request, db)
    
    existing_role = await db.roles.find_one({
        "id": role_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if existing_role.get("is_system_role"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system roles"
        )
    
    update_data = role_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.roles.update_one(
        {"id": role_id},
        {"$set": update_data}
    )
    
    return {"message": "Role updated successfully"}


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete custom role"""
    current_user = await get_current_user(request, db)
    
    role = await db.roles.find_one({
        "id": role_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.get("is_system_role"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system roles"
        )
    
    # Check if any users have this role
    users_with_role = await db.users.count_documents({"role": role_id})
    
    if users_with_role > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role: {users_with_role} users assigned to this role"
        )
    
    await db.roles.delete_one({"id": role_id})
    
    return {"message": "Role deleted successfully"}


async def initialize_system_roles(db: AsyncIOMotorDatabase, organization_id: str):
    """Initialize system roles for an organization"""
    
    for code, role_data in SYSTEM_ROLES.items():
        existing = await db.roles.find_one({
            "code": code,
            "organization_id": organization_id
        })
        
        if not existing:
            role = ExtendedRole(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                **role_data
            )
            await db.roles.insert_one(role.dict())
            print(f"✅ Created system role: {role_data['name']}")