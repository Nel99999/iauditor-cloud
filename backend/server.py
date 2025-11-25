# Fix bcrypt compatibility issue - must be first import
from . import fix_bcrypt

from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
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
        from .scheduler import start_scheduler
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
api_router.include_router(entity_router)
api_router.include_router(announcement_router)
api_router.include_router(dashboard_extended_router)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)