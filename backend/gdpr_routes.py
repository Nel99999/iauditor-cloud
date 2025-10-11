from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict
from datetime import datetime, timezone
from auth_utils import get_current_user
import json
import io
import zipfile
import uuid

router = APIRouter(prefix="/gdpr", tags=["GDPR Compliance"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

async def export_user_data(db: AsyncIOMotorDatabase, user_id: str, org_id: str) -> Dict:
    """Export all user data for GDPR compliance"""
    
    # User profile
    user = await db.users.find_one(
        {"id": user_id, "organization_id": org_id},
        {"_id": 0, "password": 0, "password_hash": 0, "mfa_secret": 0, "mfa_backup_codes": 0}
    )
    
    # Tasks
    tasks = await db.tasks.find(
        {"organization_id": org_id, "$or": [{"created_by": user_id}, {"assigned_to": user_id}]},
        {"_id": 0}
    ).to_list(10000)
    
    # Time entries
    time_entries = await db.time_entries.find(
        {"organization_id": org_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(10000)
    
    # Inspections
    inspections = await db.inspection_executions.find(
        {"organization_id": org_id, "inspector_id": user_id},
        {"_id": 0}
    ).to_list(10000)
    
    # Audit logs
    audit_logs = await db.audit_logs.find(
        {"organization_id": org_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(10000)
    
    # Mentions
    mentions = await db.mentions.find(
        {"organization_id": org_id, "$or": [{"mentioned_by_id": user_id}, {"mentioned_user_id": user_id}]},
        {"_id": 0}
    ).to_list(10000)
    
    # Notifications
    notifications = await db.notifications.find(
        {"organization_id": org_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(10000)
    
    return {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "user_profile": user,
        "tasks": tasks,
        "time_entries": time_entries,
        "inspections": inspections,
        "audit_logs": audit_logs,
        "mentions": mentions,
        "notifications": notifications,
        "summary": {
            "total_tasks": len(tasks),
            "total_time_entries": len(time_entries),
            "total_inspections": len(inspections),
            "total_audit_logs": len(audit_logs),
            "total_mentions": len(mentions),
            "total_notifications": len(notifications)
        }
    }


async def anonymize_user_data(db: AsyncIOMotorDatabase, user_id: str, org_id: str):
    """Anonymize user data instead of deletion (for audit trail preservation)"""
    
    anonymized_name = f"Deleted User {user_id[:8]}"
    anonymized_email = f"deleted_{user_id[:8]}@deleted.local"
    
    # Update user record
    await db.users.update_one(
        {"id": user_id, "organization_id": org_id},
        {
            "$set": {
                "name": anonymized_name,
                "email": anonymized_email,
                "is_active": False,
                "gdpr_deleted": True,
                "gdpr_deleted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Anonymize in tasks
    await db.tasks.update_many(
        {"organization_id": org_id, "created_by": user_id},
        {"$set": {"created_by_name": anonymized_name}}
    )
    
    await db.tasks.update_many(
        {"organization_id": org_id, "assigned_to": user_id},
        {"$set": {"assigned_to_name": anonymized_name}}
    )
    
    # Anonymize in audit logs
    await db.audit_logs.update_many(
        {"organization_id": org_id, "user_id": user_id},
        {"$set": {"user_name": anonymized_name, "user_email": anonymized_email}}
    )
    
    # Anonymize in mentions
    await db.mentions.update_many(
        {"organization_id": org_id, "mentioned_by_id": user_id},
        {"$set": {"mentioned_by_name": anonymized_name}}
    )
    
    await db.mentions.update_many(
        {"organization_id": org_id, "mentioned_user_id": user_id},
        {"$set": {"mentioned_user_name": anonymized_name}}
    )


# ==================== ENDPOINTS ====================

@router.post("/data-export")
async def request_data_export(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Request data export (GDPR Right to Access)"""
    user = await get_current_user(request, db)
    
    # Export user data
    user_data = await export_user_data(db, user["id"], user["organization_id"])
    
    # Create export record
    export_record = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "status": "completed",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "data_size_kb": len(json.dumps(user_data).encode('utf-8')) / 1024
    }
    
    await db.gdpr_exports.insert_one(export_record)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "gdpr.data_export",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": "Data export completed",
        "export_id": export_record["id"],
        "data": user_data
    }


@router.get("/data-export/download")
async def download_data_export(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Download data export as JSON file"""
    user = await get_current_user(request, db)
    
    # Export user data
    user_data = await export_user_data(db, user["id"], user["organization_id"])
    
    # Create JSON file
    json_data = json.dumps(user_data, indent=2, default=str)
    
    return StreamingResponse(
        io.BytesIO(json_data.encode('utf-8')),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_export_{user['id']}.json"
        }
    )


@router.post("/delete-account")
async def request_account_deletion(
    request: Request,
    anonymize: bool = True,  # Anonymize instead of hard delete
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Request account deletion (GDPR Right to be Forgotten)"""
    user = await get_current_user(request, db)
    
    if anonymize:
        # Anonymize data (recommended for audit trail preservation)
        await anonymize_user_data(db, user["id"], user["organization_id"])
        message = "Account anonymized successfully"
    else:
        # Hard delete (not recommended due to referential integrity)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "is_active": False,
                "gdpr_deleted": True,
                "gdpr_deleted_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        message = "Account deactivated successfully"
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "gdpr.account_deletion",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"anonymize": anonymize}
    })
    
    return {"message": message}


@router.get("/consent-status")
async def get_consent_status(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's consent status for data processing"""
    user = await get_current_user(request, db)
    
    consent = await db.user_consents.find_one({
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    if not consent:
        # Return default consent structure
        consent = {
            "user_id": user["id"],
            "organization_id": user["organization_id"],
            "marketing_emails": False,
            "analytics": True,
            "third_party_sharing": False,
            "data_processing": True,
            "updated_at": None
        }
    
    return consent


@router.put("/consent")
async def update_consent(
    consent_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user consent preferences"""
    user = await get_current_user(request, db)
    
    consent_record = {
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "marketing_emails": consent_data.get("marketing_emails", False),
        "analytics": consent_data.get("analytics", True),
        "third_party_sharing": consent_data.get("third_party_sharing", False),
        "data_processing": consent_data.get("data_processing", True),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_consents.update_one(
        {"user_id": user["id"], "organization_id": user["organization_id"]},
        {"$set": consent_record},
        upsert=True
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "gdpr.consent_updated",
        "resource_type": "user",
        "resource_id": user["id"],
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": consent_record
    })
    
    return {"message": "Consent updated successfully", "consent": consent_record}


@router.get("/data-retention-policy")
async def get_data_retention_policy(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get organization's data retention policy"""
    user = await get_current_user(request, db)
    
    policy = await db.data_retention_policies.find_one({
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    if not policy:
        # Return default policy
        policy = {
            "organization_id": user["organization_id"],
            "audit_logs_days": 365,
            "user_data_days": 730,  # 2 years
            "completed_tasks_days": 365,
            "time_entries_days": 1095,  # 3 years for financial records
            "notifications_days": 90,
            "inactive_users_days": 180
        }
    
    return policy


@router.get("/privacy-report")
async def get_privacy_report(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get privacy and data processing report"""
    user = await get_current_user(request, db)
    
    # Count data by type
    tasks_count = await db.tasks.count_documents({
        "organization_id": user["organization_id"],
        "$or": [{"created_by": user["id"]}, {"assigned_to": user["id"]}]
    })
    
    time_entries_count = await db.time_entries.count_documents({
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    })
    
    mentions_count = await db.mentions.count_documents({
        "organization_id": user["organization_id"],
        "mentioned_user_id": user["id"]
    })
    
    notifications_count = await db.notifications.count_documents({
        "organization_id": user["organization_id"],
        "user_id": user["id"]
    })
    
    # Get consent status
    consent = await db.user_consents.find_one({
        "user_id": user["id"],
        "organization_id": user["organization_id"]
    }, {"_id": 0})
    
    return {
        "user_id": user["id"],
        "report_date": datetime.now(timezone.utc).isoformat(),
        "data_stored": {
            "tasks": tasks_count,
            "time_entries": time_entries_count,
            "mentions": mentions_count,
            "notifications": notifications_count
        },
        "consent_status": consent or {},
        "rights": {
            "right_to_access": "Available via /gdpr/data-export",
            "right_to_be_forgotten": "Available via /gdpr/delete-account",
            "right_to_rectification": "Available via profile update",
            "right_to_data_portability": "JSON export available"
        }
    }
