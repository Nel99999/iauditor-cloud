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

# Malformed CSV - missing role column value
malformed_csv = b"email,name,role\ntest@example.com,Test User"

csv_file = ("test.csv", io.BytesIO(malformed_csv), "text/csv")

response = requests.post(
    f"{BASE_URL}/bulk-import/validate",
    headers=headers,
    files={"file": csv_file}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
