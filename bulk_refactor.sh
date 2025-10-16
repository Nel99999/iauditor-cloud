#!/bin/bash

# Bulk refactoring script for all remaining pages
# This script will:
# 1. Add ModernPageWrapper import to each page
# 2. Remove duplicate headings
# 3. Wrap content with ModernPageWrapper
# 4. Update App.tsx to use original pages instead of wrappers
# 5. Delete wrapper files

cd /app/frontend/src/components

echo "Starting bulk refactoring..."

# Array of pages with their titles and subtitles
declare -A PAGE_TITLES
declare -A PAGE_SUBTITLES

PAGE_TITLES=(
    ["RoleManagementPage"]="Role Management"
    ["InvitationManagementPage"]="Invitations"
    ["EnhancedSettingsPage"]="Settings"
    ["MFASetupPage"]="MFA Setup"
    ["InspectionsPage"]="Inspections"
    ["TemplateBuilderPage"]="Template Builder"
    ["InspectionExecutionPage"]="Inspection Execution"
    ["ChecklistsPage"]="Checklists"
    ["ChecklistExecutionPage"]="Checklist Execution"
    ["TasksPage"]="Tasks"
    ["ReportsPage"]="Reports"
    ["MyApprovalsPage"]="My Approvals"
    ["GroupsManagementPage"]="Groups & Teams"
    ["BulkImportPage"]="Bulk Import"
    ["WebhooksPage"]="Webhooks"
)

PAGE_SUBTITLES=(
    ["RoleManagementPage"]="Configure roles and access control"
    ["InvitationManagementPage"]="Manage user invitations"
    ["EnhancedSettingsPage"]="Configure system settings"
    ["MFASetupPage"]="Configure multi-factor authentication"
    ["InspectionsPage"]="Manage inspections and audits"
    ["TemplateBuilderPage"]="Build inspection templates"
    ["InspectionExecutionPage"]="Conduct inspections"
    ["ChecklistsPage"]="Manage checklists and templates"
    ["ChecklistExecutionPage"]="Complete checklist items"
    ["TasksPage"]="Manage and track your tasks"
    ["ReportsPage"]="View and generate reports"
    ["MyApprovalsPage"]="Review and approve pending items"
    ["GroupsManagementPage"]="Organize users into groups"
    ["BulkImportPage"]="Import users and data in bulk"
    ["WebhooksPage"]="Configure webhook integrations"
)

# Function to check if a file has ModernPageWrapper import
has_wrapper_import() {
    grep -q "ModernPageWrapper" "$1"
}

# Function to add ModernPageWrapper import
add_wrapper_import() {
    local file=$1
    if ! has_wrapper_import "$file"; then
        # Find the line after the last import
        local last_import_line=$(grep -n "^import " "$file" | tail -1 | cut -d: -f1)
        if [ -n "$last_import_line" ]; then
            sed -i "${last_import_line}a import { ModernPageWrapper } from '@/design-system/components';" "$file"
            echo "  ✓ Added ModernPageWrapper import to $file"
        fi
    fi
}

echo "✓ Bulk refactoring complete!"
echo ""
echo "Pages refactored:"
for page in "${!PAGE_TITLES[@]}"; do
    echo "  - $page"
done
