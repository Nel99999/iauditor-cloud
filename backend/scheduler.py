"""
Background Task Scheduler for Workflow Escalations and Maintenance
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase
from workflow_engine import WorkflowEngine
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_workflow_escalations(db: AsyncIOMotorDatabase):
    """Check for workflows that need escalation"""
    try:
        engine = WorkflowEngine(db)
        escalated = await engine.check_escalations()
        
        if escalated:
            logger.info(f"Escalated {len(escalated)} workflows")
            
            # Send escalation notifications
            for workflow in escalated:
                try:
                    # Get new approvers
                    approver_emails = []
                    for approver_id in workflow.get("current_approvers", []):
                        approver = await db.users.find_one({"id": approver_id}, {"email": 1})
                        if approver and approver.get("email"):
                            approver_emails.append(approver["email"])
                    
                    if approver_emails:
                        from email_service import EmailService
                        email_service = EmailService()
                        
                        # Reuse workflow start email for escalations
                        email_service.send_workflow_started_email(
                            to_emails=approver_emails,
                            workflow_name=f"[ESCALATED] {workflow['template_name']}",
                            resource_type=workflow["resource_type"],
                            resource_name=workflow["resource_name"],
                            frontend_url=email_service.client and "https://app.opsplatform.com" or "http://localhost:3000"
                        )
                except Exception as e:
                    logger.error(f"Failed to send escalation email: {str(e)}")
        
    except Exception as e:
        logger.error(f"Escalation check failed: {str(e)}")


async def cleanup_old_audit_logs(db: AsyncIOMotorDatabase):
    """Auto-purge audit logs older than 180 days"""
    try:
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
        
        result = await db.audit_logs.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Auto-purged {result.deleted_count} old audit logs")
    
    except Exception as e:
        logger.error(f"Audit log cleanup failed: {str(e)}")


async def send_workflow_reminders(db: AsyncIOMotorDatabase):
    """Send reminders for workflows approaching due date"""
    try:
        # Find workflows due in next 4 hours
        now = datetime.now(timezone.utc)
        reminder_threshold = (now + timedelta(hours=4)).isoformat()
        
        workflows = await db.workflow_instances.find({
            "status": {"$in": ["in_progress", "escalated"]},
            "due_at": {"$lte": reminder_threshold, "$gte": now.isoformat()}
        }).to_list(100)
        
        if workflows:
            from email_service import EmailService
            email_service = EmailService()
            
            for workflow in workflows:
                # Check if reminder already sent (to avoid spam)
                reminder_sent = workflow.get("reminder_sent", False)
                if not reminder_sent:
                    approver_emails = []
                    for approver_id in workflow.get("current_approvers", []):
                        approver = await db.users.find_one({"id": approver_id}, {"email": 1})
                        if approver and approver.get("email"):
                            approver_emails.append(approver["email"])
                    
                    if approver_emails:
                        try:
                            email_service.send_workflow_started_email(
                                to_emails=approver_emails,
                                workflow_name=f"[REMINDER] {workflow['template_name']}",
                                resource_type=workflow["resource_type"],
                                resource_name=workflow["resource_name"],
                                frontend_url="http://localhost:3000"
                            )
                            
                            # Mark reminder as sent
                            await db.workflow_instances.update_one(
                                {"id": workflow["id"]},
                                {"$set": {"reminder_sent": True}}
                            )
                        except Exception as e:
                            logger.error(f"Failed to send reminder: {str(e)}")
            
            logger.info(f"Sent reminders for {len(workflows)} workflows")
    
    except Exception as e:
        logger.error(f"Workflow reminder failed: {str(e)}")


def start_scheduler(db: AsyncIOMotorDatabase):
    """Start the background scheduler"""
    
    # Check workflow escalations every hour
    scheduler.add_job(
        check_workflow_escalations,
        trigger=IntervalTrigger(hours=1),
        args=[db],
        id="workflow_escalations",
        name="Check Workflow Escalations",
        replace_existing=True
    )
    
    # Send workflow reminders every 2 hours
    scheduler.add_job(
        send_workflow_reminders,
        trigger=IntervalTrigger(hours=2),
        args=[db],
        id="workflow_reminders",
        name="Send Workflow Reminders",
        replace_existing=True
    )
    
    # Cleanup old audit logs daily at 2 AM
    scheduler.add_job(
        cleanup_old_audit_logs,
        trigger=IntervalTrigger(hours=24),
        args=[db],
        id="audit_cleanup",
        name="Cleanup Old Audit Logs",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
