# API Keys Security Documentation

## Overview
This document outlines the security measures implemented for managing sensitive API keys (SendGrid and Twilio) in the v2.0 Operational Management Platform.

## Access Control

### Role-Based Access Restrictions
**ONLY Master and Developer roles** have access to API configuration settings.

#### Restricted Roles:
- ✅ **Developer** (Level 1) - Full access to all API settings
- ✅ **Master** (Level 2) - Full access to all API settings
- ❌ **Admin** (Level 3) - NO access to API keys
- ❌ **All other roles** - NO access to API keys

### Protected Endpoints

#### SendGrid Email Settings (backend/settings_routes.py)
```
GET  /api/settings/email          - View email settings (Master & Developer only)
POST /api/settings/email          - Update email settings (Master & Developer only)
POST /api/settings/email/test     - Test email connection (Master & Developer only)
```

#### Twilio SMS & WhatsApp Settings (backend/sms_routes.py)
```
GET  /api/sms/settings            - View Twilio settings (Master & Developer only)
POST /api/sms/settings            - Update Twilio settings (Master & Developer only)
POST /api/sms/test-connection     - Test Twilio connection (Master & Developer only)
```

### Access Denied Response
Users without Master or Developer roles will receive:
- **HTTP Status**: 403 Forbidden
- **Error Message**: "Only Master and Developer roles can access [resource]"

## Data Storage Security

### Database Storage
- API keys are stored in the `organization_settings` collection in MongoDB
- Keys are associated with the organization, not individual users
- MongoDB connection uses authentication and is isolated by organization

### Stored Fields
**SendGrid:**
- `sendgrid_api_key` - Full API key (stored securely in database)

**Twilio:**
- `twilio_account_sid` - Account SID
- `twilio_auth_token` - Authentication token (sensitive)
- `twilio_phone_number` - Phone number for SMS
- `twilio_whatsapp_number` - WhatsApp sandbox number

### Data Masking
When API keys are retrieved via GET endpoints, sensitive data is masked:

**SendGrid API Key:**
```
Original: SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Displayed: SG.xxxxxx...xxxx
```

**Twilio Account SID:**
```
Original: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Displayed: ACxxxxxxxx...xxxx
```

**Twilio Auth Token:**
- Never returned in GET requests (empty string)
- Only accepted in POST requests for updates

## Frontend Security

### UI Access Control
- API Settings tab only visible to Master and Developer roles
- Tab automatically hidden for users without proper permissions
- Uses `isDeveloperOrMaster()` permission check

### Location
`frontend/src/components/EnhancedSettingsPage.jsx` - API Settings tab

### Permission Hook
`frontend/src/hooks/usePermissions.js` - Contains role checking functions:
- `isDeveloper()` - Check if user is Developer
- `isMaster()` - Check if user is Master  
- `isDeveloperOrMaster()` - Check if user is Master OR Developer

## Security Best Practices

### ✅ Implemented Security Measures
1. **Role-Based Access Control (RBAC)** - Only highest level roles can manage API keys
2. **Data Masking** - Sensitive data is masked when displayed
3. **Organization Isolation** - Keys are scoped to organizations
4. **Authentication Required** - All endpoints require valid JWT tokens
5. **Frontend Protection** - UI hidden from unauthorized users
6. **Audit Trail** - All updates tracked with `updated_by` and `updated_at` fields

### 🔒 Additional Recommendations
1. **Encryption at Rest** - Consider encrypting API keys in MongoDB using field-level encryption
2. **Key Rotation** - Implement periodic key rotation reminders
3. **Audit Logging** - Log all API key access and modifications
4. **Rate Limiting** - Implement rate limiting on API key endpoints
5. **IP Whitelisting** - Consider restricting API key management to specific IPs

## Testing Access Control

### Test Scenarios
1. **Master Role** - Should have full access to API settings ✅
2. **Developer Role** - Should have full access to API settings ✅
3. **Admin Role** - Should be denied access (403 Forbidden) ✅
4. **Lower Roles** - Should be denied access (403 Forbidden) ✅

### Testing Commands
```bash
# Test with different role users
curl -X GET https://your-app.com/api/settings/email \
  -H "Authorization: Bearer <master_or_developer_token>"
# Expected: 200 OK with masked API key

curl -X GET https://your-app.com/api/settings/email \
  -H "Authorization: Bearer <admin_or_lower_token>"
# Expected: 403 Forbidden
```

## Emergency Procedures

### If API Keys are Compromised
1. **Immediate Action**: Login as Master or Developer
2. Navigate to Settings → API Settings tab
3. Update compromised keys with new ones
4. Revoke old keys in SendGrid/Twilio dashboards
5. Test connections to verify new keys work

### Key Recovery
- API keys are stored in MongoDB `organization_settings` collection
- Database administrators can access keys directly if needed
- Recommend implementing backup procedures for critical settings

## Compliance Notes

### Data Protection
- API keys are considered sensitive organizational data
- Access is restricted to minimize exposure
- Keys are not logged in application logs
- Frontend never exposes full keys in responses

### GDPR Considerations
- API keys are organizational, not personal data
- No user consent required for key storage
- Keys are deleted when organization is deleted

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-01-13 | Initial security implementation | System |
| 2025-01-13 | Restricted access to Master & Developer only | System |
| 2025-01-13 | Implemented data masking for API keys | System |

## Support

For security concerns or questions about API key management, contact:
- System Administrator
- Master or Developer role users in your organization

---

**Security Level**: HIGH
**Last Updated**: January 13, 2025
**Version**: 1.0
