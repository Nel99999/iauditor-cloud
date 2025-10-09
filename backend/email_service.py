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
