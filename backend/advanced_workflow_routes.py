from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from auth_utils import get_current_user
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-workflows", tags=["Advanced Workflows"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# =====================================
# CONDITIONAL ROUTING MODELS
# =====================================

class WorkflowCondition(BaseModel):
    """Conditional routing rule"""
    field: str  # Field to check (e.g., "score", "priority", "amount")
    operator: str  # "equals", "greater_than", "less_than", "contains"
    value: Any  # Value to compare against
    next_step: int  # Step to route to if condition met


class ConditionalStep(BaseModel):
    """Step with conditional routing"""
    step_number: int
    name: str
    conditions: List[Dict[str, Any]]
    default_step: int  # If no conditions met


# =====================================
# SLA TRACKING MODELS
# =====================================

class SLAConfig(BaseModel):
    """SLA configuration for workflow"""
    workflow_template_id: str
    target_hours: int  # Target completion time
    warning_hours: int  # Hours before SLA breach to warn
    escalation_hours: int  # Hours before auto-escalation


class SLAMetrics(BaseModel):
    """SLA performance metrics"""
    total_workflows: int
    within_sla: int
    breached_sla: int
    average_completion_hours: float
    sla_compliance_rate: float


# =====================================
# TIME-BASED PERMISSION MODELS
# =====================================

class TimeBasedPermission(BaseModel):
    """Permission with time restrictions"""
    user_id: str
    permission_id: str
    valid_from: str
    valid_until: str
    days_of_week: List[int] = []  # 0=Monday, 6=Sunday, empty=all days
    hours_of_day: List[int] = []  # 0-23, empty=all hours
    reason: str


# =====================================
# CONDITIONAL ROUTING ENDPOINTS
# =====================================

@router.post("/conditional-routing/evaluate")
async def evaluate_conditional_routing(
    request: Request,
    resource_data: dict,
    conditions: List[Dict[str, Any]],
    default_step: int,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Evaluate conditional routing rules"""
    user = await get_current_user(request, db)
    
    # Evaluate each condition
    for condition in conditions:
        field = condition["field"]
        operator = condition["operator"]
        value = condition["value"]
        next_step = condition["next_step"]
        
        # Get field value from resource data
        resource_value = resource_data.get(field)
        
        if resource_value is None:
            continue
        
        # Evaluate condition
        condition_met = False
        
        if operator == "equals":
            condition_met = resource_value == value
        elif operator == "not_equals":
            condition_met = resource_value != value
        elif operator == "greater_than":
            condition_met = float(resource_value) > float(value)
        elif operator == "less_than":
            condition_met = float(resource_value) < float(value)
        elif operator == "greater_or_equal":
            condition_met = float(resource_value) >= float(value)
        elif operator == "less_or_equal":
            condition_met = float(resource_value) <= float(value)
        elif operator == "contains":
            condition_met = value in str(resource_value)
        elif operator == "in":
            condition_met = resource_value in value
        
        if condition_met:
            return {
                "next_step": next_step,
                "condition_met": True,
                "matched_condition": condition
            }
    
    # No conditions met, use default
    return {
        "next_step": default_step,
        "condition_met": False,
        "matched_condition": None
    }


# =====================================
# SLA TRACKING ENDPOINTS
# =====================================

@router.post("/sla/config")
async def create_sla_config(
    config: SLAConfig,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Configure SLA for a workflow template"""
    user = await get_current_user(request, db)
    
    config_dict = config.model_dump()
    config_dict["organization_id"] = user["organization_id"]
    config_dict["created_by"] = user["id"]
    config_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    # Check if config already exists
    existing = await db.sla_configs.find_one({
        "workflow_template_id": config.workflow_template_id,
        "organization_id": user["organization_id"]
    })
    
    if existing:
        # Update existing
        await db.sla_configs.update_one(
            {"workflow_template_id": config.workflow_template_id},
            {"$set": config_dict}
        )
        return {"message": "SLA config updated"}
    else:
        # Create new
        await db.sla_configs.insert_one(config_dict)
        return {"message": "SLA config created"}


@router.get("/sla/config/{template_id}")
async def get_sla_config(
    template_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get SLA configuration for a workflow template"""
    user = await get_current_user(request, db)
    
    config = await db.sla_configs.find_one({
        "workflow_template_id": template_id,
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA config not found"
        )
    
    return config


@router.get("/sla/metrics/{template_id}")
async def get_sla_metrics(
    template_id: str,
    request: Request,
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get SLA performance metrics for a workflow template"""
    user = await get_current_user(request, db)
    
    # Get SLA config
    config = await db.sla_configs.find_one({
        "workflow_template_id": template_id,
        "organization_id": user["organization_id"]
    })
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA config not found"
        )
    
    target_hours = config["target_hours"]
    
    # Get completed workflows in date range
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    workflows = await db.workflow_instances.find({
        "template_id": template_id,
        "organization_id": user["organization_id"],
        "status": {"$in": ["approved", "rejected"]},
        "completed_at": {"$gte": start_date}
    }).to_list(1000)
    
    total_workflows = len(workflows)
    within_sla = 0
    breached_sla = 0
    total_hours = 0.0
    
    for wf in workflows:
        started = datetime.fromisoformat(wf["started_at"])
        completed = datetime.fromisoformat(wf["completed_at"])
        duration_hours = (completed - started).total_seconds() / 3600
        
        total_hours += duration_hours
        
        if duration_hours <= target_hours:
            within_sla += 1
        else:
            breached_sla += 1
    
    avg_hours = total_hours / total_workflows if total_workflows > 0 else 0
    compliance_rate = (within_sla / total_workflows * 100) if total_workflows > 0 else 0
    
    return SLAMetrics(
        total_workflows=total_workflows,
        within_sla=within_sla,
        breached_sla=breached_sla,
        average_completion_hours=round(avg_hours, 2),
        sla_compliance_rate=round(compliance_rate, 2)
    )


@router.get("/sla/at-risk")
async def get_at_risk_workflows(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get workflows at risk of SLA breach"""
    user = await get_current_user(request, db)
    
    # Get all SLA configs
    configs = await db.sla_configs.find({
        "organization_id": user["organization_id"]
    }).to_list(100)
    
    at_risk = []
    
    for config in configs:
        target_hours = config["target_hours"]
        warning_hours = config.get("warning_hours", target_hours * 0.8)
        
        # Find active workflows for this template
        workflows = await db.workflow_instances.find({
            "template_id": config["workflow_template_id"],
            "organization_id": user["organization_id"],
            "status": {"$in": ["in_progress", "escalated"]}
        }).to_list(100)
        
        now = datetime.now(timezone.utc)
        
        for wf in workflows:
            started = datetime.fromisoformat(wf["started_at"])
            elapsed_hours = (now - started).total_seconds() / 3600
            
            if elapsed_hours >= warning_hours:
                at_risk.append({
                    "workflow_id": wf["id"],
                    "workflow_name": wf["template_name"],
                    "resource_type": wf["resource_type"],
                    "resource_name": wf["resource_name"],
                    "elapsed_hours": round(elapsed_hours, 2),
                    "target_hours": target_hours,
                    "hours_remaining": round(target_hours - elapsed_hours, 2),
                    "at_risk": elapsed_hours >= warning_hours,
                    "breached": elapsed_hours >= target_hours
                })
    
    return at_risk


# =====================================
# TIME-BASED PERMISSIONS
# =====================================

@router.post("/time-based-permissions")
async def create_time_based_permission(
    permission: TimeBasedPermission,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a time-based permission"""
    user = await get_current_user(request, db)
    
    perm_dict = permission.model_dump()
    perm_dict["organization_id"] = user["organization_id"]
    perm_dict["created_by"] = user["id"]
    perm_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.time_based_permissions.insert_one(perm_dict)
    
    return {"message": "Time-based permission created"}


@router.get("/time-based-permissions")
async def list_time_based_permissions(
    request: Request,
    user_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List time-based permissions"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    
    if user_id:
        query["user_id"] = user_id
    
    permissions = await db.time_based_permissions.find(query, {"_id": 0}).to_list(100)
    return permissions


@router.post("/time-based-permissions/check")
async def check_time_based_permission(
    request: Request,
    user_id: str,
    permission_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if time-based permission is currently valid"""
    current_user = await get_current_user(request, db)
    
    permission = await db.time_based_permissions.find_one({
        "user_id": user_id,
        "permission_id": permission_id
    })
    
    if not permission:
        return {"granted": False, "reason": "Permission not found"}
    
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    
    # Check date validity
    if now_iso < permission["valid_from"]:
        return {"granted": False, "reason": "Not yet valid"}
    
    if now_iso > permission["valid_until"]:
        return {"granted": False, "reason": "Expired"}
    
    # Check day of week
    if permission.get("days_of_week"):
        current_day = now.weekday()  # 0=Monday
        if current_day not in permission["days_of_week"]:
            return {"granted": False, "reason": "Not valid on this day"}
    
    # Check hour of day
    if permission.get("hours_of_day"):
        current_hour = now.hour
        if current_hour not in permission["hours_of_day"]:
            return {"granted": False, "reason": "Not valid at this hour"}
    
    return {
        "granted": True,
        "permission": permission,
        "current_time": now_iso
    }


@router.delete("/time-based-permissions/{user_id}/{permission_id}")
async def delete_time_based_permission(
    user_id: str,
    permission_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a time-based permission"""
    user = await get_current_user(request, db)
    
    result = await db.time_based_permissions.delete_one({
        "user_id": user_id,
        "permission_id": permission_id,
        "organization_id": user["organization_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time-based permission not found"
        )
    
    return {"message": "Time-based permission deleted"}
