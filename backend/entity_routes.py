"""
Organizational Entity Routes - Enhanced Option B MVP
Settings-based entity management with rich metadata

Endpoints:
- CRUD for organizational entities (Profile, Organisation, Company, Branch, Brand)
- CRUD for custom field definitions
- Bulk operations
- Templates
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List, Optional
from org_models import (
    OrganizationalEntity,
    OrganizationalEntityCreate,
    OrganizationalEntityUpdate,
    CustomFieldDefinition,
    CustomFieldDefinitionCreate,
)
from auth_utils import get_current_user
import uuid

router = APIRouter(prefix="/entities", tags=["Organizational Entities"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ============================================================================
# ORGANIZATIONAL ENTITIES CRUD
# ============================================================================

@router.get("")
async def get_all_entities(
    request: Request,
    entity_type: Optional[str] = None,
    level: Optional[int] = None,
    unlinked: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all organizational entities
    
    Args:
        entity_type: Filter by type (profile, organisation, company, branch, brand)
        level: Filter by level (1-5)
        unlinked: If True, only return entities without parent_id (orphaned)
    """
    user = await get_current_user(request, db)
    
    # Build query
    query = {"organization_id": user["organization_id"], "is_active": True}
    
    if entity_type:
        query["entity_type"] = entity_type
    
    if level is not None:
        query["level"] = level
    
    if unlinked:
        query["$or"] = [
            {"parent_id": None},
            {"parent_id": {"$exists": False}}
        ]
    
    entities = await db.organizational_entities.find(
        query,
        {"_id": 0}
    ).to_list(1000)
    
    return entities


@router.get("/{entity_id}")
async def get_entity(
    entity_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get specific organizational entity by ID"""
    user = await get_current_user(request, db)
    
    entity = await db.organizational_entities.find_one(
        {"id": entity_id, "organization_id": user["organization_id"]},
        {"_id": 0}
    )
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    return entity


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: OrganizationalEntityCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create new organizational entity (in Settings, not tree)"""
    user = await get_current_user(request, db)
    
    # RBAC: Only Master and Developer can create entities
    from permission_routes import check_permission
    has_permission = await check_permission(
        db, user["id"], "organization", "create", "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can create organizational entities"
        )
    
    # Create entity
    entity = OrganizationalEntity(
        **entity_data.model_dump(),
        organization_id=user["organization_id"],
        created_by=user["id"],
        parent_id=None  # Entities created in Settings are orphaned by default
    )
    
    entity_dict = entity.model_dump()
    entity_dict["created_at"] = entity_dict["created_at"].isoformat()
    entity_dict["updated_at"] = entity_dict["updated_at"].isoformat()
    
    await db.organizational_entities.insert_one(entity_dict)
    
    # Log to audit
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "action": f"entity.{entity_data.entity_type}.created",
        "resource_type": "organizational_entity",
        "resource_id": entity.id,
        "details": f"Created {entity_data.entity_type}: {entity_data.name}",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return entity


@router.put("/{entity_id}")
async def update_entity(
    entity_id: str,
    entity_data: OrganizationalEntityUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update organizational entity"""
    user = await get_current_user(request, db)
    
    # Verify entity exists
    entity = await db.organizational_entities.find_one(
        {"id": entity_id, "organization_id": user["organization_id"]}
    )
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    # RBAC: Only Master and Developer can update entities
    from permission_routes import check_permission
    has_permission = await check_permission(
        db, user["id"], "organization", "update", "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can update organizational entities"
        )
    
    # Update entity
    update_data = {k: v for k, v in entity_data.model_dump(exclude_unset=True).items() if v is not None}
    update_data["updated_by"] = user["id"]
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.organizational_entities.update_one(
        {"id": entity_id},
        {"$set": update_data}
    )
    
    # Log to audit
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "action": f"entity.{entity['entity_type']}.updated",
        "resource_type": "organizational_entity",
        "resource_id": entity_id,
        "details": f"Updated {entity['entity_type']}: {entity.get('name')}",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Entity updated successfully"}


@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete organizational entity (soft delete)"""
    user = await get_current_user(request, db)
    
    # Verify entity exists
    entity = await db.organizational_entities.find_one(
        {"id": entity_id, "organization_id": user["organization_id"]}
    )
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    # Check if entity is linked in hierarchy
    if entity.get("parent_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete entity that is linked in hierarchy. Unlink it first."
        )
    
    # Check if entity has children
    has_children = await db.organizational_entities.count_documents({
        "parent_id": entity_id,
        "is_active": True
    })
    
    if has_children > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete entity with {has_children} children. Remove children first."
        )
    
    # RBAC: Only Master and Developer can delete entities
    from permission_routes import check_permission
    has_permission = await check_permission(
        user, "organization", "delete", "organization", db
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can delete organizational entities"
        )
    
    # Soft delete
    await db.organizational_entities.update_one(
        {"id": entity_id},
        {"$set": {
            "is_active": False,
            "status": "deleted",
            "updated_by": user["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log to audit
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "action": f"entity.{entity['entity_type']}.deleted",
        "resource_type": "organizational_entity",
        "resource_id": entity_id,
        "details": f"Deleted {entity['entity_type']}: {entity.get('name')}",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Entity deleted successfully"}


# ============================================================================
# CUSTOM FIELDS CRUD
# ============================================================================

@router.get("/custom-fields")
async def get_custom_fields(
    request: Request,
    entity_type: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all custom field definitions for organization"""
    user = await get_current_user(request, db)
    
    query = {"organization_id": user["organization_id"], "is_active": True}
    
    if entity_type:
        query["entity_type"] = entity_type
    
    fields = await db.custom_field_definitions.find(
        query,
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    return fields


@router.post("/custom-fields", status_code=status.HTTP_201_CREATED)
async def create_custom_field(
    field_data: CustomFieldDefinitionCreate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create custom field definition (Master/Developer only)"""
    user = await get_current_user(request, db)
    
    # RBAC: Only Master and Developer
    user_role = await db.roles.find_one({
        "code": user["role"],
        "organization_id": user["organization_id"]
    })
    
    if not user_role or user_role.get("level", 10) > 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can create custom fields"
        )
    
    # Check if field_id already exists for this entity type
    existing = await db.custom_field_definitions.find_one({
        "organization_id": user["organization_id"],
        "entity_type": field_data.entity_type,
        "field_id": field_data.field_id,
        "is_active": True
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field '{field_data.field_id}' already exists for {field_data.entity_type}"
        )
    
    # Create field definition
    field_def = CustomFieldDefinition(
        **field_data.model_dump(),
        organization_id=user["organization_id"],
        created_by=user["id"]
    )
    
    field_dict = field_def.model_dump()
    field_dict["created_at"] = field_dict["created_at"].isoformat()
    
    await db.custom_field_definitions.insert_one(field_dict)
    
    return field_def


@router.delete("/custom-fields/{field_id}")
async def delete_custom_field(
    field_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete custom field definition"""
    user = await get_current_user(request, db)
    
    # RBAC: Only Master and Developer
    user_role = await db.roles.find_one({
        "code": user["role"],
        "organization_id": user["organization_id"]
    })
    
    if not user_role or user_role.get("level", 10) > 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master and Developer roles can delete custom fields"
        )
    
    # Soft delete
    result = await db.custom_field_definitions.update_one(
        {"id": field_id, "organization_id": user["organization_id"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field not found"
        )
    
    return {"message": "Custom field deleted successfully"}


# ============================================================================
# LOGO UPLOAD
# ============================================================================

@router.post("/{entity_id}/upload-logo")
async def upload_entity_logo(
    entity_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload logo for organizational entity"""
    from fastapi import File, UploadFile
    import gridfs
    import pymongo
    import os
    
    user = await get_current_user(request, db)
    
    # Verify entity exists
    entity = await db.organizational_entities.find_one(
        {"id": entity_id, "organization_id": user["organization_id"]}
    )
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    # Get file from request
    form = await request.form()
    file = form.get("file")
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # Save to GridFS
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    sync_client = pymongo.MongoClient(mongo_url)
    sync_db = sync_client[db_name]
    fs = gridfs.GridFS(sync_db)
    
    file_content = await file.read()
    file_id = fs.put(
        file_content,
        filename=f"entity_logo_{entity_id}",
        content_type=file.content_type
    )
    
    # Update entity with logo URL
    logo_url = f"/api/entities/{entity_id}/logo/{str(file_id)}"
    
    await db.organizational_entities.update_one(
        {"id": entity_id},
        {"$set": {
            "logo_url": logo_url,
            "updated_by": user["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": logo_url
    }


@router.get("/{entity_id}/logo/{file_id}")
async def get_entity_logo(entity_id: str, file_id: str):
    """Retrieve entity logo"""
    import gridfs
    import pymongo
    from bson import ObjectId
    from fastapi.responses import Response
    import os
    
    try:
        # Get GridFS file
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        sync_client = pymongo.MongoClient(mongo_url)
        sync_db = sync_client[db_name]
        fs = gridfs.GridFS(sync_db)
        
        grid_out = fs.get(ObjectId(file_id))
        content = grid_out.read()
        content_type = grid_out.content_type or "image/png"
        
        return Response(content=content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Logo not found")
