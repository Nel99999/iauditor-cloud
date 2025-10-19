#!/usr/bin/env python3
"""
Add RBAC permission checks to remaining create endpoints
"""
import re

files_to_fix = [
    {
        "file": "/app/backend/checklist_routes.py",
        "resource": "checklist",
        "search_pattern": r'(@router\.post\("/templates"[^\n]*\n)(async def create_checklist_template[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*\n)(    """[^"]*""")',
        "permission_check": '''    # SECURITY: Check permission before allowing creation
    from permission_routes import check_permission
    has_permission = await check_permission(db, user["id"], "checklist", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create checklists")
    '''
    },
    {
        "file": "/app/backend/project_routes.py",
        "resource": "project",
        "search_pattern": r'(@router\.post\(""[^\n]*\n)(async def create_project[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*\n)(    """[^"]*""")',
        "permission_check": '''    # SECURITY: Check permission before allowing creation
    from permission_routes import check_permission
    has_permission = await check_permission(db, user["id"], "project", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create projects")
    '''
    },
    {
        "file": "/app/backend/incident_routes.py",
        "resource": "incident",
        "search_pattern": r'(@router\.post\(""[^\n]*\n)(async def create_incident[^\n]*\n[^\n]*\n[^\n]*\n[^\n]*\n)(    """[^"]*""")',
        "permission_check": '''    # SECURITY: Check permission before allowing creation
    from permission_routes import check_permission
    has_permission = await check_permission(db, user["id"], "incident", "create", "organization")
    if not has_permission:
        raise HTTPException(status_code=403, detail="You don't have permission to create incidents")
    '''
    }
]

for fix_info in files_to_fix:
    try:
        with open(fix_info["file"], 'r') as f:
            content = f.read()
        
        # Find the function and add permission check right after get_current_user
        # Look for the pattern: user = await get_current_user(request, db)
        pattern = r'(user = await get_current_user\(request, db\)\n)'
        
        # Check if permission check already exists
        if "check_permission" in content:
            print(f"✅ {fix_info['file']} - Permission check already exists")
            continue
        
        # Add permission check after get_current_user
        replacement = r'\1' + fix_info['permission_check'] + '\n'
        new_content = re.sub(pattern, replacement, content, count=1)
        
        if new_content != content:
            with open(fix_info["file"], 'w') as f:
                f.write(new_content)
            print(f"✅ {fix_info['file']} - Added RBAC permission check")
        else:
            print(f"⚠️  {fix_info['file']} - Pattern not found, needs manual fix")
            
    except Exception as e:
        print(f"❌ {fix_info['file']} - Error: {str(e)}")

print("\nDone! Now restart backend to apply changes.")
