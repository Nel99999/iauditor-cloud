# 📱 Twilio SMS & WhatsApp Integration Guide

## Overview

Your platform now supports **SMS and WhatsApp messaging** via Twilio for:
- Workflow approval notifications
- Task assignment alerts
- Inspection reminders
- Emergency notifications  
- User invitations (optional SMS channel)

---

## 🚀 Quick Start

### Step 1: Get Twilio Credentials

1. **Create a Twilio Account**
   - Go to https://www.twilio.com/
   - Sign up for a free account
   - Get **$15 free credit** for testing

2. **Get Your Credentials** (from Twilio Console)
   - **Account SID** - Found on dashboard
   - **Auth Token** - Found on dashboard (click "View" to reveal)
   - **Phone Number** - Purchase a phone number ($1/month for SMS-capable number)

3. **Setup WhatsApp (Optional)**
   - Go to Messaging → Try it Out → Send a WhatsApp message
   - Follow instructions to join the WhatsApp Sandbox
   - Get your **WhatsApp Number** (format: `whatsapp:+14155238886`)
   - For production: Apply for WhatsApp Business API approval

### Step 2: Configure in Your App

1. **Navigate to Settings**
   - Login as Admin/Master/Developer
   - Go to Settings → Integrations (or Communications)

2. **Enter Twilio Credentials**
   ```
   Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Auth Token: your_auth_token_here
   Phone Number: +1234567890 (your Twilio number)
   WhatsApp Number: +14155238886 (optional, for WhatsApp)
   ```

3. **Test Connection**
   - Click "Test Connection" button
   - Should see "✅ Twilio connection successful"

---

## 📡 API Endpoints

### Configuration

**Get Settings** (Admin only)
```bash
GET /api/sms/settings
Authorization: Bearer {token}
```

**Save Settings** (Admin only)
```bash
POST /api/sms/settings
{
  "account_sid": "ACxxxxx",
  "auth_token": "your_token",
  "phone_number": "+1234567890",
  "whatsapp_number": "+14155238886"
}
```

**Test Connection**
```bash
POST /api/sms/test-connection
Authorization: Bearer {token}
```

### Sending Messages

**Send SMS**
```bash
POST /api/sms/send
{
  "to_number": "+1234567890",
  "message": "Your workflow has been approved!",
  "from_number": "+0987654321"  // optional
}
```

**Send WhatsApp**
```bash
POST /api/sms/whatsapp/send
{
  "to_number": "+1234567890",
  "message": "Task assigned: Review inspection report",
  "media_url": "https://example.com/image.jpg"  // optional
}
```

**Send Bulk SMS**
```bash
POST /api/sms/send-bulk
{
  "phone_numbers": ["+1111111111", "+2222222222"],
  "message": "Emergency: System maintenance at 10 PM"
}
```

**Send Bulk WhatsApp**
```bash
POST /api/sms/whatsapp/send-bulk
{
  "phone_numbers": ["+1111111111", "+2222222222"],
  "message": "Team meeting tomorrow at 9 AM",
  "media_url": "https://example.com/agenda.pdf"  // optional
}
```

**Check Message Status**
```bash
GET /api/sms/message-status/{message_sid}
```

### User Preferences

**Get Preferences**
```bash
GET /api/sms/preferences
```

**Update Preferences**
```bash
PUT /api/sms/preferences
{
  "sms_enabled": true,
  "whatsapp_enabled": true,
  "phone_number": "+1234567890"
}
```

---

## 💡 Use Cases

### 1. Workflow Notifications

```python
# In workflow_engine.py
from sms_service import SMSService

# Send approval notification
sms_service = SMSService()
sms_service.send_sms(
    to_number=approver_phone,
    message=f"Workflow '{workflow_name}' requires your approval. View: {link}"
)
```

### 2. Task Assignments

```python
# When task is assigned
sms_service.send_whatsapp(
    to_number=assignee_phone,
    message=f"New task assigned: {task_title}. Priority: {priority}"
)
```

### 3. Inspection Alerts

```python
# Send inspection reminder with photo
sms_service.send_whatsapp(
    to_number=inspector_phone,
    message="Inspection due in 1 hour: Safety Checklist",
    media_url="https://your-app.com/inspection-photo.jpg"
)
```

### 4. Emergency Notifications

```python
# Bulk alert to all users
phone_numbers = [user['phone'] for user in users if user.get('phone')]
sms_service.send_bulk_sms(
    phone_numbers=phone_numbers,
    message="URGENT: System maintenance starting in 30 minutes"
)
```

---

## 📝 Phone Number Format

**Always use E.164 format:**
```
✅ Correct: +1234567890
✅ Correct: +447700900123
❌ Wrong: 1234567890
❌ Wrong: (123) 456-7890
```

The SMS service auto-formats numbers, but E.164 is recommended.

---

## 🔒 Security Best Practices

1. **Never Expose Credentials**
   - Store in database (encrypted)
   - Never log Auth Token
   - Use environment variables for defaults

2. **Rate Limiting**
   - Twilio has rate limits
   - Implement cooldown periods
   - Use bulk endpoints for multiple recipients

3. **Validate Phone Numbers**
   - Check format before sending
   - Use Twilio Lookup API (optional)
   - Handle invalid number errors

4. **User Consent**
   - Get user permission before sending
   - Provide opt-out mechanism
   - Respect notification preferences

5. **Cost Management**
   - SMS: ~$0.0075 per message
   - WhatsApp: ~$0.005 per message
   - Set budget alerts in Twilio Console

---

## 💰 Pricing (2024)

### SMS
- **US/Canada**: $0.0075 per message
- **International**: $0.01 - $0.20 per message
- **Monthly Phone Number**: $1.00

### WhatsApp
- **Business-initiated**: $0.005 - $0.020 per message
- **User-initiated (24h window)**: Free
- **Setup**: Free sandbox, $0 for production

### Voice (Not Implemented)
- Voice calls: $0.013 - $0.085 per minute
- Currently NO voice functionality

---

## 🧪 Testing

### Sandbox Testing (Free)

**SMS Sandbox:**
- Use verified phone numbers
- Add numbers in Twilio Console → Phone Numbers → Verified Caller IDs
- No cost for sandbox testing

**WhatsApp Sandbox:**
1. Go to Messaging → Try WhatsApp
2. Send "join {your-code}" to sandbox number
3. Test messages for free
4. Sandbox number: `whatsapp:+14155238886` (example)

### Production Testing

```python
# Test SMS
result = sms_service.send_sms(
    to_number="+1234567890",
    message="Test message from your app"
)
print(result)

# Test WhatsApp
result = sms_service.send_whatsapp(
    to_number="+1234567890",
    message="Test WhatsApp message",
    media_url="https://example.com/test.jpg"
)
print(result)

# Check status
status = sms_service.get_message_status(result['message_sid'])
print(status)
```

---

## 🐛 Troubleshooting

### Common Errors

**Error: "Twilio not configured"**
- Solution: Add Twilio credentials in Settings

**Error: "The 'To' number is not a valid phone number"**
- Solution: Use E.164 format (+1234567890)

**Error: "The number +X is unverified"**
- Solution: Verify number in Twilio Console (trial accounts only)

**Error: "Permission to send an SMS has not been enabled"**
- Solution: Upgrade Twilio account or verify phone number

**WhatsApp Error: "User not in allowed list"**
- Solution: Join WhatsApp sandbox first

### Check Logs

```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log | grep -i twilio

# Database settings
mongo operations_db
db.organization_settings.find({}, {twilio_account_sid: 1})
```

---

## 🔄 Integration with Existing Features

### Notification System

Update `notification_routes.py` to support SMS/WhatsApp:

```python
async def send_notification(user_id, message):
    # Get user preferences
    prefs = await db.user_preferences.find_one({"user_id": user_id})
    
    # Send via SMS if enabled
    if prefs.get('sms_enabled') and prefs.get('phone_number'):
        sms_service.send_sms(
            to_number=prefs['phone_number'],
            message=message
        )
    
    # Send via WhatsApp if enabled
    if prefs.get('whatsapp_enabled') and prefs.get('phone_number'):
        sms_service.send_whatsapp(
            to_number=prefs['phone_number'],
            message=message
        )
    
    # Also send in-app notification (existing)
    await create_notification(user_id, message)
```

### User Profile

Add phone number field to user profile:
- Settings → Profile → Phone Number
- Auto-validates E.164 format
- Used for SMS/WhatsApp notifications

---

## 📊 Monitoring

### Twilio Console
- View message logs
- Monitor delivery rates
- Check error rates
- Set up usage alerts

### Database Tracking
```javascript
// Store message history
{
  message_sid: "SM...",
  to: "+1234567890",
  type: "sms" | "whatsapp",
  status: "sent" | "delivered" | "failed",
  sent_at: ISODate(),
  delivered_at: ISODate(),
  error: null
}
```

---

## 🚀 Next Steps

1. **Setup Twilio Account** (5 min)
2. **Configure in App** (2 min)
3. **Test Connection** (1 min)
4. **Enable User Preferences** (users can opt-in)
5. **Integrate with Workflows** (add notification calls)
6. **Monitor Usage** (check Twilio Console)

---

## 📞 Support

**Twilio Support:**
- Docs: https://www.twilio.com/docs
- Support: https://support.twilio.com/
- Community: https://www.twilio.com/community

**Implementation Support:**
- Backend: `/app/backend/sms_service.py`
- Routes: `/app/backend/sms_routes.py`
- API Docs: `{your-url}/api/docs#/SMS%20%26%20WhatsApp`

---

## ✅ Verification Checklist

- [ ] Twilio account created
- [ ] Phone number purchased
- [ ] Credentials configured in app
- [ ] Test connection successful
- [ ] SMS test message sent
- [ ] WhatsApp sandbox joined (if using)
- [ ] User preferences enabled
- [ ] Integrated with notification system
- [ ] Monitoring setup in Twilio Console
- [ ] Budget alerts configured

---

**Status: ✅ SMS & WhatsApp Integration Complete**  
**Ready for production use with proper configuration**
