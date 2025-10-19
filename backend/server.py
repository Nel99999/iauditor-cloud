# Fix bcrypt compatibility issue - must be first import
import fix_bcrypt

from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import all routes
from auth_routes import router as auth_router
from org_routes import router as org_router
from inspection_routes import router as inspection_router
from checklist_routes import router as checklist_router
from task_routes import router as task_router
from reports_routes import router as reports_router
from user_routes import router as user_router
from permission_routes import router as permission_router
from invitation_routes import router as invitation_router
from deactivation_routes import router as deactivation_router
from role_routes import router as role_router
from dashboard_routes import router as dashboard_router
from workflow_routes import router as workflow_router
from context_permission_routes import router as context_permission_router
from audit_routes import router as audit_router
from advanced_workflow_routes import router as advanced_workflow_router
from mfa_routes import router as mfa_router
from security_routes import router as security_router
from subtask_routes import router as subtask_router
from attachment_routes import router as attachment_router
from comment_routes import router as comment_router
from asset_routes import router as asset_router
from workorder_routes import router as workorder_router
from inventory_routes import router as inventory_router
from incident_routes import router as incident_router
from training_routes import router as training_router
from financial_routes import router as financial_router
from hr_routes import router as hr_router
from chat_routes import router as chat_router
from contractor_routes import router as contractor_router
from emergency_routes import router as emergency_router
from dashboard_enhanced_routes import router as dashboard_enhanced_router
from project_routes import router as project_router
from group_routes import router as group_router
from bulk_import_routes import router as bulk_import_router
from webhook_routes import router as webhook_router
from search_routes import router as search_router
from mention_routes import router as mention_router
from notification_routes import router as notification_router
from time_tracking_routes import router as time_tracking_router
from analytics_routes import router as analytics_router
from gdpr_routes import router as gdpr_router
from sms_routes import router as sms_router
from approval_routes import router as approval_router
from user_context_routes import router as user_context_router
from session_routes import router as session_router
from developer_routes import router as developer_router
from sidebar_routes import router as sidebar_router
from org_sidebar_routes import router as org_sidebar_router


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Operational Management Platform API")


@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection and collections"""
    try:
        # MongoDB connection
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'operational_platform')  # Fixed: Use correct default
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await db.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Store db instance
        app.state.db = db
        
        # Note: System roles initialized per organization during registration
        
        # Start background scheduler
        from scheduler import start_scheduler
        start_scheduler(db)
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        raise

# Create API router
api_router = APIRouter(prefix="/api")

# Enable CORS
allowed_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
from security_middleware import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting
from rate_limiter import limiter, get_rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@api_router.get("/")
async def health_check():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(status_check: StatusCheck):
    status_check_dict = status_check.model_dump()
    status_check_dict['timestamp'] = status_check_dict['timestamp'].isoformat()
    await db.status_checks.insert_one(status_check_dict)
    return status_check


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Import settings router
from settings_routes import router as settings_router
from preferences_routes import router as preferences_router

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(org_router)
api_router.include_router(inspection_router)
api_router.include_router(checklist_router)
api_router.include_router(task_router)
api_router.include_router(reports_router)
api_router.include_router(sidebar_router)
api_router.include_router(user_router)
api_router.include_router(permission_router)
api_router.include_router(invitation_router)
api_router.include_router(deactivation_router)
api_router.include_router(role_router)
api_router.include_router(settings_router)
api_router.include_router(preferences_router)
api_router.include_router(dashboard_router)
api_router.include_router(workflow_router)
api_router.include_router(context_permission_router)
api_router.include_router(audit_router)
api_router.include_router(advanced_workflow_router)
api_router.include_router(mfa_router)
api_router.include_router(security_router)
api_router.include_router(subtask_router)
api_router.include_router(attachment_router)
api_router.include_router(comment_router)
api_router.include_router(asset_router)
api_router.include_router(workorder_router)
api_router.include_router(inventory_router)
api_router.include_router(incident_router)
api_router.include_router(training_router)
api_router.include_router(financial_router)
api_router.include_router(hr_router)
api_router.include_router(chat_router)
api_router.include_router(contractor_router)
api_router.include_router(emergency_router)
api_router.include_router(dashboard_enhanced_router)
api_router.include_router(project_router)
api_router.include_router(group_router)
api_router.include_router(bulk_import_router)
api_router.include_router(webhook_router)
api_router.include_router(search_router)
api_router.include_router(mention_router)
api_router.include_router(notification_router)
api_router.include_router(time_tracking_router)
api_router.include_router(analytics_router)
api_router.include_router(gdpr_router)
api_router.include_router(sms_router)
api_router.include_router(approval_router)
api_router.include_router(user_context_router)
api_router.include_router(session_router)
api_router.include_router(developer_router)
api_router.include_router(org_sidebar_router)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)