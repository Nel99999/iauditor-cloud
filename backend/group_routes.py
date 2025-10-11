from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
from group_models import UserGroup, GroupCreate, GroupUpdate, GroupMemberAdd, GroupStats
from auth_utils import get_current_user
import uuid

router = APIRouter(prefix="/groups", tags=["User Groups"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

async def calculate_group_level(db: AsyncIOMotorDatabase, parent_group_id: Optional[str]) -> int:
    """Calculate group nesting level"""
    if not parent_group_id:
        return 1
    
    parent = await db.user_groups.find_one({"id": parent_group_id})
    if parent:
        return parent.get("level", 1) + 1
    return 1


async def update_member_count(db: AsyncIOMotorDatabase, group_id: str):
    """Update member count for a group"""
    group = await db.user_groups.find_one({"id": group_id})
    if group:
        member_count = len(group.get("member_ids", []))
        await db.user_groups.update_one(
            {"id": group_id},
            {"$set": {"member_count": member_count}}
        )


async def get_user_groups_recursive(db: AsyncIOMotorDatabase, user_id: str, org_id: str) -> List[str]:
    """Get all groups a user belongs to (including nested)"""
    groups = await db.user_groups.find(
        {"organization_id": org_id, "member_ids": user_id}
    ).to_list(1000)
    
    group_ids = [g["id"] for g in groups]
    
    # Get parent groups recursively
    for group in groups:
        if group.get("parent_group_id"):
            parent_groups = await get_parent_groups(db, group["parent_group_id"], org_id)
            group_ids.extend(parent_groups)
    
    return list(set(group_ids))


async def get_parent_groups(db: AsyncIOMotorDatabase, group_id: str, org_id: str) -> List[str]:
    """Get all parent groups recursively"""
    parents = []
    current_id = group_id
    
    while current_id:
        group = await db.user_groups.find_one({"id": current_id, "organization_id": org_id})
        if not group:
            break
        parents.append(current_id)
        current_id = group.get("parent_group_id")
    
    return parents


# ==================== ENDPOINTS ====================

@router.post("", response_model=UserGroup)
async def create_group(
    group_data: GroupCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new user group"""
    user = await get_current_user(request, db)
    
    # Check if name already exists
    existing = await db.user_groups.find_one({
        "organization_id": user["organization_id"],
        "name": group_data.name
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group with this name already exists"
        )
    
    # Calculate level
    level = await calculate_group_level(db, group_data.parent_group_id)
    
    # Create group
    group = UserGroup(
        organization_id=user["organization_id"],
        name=group_data.name,
        description=group_data.description,
        color=group_data.color,
        icon=group_data.icon,
        parent_group_id=group_data.parent_group_id,
        level=level,
        role_id=group_data.role_id,
        unit_id=group_data.unit_id,
        created_by=user["id"],
        created_by_name=user["name"]
    )
    
    group_dict = group.model_dump()
    group_dict["created_at"] = group_dict["created_at"].isoformat()
    group_dict["updated_at"] = group_dict["updated_at"].isoformat()
    
    await db.user_groups.insert_one(group_dict)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "group.created",
        "resource_type": "group",
        "resource_id": group.id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"group_name": group.name}
    })
    
    return UserGroup(**group_dict)


@router.get("", response_model=List[UserGroup])
async def get_groups(
    request: Request,
    include_inactive: bool = False,
    parent_group_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all groups for organization"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if not include_inactive:
        query["is_active"] = True
    
    if parent_group_id:
        query["parent_group_id"] = parent_group_id
    
    groups = await db.user_groups.find(query, {"_id": 0}).to_list(1000)
    return [UserGroup(**g) for g in groups]


@router.get("/hierarchy", response_model=List[UserGroup])
async def get_groups_hierarchy(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get groups in hierarchical structure"""
    user = await get_current_user(request, db)
    
    groups = await db.user_groups.find(
        {"organization_id": user["organization_id"], "is_active": True},
        {"_id": 0}
    ).sort("level", 1).sort("name", 1).to_list(1000)
    
    return [UserGroup(**g) for g in groups]


@router.get("/stats", response_model=GroupStats)
async def get_group_stats(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get group statistics"""
    user = await get_current_user(request, db)
    
    groups = await db.user_groups.find(
        {"organization_id": user["organization_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    total_groups = len(groups)
    active_groups = len([g for g in groups if g.get("is_active", True)])
    total_members = sum(g.get("member_count", 0) for g in groups)
    
    groups_by_level = {}
    for group in groups:
        level = group.get("level", 1)
        groups_by_level[f"level_{level}"] = groups_by_level.get(f"level_{level}", 0) + 1
    
    return GroupStats(
        total_groups=total_groups,
        active_groups=active_groups,
        total_members=total_members,
        groups_by_level=groups_by_level
    )


@router.get("/{group_id}", response_model=UserGroup)
async def get_group(
    group_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get specific group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return UserGroup(**group)


@router.put("/{group_id}", response_model=UserGroup)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.get("is_system_group"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system groups"
        )
    
    update_data = group_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.user_groups.update_one(
        {"id": group_id},
        {"$set": update_data}
    )
    
    updated_group = await db.user_groups.find_one({"id": group_id}, {"_id": 0})
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "group.updated",
        "resource_type": "group",
        "resource_id": group_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"changes": list(update_data.keys())}
    })
    
    return UserGroup(**updated_group)


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if group.get("is_system_group"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system groups"
        )
    
    # Check for child groups
    child_groups = await db.user_groups.find_one({
        "parent_group_id": group_id,
        "organization_id": user["organization_id"]
    })
    
    if child_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete group with child groups. Delete child groups first."
        )
    
    # Delete group
    await db.user_groups.delete_one({"id": group_id})
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "group.deleted",
        "resource_type": "group",
        "resource_id": group_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"group_name": group.get("name")}
    })
    
    return {"message": "Group deleted successfully"}


@router.post("/{group_id}/members")
async def add_group_members(
    group_id: str,
    member_data: GroupMemberAdd,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add members to group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Verify all users exist and belong to organization
    for user_id in member_data.user_ids:
        user_exists = await db.users.find_one({
            "id": user_id,
            "organization_id": user["organization_id"]
        })
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} not found in organization"
            )
    
    # Add members (avoid duplicates)
    current_members = set(group.get("member_ids", []))
    new_members = set(member_data.user_ids)
    updated_members = list(current_members | new_members)
    
    await db.user_groups.update_one(
        {"id": group_id},
        {"$set": {"member_ids": updated_members}}
    )
    
    await update_member_count(db, group_id)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "group.members_added",
        "resource_type": "group",
        "resource_id": group_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"added_count": len(new_members - current_members)}
    })
    
    return {"message": f"Added {len(new_members - current_members)} members to group"}


@router.delete("/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: str,
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Remove member from group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Remove member
    await db.user_groups.update_one(
        {"id": group_id},
        {"$pull": {"member_ids": user_id}}
    )
    
    await update_member_count(db, group_id)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "group.member_removed",
        "resource_type": "group",
        "resource_id": group_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"removed_user_id": user_id}
    })
    
    return {"message": "Member removed from group"}


@router.get("/{group_id}/members")
async def get_group_members(
    group_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all members of a group"""
    user = await get_current_user(request, db)
    
    group = await db.user_groups.find_one(
        {"id": group_id, "organization_id": user["organization_id"]}
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    member_ids = group.get("member_ids", [])
    
    if not member_ids:
        return []
    
    # Get user details
    members = await db.users.find(
        {"id": {"$in": member_ids}},
        {"_id": 0, "password": 0, "password_hash": 0}
    ).to_list(1000)
    
    return members


@router.get("/user/{user_id}/groups")
async def get_user_groups(
    user_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all groups a user belongs to"""
    user = await get_current_user(request, db)
    
    groups = await db.user_groups.find(
        {
            "organization_id": user["organization_id"],
            "member_ids": user_id,
            "is_active": True
        },
        {"_id": 0}
    ).to_list(1000)
    
    return [UserGroup(**g) for g in groups]
