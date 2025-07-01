import requests
import json
import uuid  # <-- Import the uuid library
from get_corti_bearer_token import get_access_token # <-- Import the function

# --- 1. Get a fresh access token ---
try:
    print("Getting a new access token...")
    access_token = get_access_token()
    print("Successfully retrieved token.")
except requests.exceptions.RequestException as e:
    print(f"Failed to get access token: {e}")
    exit()

# --- 2. Define the interaction details ---
url = "https://api.eu.corti.app/v2/interactions/"

# Generate a unique ID to avoid duplicate errors
run_uuid = uuid.uuid4()

payload = {
    "encounter": {
        "type": "emergency",
        "status": "in-progress",
        "identifier": f"myencouterid-{run_uuid}",  # <-- Make identifier unique
        "period": {
            "startedAt": "2025-07-01T12:34:56Z",
            "endedAt": "2025-07-01T13:34:56Z"
        },
        "title": f"mytittle-{run_uuid}" # <-- Also make title unique
    },
    "patient": {"identifier": f"mypatientid-{run_uuid}"} # <-- Make identifier unique
}

# --- 3. Set headers with the new token ---
headers = {
    "Authorization": f"Bearer {access_token}",
    "Tenant-Name": "base", # This should match the tenant used for the token
    "Content-Type": "application/json"
}

# --- 4. Make the API request ---
print("\nCreating a new interaction...")
try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)
    
    print("Interaction created successfully!")
    print("Response:")
    print(json.dumps(response.json(), indent=2))

except requests.exceptions.RequestException as e:
    print(f"\nAn API error occurred: {e}")
    if e.response is not None:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Body: {e.response.text}")