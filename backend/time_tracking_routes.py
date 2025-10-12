from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from auth_utils import get_current_user
import uuid

router = APIRouter(prefix="/time-tracking", tags=["Time Tracking"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== MODELS ====================

class TimeEntry(BaseModel):
    """Time entry model"""
    task_id: str
    description: Optional[str] = None
    started_at: Optional[str] = None  # ISO format
    ended_at: Optional[str] = None
    duration_minutes: Optional[int] = None  # Auto-calculated if start/end provided
    billable: bool = False


class TimeEntryUpdate(BaseModel):
    """Update time entry"""
    description: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_minutes: Optional[int] = None
    billable: Optional[bool] = None


# ==================== HELPER FUNCTIONS ====================

def calculate_duration(start_time: str, end_time: str) -> int:
    """Calculate duration in minutes"""
    start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    duration = (end - start).total_seconds() / 60
    return int(duration)


# ==================== ENDPOINTS ====================

@router.post("/entries")
async def create_time_entry(
    entry_data: TimeEntry,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create time entry"""
    user = await get_current_user(request, db)
    
    # Verify task exists
    task = await db.tasks.find_one({
        "id": entry_data.task_id,
        "organization_id": user["organization_id"]
    })
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Calculate duration if start/end provided
    duration = entry_data.duration_minutes
    if entry_data.started_at and entry_data.ended_at and not duration:
        duration = calculate_duration(entry_data.started_at, entry_data.ended_at)
    
    time_entry = {
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "task_id": entry_data.task_id,
        "task_title": task.get("title"),
        "user_id": user["id"],
        "user_name": user["name"],
        "description": entry_data.description,
        "started_at": entry_data.started_at or datetime.now(timezone.utc).isoformat(),
        "ended_at": entry_data.ended_at,
        "duration_minutes": duration,
        "billable": entry_data.billable,
        "is_running": entry_data.ended_at is None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Create a copy for insertion to avoid _id contamination
    insert_dict = time_entry.copy()
    await db.time_entries.insert_one(insert_dict)
    
    # Update task with time tracking
    await db.tasks.update_one(
        {"id": entry_data.task_id},
        {
            "$inc": {"total_time_minutes": duration or 0},
            "$set": {"has_time_entries": True}
        }
    )
    
    # Return clean dict without MongoDB _id
    return time_entry


@router.get("/entries")
async def get_time_entries(
    request: Request,
    task_id: Optional[str] = None,
    user_id: Optional[str] = None,
    running_only: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get time entries"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if task_id:
        query["task_id"] = task_id
    
    if user_id:
        query["user_id"] = user_id
    else:
        query["user_id"] = user["id"]  # Default to current user
    
    if running_only:
        query["is_running"] = True
    
    if start_date:
        query["started_at"] = {"$gte": start_date}
    
    if end_date:
        if "started_at" in query:
            query["started_at"]["$lte"] = end_date
        else:
            query["started_at"] = {"$lte": end_date}
    
    entries = await db.time_entries.find(
        query,
        {"_id": 0}
    ).sort("started_at", -1).limit(limit).to_list(limit)
    
    return {"entries": entries, "total": len(entries)}


@router.get("/entries/{entry_id}")
async def get_time_entry(
    entry_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get specific time entry"""
    user = await get_current_user(request, db)
    
    entry = await db.time_entries.find_one({
        "id": entry_id,
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    return entry


@router.put("/entries/{entry_id}")
async def update_time_entry(
    entry_id: str,
    entry_update: TimeEntryUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update time entry"""
    user = await get_current_user(request, db)
    
    entry = await db.time_entries.find_one({
        "id": entry_id,
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    })
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    update_data = entry_update.model_dump(exclude_unset=True)
    
    # Recalculate duration if dates changed
    if ("started_at" in update_data or "ended_at" in update_data):
        start = update_data.get("started_at", entry.get("started_at"))
        end = update_data.get("ended_at", entry.get("ended_at"))
        
        if start and end:
            update_data["duration_minutes"] = calculate_duration(start, end)
            update_data["is_running"] = False
    
    await db.time_entries.update_one(
        {"id": entry_id},
        {"$set": update_data}
    )
    
    updated_entry = await db.time_entries.find_one({"id": entry_id}, {"_id": 0})
    return updated_entry


@router.post("/entries/{entry_id}/stop")
async def stop_time_entry(
    entry_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Stop running time entry"""
    user = await get_current_user(request, db)
    
    entry = await db.time_entries.find_one({
        "id": entry_id,
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "is_running": True
    })
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Running time entry not found"
        )
    
    end_time = datetime.now(timezone.utc).isoformat()
    duration = calculate_duration(entry["started_at"], end_time)
    
    await db.time_entries.update_one(
        {"id": entry_id},
        {
            "$set": {
                "ended_at": end_time,
                "duration_minutes": duration,
                "is_running": False
            }
        }
    )
    
    # Update task total time
    await db.tasks.update_one(
        {"id": entry["task_id"]},
        {"$inc": {"total_time_minutes": duration}}
    )
    
    return {"message": "Time entry stopped", "duration_minutes": duration}


@router.delete("/entries/{entry_id}")
async def delete_time_entry(
    entry_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete time entry"""
    user = await get_current_user(request, db)
    
    entry = await db.time_entries.find_one({
        "id": entry_id,
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    })
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    # Subtract time from task
    if entry.get("duration_minutes"):
        await db.tasks.update_one(
            {"id": entry["task_id"]},
            {"$inc": {"total_time_minutes": -entry["duration_minutes"]}}
        )
    
    await db.time_entries.delete_one({"id": entry_id})
    
    return {"message": "Time entry deleted"}


@router.get("/stats")
async def get_time_tracking_stats(
    request: Request,
    task_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get time tracking statistics"""
    user = await get_current_user(request, db)
    
    query = {
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    }
    
    if task_id:
        query["task_id"] = task_id
    
    if start_date:
        query["started_at"] = {"$gte": start_date}
    
    if end_date:
        if "started_at" in query:
            query["started_at"]["$lte"] = end_date
        else:
            query["started_at"] = {"$lte": end_date}
    
    entries = await db.time_entries.find(query, {"_id": 0}).to_list(1000)
    
    total_minutes = sum(e.get("duration_minutes", 0) for e in entries if not e.get("is_running"))
    billable_minutes = sum(e.get("duration_minutes", 0) for e in entries if e.get("billable") and not e.get("is_running"))
    
    return {
        "total_entries": len(entries),
        "total_hours": round(total_minutes / 60, 2),
        "total_minutes": total_minutes,
        "billable_hours": round(billable_minutes / 60, 2),
        "billable_minutes": billable_minutes,
        "non_billable_hours": round((total_minutes - billable_minutes) / 60, 2),
        "running_entries": len([e for e in entries if e.get("is_running")])
    }


@router.get("/reports/daily")
async def get_daily_time_report(
    request: Request,
    date: Optional[str] = None,  # YYYY-MM-DD
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get daily time report"""
    user = await get_current_user(request, db)
    
    # Default to today
    if not date:
        date = datetime.now(timezone.utc).date().isoformat()
    
    # Get entries for the day
    start_of_day = f"{date}T00:00:00Z"
    end_of_day = f"{date}T23:59:59Z"
    
    entries = await db.time_entries.find({
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "started_at": {"$gte": start_of_day, "$lte": end_of_day}
    }, {"_id": 0}).to_list(1000)
    
    # Group by task
    by_task = {}
    for entry in entries:
        task_id = entry["task_id"]
        if task_id not in by_task:
            by_task[task_id] = {
                "task_id": task_id,
                "task_title": entry.get("task_title"),
                "entries": [],
                "total_minutes": 0
            }
        by_task[task_id]["entries"].append(entry)
        if not entry.get("is_running"):
            by_task[task_id]["total_minutes"] += entry.get("duration_minutes", 0)
    
    return {
        "date": date,
        "total_minutes": sum(e.get("duration_minutes", 0) for e in entries if not e.get("is_running")),
        "total_hours": round(sum(e.get("duration_minutes", 0) for e in entries if not e.get("is_running")) / 60, 2),
        "tasks": list(by_task.values())
    }
