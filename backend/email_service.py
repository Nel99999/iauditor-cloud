from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from typing import Optional

class EmailService:
    """Email service using SendGrid"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('SENDGRID_API_KEY')
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
    
    def send_invitation_email(
        self,
        to_email: str,
        inviter_name: str,
        organization_name: str,
        invitation_token: str,
        frontend_url: str
    ) -> bool:
        """Send invitation email"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
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
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject=f'Invitation to join {organization_name} on OpsPlatform',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_invitation_reminder(
        self,
        to_email: str,
        organization_name: str,
        days_left: int,
        invitation_token: str,
        frontend_url: str
    ) -> bool:
        """Send invitation reminder email"""
        if not self.client:
            return False
        
        try:
            invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ef4444; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #ef4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .urgent {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⏰ Invitation Expiring Soon</h1>
                    </div>
                    <div class="content">
                        <div class="urgent">
                            <strong>⚠️ Urgent:</strong> Your invitation to join <strong>{organization_name}</strong> expires in <strong>{days_left} day(s)</strong>!
                        </div>
                        
                        <p>You haven't accepted your invitation yet. Don't miss out!</p>
                        
                        <div style="text-align: center;">
                            <a href="{invitation_link}" class="button">Accept Invitation Now</a>
                        </div>
                        
                        <p>After the invitation expires, you'll need to request a new one from your administrator.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject=f'Reminder: Your OpsPlatform invitation expires in {days_left} day(s)',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send reminder: {str(e)}")
            return False

    
    def send_registration_pending_email(
        self,
        to_email: str,
        name: str,
        organization_name: str = "OpsPlatform"
    ) -> bool:
        """Send email to user after registration (pending approval)"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .info-box {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Registration Successful!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name},</p>
                        <p>Thank you for registering with {organization_name}!</p>
                        
                        <div class="info-box">
                            <strong>ℹ️ Account Status:</strong> Your account is currently <strong>pending approval</strong>. 
                            An administrator will review your registration and you'll receive an email once your account is approved.
                        </div>
                        
                        <p>This usually takes 24-48 hours. You'll receive an email notification once your account is approved and you can start using the platform.</p>
                        
                        <p>If you have any questions, please contact your administrator.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from {organization_name}. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject='Registration Successful - Pending Approval',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send registration pending email: {str(e)}")
            return False
    
    def send_registration_approved_email(
        self,
        to_email: str,
        name: str,
        login_url: str,
        organization_name: str = "OpsPlatform"
    ) -> bool:
        """Send email to user when registration is approved"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Account Approved!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name},</p>
                        <p>Great news! Your account for <strong>{organization_name}</strong> has been approved.</p>
                        
                        <div class="success-box">
                            <strong>✅ You can now log in and start using the platform!</strong>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{login_url}" class="button">Log In Now</a>
                        </div>
                        
                        <p>If you have any questions or need assistance getting started, please contact your administrator.</p>
                        
                        <p>Welcome aboard!</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from {organization_name}. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject='Account Approved - Welcome to OpsPlatform!',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send approval email: {str(e)}")
            return False
    
    def send_registration_rejected_email(
        self,
        to_email: str,
        name: str,
        reason: Optional[str] = None,
        organization_name: str = "OpsPlatform"
    ) -> bool:
        """Send email to user when registration is rejected"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
            reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                    .warning-box {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Registration Update</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name},</p>
                        <p>We regret to inform you that your registration for <strong>{organization_name}</strong> was not approved at this time.</p>
                        
                        <div class="warning-box">
                            {reason_text}
                        </div>
                        
                        <p>If you believe this was a mistake or would like more information, please contact your administrator or support team.</p>
                        
                        <p>You're welcome to re-register if your circumstances have changed.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from {organization_name}. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject='Registration Status Update',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send rejection email: {str(e)}")
            return False

    
    def test_connection(self) -> bool:
        """Test SendGrid connection"""
        if not self.client:
            return False
        
        try:
            # SendGrid doesn't have a dedicated ping endpoint, so we'll just check if client exists
            return True
        except Exception as e:
            print(f"❌ SendGrid test failed: {str(e)}")
            return False

    
    def send_workflow_started_email(
        self,
        to_emails: list,
        workflow_name: str,
        resource_type: str,
        resource_name: str,
        frontend_url: str
    ) -> bool:
        """Send notification when workflow is started"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_emails}")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .info-box {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📋 New Approval Request</h1>
                    </div>
                    <div class="content">
                        <p>Hi there!</p>
                        <p>A new workflow <strong>{workflow_name}</strong> has been started and requires your approval.</p>
                        <div class="info-box">
                            <p><strong>Resource Type:</strong> {resource_type}</p>
                            <p><strong>Resource Name:</strong> {resource_name}</p>
                        </div>
                        <p>Please review and take action on this workflow.</p>
                        <a href="{frontend_url}/approvals" class="button">View My Approvals</a>
                        <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                            Click the button above to go to your approvals dashboard.
                        </p>
                    </div>
                    <div class="footer">
                        <p>© 2025 OpsPlatform. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            for email in to_emails:
                message = Mail(
                    from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                    to_emails=To(email),
                    subject=f'New Approval Request: {workflow_name}',
                    html_content=Content("text/html", html_content)
                )
                self.client.send(message)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send workflow start email: {str(e)}")
            return False
    
    def send_workflow_approved_email(
        self,
        to_email: str,
        workflow_name: str,
        resource_type: str,
        resource_name: str,
        approved_by: str,
        frontend_url: str
    ) -> bool:
        """Send notification when workflow is approved"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Workflow Approved!</h1>
                    </div>
                    <div class="content">
                        <p>Hi there!</p>
                        <p>Great news! Your workflow <strong>{workflow_name}</strong> has been approved.</p>
                        <div class="success-box">
                            <p><strong>Resource Type:</strong> {resource_type}</p>
                            <p><strong>Resource Name:</strong> {resource_name}</p>
                            <p><strong>Approved By:</strong> {approved_by}</p>
                        </div>
                        <a href="{frontend_url}/workflows" class="button">View Workflow</a>
                    </div>
                    <div class="footer">
                        <p>© 2025 OpsPlatform. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject=f'Workflow Approved: {workflow_name}',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send workflow approved email: {str(e)}")
            return False
    
    def send_workflow_rejected_email(
        self,
        to_email: str,
        workflow_name: str,
        resource_type: str,
        resource_name: str,
        rejected_by: str,
        comments: str,
        frontend_url: str
    ) -> bool:
        """Send notification when workflow is rejected"""
        if not self.client:
            print(f"⚠️ SendGrid not configured. Email would be sent to {to_email}")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
                    .button {{ display: inline-block; background: #ef4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .error-box {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ Workflow Rejected</h1>
                    </div>
                    <div class="content">
                        <p>Hi there!</p>
                        <p>Your workflow <strong>{workflow_name}</strong> has been rejected.</p>
                        <div class="error-box">
                            <p><strong>Resource Type:</strong> {resource_type}</p>
                            <p><strong>Resource Name:</strong> {resource_name}</p>
                            <p><strong>Rejected By:</strong> {rejected_by}</p>
                            <p><strong>Comments:</strong> {comments or 'No comments provided'}</p>
                        </div>
                        <p>Please review the comments and take appropriate action.</p>
                        <a href="{frontend_url}/workflows" class="button">View Workflow</a>
                    </div>
                    <div class="footer">
                        <p>© 2025 OpsPlatform. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email('noreply@opsplatform.com', 'OpsPlatform'),
                to_emails=To(to_email),
                subject=f'Workflow Rejected: {workflow_name}',
                html_content=Content("text/html", html_content)
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ Failed to send workflow rejected email: {str(e)}")
            return False

