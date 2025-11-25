from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from .auth_utils import get_current_user, get_password_hash
import csv
import io
import uuid

router = APIRouter(prefix="/bulk-import", tags=["Bulk Import"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


# ==================== HELPER FUNCTIONS ====================

def validate_csv_row(row: dict, row_number: int) -> tuple:
    """Validate a single CSV row"""
    errors = []
    
    # Required fields
    if not row.get("email"):
        errors.append(f"Row {row_number}: Email is required")
    if not row.get("name"):
        errors.append(f"Row {row_number}: Name is required")
    
    # Email format validation (basic)
    email = row.get("email", "")
    if email and "@" not in email:
        errors.append(f"Row {row_number}: Invalid email format")
    
    # Role validation
    valid_roles = ["viewer", "operator", "inspector", "supervisor", "manager", "team_lead", "operations_manager", "admin", "master", "developer"]
    role = row.get("role", "viewer").lower()
    if role and role not in valid_roles:
        errors.append(f"Row {row_number}: Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    return (len(errors) == 0, errors)


def parse_csv_file(file_content: str) -> tuple:
    """Parse CSV file content"""
    try:
        csv_reader = csv.DictReader(io.StringIO(file_content))
        rows = list(csv_reader)
        return (True, rows, None)
    except Exception as e:
        return (False, [], str(e))


# ==================== ENDPOINTS ====================

@router.post("/validate")
async def validate_bulk_import(
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Validate CSV file for bulk user import - Requires user.create.organization permission"""
    user = await get_current_user(request, db)
    
    # Check permission (not hardcoded role)
    from .permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "user",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to import users"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Read file content
    content = await file.read()
    file_content = content.decode('utf-8')
    
    # Parse CSV
    success, rows, error = parse_csv_file(file_content)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {error}"
        )
    
    # Get current user's role level for hierarchy check
    current_user_role = await db.roles.find_one({
        "code": user.get("role"),
        "organization_id": user["organization_id"]
    })
    current_level = current_user_role.get("level", 999) if current_user_role else 999
    
    # Validate rows
    valid_rows = []
    invalid_rows = []
    duplicate_emails = []
    
    for i, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
        is_valid, errors = validate_csv_row(row, i)
        
        # Additional role hierarchy check
        role_code = row.get("role", "viewer").lower()
        target_role = await db.roles.find_one({
            "code": role_code,
            "organization_id": user["organization_id"]
        })
        
        if target_role:
            target_level = target_role.get("level", 999)
            # Can only import users with equal or lower authority (higher level number)
            if current_level > target_level:
                errors.append(f"Cannot import {role_code} role (higher authority than your role)")
                is_valid = False
        
        # Check if email already exists
        email = row.get("email", "").lower().strip()
        existing_user = await db.users.find_one({
            "email": email,
            "organization_id": user["organization_id"]
        })
        
        if existing_user:
            duplicate_emails.append({
                "row": i,
                "email": email,
                "message": "Email already exists in organization"
            })
            invalid_rows.append({
                "row": i,
                "data": row,
                "errors": ["Email already exists"]
            })
        elif is_valid:
            valid_rows.append({
                "row": i,
                "email": email,
                "name": row.get("name"),
                "role": role_code,
                "group": row.get("group", "")
            })
        else:
            invalid_rows.append({
                "row": i,
                "data": row,
                "errors": errors
            })
    
    return {
        "is_valid": len(invalid_rows) == 0,
        "total_count": len(rows),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "duplicate_count": len(duplicate_emails),
        "preview": valid_rows[:10],  # Show first 10
        "errors": invalid_rows[:20],  # Show first 20 errors
        "duplicates": duplicate_emails[:20]
    }


@router.post("/users")
async def import_users(
    file: UploadFile = File(...),
    send_invitations: bool = True,
    request: Request = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Import users from CSV file - Requires user.create.organization permission"""
    user = await get_current_user(request, db)
    
    # Check permission (not hardcoded role)
    from .permission_routes import check_permission
    has_permission = await check_permission(
        db,
        user["id"],
        "user",
        "create",
        "organization"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to import users"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Read file content
    content = await file.read()
    file_content = content.decode('utf-8')
    
    # Parse CSV
    success, rows, error = parse_csv_file(file_content)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {error}"
        )
    
    # Get current user's role level for hierarchy check
    current_user_role = await db.roles.find_one({
        "code": user.get("role"),
        "organization_id": user["organization_id"]
    })
    current_level = current_user_role.get("level", 999) if current_user_role else 999
    
    # Process rows
    imported_users = []
    failed_imports = []
    
    for i, row in enumerate(rows, start=2):
        try:
            # Validate row
            is_valid, errors = validate_csv_row(row, i)
            
            if not is_valid:
                failed_imports.append({
                    "row": i,
                    "email": row.get("email"),
                    "errors": errors
                })
                continue
            
            # Role hierarchy check
            role_code = row.get("role", "viewer").lower()
            target_role = await db.roles.find_one({
                "code": role_code,
                "organization_id": user["organization_id"]
            })
            
            if target_role:
                target_level = target_role.get("level", 999)
                if current_level > target_level:
                    failed_imports.append({
                        "row": i,
                        "email": row.get("email"),
                        "errors": [f"Cannot import {role_code} role (higher authority than your role)"]
                    })
                    continue
            
            email = row.get("email", "").lower().strip()
            
            # Check if email already exists
            existing_user = await db.users.find_one({
                "email": email,
                "organization_id": user["organization_id"]
            })
            
            if existing_user:
                failed_imports.append({
                    "row": i,
                    "email": email,
                    "errors": ["Email already exists"]
                })
                continue
            
            # Create user
            new_user = {
                "id": str(uuid.uuid4()),
                "email": email,
                "name": row.get("name", "").strip(),
                "role": role_code,
                "organization_id": user["organization_id"],
                "auth_provider": "local",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Set default password if provided
            if row.get("password"):
                new_user["password_hash"] = get_password_hash(row["password"])
            
            await db.users.insert_one(new_user)
            
            # Add to group if specified
            group_name = row.get("group", "").strip()
            if group_name:
                group = await db.user_groups.find_one({
                    "organization_id": user["organization_id"],
                    "name": group_name
                })
                if group:
                    await db.user_groups.update_one(
                        {"id": group["id"]},
                        {"$addToSet": {"member_ids": new_user["id"]}}
                    )
            
            imported_users.append({
                "email": email,
                "name": new_user["name"],
                "role": new_user["role"]
            })
            
            # Send invitation if requested
            if send_invitations:
                # Create invitation
                invitation = {
                    "id": str(uuid.uuid4()),
                    "organization_id": user["organization_id"],
                    "email": email,
                    "role_id": new_user["role"],
                    "invited_by": user["id"],
                    "invited_by_name": user["name"],
                    "status": "pending",
                    "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.invitations.insert_one(invitation)
                
                # TODO: Send invitation email
        
        except Exception as e:
            failed_imports.append({
                "row": i,
                "email": row.get("email"),
                "errors": [str(e)]
            })
    
    # Log audit event
    await db.audit_logs.insert_one({
        "id": str(uuid.uuid4()),
        "organization_id": user["organization_id"],
        "user_id": user["id"],
        "user_email": user["email"],
        "user_name": user["name"],
        "action": "users.bulk_imported",
        "resource_type": "user",
        "resource_id": "bulk",
        "result": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "total_rows": len(rows),
            "imported": len(imported_users),
            "failed": len(failed_imports),
            "filename": file.filename
        }
    })
    
    return {
        "message": "Import completed",
        "imported_count": len(imported_users),
        "failed_count": len(failed_imports),
        "imported_users": imported_users,
        "failed_imports": failed_imports[:50]  # Limit to first 50 errors
    }


@router.get("/users/template")
async def get_import_template(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get CSV template for user import"""
    user = await get_current_user(request, db)
    
    # Create CSV template
    template = "email,name,role,group,password\n"
    template += "john.doe@example.com,John Doe,manager,Engineering Team,TempPassword123\n"
    template += "jane.smith@example.com,Jane Smith,inspector,Quality Team,TempPassword456\n"
    
    return {
        "template": template,
        "instructions": {
            "required_fields": ["email", "name"],
            "optional_fields": ["role", "group", "password"],
            "valid_roles": ["admin", "manager", "supervisor", "inspector", "viewer"],
            "notes": [
                "Email must be unique within organization",
                "Role defaults to 'viewer' if not specified",
                "Group must exist in organization",
                "Password is optional; users will receive invitation email"
            ]
        }
    }




@router.get("/template")
async def get_import_template_alias(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get CSV template for import (alias for /users/template)"""
    return await get_import_template(request, db)
