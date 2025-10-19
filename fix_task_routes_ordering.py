# Fix task_routes.py route ordering
import re

with open('/app/backend/task_routes.py', 'r') as f:
    content = f.read()

# Find all route blocks
pattern = r'(@router\.[a-z]+\([^)]*\)[^\n]*\n(?:async )?def [^(]+\([^)]*(?:\)[^)]*)*:.*?(?=@router\.|$))'
matches = list(re.finditer(pattern, content, re.DOTALL))

print(f"Found {len(matches)} route definitions")

# Identify routes that need to be moved (specific routes before parametric)
specific_routes_to_move = []
parametric_routes = []
other_routes = []

for match in matches:
    route_def = match.group(1)
    
    # Check if it's a parametric route (has {parameter})
    if '/{' in route_def.split('\n')[0]:
        parametric_routes.append((match.start(), match.end(), route_def))
    # Check if it's a specific path route that comes after parametric
    elif any(path in route_def.split('\n')[0] for path in ['/stats', '/templates', '/from-template', '/analytics']):
        specific_routes_to_move.append((match.start(), match.end(), route_def))
    else:
        other_routes.append((match.start(), match.end(), route_def))

print(f"Parametric routes: {len(parametric_routes)}")
print(f"Specific routes to move: {len(specific_routes_to_move)}")
print(f"Other routes: {len(other_routes)}")

# Show what we found
print("\nParametric routes:")
for start, end, route in parametric_routes[:3]:
    first_line = route.split('\n')[0]
    print(f"  {first_line}")

print("\nSpecific routes that need moving:")
for start, end, route in specific_routes_to_move:
    first_line = route.split('\n')[0]
    print(f"  {first_line}")
