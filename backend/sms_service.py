"""
SMS and WhatsApp Service using Twilio
Handles sending notifications via SMS and WhatsApp
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """SMS and WhatsApp service using Twilio"""
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        phone_number: Optional[str] = None,
        whatsapp_number: Optional[str] = None
    ):
        self.account_sid = account_sid or os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = phone_number or os.environ.get('TWILIO_PHONE_NUMBER')
        self.whatsapp_number = whatsapp_number or os.environ.get('TWILIO_WHATSAPP_NUMBER')
        
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number to E.164 format"""
        # Remove spaces, dashes, and parentheses
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Add + if not present
        if not phone.startswith("+"):
            phone = "+" + phone
        
        return phone
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None
    ) -> dict:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format or will be formatted)
            message: Message body
            from_number: Optional sender number (uses default if not provided)
            
        Returns:
            dict with status and message_sid or error
        """
        if not self.client:
            logger.warning(f"⚠️ Twilio not configured. SMS would be sent to {to_number}")
            return {
                "success": False,
                "error": "Twilio not configured",
                "message": f"SMS to {to_number}: {message}"
            }
        
        try:
            to_number = self._format_phone_number(to_number)
            from_number = from_number or self.phone_number
            
            if not from_number:
                raise ValueError("No sender phone number configured")
            
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "code": e.code
            }
        except Exception as e:
            logger.error(f"Error sending SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_whatsapp(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None,
        media_url: Optional[str] = None
    ) -> dict:
        """
        Send WhatsApp message
        
        Args:
            to_number: Recipient phone number (E.164 format or will be formatted)
            message: Message body
            from_number: Optional sender WhatsApp number (uses default if not provided)
            media_url: Optional media URL (image, PDF, etc.)
            
        Returns:
            dict with status and message_sid or error
        """
        if not self.client:
            logger.warning(f"⚠️ Twilio not configured. WhatsApp would be sent to {to_number}")
            return {
                "success": False,
                "error": "Twilio not configured",
                "message": f"WhatsApp to {to_number}: {message}"
            }
        
        try:
            to_number = self._format_phone_number(to_number)
            from_number = from_number or self.whatsapp_number
            
            if not from_number:
                raise ValueError("No sender WhatsApp number configured")
            
            # Format for WhatsApp
            from_whatsapp = f"whatsapp:{from_number}"
            to_whatsapp = f"whatsapp:{to_number}"
            
            message_params = {
                "body": message,
                "from_": from_whatsapp,
                "to": to_whatsapp
            }
            
            # Add media if provided
            if media_url:
                message_params["media_url"] = [media_url]
            
            message_obj = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp sent successfully to {to_number}, SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "code": e.code
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_bulk_sms(
        self,
        phone_numbers: List[str],
        message: str
    ) -> dict:
        """
        Send SMS to multiple recipients
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: Message body
            
        Returns:
            dict with success count and results
        """
        results = []
        success_count = 0
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                "phone": phone,
                "result": result
            })
            if result.get("success"):
                success_count += 1
        
        return {
            "total": len(phone_numbers),
            "success": success_count,
            "failed": len(phone_numbers) - success_count,
            "results": results
        }
    
    def send_bulk_whatsapp(
        self,
        phone_numbers: List[str],
        message: str,
        media_url: Optional[str] = None
    ) -> dict:
        """
        Send WhatsApp to multiple recipients
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: Message body
            media_url: Optional media URL
            
        Returns:
            dict with success count and results
        """
        results = []
        success_count = 0
        
        for phone in phone_numbers:
            result = self.send_whatsapp(phone, message, media_url=media_url)
            results.append({
                "phone": phone,
                "result": result
            })
            if result.get("success"):
                success_count += 1
        
        return {
            "total": len(phone_numbers),
            "success": success_count,
            "failed": len(phone_numbers) - success_count,
            "results": results
        }
    
    def test_connection(self) -> dict:
        """Test Twilio connection"""
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }
        
        try:
            # Try to fetch account info
            account = self.client.api.accounts(self.account_sid).fetch()
            
            return {
                "success": True,
                "account_sid": account.sid,
                "status": account.status,
                "friendly_name": account.friendly_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_message_status(self, message_sid: str) -> dict:
        """
        Get status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            dict with message status
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio not configured"
            }
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
