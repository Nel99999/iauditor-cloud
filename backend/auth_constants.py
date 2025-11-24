"""
Authentication Constants and Messages
"""

# Approval Status Messages
MSG_REGISTRATION_PENDING = "Registration successful! Your profile is pending Developer approval. You will receive an email once approved."
MSG_ACCOUNT_LOCKED = "Account is locked. Try again in {minutes} minutes."
MSG_ACCOUNT_LOCKED_TOO_MANY_ATTEMPTS = "Account locked due to too many failed attempts. Try again in {minutes} minutes."
MSG_INVALID_CREDENTIALS = "Invalid email or password"
MSG_REGISTRATION_PENDING_ERROR = "Your registration is pending admin approval. You will receive an email once your account is approved."
MSG_REGISTRATION_REJECTED_ERROR = "Your registration was not approved. Please contact support for more information."
MSG_ACCOUNT_DISABLED = "Account is disabled"

# Email Templates (Subjects)
SUBJECT_PROFILE_CREATION = "Profile Creation Request Received - Pending Developer Approval"
SUBJECT_PASSWORD_RESET = "Password Reset Request - Operations Platform"
SUBJECT_PASSWORD_CHANGED = "Password Changed Successfully - Operations Platform"
