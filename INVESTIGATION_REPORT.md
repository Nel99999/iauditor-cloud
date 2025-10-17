# Investigation Report: New Profile Creation & Password Reset Issues

**Date:** October 2025
**Investigator:** AI Development Agent

---

## 🔍 INVESTIGATION FINDINGS

### **ISSUE 1: New Profile Creation Workflow**

#### Current Implementation:
✅ **What's Already Working:**
- UserApprovalPage component exists (`/app/frontend/src/components/UserApprovalPage.tsx`)
- Backend approval system implemented (`/app/backend/approval_routes.py`)
  - `/api/users/pending-approvals` - Get pending users
  - `/api/users/{user_id}/approve` - Approve user
  - `/api/users/{user_id}/reject` - Reject user
- Email templates exist in `email_service.py`:
  - `send_registration_pending_email()` - Notify user registration is pending
  - `send_registration_approved_email()` - Notify user they're approved
  - `send_registration_rejected_email()` - Notify user they're rejected
- Login blocking for pending users (auth_routes.py line 170-175):
  ```python
  if approval_status == "pending":
      raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Your registration is pending admin approval..."
      )
  ```

❌ **What Needs to be Fixed:**
1. **UI Text Change** (RegisterPage.tsx line 163):
   - Current: "I want to create an organization"
   - Required: "I want to create a **NEW** Profile" (NEW in bold)

2. **Registration Flow** (auth_routes.py lines 43-103):
   - Currently: Users who create org → auto-approved as "master" role
   - Required: All new registrations → "pending" status, awaiting Developer approval

3. **Approval Permissions** (approval_routes.py):
   - Currently: Uses generic "user.approve.organization" permission
   - Required: ONLY Developer role can approve (need to verify permission assignment)

4. **Email Notifications** (approval_routes.py):
   - Line 152: "TODO: Send approval email to user"
   - Line 248: "TODO: Send rejection email to user"
   - Need to integrate EmailService calls

---

### **ISSUE 2: Password Reset Not Working**

#### Current Implementation:
✅ **What's Already Working:**
- ForgotPasswordPage component exists and functional
- ResetPasswordPage component exists and functional
- Backend endpoints implemented:
  - `/api/auth/forgot-password` (auth_routes.py line 346)
  - `/api/auth/reset-password` (auth_routes.py line 438)
- Email sending logic implemented (auth_routes.py lines 378-428)
- Password reset token generation and validation working

❌ **Root Cause of Failure:**
1. **SendGrid Configuration Missing:**
   - Backend `.env` file has NO SendGrid API key
   - Code tries to fetch from `organization_settings` collection (line 388):
     ```python
     org_settings = await db.organization_settings.find_one(
         {"organization_id": user.get("organization_id")}
     )
     ```
   - If no org settings found → EmailService not initialized → No email sent

2. **Silent Failure:**
   - Code catches exceptions and returns success anyway (line 429-431):
     ```python
     except Exception as e:
         # Log error but don't fail the request
         print(f"Failed to send password reset email: {str(e)}")
     ```
   - User sees "success" message but email never arrives

3. **Email Service Constructor Issue:**
   - `email_service.py` line 9-11:
     ```python
     def __init__(self, api_key: Optional[str] = None):
         self.api_key = api_key or os.environ.get('SENDGRID_API_KEY')
         self.client = SendGridAPIClient(self.api_key) if self.api_key else None
     ```
   - If `api_key` is None and env var not set → `self.client = None`
   - Line 22-24: If client is None → returns False, no email sent

---

## 📋 PROPOSED SOLUTION

### **Phase 1: New Profile Creation Workflow**

#### Step 1: Update Registration UI
**File:** `/app/frontend/src/components/RegisterPage.tsx`
- Change line 163 text to: `"I want to create a NEW Profile"` with bold styling

#### Step 2: Modify Registration Backend
**File:** `/app/backend/auth_routes.py`
- Remove auto-approval for organization creators
- Set all new registrations to `approval_status: "pending"`
- Set `is_active: False` for pending users
- Send registration pending email notification

#### Step 3: Update Approval System
**File:** `/app/backend/approval_routes.py`
- Integrate email notifications:
  - Call `send_registration_approved_email()` in approve endpoint
  - Call `send_registration_rejected_email()` in reject endpoint
- Verify permission check restricts to Developer role only

#### Step 4: Verify Permissions
**Check:** Permission system to ensure only "developer" role has "user.approve.organization" permission

---

### **Phase 2: Password Reset Fix**

#### Step 1: Investigate SendGrid Configuration
- Check if organization has SendGrid API key in `organization_settings` collection
- If not, need to configure SendGrid via Settings page

#### Step 2: Add SendGrid Configuration
**Options:**
A. **Per-Organization Setup** (Current approach):
   - User must configure SendGrid in Settings → API Settings
   - Store in `organization_settings` collection
   
B. **Global Environment Variable** (Alternative):
   - Add `SENDGRID_API_KEY` to `/app/backend/.env`
   - Works for all organizations

#### Step 3: Test Email Functionality
- Test forgot password flow
- Verify email delivery
- Check spam folder if not received

---

## 🎯 IMPLEMENTATION PLAN

### **Priority 1: New Profile Creation (User's Main Request)**
1. ✅ Update RegisterPage.tsx checkbox text
2. ✅ Modify auth_routes.py registration flow
3. ✅ Add email notifications to approval_routes.py
4. ✅ Test registration → approval → email workflow

### **Priority 2: Password Reset (User's Secondary Request)**
1. ✅ Check organization_settings for SendGrid key
2. ✅ If missing, prompt user to configure OR add to .env
3. ✅ Test password reset email flow
4. ✅ Verify both Login page and Settings page password reset

---

## 🚨 IMPORTANT QUESTIONS FOR USER

### **SendGrid Configuration:**
**User said:** "the api key is correct and your testing show that it is working"

**Need Clarification:**
1. Is the SendGrid API key stored in:
   - [ ] Organization Settings (via Settings page)?
   - [ ] Backend .env file?
   - [ ] Somewhere else?

2. When you say "testing shows it is working":
   - What was tested? (Invitation emails? Other notifications?)
   - Which endpoint was tested?
   - Can you share the test results or logs?

3. For password reset specifically:
   - Are you testing from **Login page** "Forgot Password" link?
   - Or from **Settings page** "Change Password"?
   - Any error messages in browser console or backend logs?

---

## 📝 NEXT STEPS

**Awaiting User Confirmation:**
1. Confirm SendGrid is configured for the production organization
2. Confirm which password reset flow is being tested
3. Approve implementation plan

**Once Approved, I will:**
1. Implement all changes for New Profile Creation workflow
2. Debug and fix password reset email sending
3. Test both features end-to-end
4. Update test_result.md with findings
5. Deliver comprehensive testing report

---

**Ready to proceed upon your confirmation! 🚀**
