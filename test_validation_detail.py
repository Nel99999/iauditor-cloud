import requests
import io

BASE_URL = "https://workflow-engine-18.preview.emergentagent.com/api"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "llewellyn@bluedawncapital.co.za", "password": "TestPassword123!"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test CSV
csv_content = """email,name,role
test_bulk1@example.com,Test User 1,viewer
test_bulk2@example.com,Test User 2,operator
test_bulk3@example.com,Test User 3,inspector
invalid@test,Invalid User,viewer
duplicate@test.com,Duplicate,invalidrole"""

csv_file = ("test.csv", io.BytesIO(csv_content.encode('utf-8')), "text/csv")

response = requests.post(
    f"{BASE_URL}/bulk-import/validate",
    headers=headers,
    files={"file": csv_file}
)

import json
print(json.dumps(response.json(), indent=2))
