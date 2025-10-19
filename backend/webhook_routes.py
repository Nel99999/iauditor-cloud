from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime, timezone, timedelta
from webhook_models import Webhook, WebhookCreate, WebhookUpdate, WebhookDelivery, WEBHOOK_EVENTS
from auth_utils import get_current_user
import uuid
import secrets
import hmac
import hashlib
import aiohttp
import json

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

def generate_webhook_secret() -> str:
    """Generate a secure webhook secret"""
    return secrets.token_urlsafe(32)


def create_signature(payload: str, secret: str) -> str:
    """Create HMAC signature for webhook payload"""
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


async def deliver_webhook(
    webhook: dict,
    event_type: str,
    payload: dict,
    db: AsyncIOMotorDatabase
):
    """Deliver webhook to endpoint with retry logic"""
    delivery_id = str(uuid.uuid4())
    
    # Create delivery log
    delivery = {
        "id": delivery_id,
        "webhook_id": webhook["id"],
        "organization_id": webhook["organization_id"],
        "event_type": event_type,
        "payload": payload,
        "status": "pending",
        "attempt_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.webhook_deliveries.insert_one(delivery)
    
    # Prepare webhook payload
    webhook_payload = {
        "id": delivery_id,
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": payload
    }
    
    payload_str = json.dumps(webhook_payload)
    signature = create_signature(payload_str, webhook["secret"])
    
    # Attempt delivery
    max_retries = webhook.get("max_retries", 3)
    retry_delay = webhook.get("retry_delay", 60)
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    str(webhook["url"]),
                    json=webhook_payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-ID": webhook["id"],
                        "X-Webhook-Delivery-ID": delivery_id
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    
                    # Update delivery status
                    await db.webhook_deliveries.update_one(
                        {"id": delivery_id},
                        {
                            "$set": {
                                "status": "success" if response.status < 400 else "failed",
                                "status_code": response.status,
                                "response_body": response_text[:1000],  # Limit size
                                "attempt_count": attempt + 1,
                                "delivered_at": datetime.now(timezone.utc).isoformat()
                            }
                        }
                    )
                    
                    # Update webhook statistics
                    if response.status < 400:
                        await db.webhooks.update_one(
                            {"id": webhook["id"]},
                            {
                                "$inc": {
                                    "total_deliveries": 1,
                                    "successful_deliveries": 1
                                },
                                "$set": {
                                    "last_delivery_at": datetime.now(timezone.utc).isoformat(),
                                    "last_delivery_status": "success"
                                }
                            }
                        )
                        return True
                    else:
                        # Retry on failure
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
        
        except Exception as e:
            # Update delivery with error
            await db.webhook_deliveries.update_one(
                {"id": delivery_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(e),
                        "attempt_count": attempt + 1
                    }
                }
            )
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
    
    # All retries failed
    await db.webhooks.update_one(
        {"id": webhook["id"]},
        {
            "$inc": {
                "total_deliveries": 1,
                "failed_deliveries": 1
            },
            "$set": {
                "last_delivery_at": datetime.now(timezone.utc).isoformat(),
                "last_delivery_status": "failed"
            }
        }
    )
    
    return False


async def trigger_webhooks(
    event_type: str,
    payload: dict,
    organization_id: str,
    db: AsyncIOMotorDatabase
):
    """Trigger all webhooks subscribed to an event"""
    # Find active webhooks for this event
    webhooks = await db.webhooks.find({
        "organization_id": organization_id,
        "is_active": True,
        "events": event_type
    }).to_list(100)
    
    # Deliver to each webhook asynchronously
    for webhook in webhooks:
        # Don't await - fire and forget with retry logic
        asyncio.create_task(deliver_webhook(webhook, event_type, payload, db))


# ==================== ENDPOINTS ====================

@router.get("/events")
async def get_available_events():
    """Get list of available webhook events"""
    return {
        "events": WEBHOOK_EVENTS,
        "categories": {
            "user": [e for e in WEBHOOK_EVENTS if e.startswith("user.")],
            "task": [e for e in WEBHOOK_EVENTS if e.startswith("task.")],
            "inspection": [e for e in WEBHOOK_EVENTS if e.startswith("inspection.")],
            "checklist": [e for e in WEBHOOK_EVENTS if e.startswith("checklist.")],
            "workflow": [e for e in WEBHOOK_EVENTS if e.startswith("workflow.")],
            "group": [e for e in WEBHOOK_EVENTS if e.startswith("group.")]
        }
    }


@router.post("", response_model=Webhook, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new webhook"""
    user = await get_current_user(request, db)
    
    # Validate events
    invalid_events = [e for e in webhook_data.events if e not in WEBHOOK_EVENTS]
    if invalid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid events: {', '.join(invalid_events)}"
        )
    
    # Generate secret
    secret = generate_webhook_secret()
    
    # Create webhook
    webhook = Webhook(
        organization_id=user["organization_id"],
        name=webhook_data.name,
        url=webhook_data.url,
        secret=secret,
        events=webhook_data.events,
        created_by=user["id"],
        created_by_name=user["name"]
    )
    
    webhook_dict = webhook.model_dump()
    webhook_dict["created_at"] = webhook_dict["created_at"].isoformat()
    webhook_dict["updated_at"] = webhook_dict["updated_at"].isoformat()
    webhook_dict["url"] = str(webhook_dict["url"])  # Convert HttpUrl to string for MongoDB
    
    await db.webhooks.insert_one(webhook_dict)
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "webhook.created",
        "resource_type": "webhook",
        "resource_id": webhook.id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"webhook_name": webhook.name, "url": str(webhook.url)}
    })
    
    return Webhook(**webhook_dict)


@router.get("", response_model=List[Webhook])
async def get_webhooks(
    request: Request,
    include_inactive: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all webhooks"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"]}
    if not include_inactive:
        query["is_active"] = True
    
    webhooks = await db.webhooks.find(query, {"_id": 0}).to_list(1000)
    return [Webhook(**w) for w in webhooks]


@router.get("/{webhook_id}", response_model=Webhook)
async def get_webhook(
    webhook_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get specific webhook"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return Webhook(**webhook)


@router.put("/{webhook_id}", response_model=Webhook)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update webhook"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Validate events if provided
    if webhook_data.events:
        invalid_events = [e for e in webhook_data.events if e not in WEBHOOK_EVENTS]
        if invalid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid events: {', '.join(invalid_events)}"
            )
    
    update_data = webhook_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.webhooks.update_one(
        {"id": webhook_id},
        {"$set": update_data}
    )
    
    updated_webhook = await db.webhooks.find_one({"id": webhook_id}, {"_id": 0})
    
    return Webhook(**updated_webhook)


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete webhook"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    await db.webhooks.delete_one({"id": webhook_id})
    
    return {"message": "Webhook deleted successfully"}


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Test webhook delivery"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Send test payload
    test_payload = {
        "test": True,
        "message": "This is a test webhook delivery",
        "webhook_id": webhook_id,
        "organization_id": user["organization_id"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Trigger delivery in background
    background_tasks.add_task(
        deliver_webhook,
        webhook,
        "webhook.test",
        test_payload,
        db
    )
    
    return {"message": "Test webhook triggered"}


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    request: Request,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get webhook delivery logs"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    deliveries = await db.webhook_deliveries.find(
        {"webhook_id": webhook_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return deliveries


@router.post("/{webhook_id}/regenerate-secret")
async def regenerate_webhook_secret(
    webhook_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Regenerate webhook secret"""
    user = await get_current_user(request, db)
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "organization_id": user["organization_id"]}
    )
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Generate new secret
    new_secret = generate_webhook_secret()
    
    await db.webhooks.update_one(
        {"id": webhook_id},
        {"$set": {"secret": new_secret, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Secret regenerated", "secret": new_secret}


# Import asyncio for background tasks
import asyncio
