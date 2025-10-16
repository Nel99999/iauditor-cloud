#!/usr/bin/env python3
"""
Automated script to refactor remaining pages by:
1. Adding ModernPageWrapper import
2. Finding and extracting title/subtitle from wrapper files
3. Removing duplicate headings
4. Wrapping content with ModernPageWrapper
"""

import re
import os
from pathlib import Path

# Mapping extracted from wrapper files
PAGE_CONFIGS = {
    'ChecklistsPage': {'title': 'Checklists', 'subtitle': 'Manage checklists and templates'},
    'TasksPage': {'title': 'Tasks', 'subtitle': 'Manage and track your tasks'},
    'ReportsPage': {'title': 'Reports', 'subtitle': 'View and generate reports'},
    'MyApprovalsPage': {'title': 'My Approvals', 'subtitle': 'Review and approve pending items'},
    'GroupsManagementPage': {'title': 'Groups & Teams', 'subtitle': 'Organize users into groups'},
    'WebhooksPage': {'title': 'Webhooks', 'subtitle': 'Configure webhook integrations'},
    'BulkImportPage': {'title': 'Bulk Import', 'subtitle': 'Import users and data in bulk'},
    'ChecklistExecutionPage': {'title': 'Checklist Execution', 'subtitle': 'Complete checklist items'},
    'InspectionsPage': {'title': 'Inspections', 'subtitle': 'Manage inspections and audits'},
    'TemplateBuilderPage': {'title': 'Template Builder', 'subtitle': 'Build inspection templates'},
    'InspectionExecutionPage': {'title': 'Inspection Execution', 'subtitle': 'Conduct inspections'},
}

COMPONENTS_DIR = Path('/app/frontend/src/components')

def refactor_page(page_name, title, subtitle):
    """Refactor a single page to use ModernPageWrapper"""
    
    page_file = COMPONENTS_DIR / f"{page_name}.tsx"
    
    if not page_file.exists():
        print(f"❌ File not found: {page_file}")
        return False
        
    print(f"\n📝 Refactoring {page_name}...")
    
    content = page_file.read_text()
    
    # Step 1: Add ModernPageWrapper import if not present
    if 'ModernPageWrapper' not in content:
        # Find position after last import
        import_pattern = r'(import .+;\n)+' 
        matches = list(re.finditer(r'^import .+;$', content, re.MULTILINE))
        if matches:
            last_import_pos = matches[-1].end()
            import_statement = "\nimport { ModernPageWrapper } from '@/design-system/components';"
            content = content[:last_import_pos] + import_statement + content[last_import_pos:]
            print(f"  ✓ Added ModernPageWrapper import")
    
    # Step 2: Find and remove the heading block
    # Pattern 1: Complete header with flex container
    header_pattern = r'<div className="flex[^"]*items-center[^"]*">\s*<div>\s*<h1[^>]*>[^<]*</h1>\s*<p[^>]*>[^<]*</p>\s*</div>(?:\s*<Button[^>]*>[^<]*(?:<[^>]+>[^<]*</[^>]+>)?[^<]*</Button>)?\s*</div>'
    
    header_match = re.search(header_pattern, content, re.DOTALL)
    
    if header_match:
        print(f"  ✓ Found duplicate heading block")
        # Extract the button if present
        button_match = re.search(r'<Button[^>]*>.*?</Button>', header_match.group(0), re.DOTALL)
        has_button = button_match is not None
        
        # Remove the entire header block
        content = content.replace(header_match.group(0), '', 1)
    else:
        print(f"  ⚠️  No duplicate heading found (might be okay)")
        has_button = False
    
    # Step 3: Wrap return with ModernPageWrapper
    # Find the component function and return statement
    func_pattern = rf'const {page_name}[^{{]*\{{(.+?)^\}};'
    func_match = re.search(func_pattern, content, re.DOTALL | re.MULTILINE)
    
    if not func_match:
        print(f"  ❌ Could not find function definition")
        return False
    
    # Find return statement
    return_pattern = r'return \(\s*<div className="space-y-6">'
    return_match = re.search(return_pattern, content)
    
    if return_match:
        # Replace return statement to include ModernPageWrapper
        new_return = f'''return (
    <ModernPageWrapper 
      title="{title}" 
      subtitle="{subtitle}"
    >
      <div className="space-y-6">'''
        content = content.replace(return_match.group(0), new_return, 1)
        print(f"  ✓ Wrapped with ModernPageWrapper")
        
        # Find and update the closing tags
        # Look for the last closing div before the semicolon
        closing_pattern = r'</div>\s*\);\s*};'
        closing_match = re.search(closing_pattern, content)
        
        if closing_match:
            new_closing = '''</div>
    </ModernPageWrapper>
  );
};'''
            content = content.replace(closing_match.group(0), new_closing, 1)
            print(f"  ✓ Added closing ModernPageWrapper tag")
        
    else:
        print(f"  ⚠️  Could not find return statement pattern")
    
    # Write back
    page_file.write_text(content)
    print(f"  ✅ Successfully refactored {page_name}")
    return True

def main():
    print("=" * 60)
    print("🚀 Starting automated page refactoring")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for page_name, config in PAGE_CONFIGS.items():
        try:
            if refactor_page(page_name, config['title'], config['subtitle']):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ❌ Error refactoring {page_name}: {str(e)}")
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully refactored: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
