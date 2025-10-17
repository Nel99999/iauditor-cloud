from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from org_models import (
    OrganizationUnit,
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
    UserOrgAssignment,
    UserOrgAssignmentCreate,
    UserInvitation,
    UserInvitationCreate,
    OrganizationHierarchy,
    PermissionCheck,
)
from auth_utils import get_current_user
from sanitization import sanitize_dict

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


async def check_user_permission(
    user: dict,
    unit_id: str,
    required_role: str,
    db: AsyncIOMotorDatabase
) -> bool:
    """Check if user has permission for a specific unit"""
    # Admin has access to everything
    if user.get("role") == "admin":
        return True
    
    # Check user's assignment to this unit or parent units
    assignment = await db.user_org_assignments.find_one({
        "user_id": user["id"],
        "unit_id": unit_id
    })
    
    if not assignment:
        return False
    
    # Role hierarchy: admin > manager > inspector > viewer
    role_hierarchy = {"admin": 4, "manager": 3, "inspector": 2, "viewer": 1}
    user_role_level = role_hierarchy.get(assignment.get("role", "viewer"), 0)
    required_role_level = role_hierarchy.get(required_role, 0)
    
    return user_role_level >= required_role_level


async def build_unit_path(unit_id: str, db: AsyncIOMotorDatabase) -> str:
    """Build hierarchical path for a unit"""
    path_parts = []
    current_id = unit_id
    
    while current_id:
        unit = await db.organization_units.find_one({"id": current_id}, {"_id": 0})
        if not unit:
            break
        path_parts.insert(0, unit["name"])
        current_id = unit.get("parent_id")
    
    return "/" + "/".join(path_parts)


@router.get("/units")
async def get_organization_units(
    request: Request,
    show_inactive: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all organization units for current user's organization
    
    Args:
        show_inactive: If True, includes inactive units. Default False (active only)
    """
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Build query - show all or active only
    query = {"organization_id": user["organization_id"]}
    if not show_inactive:
        query["is_active"] = True
    
    units = await db.organization_units.find(
        query,
        {"_id": 0}
    ).to_list(1000)
    
    # Calculate user count for each unit
    for unit in units:
        user_count = await db.users.count_documents({
            "org_unit_id": unit["id"],
            "is_active": True
        })
        unit["user_count"] = user_count
    
    return units



@router.get("/units/{unit_id}")
async def get_organization_unit(
    unit_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific organization unit by ID"""
    user = await get_current_user(request, db)
    
    unit = await db.organization_units.find_one(
        {"id": unit_id, "organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    )
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found"
        )
    
    # Get user count for this unit
    user_count = await db.user_org_assignments.count_documents({
        "unit_id": unit_id,
        "organization_id": user["organization_id"]
    })
    unit["user_count"] = user_count
    
    return unit


@router.get("/hierarchy")
async def get_organization_hierarchy(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get organization hierarchy as a tree structure"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Get all units
    units = await db.organization_units.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).sort("level", 1).to_list(1000)
    
    # Get user counts per unit
    user_counts = {}
    assignments = await db.user_org_assignments.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    for assignment in assignments:
        unit_id = assignment["unit_id"]
        user_counts[unit_id] = user_counts.get(unit_id, 0) + 1
    
    # Build tree structure
    unit_map = {}
    for unit in units:
        unit_map[unit["id"]] = {
            "id": unit["id"],
            "name": unit["name"],
            "description": unit.get("description"),
            "level": unit["level"],
            "parent_id": unit.get("parent_id"),
            "children": [],
            "user_count": user_counts.get(unit["id"], 0),
        }
    
    # Build tree by linking children to parents
    root_units = []
    for unit_id, unit_data in unit_map.items():
        parent_id = unit_data["parent_id"]
        if parent_id and parent_id in unit_map:
            unit_map[parent_id]["children"].append(unit_data)
        else:
            root_units.append(unit_data)
    
    return root_units


@router.post("/units", status_code=status.HTTP_201_CREATED)
async def create_organization_unit(
    unit_data: OrganizationUnitCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new organization unit"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Validate parent if provided
    if unit_data.parent_id:
        parent = await db.organization_units.find_one(
            {"id": unit_data.parent_id, "organization_id": user["organization_id"]}
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent unit not found",
            )
        
        # Validate level hierarchy (child must be parent level + 1)
        if unit_data.level != parent["level"] + 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unit level must be {parent['level'] + 1} (one level below parent)",
            )
    elif unit_data.level != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Root units must be level 1",
        )
    
    # Create unit
    unit = OrganizationUnit(
        organization_id=user["organization_id"],
        name=unit_data.name,
        description=unit_data.description,
        level=unit_data.level,
        parent_id=unit_data.parent_id,
        created_by=user["id"],
    )
    
    # Build path
    unit.path = await build_unit_path(unit.id, db)
    
    unit_dict = unit.model_dump()
    unit_dict["created_at"] = unit_dict["created_at"].isoformat()
    unit_dict["updated_at"] = unit_dict["updated_at"].isoformat()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = unit_dict.copy()
    await db.organization_units.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return unit_dict


@router.put("/units/{unit_id}")
async def update_organization_unit(
    unit_id: str,
    unit_data: OrganizationUnitUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an organization unit"""
    user = await get_current_user(request, db)
    
    # Find unit
    unit = await db.organization_units.find_one(
        {"id": unit_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found",
        )
    
    # Update fields
    update_data = unit_data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.organization_units.update_one(
            {"id": unit_id},
            {"$set": update_data}
        )
    
    # Get updated unit
    updated_unit = await db.organization_units.find_one({"id": unit_id}, {"_id": 0})
    return updated_unit


@router.delete("/units/{unit_id}")
async def delete_organization_unit(
    unit_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Soft delete an organization unit"""
    user = await get_current_user(request, db)
    
    # Find unit
    unit = await db.organization_units.find_one(
        {"id": unit_id, "organization_id": user["organization_id"]}
    )
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found",
        )
    
    # Check if unit has children
    children = await db.organization_units.find_one(
        {"parent_id": unit_id, "is_active": True}
    )
    
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete unit with active children",
        )
    
    # Soft delete
    await db.organization_units.update_one(
        {"id": unit_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Organization unit deleted successfully"}


@router.post("/units/{unit_id}/assign-user", status_code=status.HTTP_201_CREATED)
async def assign_user_to_unit(
    unit_id: str,
    assignment_data: UserOrgAssignmentCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Assign a user to an organization unit with a role"""
    user = await get_current_user(request, db)
    
    # Validate unit exists
    unit = await db.organization_units.find_one(
        {"id": unit_id, "organization_id": user["organization_id"]}
    )
    
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found",
        )
    
    # Validate target user exists
    target_user = await db.users.find_one({"id": assignment_data.user_id})
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if already assigned
    existing = await db.user_org_assignments.find_one({
        "user_id": assignment_data.user_id,
        "unit_id": unit_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already assigned to this unit",
        )
    
    # Create assignment
    assignment = UserOrgAssignment(
        user_id=assignment_data.user_id,
        organization_id=user["organization_id"],
        unit_id=unit_id,
        role=assignment_data.role,
        assigned_by=user["id"],
    )
    
    assignment_dict = assignment.model_dump()
    assignment_dict["created_at"] = assignment_dict["created_at"].isoformat()
    
    await db.user_org_assignments.insert_one(assignment_dict)
    
    # Update user's organization_id if not set
    if not target_user.get("organization_id"):
        await db.users.update_one(
            {"id": assignment_data.user_id},
            {"$set": {"organization_id": user["organization_id"]}}
        )
    
    return assignment


@router.get("/units/{unit_id}/users")
async def get_unit_users(
    unit_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all users assigned to a unit"""
    user = await get_current_user(request, db)
    
    # Get assignments
    assignments = await db.user_org_assignments.find(
        {"unit_id": unit_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    # Enrich with user data
    result = []
    for assignment in assignments:
        user_data = await db.users.find_one(
            {"id": assignment["user_id"]},
            {"_id": 0, "password_hash": 0}
        )
        if user_data:
            result.append({
                "assignment_id": assignment["id"],
                "user": user_data,
                "role": assignment["role"],
                "assigned_at": assignment["created_at"]
            })
    
    return result


@router.post("/invitations", status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation_data: UserInvitationCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create an invitation for a user to join the organization"""
    user = await get_current_user(request, db)
    
    if not user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": invitation_data.email})
    if existing_user and existing_user.get("organization_id") == user["organization_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to this organization",
        )
    
    # Create invitation
    invitation = UserInvitation(
        email=invitation_data.email,
        organization_id=user["organization_id"],
        unit_id=invitation_data.unit_id,
        role=invitation_data.role,
        invited_by=user["id"],
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    
    invitation_dict = invitation.model_dump()
    invitation_dict["expires_at"] = invitation_dict["expires_at"].isoformat()
    invitation_dict["created_at"] = invitation_dict["created_at"].isoformat()
    
    await db.user_invitations.insert_one(invitation_dict)
    
    return invitation


@router.get("/invitations")
async def get_invitations(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all pending invitations for the organization"""
    user = await get_current_user(request, db)
    
    invitations = await db.user_invitations.find(
        {"organization_id": user["organization_id"], "status": "pending"},
        {"_id": 0}
    ).to_list(1000)
    
    return invitations