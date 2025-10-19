"""
Permission Dependencies for FastAPI
These dependencies run BEFORE endpoint execution and Pydantic validation
"""
from fastapi import HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from auth_utils import get_current_user
from permission_routes import check_permission


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database from request"""
    return request.app.state.db


async def require_permission(
    resource_type: str,
    action: str,
    scope: str = "organization"
):
    """
    Dependency factory that creates a permission checker
    Usage: @router.post("/endpoint", dependencies=[Depends(require_permission("resource", "create"))])
    """
    async def permission_checker(
        request: Request,
        db: AsyncIOMotorDatabase = Depends(get_db)
    ):
        user = await get_current_user(request, db)
        
        has_permission = await check_permission(
            db,
            user["id"],
            resource_type,
            action,
            scope
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to {action} {resource_type}. Contact your administrator for access."
            )
        
        return user
    
    return permission_checker


# Common permission dependencies
async def require_inspection_create_permission(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Dependency that checks inspection creation permission before endpoint runs"""
    user = await get_current_user(request, db)
    
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "inspection",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create inspection templates"
        )
    
    return user


async def require_task_create_permission(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Dependency that checks task creation permission before endpoint runs"""
    user = await get_current_user(request, db)
    
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "task",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create tasks"
        )
    
    return user


async def require_asset_create_permission(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Dependency that checks asset creation permission before endpoint runs"""
    user = await get_current_user(request, db)
    
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "asset",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create assets"
        )
    
    return user


async def require_workorder_create_permission(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Dependency that checks work order creation permission before endpoint runs"""
    user = await get_current_user(request, db)
    
    from permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "workorder",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create work orders"
        )
    
    return user
