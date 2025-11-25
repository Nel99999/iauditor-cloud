"""
Email Retry Service - Wrapper for reliable email delivery with retry logic
"""
from .email_service import EmailService
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class EmailRetryService:
    """Enhanced email service with retry mechanism and audit logging"""
    
    def __init__(self, db: AsyncIOMotorDatabase, email_service: Optional[EmailService] = None):
        self.db = db
        self.email_service = email_service or EmailService()
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # Exponential backoff in seconds
    
    async def send_email_with_retry(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        email_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send email with retry mechanism and database logging
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            email_type: Type of email for logging (e.g., "invitation", "workflow", "reset")
            metadata: Additional metadata to store (workflow_id, user_id, etc.)
            from_email: Optional sender email override
            from_name: Optional sender name override
            
        Returns:
            bool: True if email was sent successfully (within max retries)
        """
        attempt = 0
        last_error = None
        
        # Create initial email log entry
        email_log = {
            "to_email": to_email,
            "subject": subject,
            "email_type": email_type,
            "metadata": metadata or {},
            "attempts": [],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert log entry
        result = await self.db.email_logs.insert_one(email_log)
        log_id = result.inserted_id
        
        while attempt < self.max_retries:
            attempt += 1
            
            try:
                logger.info(f"Attempting to send email to {to_email} (attempt {attempt}/{self.max_retries})")
                
                # Attempt to send email
                success = self.email_service.send_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    from_email=from_email,
                    from_name=from_name
                )
                
                # Log this attempt
                attempt_log = {
                    "attempt_number": attempt,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": success,
                    "error": None
                }
                
                await self.db.email_logs.update_one(
                    {"_id": log_id},
                    {
                        "$push": {"attempts": attempt_log},
                        "$set": {
                            "status": "sent" if success else "pending",
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                if success:
                    logger.info(f"Email sent successfully to {to_email} on attempt {attempt}")
                    return True
                else:
                    last_error = "SendGrid returned non-success status"
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Email send attempt {attempt} failed: {last_error}")
                
                # Log failed attempt
                attempt_log = {
                    "attempt_number": attempt,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": last_error
                }
                
                await self.db.email_logs.update_one(
                    {"_id": log_id},
                    {
                        "$push": {"attempts": attempt_log},
                        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
            
            # If not successful and more retries remaining, wait before next attempt
            if attempt < self.max_retries:
                delay = self.retry_delays[attempt - 1]
                logger.info(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts. Last error: {last_error}")
        
        await self.db.email_logs.update_one(
            {"_id": log_id},
            {
                "$set": {
                    "status": "failed",
                    "final_error": last_error,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return False
    
    async def send_invitation_with_retry(
        self,
        to_email: str,
        inviter_name: str,
        organization_name: str,
        invitation_token: str,
        frontend_url: str
    ) -> bool:
        """Send invitation email with retry"""
        # Build HTML content from email_service template
        invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                .expires {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 You're Invited!</h1>
                </div>
                <div class="content">
                    <p>Hi there!</p>
                    <p><strong>{inviter_name}</strong> has invited you to join <strong>{organization_name}</strong> on OpsPlatform.</p>
                    
                    <div style="text-align: center;">
                        <a href="{invitation_link}" class="button">Accept Invitation</a>
                    </div>
                    
                    <div class="expires">
                        <strong>⏰ Important:</strong> This invitation expires in <strong>7 days</strong>. Please accept it before it expires.
                    </div>
                    
                    <p>OpsPlatform is an operational management platform that helps teams streamline inspections, tasks, and reporting.</p>
                    
                    <p>If you have any questions, please contact your administrator.</p>
                </div>
                <div class="footer">
                    <p>This is an automated email from OpsPlatform. Please do not reply.</p>
                    <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email_with_retry(
            to_email=to_email,
            subject=f'Invitation to join {organization_name} on OpsPlatform',
            html_content=html_content,
            email_type="invitation",
            metadata={
                "inviter_name": inviter_name,
                "organization_name": organization_name,
                "invitation_token": invitation_token
            }
        )
    
    async def get_email_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get email delivery statistics for the last N days"""
        from datetime import timedelta
        
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        total = await self.db.email_logs.count_documents({"created_at": {"$gte": since}})
        sent = await self.db.email_logs.count_documents({
            "created_at": {"$gte": since},
            "status": "sent"
        })
        failed = await self.db.email_logs.count_documents({
            "created_at": {"$gte": since},
            "status": "failed"
        })
        pending = await self.db.email_logs.count_documents({
            "created_at": {"$gte": since},
            "status": "pending"
        })
        
        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "pending": pending,
            "success_rate": (sent / total * 100) if total > 0 else 0,
            "period_days": days
        }
