from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from workflow_models import AuditLog, AuditLogCreate
from auth_utils import get_current_user
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


async def log_audit_event(
    db: AsyncIOMotorDatabase,
    user: dict,
    action: str,
    resource_type: str,
    resource_id: str,
    result: str,
    permission_checked: Optional[str] = None,
    context: dict = None,
    changes: dict = None
):
    """Helper function to log audit events"""
    audit_log = AuditLog(
        organization_id=user["organization_id"],
        user_id=user["id"],
        user_email=user["email"],
        user_name=user["name"],
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        permission_checked=permission_checked,
        result=result,
        context=context or {},
        changes=changes
    )
    
    audit_dict = audit_log.model_dump()
    await db.audit_logs.insert_one(audit_dict)
    
    logger.info(f"Audit: {user['name']} - {action} on {resource_type}/{resource_id} - {result}")


@router.post("/log", status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    log_data: AuditLogCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Manually create an audit log entry"""
    user = await get_current_user(request, db)
    
    await log_audit_event(
        db=db,
        user=user,
        action=log_data.action,
        resource_type=log_data.resource_type,
        resource_id=log_data.resource_id,
        result=log_data.result,
        permission_checked=log_data.permission_checked,
        context=log_data.context,
        changes=log_data.changes
    )
    
    return {"message": "Audit log created successfully"}


@router.get("/logs")
async def get_audit_logs(
    request: Request,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[str] = None,
    result: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get audit logs with filtering"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if action:
        query["action"] = action
    
    if resource_type:
        query["resource_type"] = resource_type
    
    if user_id:
        query["user_id"] = user_id
    
    if result:
        query["result"] = result
    
    if start_date:
        query["timestamp"] = {"$gte": start_date}
    
    if end_date:
        if "timestamp" in query:
            query["timestamp"]["$lte"] = end_date
        else:
            query["timestamp"] = {"$lte": end_date}
    
    logs = await db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return logs


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific audit log"""
    user = await get_current_user(request, db)
    
    log = await db.audit_logs.find_one(
        {"id": log_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return log


@router.get("/stats")
async def get_audit_stats(
    request: Request,
    days: int = 7,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get audit trail statistics"""
    user = await get_current_user(request, db)
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    query = {
        "organization_id": user["organization_id"],
        "timestamp": {"$gte": start_date}
    }
    
    # Total logs
    total_logs = await db.audit_logs.count_documents(query)
    
    # By action
    actions_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    actions = await db.audit_logs.aggregate(actions_pipeline).to_list(100)
    
    # By user
    users_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$user_id", "user_name": {"$first": "$user_name"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_users = await db.audit_logs.aggregate(users_pipeline).to_list(10)
    
    # By result
    results_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$result", "count": {"$sum": 1}}}
    ]
    results = await db.audit_logs.aggregate(results_pipeline).to_list(100)
    
    # Failed permissions
    failed_permissions = await db.audit_logs.count_documents({
        **query,
        "result": "denied"
    })
    
    return {
        "period_days": days,
        "total_logs": total_logs,
        "actions": [{"action": a["_id"], "count": a["count"]} for a in actions],
        "top_users": [{"user_id": u["_id"], "user_name": u["user_name"], "count": u["count"]} for u in top_users],
        "results": [{"result": r["_id"], "count": r["count"]} for r in results],
        "failed_permissions": failed_permissions
    }


@router.post("/compliance-report")
async def generate_compliance_report(
    request: Request,
    start_date: str,
    end_date: str,
    report_type: str = "full",
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Generate compliance report for date range"""
    user = await get_current_user(request, db)
    
    query = {
        "organization_id": user["organization_id"],
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }
    
    # Get all logs in range
    all_logs = await db.audit_logs.find(query, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    
    # Security events
    security_events = [log for log in all_logs if log.get("result") == "denied" or "permission" in log.get("action", "")]
    
    # User activities
    user_activities = {}
    for log in all_logs:
        uid = log["user_id"]
        if uid not in user_activities:
            user_activities[uid] = {
                "user_name": log["user_name"],
                "total_actions": 0,
                "failed_actions": 0,
                "actions": []
            }
        user_activities[uid]["total_actions"] += 1
        if log.get("result") == "denied" or log.get("result") == "failure":
            user_activities[uid]["failed_actions"] += 1
        user_activities[uid]["actions"].append(log["action"])
    
    # Resource changes
    resource_changes = [log for log in all_logs if log.get("changes")]
    
    report = {
        "report_type": report_type,
        "period": {"start": start_date, "end": end_date},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": user["name"],
        "summary": {
            "total_events": len(all_logs),
            "security_events": len(security_events),
            "unique_users": len(user_activities),
            "resource_changes": len(resource_changes)
        },
        "security_events": security_events[:100],  # Limit to 100
        "user_activities": user_activities,
        "resource_changes": resource_changes[:100]  # Limit to 100
    }
    
    if report_type == "summary":
        # Return only summary
        return {
            "report_type": report_type,
            "period": report["period"],
            "generated_at": report["generated_at"],
            "summary": report["summary"]
        }
    
    return report


@router.delete("/logs")
async def purge_old_logs(
    request: Request,
    days: int = 90,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Purge audit logs older than specified days (Developer only)"""
    user = await get_current_user(request, db)
    
    # Only developer role can purge
    if user.get("role") != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only developers can purge audit logs"
        )
    
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    result = await db.audit_logs.delete_many({
        "organization_id": user["organization_id"],
        "timestamp": {"$lt": cutoff_date}
    })
    
    logger.info(f"Purged {result.deleted_count} audit logs older than {days} days")
    
    return {
        "message": f"Purged {result.deleted_count} audit logs",
        "cutoff_date": cutoff_date
    }
