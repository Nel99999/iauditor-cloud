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
async def require_user_read(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Require permission to read users"""
    user = await get_current_user(request, db)
    has_permission = await check_permission(db, user["id"], "user", "read", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to view users")
    return user


async def require_inspection_create(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Require permission to create inspections"""
    user = await get_current_user(request, db)
    has_permission = await check_permission(db, user["id"], "inspection", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create inspections")
    return user


async def require_task_create(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Require permission to create tasks"""
    user = await get_current_user(request, db)
    has_permission = await check_permission(db, user["id"], "task", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create tasks")
    return user


async def require_asset_create(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Require permission to create assets"""
    user = await get_current_user(request, db)
    has_permission = await check_permission(db, user["id"], "asset", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create assets")
    return user


async def require_workorder_create(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Require permission to create work orders"""
    user = await get_current_user(request, db)
    has_permission = await check_permission(db, user["id"], "workorder", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create work orders")
    return user
