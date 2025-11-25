
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
        "color": "#14b8a6",  # Teal
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
        "color": "#bef264",  # Bright Neon Lime
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
    
    role_dict = new_role.dict()
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = role_dict.copy()
    await db.roles.insert_one(insert_dict)
    
    # Return clean dict without MongoDB _id
    return role_dict


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


@router.get("/{role_id}/permissions")
async def get_role_permissions(
    role_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all permissions for a specific role"""
    current_user = await get_current_user(request, db)
    
    role = await db.roles.find_one({
        "id": role_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get role permissions
    role_perms = await db.role_permissions.find(
        {"role_id": role_id},
        {"_id": 0}
    ).to_list(length=None)
    
    return role_perms


@router.post("/{role_id}/permissions/bulk")
async def update_role_permissions_bulk(
    role_id: str,
    permission_ids: list[str],
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Bulk update permissions for a role"""
    current_user = await get_current_user(request, db)
    
    role = await db.roles.find_one({
        "id": role_id,
        "organization_id": current_user["organization_id"]
    })
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Remove existing permissions for this role
    await db.role_permissions.delete_many({"role_id": role_id})
    
    # Add new permissions
    for perm_id in permission_ids:
        role_perm = {
            "id": str(uuid.uuid4()),
            "role_id": role_id,
            "permission_id": perm_id,
            "granted": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.role_permissions.insert_one(role_perm)
    
    return {"message": f"Updated permissions for role", "count": len(permission_ids)}


async def assign_default_permissions_to_role(db: AsyncIOMotorDatabase, role_id: str, role_code: str):
    """Assign default permissions to a system role based on hierarchy"""
    
    # Define default permission sets by role
    permission_sets = {
        "developer": "all",  # All permissions
        "master": "all",     # All permissions
        "admin": ["inspection.create.team", "inspection.read.all", "inspection.update.own", "inspection.approve.team",
                  "task.create.own", "task.read.team", "task.update.own", "task.assign.team", "task.delete.own",
                  "user.create.organization", "user.read.organization", "user.update.organization", "user.delete.organization",
                  "user.invite.organization", "user.approve.organization", "user.reject.organization",
                  "report.read.all", "report.export.all"],
        "operations_manager": ["inspection.read.all", "inspection.approve.team",
                               "task.read.team", "task.assign.team",
                               "report.read.all", "report.export.all"],
        "team_lead": ["inspection.create.team", "inspection.read.team", "inspection.update.own",
                      "task.create.own", "task.read.team", "task.update.own", "task.assign.team",
                      "report.read.own", "user.read.organization"],
        "manager": ["inspection.read.team", "inspection.approve.team",
                    "task.read.team", "task.assign.team",
                    "report.read.all"],
        "supervisor": ["inspection.read.team", "inspection.update.own",
                       "task.create.own", "task.read.team", "task.update.own",
                       "report.read.own"],
        "inspector": ["inspection.create.own", "inspection.read.own", "inspection.update.own",
                      "task.read.own", "task.update.own"],
        "operator": ["task.read.own", "task.update.own"],
        "viewer": ["inspection.read.own", "task.read.own", "report.read.own"]
    }
    
    perm_set = permission_sets.get(role_code, [])
    
    if perm_set == "all":
        # Get all permissions
        permissions = await db.permissions.find({}, {"_id": 0}).to_list(length=None)
    else:
        # Get specific permissions
        permissions = []
        for perm_key in perm_set:
            parts = perm_key.split(".")
            if len(parts) == 3:
                resource_type, action, scope = parts
                perm = await db.permissions.find_one({
                    "resource_type": resource_type,
                    "action": action,
                    "scope": scope
                })
                if perm:
                    permissions.append(perm)
    
    # Assign permissions to role
    for perm in permissions:
        existing = await db.role_permissions.find_one({
            "role_id": role_id,
            "permission_id": perm["id"]
        })
        
        if not existing:
            role_perm = {
                "id": str(uuid.uuid4()),
                "role_id": role_id,
                "permission_id": perm["id"],
                "granted": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.role_permissions.insert_one(role_perm)


async def initialize_system_roles(db: AsyncIOMotorDatabase, organization_id: str):
    """Initialize system roles for an organization with default permissions"""
    
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
            
            # Assign default permissions
            await assign_default_permissions_to_role(db, role.id, code)
            print(f"✅ Assigned default permissions to: {role_data['name']}")