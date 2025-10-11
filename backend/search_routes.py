from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Optional
from auth_utils import get_current_user
import re

router = APIRouter(prefix="/search", tags=["Search"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

async def search_users(db: AsyncIOMotorDatabase, query: str, org_id: str, limit: int) -> List[Dict]:
    """Search users"""
    regex = re.compile(query, re.IGNORECASE)
    
    users = await db.users.find(
        {
            "organization_id": org_id,
            "$or": [
                {"name": {"$regex": regex}},
                {"email": {"$regex": regex}}
            ]
        },
        {"_id": 0, "password": 0, "password_hash": 0, "mfa_secret": 0}
    ).limit(limit).to_list(limit)
    
    return [{**user, "type": "user", "title": user.get("name"), "subtitle": user.get("email")} for user in users]


async def search_tasks(db: AsyncIOMotorDatabase, query: str, org_id: str, limit: int) -> List[Dict]:
    """Search tasks"""
    regex = re.compile(query, re.IGNORECASE)
    
    tasks = await db.tasks.find(
        {
            "organization_id": org_id,
            "$or": [
                {"title": {"$regex": regex}},
                {"description": {"$regex": regex}}
            ]
        },
        {"_id": 0}
    ).limit(limit).to_list(limit)
    
    return [{**task, "type": "task", "subtitle": f"Status: {task.get('status')}"} for task in tasks]


async def search_inspections(db: AsyncIOMotorDatabase, query: str, org_id: str, limit: int) -> List[Dict]:
    """Search inspections"""
    regex = re.compile(query, re.IGNORECASE)
    
    inspections = await db.inspection_executions.find(
        {
            "organization_id": org_id,
            "template_name": {"$regex": regex}
        },
        {"_id": 0}
    ).limit(limit).to_list(limit)
    
    return [{**insp, "type": "inspection", "title": insp.get("template_name"), "subtitle": f"Score: {insp.get('score', 'N/A')}"} for insp in inspections]


async def search_checklists(db: AsyncIOMotorDatabase, query: str, org_id: str, limit: int) -> List[Dict]:
    """Search checklists"""
    regex = re.compile(query, re.IGNORECASE)
    
    checklists = await db.checklist_executions.find(
        {
            "organization_id": org_id,
            "template_name": {"$regex": regex}
        },
        {"_id": 0}
    ).limit(limit).to_list(limit)
    
    return [{**check, "type": "checklist", "title": check.get("template_name"), "subtitle": f"{check.get('completion_percentage', 0)}% complete"} for check in checklists]


async def search_groups(db: AsyncIOMotorDatabase, query: str, org_id: str, limit: int) -> List[Dict]:
    """Search groups"""
    regex = re.compile(query, re.IGNORECASE)
    
    groups = await db.user_groups.find(
        {
            "organization_id": org_id,
            "$or": [
                {"name": {"$regex": regex}},
                {"description": {"$regex": regex}}
            ]
        },
        {"_id": 0}
    ).limit(limit).to_list(limit)
    
    return [{**group, "type": "group", "title": group.get("name"), "subtitle": f"{group.get('member_count', 0)} members"} for group in groups]


# ==================== ENDPOINTS ====================

@router.get("/global")
async def global_search(
    q: str,
    request: Request,
    types: Optional[str] = None,  # Comma-separated: user,task,inspection
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Global search across all resources
    
    Query Parameters:
    - q: Search query
    - types: Filter by resource types (comma-separated)
    - limit: Results per type (default: 10)
    """
    user = await get_current_user(request, db)
    
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    
    # Determine which types to search
    search_types = []
    if types:
        search_types = [t.strip() for t in types.split(",")]
    else:
        search_types = ["user", "task", "inspection", "checklist", "group"]
    
    results = {
        "query": q,
        "results": [],
        "total": 0
    }
    
    # Search each type
    if "user" in search_types:
        user_results = await search_users(db, q, user["organization_id"], limit)
        results["results"].extend(user_results)
    
    if "task" in search_types:
        task_results = await search_tasks(db, q, user["organization_id"], limit)
        results["results"].extend(task_results)
    
    if "inspection" in search_types:
        inspection_results = await search_inspections(db, q, user["organization_id"], limit)
        results["results"].extend(inspection_results)
    
    if "checklist" in search_types:
        checklist_results = await search_checklists(db, q, user["organization_id"], limit)
        results["results"].extend(checklist_results)
    
    if "group" in search_types:
        group_results = await search_groups(db, q, user["organization_id"], limit)
        results["results"].extend(group_results)
    
    results["total"] = len(results["results"])
    
    # Group by type
    results["by_type"] = {}
    for result in results["results"]:
        result_type = result["type"]
        if result_type not in results["by_type"]:
            results["by_type"][result_type] = []
        results["by_type"][result_type].append(result)
    
    return results


@router.get("/users")
async def search_users_only(
    q: str,
    request: Request,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search users only"""
    user = await get_current_user(request, db)
    
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    
    results = await search_users(db, q, user["organization_id"], limit)
    return {"results": results, "total": len(results)}


@router.get("/tasks")
async def search_tasks_only(
    q: str,
    request: Request,
    status_filter: Optional[str] = None,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Search tasks only"""
    user = await get_current_user(request, db)
    
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    
    results = await search_tasks(db, q, user["organization_id"], limit)
    
    # Filter by status if provided
    if status_filter:
        results = [r for r in results if r.get("status") == status_filter]
    
    return {"results": results, "total": len(results)}


@router.get("/suggestions")
async def get_search_suggestions(
    q: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get search suggestions (autocomplete)"""
    user = await get_current_user(request, db)
    
    if not q or len(q) < 2:
        return {"suggestions": []}
    
    regex = re.compile(f"^{q}", re.IGNORECASE)
    
    # Get suggestions from different sources
    suggestions = []
    
    # User names
    users = await db.users.find(
        {
            "organization_id": user["organization_id"],
            "name": {"$regex": regex}
        },
        {"name": 1, "_id": 0}
    ).limit(5).to_list(5)
    suggestions.extend([{"text": u["name"], "type": "user"} for u in users])
    
    # Task titles
    tasks = await db.tasks.find(
        {
            "organization_id": user["organization_id"],
            "title": {"$regex": regex}
        },
        {"title": 1, "_id": 0}
    ).limit(5).to_list(5)
    suggestions.extend([{"text": t["title"], "type": "task"} for t in tasks])
    
    # Group names
    groups = await db.user_groups.find(
        {
            "organization_id": user["organization_id"],
            "name": {"$regex": regex}
        },
        {"name": 1, "_id": 0}
    ).limit(5).to_list(5)
    suggestions.extend([{"text": g["name"], "type": "group"} for g in groups])
    
    return {"suggestions": suggestions[:10]}
