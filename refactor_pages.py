#!/usr/bin/env python3
"""
Script to refactor all *PageNew.tsx wrapper files by:
1. Extracting title/subtitle from wrapper
2. Updating original page to use ModernPageWrapper
3. Removing duplicate headings from original page
"""

import re
import os
from pathlib import Path

# Mapping of wrapper files to their titles and subtitles
PAGE_MAPPINGS = {
    'BulkImportPage': {'title': 'Bulk Import', 'subtitle': 'Import users and data in bulk'},
    'ChecklistExecutionPage': {'title': 'Checklist Execution', 'subtitle': 'Complete checklist items'},
    'ChecklistsPage': {'title': 'Checklists', 'subtitle': 'Manage checklists and templates'},
    'EnhancedSettingsPage': {'title': 'Settings', 'subtitle': 'Configure system settings'},
    'GroupsManagementPage': {'title': 'Groups & Teams', 'subtitle': 'Organize users into groups'},
    'InspectionExecutionPage': {'title': 'Inspection Execution', 'subtitle': 'Conduct inspections'},
    'InspectionsPage': {'title': 'Inspections', 'subtitle': 'Manage inspections and audits'},
    'InvitationManagementPage': {'title': 'Invitations', 'subtitle': 'Manage user invitations'},
    'MFASetupPage': {'title': 'MFA Setup', 'subtitle': 'Configure multi-factor authentication'},
    'MyApprovalsPage': {'title': 'My Approvals', 'subtitle': 'Review and approve pending items'},
    'ReportsPage': {'title': 'Reports', 'subtitle': 'View and generate reports'},
    'RoleManagementPage': {'title': 'Role Management', 'subtitle': 'Configure roles and access control'},
    'TasksPage': {'title': 'Tasks', 'subtitle': 'Manage and track your tasks'},
    'TemplateBuilderPage': {'title': 'Template Builder', 'subtitle': 'Build inspection templates'},
    'UserManagementPage': {'title': 'User Management', 'subtitle': 'Manage system users and permissions'},
    'WebhooksPage': {'title': 'Webhooks', 'subtitle': 'Configure webhook integrations'},
}

# Pages that don't need wrapper (auth pages)
SKIP_PAGES = ['LoginPage', 'RegisterPage', 'ForgotPasswordPage', 'ResetPasswordPage']

COMPONENTS_DIR = Path('/app/frontend/src/components')

def add_modern_page_wrapper_import(content: str) -> str:
    """Add ModernPageWrapper import if not present"""
    if 'ModernPageWrapper' in content:
        return content
    
    # Find the last import statement
    import_lines = []
    other_lines = []
    in_imports = True
    
    for line in content.split('\n'):
        if in_imports and (line.startswith('import ') or line.strip() == ''):
            import_lines.append(line)
        else:
            in_imports = False
            other_lines.append(line)
    
    # Add the ModernPageWrapper import after other imports
    import_lines.append("import { ModernPageWrapper } from '@/design-system/components';")
    
    return '\n'.join(import_lines + other_lines)

def remove_duplicate_heading(content: str, page_name: str) -> str:
    """Remove duplicate heading section from the page"""
    
    # Pattern to match heading sections like:
    # <div className="flex justify-between items-center">
    #   <div>
    #     <h1 ...>Title</h1>
    #     <p ...>Description</p>
    #   </div>
    #   <Button ...>Action</Button>
    # </div>
    
    # Look for h1 tags with common patterns
    patterns = [
        # Pattern 1: Complete header block with flex container
        r'<div className="flex justify-between items-center">\s*<div>\s*<h1[^>]*>.*?</h1>\s*<p[^>]*>.*?</p>\s*</div>\s*(?:<Button[^>]*>.*?</Button>)?\s*</div>',
        # Pattern 2: Just the heading div
        r'<div>\s*<h1[^>]*>.*?</h1>\s*<p[^>]*>.*?</p>\s*</div>',
        # Pattern 3: Standalone h1 with description
        r'<h1[^>]*>.*?</h1>\s*<p[^>]*>.*?</p>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            print(f"  Found duplicate heading in {page_name}: {match.group(0)[:100]}...")
            # Remove only the heading part, keeping other content
            content = content.replace(match.group(0), '', 1)
            break
    
    return content

def wrap_with_modern_page_wrapper(content: str, page_name: str, title: str, subtitle: str) -> str:
    """Wrap the return statement with ModernPageWrapper"""
    
    # Find the main return statement
    # Look for patterns like: return ( ... );
    
    # First, check if already wrapped
    if 'ModernPageWrapper' in content and '<ModernPageWrapper' in content:
        print(f"  {page_name} already wrapped with ModernPageWrapper")
        return content
    
    # Find the function component definition
    func_match = re.search(rf'const {page_name}\s*[=:][^{{]*\{{', content)
    if not func_match:
        print(f"  Could not find function definition for {page_name}")
        return content
    
    # Find the return statement
    return_match = re.search(r'return\s*\(', content[func_match.end():])
    if not return_match:
        print(f"  Could not find return statement in {page_name}")
        return content
    
    return_pos = func_match.end() + return_match.end()
    
    # Find the matching closing parenthesis
    depth = 1
    i = return_pos
    while i < len(content) and depth > 0:
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
        i += 1
    
    if depth != 0:
        print(f"  Could not find matching closing parenthesis in {page_name}")
        return content
    
    closing_pos = i - 1
    
    # Extract the content inside return()
    return_content = content[return_pos:closing_pos].strip()
    
    # Check if there's a top-level div
    if return_content.startswith('<div'):
        # Find where the opening div ends
        div_match = re.match(r'<div[^>]*>', return_content)
        if div_match:
            opening_div = div_match.group(0)
            # Keep the div, but wrap it
            new_return = f'''
    <ModernPageWrapper 
      title="{title}" 
      subtitle="{subtitle}"
    >
      {return_content}
    </ModernPageWrapper>'''
        else:
            new_return = f'''
    <ModernPageWrapper 
      title="{title}" 
      subtitle="{subtitle}"
    >
      {return_content}
    </ModernPageWrapper>'''
    else:
        new_return = f'''
    <ModernPageWrapper 
      title="{title}" 
      subtitle="{subtitle}"
    >
      {return_content}
    </ModernPageWrapper>'''
    
    # Replace the return content
    new_content = content[:return_pos] + new_return + '\n  ' + content[closing_pos:]
    
    return new_content

def refactor_page(page_name: str):
    """Refactor a single page"""
    print(f"\nRefactoring {page_name}...")
    
    if page_name in SKIP_PAGES:
        print(f"  Skipping {page_name} (auth page)")
        return
    
    if page_name not in PAGE_MAPPINGS:
        print(f"  No mapping found for {page_name}")
        return
    
    page_file = COMPONENTS_DIR / f"{page_name}.tsx"
    if not page_file.exists():
        print(f"  File not found: {page_file}")
        return
    
    print(f"  Reading {page_file}")
    content = page_file.read_text()
    
    # Step 1: Add ModernPageWrapper import
    content = add_modern_page_wrapper_import(content)
    
    # Step 2: Remove duplicate heading
    content = remove_duplicate_heading(content, page_name)
    
    # Step 3: Wrap with ModernPageWrapper
    mapping = PAGE_MAPPINGS[page_name]
    content = wrap_with_modern_page_wrapper(content, page_name, mapping['title'], mapping['subtitle'])
    
    # Write back
    page_file.write_text(content)
    print(f"  ✓ Refactored {page_name}")

def main():
    print("Starting page refactoring...")
    
    for page_name in PAGE_MAPPINGS.keys():
        refactor_page(page_name)
    
    print("\n✓ Refactoring complete!")

if __name__ == '__main__':
    main()
