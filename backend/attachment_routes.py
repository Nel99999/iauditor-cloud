from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from typing import List
from datetime import datetime, timezone
from .auth_utils import get_current_user
import uuid
import io

router = APIRouter(prefix="/attachments", tags=["Attachments"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# Max file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


# ==================== ENDPOINTS ====================

@router.get("")
async def list_all_attachments(
    request: Request,
    resource_type: str = None,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all attachments for the organization, optionally filtered by resource type"""
    user = await get_current_user(request, db)
    
    # Build query
    query = {}
    
    # Get all resources for this organization and extract their attachments
    resources_to_check = ["tasks", "inspections", "checklists", "assets", "work_orders", "projects"]
    
    if resource_type:
        resources_to_check = [resource_type + "s" if not resource_type.endswith("s") else resource_type]
    
    all_attachments = []
    
    for collection_name in resources_to_check:
        if collection_name in dir(db):
            collection = getattr(db, collection_name)
            resources = await collection.find(
                {"organization_id": user["organization_id"]},
                {"_id": 0, "id": 1, "attachments": 1, "title": 1, "name": 1}
            ).to_list(1000)
            
            for resource in resources:
                attachments = resource.get("attachments", [])
                for att in attachments:
                    att["resource_type"] = collection_name.rstrip("s")
                    att["resource_id"] = resource.get("id")
                    att["resource_name"] = resource.get("title") or resource.get("name") or "Unnamed"
                    all_attachments.append(att)
    
    # Sort by created_at descending
    all_attachments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Limit results
    return all_attachments[:limit]



@router.post("/{resource_type}/{resource_id}/upload")
async def upload_attachment(
    resource_type: str,  # task, inspection, checklist
    resource_id: str,
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload file attachment"""
    user = await get_current_user(request, db)
    
    # Validate resource type
    if resource_type not in ["task", "inspection", "checklist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type. Must be: task, inspection, or checklist"
        )
    
    # Get collection based on resource type
    collection_map = {
        "task": "tasks",
        "inspection": "inspection_executions",
        "checklist": "checklist_executions"
    }
    collection = db[collection_map[resource_type]]
    
    # Verify resource exists and user has access
    resource = await collection.find_one(
        {"id": resource_id, "organization_id": user["organization_id"]}
    )
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Store file in GridFS
    fs = AsyncIOMotorGridFSBucket(db)
    file_id = await fs.upload_from_stream(
        file.filename,
        content,
        metadata={
            "resource_type": resource_type,
            "resource_id": resource_id,
            "organization_id": user["organization_id"],
            "uploaded_by": user["id"],
            "uploaded_by_name": user["name"],
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    # Create attachment record
    attachment = {
        "id": str(file_id),
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "uploaded_by": user["id"],
        "uploaded_by_name": user["name"],
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add attachment to resource
    await collection.update_one(
        {"id": resource_id},
        {
            "$push": {"attachments": attachment},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "attachment.uploaded",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "filename": file.filename,
            "size": len(content)
        }
    })
    
    return {
        "message": "File uploaded successfully",
        "attachment": attachment
    }


@router.get("/{resource_type}/{resource_id}/attachments")
async def get_attachments(
    resource_type: str,
    resource_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all attachments for a resource"""
    user = await get_current_user(request, db)
    
    # Validate resource type
    if resource_type not in ["task", "inspection", "checklist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type"
        )
    
    # Get collection
    collection_map = {
        "task": "tasks",
        "inspection": "inspection_executions",
        "checklist": "checklist_executions"
    }
    collection = db[collection_map[resource_type]]
    
    # Get resource
    resource = await collection.find_one(
        {"id": resource_id, "organization_id": user["organization_id"]}
    )
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found"
        )
    
    return resource.get("attachments", [])


@router.get("/download/{file_id}")
async def download_attachment(
    file_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Download attachment file"""
    user = await get_current_user(request, db)
    
    try:
        from bson import ObjectId
        fs = AsyncIOMotorGridFSBucket(db)
        
        # Get file metadata
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        metadata = grid_out.metadata
        
        # Verify access
        if metadata.get("organization_id") != user["organization_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Read file content
        content = await grid_out.read()
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=metadata.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename=\"{grid_out.filename}\""
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )


@router.delete("/{resource_type}/{resource_id}/attachments/{file_id}")
async def delete_attachment(
    resource_type: str,
    resource_id: str,
    file_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete attachment"""
    user = await get_current_user(request, db)
    
    # Validate resource type
    if resource_type not in ["task", "inspection", "checklist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type"
        )
    
    # Get collection
    collection_map = {
        "task": "tasks",
        "inspection": "inspection_executions",
        "checklist": "checklist_executions"
    }
    collection = db[collection_map[resource_type]]
    
    # Get resource
    resource = await collection.find_one(
        {"id": resource_id, "organization_id": user["organization_id"]}
    )
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type.capitalize()} not found"
        )
    
    # Remove attachment from resource
    await collection.update_one(
        {"id": resource_id},
        {
            "$pull": {"attachments": {"id": file_id}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Delete file from GridFS
    try:
        from bson import ObjectId
        fs = AsyncIOMotorGridFSBucket(db)
        await fs.delete(ObjectId(file_id))
    except:
        pass  # File might not exist in GridFS
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "attachment.deleted",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"file_id": file_id}
    })
    
    return {"message": "Attachment deleted successfully"}
