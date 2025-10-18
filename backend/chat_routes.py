from fastapi import APIRouter, HTTPException, status, Depends, Request, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List
import json

from chat_models import Channel, Message
from auth_utils import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# Store active WebSocket connections
active_connections: dict = {}


@router.post("/channels", status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create chat channel"""
    user = await get_current_user(request, db)
    
    channel = Channel(
        organization_id=user["organization_id"],
        name=channel_data.get("name"),
        channel_type=channel_data.get("channel_type", "team"),
        description=channel_data.get("description"),
        member_ids=channel_data.get("member_ids", [user["id"]]),
        owner_id=user["id"],
        created_by=user["id"],
    )
    
    channel_dict = channel.model_dump()
    channel_dict["created_at"] = channel_dict["created_at"].isoformat()
    
    await db.channels.insert_one(channel_dict.copy())
    return channel_dict


@router.get("/channels")
async def list_channels(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List user's channels"""
    user = await get_current_user(request, db)
    
    channels = await db.channels.find(
        {
            "organization_id": user["organization_id"],
            "member_ids": user["id"],
            "is_archived": False
        },
        {"_id": 0}
    ).to_list(1000)
    
    return channels


@router.get("/channels/{channel_id}/messages")
async def get_messages(
    channel_id: str,
    request: Request,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get channel messages"""
    user = await get_current_user(request, db)
    
    messages = await db.messages.find(
        {"channel_id": channel_id},
        {"_id": 0}
    ).sort("sent_at", -1).limit(limit).to_list(limit)
    
    return messages


@router.post("/channels/{channel_id}/messages")
async def send_message(
    channel_id: str,
    message_data: dict,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send message to channel"""
    user = await get_current_user(request, db)
    
    message = Message(
        channel_id=channel_id,
        sender_id=user["id"],
        sender_name=user["name"],
        content=message_data.get("content"),
        mentions=message_data.get("mentions", []),
        parent_message_id=message_data.get("parent_message_id"),
    )
    
    message_dict = message.model_dump()
    message_dict["sent_at"] = message_dict["sent_at"].isoformat()
    
    await db.messages.insert_one(message_dict.copy())
    
    # Broadcast to WebSocket connections in this channel
    if channel_id in active_connections:
        for connection in active_connections[channel_id]:
            try:
                await connection.send_json(message_dict)
            except:
                pass
    
    return message_dict


@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Add connection to active connections
    if channel_id not in active_connections:
        active_connections[channel_id] = []
    active_connections[channel_id].append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Broadcast to all connections in channel
            for connection in active_connections[channel_id]:
                if connection != websocket:
                    await connection.send_text(data)
    
    except WebSocketDisconnect:
        active_connections[channel_id].remove(websocket)
        if not active_connections[channel_id]:
            del active_connections[channel_id]
