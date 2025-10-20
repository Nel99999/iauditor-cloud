# This file documents all missing endpoints that need to be implemented
# Listed from backend testing results

MISSING_ENDPOINTS = [
    # Organizations
    "GET /api/organizations/stats",
    "GET /api/organizations/sidebar-settings",
    
    # Assets  
    "GET /api/assets/types",  # Note: /assets/types/catalog exists
    
    # Work Orders
    "GET /api/work-orders/stats",  # Note: /work-orders/stats/overview exists
    
    # Inventory
    # Note: All exist at /inventory/items/* paths
    
    # Projects
    "GET /api/projects/stats",  # Note: /projects/stats/overview exists
    
    # Training
    # Note: Endpoints exist, tests using wrong paths
    
    # Dashboards
    # Note: /dashboards/executive and /dashboards/maintenance exist
    
    # Others
    "GET /api/workflows",  # /workflows/templates exists
    "GET /api/bulk-import/template",
    "GET /api/search",
]

NOTE = """
Many '404' errors are actually test script issues using wrong endpoint paths:
- Correct: /work-orders (not /workorders)
- Correct: /inventory/items (not /inventory)
- Correct: /training/courses (not /training/programs)
- Correct: /dashboards/executive (not /dashboard/executive)
"""
