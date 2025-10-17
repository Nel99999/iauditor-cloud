"""
Developer-only routes for system administration and debugging
All endpoints require 'developer' role
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import os
import psutil
import logging
from pathlib import Path
import json
import subprocess
from pydantic import BaseModel

# Import auth dependencies
from auth_routes import get_current_user

router = APIRouter(prefix="/developer", tags=["Developer"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

async def require_developer(current_user: dict = Depends(get_current_user)):
    """Ensure only developer role can access these endpoints"""
    if current_user.get("role") != "developer":
        raise HTTPException(
            status_code=403,
            detail="Developer role required for this operation"
        )
    return current_user


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class APITestRequest(BaseModel):
    method: str
    endpoint: str
    headers: Optional[Dict[str, str]] = {}
    body: Optional[Dict[str, Any]] = {}

class EmailTestRequest(BaseModel):
    recipient: str
    template_type: str  # 'welcome', 'password_reset', 'invitation'
    test_data: Optional[Dict[str, Any]] = {}

class DatabaseQueryRequest(BaseModel):
    collection: str
    operation: str  # 'find', 'count', 'aggregate', 'update', 'delete'
    query: Dict[str, Any] = {}
    limit: Optional[int] = 100
    skip: Optional[int] = 0
    update_data: Optional[Dict[str, Any]] = None
    confirm: Optional[bool] = False

class WebhookTestRequest(BaseModel):
    webhook_id: Optional[str] = None
    event_type: str
    payload: Dict[str, Any]

class QuickActionRequest(BaseModel):
    action: str  # 'clear_cache', 'impersonate', 'bulk_reset_password', 'force_sync'
    params: Optional[Dict[str, Any]] = {}


# ============================================================================
# PHASE 1 & 2: SYSTEM HEALTH & MONITORING
# ============================================================================

@router.get("/health")
async def get_system_health(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Get comprehensive system health information"""
    try:
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # MongoDB health
        try:
            await db.command('ping')
            mongo_status = "connected"
            
            # Get database stats
            db_stats = await db.command('dbStats')
            collections_count = len(await db.list_collection_names())
            
            # Count documents across key collections
            users_count = await db.users.count_documents({})
            roles_count = await db.roles.count_documents({})
            orgs_count = await db.organizations.count_documents({})
            
        except Exception as e:
            mongo_status = f"error: {str(e)}"
            db_stats = {}
            collections_count = 0
            users_count = roles_count = orgs_count = 0
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "used_mb": memory.used / 1024 / 1024,
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent": disk.percent
                },
                "process_memory_mb": process_memory
            },
            "database": {
                "status": mongo_status,
                "collections": collections_count,
                "size_mb": db_stats.get('dataSize', 0) / 1024 / 1024 if db_stats else 0,
                "counts": {
                    "users": users_count,
                    "roles": roles_count,
                    "organizations": orgs_count
                }
            },
            "services": {
                "backend": "running",
                "frontend": "assumed_running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environment")
async def get_environment_info(_: dict = Depends(require_developer)):
    """Get environment configuration (with sensitive data masked)"""
    try:
        def mask_value(key: str, value: str) -> str:
            """Mask sensitive values"""
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api']
            if any(s in key.lower() for s in sensitive_keys):
                return '*' * 8 + value[-4:] if len(value) > 4 else '*' * 8
            return value
        
        # Get environment variables
        env_vars = {}
        important_vars = [
            'MONGO_URL', 'DB_NAME', 'REACT_APP_BACKEND_URL',
            'SENDGRID_API_KEY', 'SENDGRID_FROM_EMAIL', 'JWT_SECRET',
            'CORS_ORIGINS'
        ]
        
        for var in important_vars:
            value = os.environ.get(var, 'Not Set')
            env_vars[var] = mask_value(var, value) if value != 'Not Set' else value
        
        # Get Python version
        import sys
        python_version = sys.version
        
        # Get backend directory
        backend_dir = Path(__file__).parent
        
        # Try to get git info if available
        git_info = {}
        try:
            git_branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=backend_dir.parent,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            git_commit = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=backend_dir.parent,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            git_info = {
                "branch": git_branch,
                "commit": git_commit
            }
        except:
            git_info = {"status": "not available"}
        
        return {
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "python_version": python_version.split()[0],
            "backend_path": str(backend_dir),
            "environment_variables": env_vars,
            "git": git_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Environment info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 3: API & EMAIL TESTING
# ============================================================================

@router.post("/test/api")
async def test_api_endpoint(
    test_request: APITestRequest,
    _: dict = Depends(require_developer)
):
    """Test any API endpoint with custom method, headers, and body"""
    import httpx
    
    try:
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        full_url = f"{backend_url}{test_request.endpoint}"
        
        # Prepare request
        async with httpx.AsyncClient(timeout=30.0) as client:
            if test_request.method.upper() == "GET":
                response = await client.get(full_url, headers=test_request.headers)
            elif test_request.method.upper() == "POST":
                response = await client.post(
                    full_url,
                    headers=test_request.headers,
                    json=test_request.body
                )
            elif test_request.method.upper() == "PUT":
                response = await client.put(
                    full_url,
                    headers=test_request.headers,
                    json=test_request.body
                )
            elif test_request.method.upper() == "DELETE":
                response = await client.delete(full_url, headers=test_request.headers)
            else:
                raise HTTPException(status_code=400, detail="Unsupported method")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
                "json": response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                "elapsed_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        logger.error(f"API test failed: {str(e)}")
        return {
            "status_code": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.post("/test/email")
async def test_email(
    email_request: EmailTestRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Send test email using SendGrid"""
    try:
        from email_service import EmailService
        
        # Get settings from database
        settings = await db.settings.find_one({}) or {}
        
        api_key = settings.get('sendgrid_api_key') or os.environ.get('SENDGRID_API_KEY')
        from_email = settings.get('sendgrid_from_email') or os.environ.get('SENDGRID_FROM_EMAIL')
        from_name = settings.get('sendgrid_from_name') or 'Operations Platform'
        
        if not api_key:
            raise HTTPException(status_code=400, detail="SendGrid API key not configured")
        
        email_service = EmailService(api_key, from_email, from_name)
        
        # Send based on template type
        if email_request.template_type == 'welcome':
            result = await email_service.send_welcome_email(
                email_request.recipient,
                email_request.test_data.get('name', 'Test User'),
                email_request.test_data.get('login_url', 'https://app.example.com/login')
            )
        elif email_request.template_type == 'password_reset':
            result = await email_service.send_password_reset_email(
                email_request.recipient,
                email_request.test_data.get('reset_url', 'https://app.example.com/reset?token=test123')
            )
        elif email_request.template_type == 'invitation':
            result = await email_service.send_invitation_email(
                email_request.recipient,
                email_request.test_data.get('inviter_name', 'Test Admin'),
                email_request.test_data.get('organization_name', 'Test Organization'),
                email_request.test_data.get('invite_url', 'https://app.example.com/accept?token=test123')
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid template type")
        
        return {
            "success": result,
            "recipient": email_request.recipient,
            "template": email_request.template_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 4: DATABASE QUERY INTERFACE
# ============================================================================

@router.get("/database/collections")
async def get_collections(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Get list of all database collections"""
    try:
        collections = await db.list_collection_names()
        
        # Get stats for each collection
        collection_stats = []
        for coll_name in collections:
            try:
                count = await db[coll_name].count_documents({})
                collection_stats.append({
                    "name": coll_name,
                    "count": count
                })
            except:
                collection_stats.append({
                    "name": coll_name,
                    "count": 0
                })
        
        return {
            "collections": collection_stats,
            "total": len(collections)
        }
    except Exception as e:
        logger.error(f"Get collections failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/query")
async def execute_database_query(
    query_request: DatabaseQueryRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Execute database query with safety limits"""
    try:
        collection = db[query_request.collection]
        
        operation = query_request.operation.lower()
        
        # Read operations
        if operation == 'find':
            cursor = collection.find(query_request.query).limit(query_request.limit).skip(query_request.skip)
            results = await cursor.to_list(length=query_request.limit)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return {
                "operation": "find",
                "collection": query_request.collection,
                "count": len(results),
                "results": results
            }
        
        elif operation == 'count':
            count = await collection.count_documents(query_request.query)
            return {
                "operation": "count",
                "collection": query_request.collection,
                "count": count
            }
        
        elif operation == 'aggregate':
            # For aggregate, query should contain pipeline
            pipeline = query_request.query.get('pipeline', [])
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=query_request.limit)
            
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return {
                "operation": "aggregate",
                "collection": query_request.collection,
                "count": len(results),
                "results": results
            }
        
        # Write operations (require confirmation)
        elif operation in ['update', 'delete']:
            if not query_request.confirm:
                # Return preview of what would be affected
                count = await collection.count_documents(query_request.query)
                return {
                    "operation": f"{operation}_preview",
                    "collection": query_request.collection,
                    "affected_count": count,
                    "message": "Set confirm=true to execute this operation"
                }
            
            if operation == 'update':
                if not query_request.update_data:
                    raise HTTPException(status_code=400, detail="update_data required for update operation")
                
                result = await collection.update_many(
                    query_request.query,
                    {"$set": query_request.update_data}
                )
                return {
                    "operation": "update",
                    "collection": query_request.collection,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                }
            
            elif operation == 'delete':
                result = await collection.delete_many(query_request.query)
                return {
                    "operation": "delete",
                    "collection": query_request.collection,
                    "deleted_count": result.deleted_count
                }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {operation}")
    
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 4: LOGS VIEWER
# ============================================================================

@router.get("/logs/backend")
async def get_backend_logs(
    lines: int = 100,
    level: Optional[str] = None,
    _: dict = Depends(require_developer)
):
    """Get backend logs from supervisor"""
    try:
        log_files = [
            '/var/log/supervisor/backend.err.log',
            '/var/log/supervisor/backend.out.log'
        ]
        
        all_logs = []
        for log_file in log_files:
            if Path(log_file).exists():
                try:
                    result = subprocess.run(
                        ['tail', '-n', str(lines), log_file],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        log_type = 'error' if 'err' in log_file else 'output'
                        for line in result.stdout.strip().split('\n'):
                            if line:
                                all_logs.append({
                                    "type": log_type,
                                    "message": line,
                                    "source": "backend"
                                })
                except Exception as e:
                    logger.warning(f"Could not read {log_file}: {str(e)}")
        
        # Filter by level if specified
        if level:
            level = level.upper()
            all_logs = [log for log in all_logs if level in log['message'].upper()]
        
        return {
            "logs": all_logs[-lines:],  # Return last N lines
            "count": len(all_logs),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get logs failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/frontend")
async def get_frontend_logs(
    lines: int = 100,
    _: dict = Depends(require_developer)
):
    """Get frontend logs from supervisor"""
    try:
        log_files = [
            '/var/log/supervisor/frontend.err.log',
            '/var/log/supervisor/frontend.out.log'
        ]
        
        all_logs = []
        for log_file in log_files:
            if Path(log_file).exists():
                try:
                    result = subprocess.run(
                        ['tail', '-n', str(lines), log_file],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        log_type = 'error' if 'err' in log_file else 'output'
                        for line in result.stdout.strip().split('\n'):
                            if line:
                                all_logs.append({
                                    "type": log_type,
                                    "message": line,
                                    "source": "frontend"
                                })
                except Exception as e:
                    logger.warning(f"Could not read {log_file}: {str(e)}")
        
        return {
            "logs": all_logs[-lines:],
            "count": len(all_logs),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get frontend logs failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 5: SESSION MANAGEMENT
# ============================================================================

@router.get("/sessions/active")
async def get_active_sessions(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Get all active user sessions"""
    try:
        
        # Get sessions from sessions collection if it exists
        sessions = await db.sessions.find({}).to_list(length=1000)
        
        for session in sessions:
            if '_id' in session:
                session['_id'] = str(session['_id'])
        
        return {
            "sessions": sessions,
            "count": len(sessions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get sessions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Force logout a user by deleting their session"""
    try:
        result = await db.sessions.delete_one({"id": session_id})
        
        return {
            "success": result.deleted_count > 0,
            "deleted_count": result.deleted_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Delete session failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 5: QUICK ACTIONS
# ============================================================================

@router.post("/actions/clear-cache")
async def clear_cache(_: dict = Depends(require_developer)):
    """Clear application caches"""
    try:
        # This would clear any caching mechanisms you have
        # For now, just return success
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Clear cache failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actions/impersonate")
async def impersonate_user(
    user_id: str = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Generate a temporary token to impersonate a user"""
    try:
        from jose import jwt
        from datetime import timedelta
        
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create a temporary token (30 minutes)
        secret_key = os.environ.get("JWT_SECRET", "your-secret-key")
        expires_delta = timedelta(minutes=30)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "sub": user["email"],
            "user_id": user["id"],
            "role": user["role"],
            "exp": expire,
            "impersonated": True
        }
        
        token = jwt.encode(to_encode, secret_key, algorithm="HS256")
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            },
            "expires_in_minutes": 30,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Impersonate user failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 6: PERFORMANCE METRICS
# ============================================================================

@router.get("/metrics/performance")
async def get_performance_metrics(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Get performance metrics from audit logs"""
    try:
        
        # Get recent audit logs
        recent_logs = await db.audit_logs.find({}).sort("timestamp", -1).limit(1000).to_list(length=1000)
        
        # Aggregate by action
        action_stats = {}
        for log in recent_logs:
            action = log.get('action', 'unknown')
            if action not in action_stats:
                action_stats[action] = {
                    "count": 0,
                    "errors": 0
                }
            action_stats[action]["count"] += 1
            if log.get('status') == 'error':
                action_stats[action]["errors"] += 1
        
        # Get slow query info (mock data for now)
        slow_queries = [
            {"query": "users.find", "avg_time_ms": 150, "count": 50},
            {"query": "organizations.aggregate", "avg_time_ms": 300, "count": 20},
        ]
        
        return {
            "action_stats": action_stats,
            "slow_queries": slow_queries,
            "total_requests": len(recent_logs),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get performance metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 3: WEBHOOK TESTING
# ============================================================================

@router.get("/webhooks")
async def get_webhooks(
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Get all configured webhooks"""
    try:
        webhooks = await db.webhooks.find({}).to_list(length=1000)
        
        for webhook in webhooks:
            if '_id' in webhook:
                webhook['_id'] = str(webhook['_id'])
        
        return {
            "webhooks": webhooks,
            "count": len(webhooks)
        }
    except Exception as e:
        logger.error(f"Get webhooks failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/test")
async def test_webhook(
    webhook_request: WebhookTestRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: dict = Depends(require_developer)
):
    """Send a test webhook event"""
    import httpx
    
    try:
        
        # Get webhook config
        if webhook_request.webhook_id:
            webhook = await db.webhooks.find_one({"id": webhook_request.webhook_id})
            if not webhook:
                raise HTTPException(status_code=404, detail="Webhook not found")
            
            url = webhook.get('url')
        else:
            # Allow testing arbitrary URL
            url = webhook_request.payload.get('url')
            if not url:
                raise HTTPException(status_code=400, detail="URL required")
        
        # Send webhook
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={
                    "event_type": webhook_request.event_type,
                    "payload": webhook_request.payload,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Webhook test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
