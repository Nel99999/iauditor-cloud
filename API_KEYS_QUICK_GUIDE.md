# API Keys Management - Quick Reference Guide

## 🔐 Who Can Manage API Keys?

**ONLY these roles:**
- ✅ Developer (Level 1)
- ✅ Master (Level 2)

**Cannot access:**
- ❌ Admin (Level 3)
- ❌ All other roles

---

## 📍 Where to Manage API Keys

1. Login as Master or Developer
2. Navigate to **Settings** (click your profile avatar → Settings)
3. Click on **API Settings** tab
4. You'll see two sections:
   - **SendGrid Email Configuration**
   - **Twilio SMS & WhatsApp Configuration**

---

## 📧 SendGrid Email Setup

### What You Need:
- SendGrid API Key (starts with "SG.")

### Steps:
1. Get your API key from [SendGrid Dashboard](https://app.sendgrid.com/settings/api_keys)
2. Paste it in the "SendGrid API Key" field
3. Click **Save API Key**
4. Click **Test Connection** to verify

### Free Tier:
- 100 emails/day FREE
- Sign up at [SendGrid](https://signup.sendgrid.com/)

---

## 📱 Twilio SMS & WhatsApp Setup

### What You Need:
- Account SID (starts with "AC")
- Auth Token
- Phone Number for SMS (e.g., +1234567890)
- WhatsApp Number (optional, e.g., +14155238886)

### Steps:
1. Get credentials from [Twilio Console](https://console.twilio.com)
2. Fill in all four fields:
   - Account SID
   - Auth Token
   - Phone Number (SMS)
   - WhatsApp Number (optional)
3. Click **Save Twilio Settings**
4. Click **Test Connection** to verify

### Testing Messages:
Once configured, you can test:
1. **Test SMS**: Enter a phone number and click "Send Test SMS"
2. **Test WhatsApp**: Enter a phone number and click "Send Test WhatsApp"

### Free Trial:
- $15 FREE credit when you sign up
- SMS: ~$0.0075 per message
- WhatsApp: ~$0.005 per message

---

## 🔍 What You'll See

### Configured Status:
- ✅ Green badge: "Configured" or "Twilio Configured"
- 🔒 API keys are masked for security:
  - SendGrid: `SG.xxxxxx...xxxx`
  - Twilio: `ACxxxxxxxx...xxxx`

### Test Results:
After testing connection or sending messages, you'll see:
- ✅ **Green box**: Success with message details
- ❌ **Red box**: Failed with error message

---

## 🚨 Security Notes

### Key Storage:
- Keys are encrypted and stored in the database
- Only visible to Master and Developer roles
- Associated with your organization

### Key Visibility:
- Full keys are NEVER displayed after saving
- Keys are masked: `SG.xxxxxx...xxxx`
- To update, enter a new key and save

### Access Denied:
If you see "Only Master and Developer roles can access API settings":
- You don't have sufficient permissions
- Contact a Master or Developer in your organization

---

## ❓ Troubleshooting

### "Connection Failed" - SendGrid
- ✅ Verify API key is correct
- ✅ Check API key has "Mail Send" permissions
- ✅ Ensure SendGrid account is verified

### "Connection Failed" - Twilio
- ✅ Verify Account SID and Auth Token are correct
- ✅ Check phone number format includes country code (+1...)
- ✅ Ensure Twilio account has available credit

### "WhatsApp Failed"
- ✅ Recipient must join your WhatsApp sandbox first
- ✅ Send join code from Twilio Console → Messaging → Try WhatsApp
- ✅ WhatsApp number must be in format: `whatsapp:+1234567890`

### "API Settings Tab Not Visible"
- ❌ You don't have Master or Developer role
- Contact your organization's Master or Developer

---

## 📊 Message Costs

### SendGrid Email:
- Free: 100 emails/day
- Paid plans start at $19.95/month for 50,000 emails

### Twilio SMS:
- ~$0.0075 per SMS message sent
- ~$0.0075 per SMS message received

### Twilio WhatsApp:
- ~$0.005 per message sent
- Free messages received

---

## 🆘 Need Help?

1. **API Keys Help**:
   - SendGrid: [SendGrid Documentation](https://docs.sendgrid.com/)
   - Twilio: [Twilio Documentation](https://www.twilio.com/docs)

2. **Platform Help**:
   - Contact your organization's Master or Developer
   - Check the API_KEYS_SECURITY.md document for technical details

3. **Emergency**:
   - If keys are compromised, immediately update them
   - Revoke old keys in SendGrid/Twilio dashboards

---

**Quick Tips:**
- 💡 Test connections after saving keys
- 💡 Keep API keys confidential
- 💡 Update keys if compromised
- 💡 Monitor usage in SendGrid/Twilio dashboards
- 💡 Set up billing alerts to avoid unexpected charges

---

**Last Updated**: January 13, 2025
