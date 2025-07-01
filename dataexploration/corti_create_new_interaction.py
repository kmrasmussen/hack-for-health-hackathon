import requests
import json
import uuid
from get_corti_bearer_token import get_access_token

def create_corti_interaction(access_token: str) -> str | None:
    """
    Creates a new interaction in Corti and returns the interaction ID.
    
    Args:
        access_token: A valid Corti bearer token.

    Returns:
        The interaction ID if successful, otherwise None.
    """
    print("\nCreating a new interaction...")
    url = "https://api.eu.corti.app/v2/interactions/"
    run_uuid = uuid.uuid4()

    payload = {
        "encounter": {
            "type": "emergency",
            "status": "in-progress",
            "identifier": f"myencouterid-{run_uuid}",
            "period": {
                "startedAt": "2025-07-01T12:34:56Z",
                "endedAt": "2025-07-01T13:34:56Z"
            },
            "title": f"mytittle-{run_uuid}"
        },
        "patient": {"identifier": f"mypatientid-{run_uuid}"}
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Tenant-Name": "base",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        interaction_data = response.json()
        interaction_id = interaction_data.get("interactionId")
        
        print("Interaction created successfully!")
        print(json.dumps(interaction_data, indent=2))
        return interaction_id

    except requests.exceptions.RequestException as e:
        print(f"\nAn API error occurred: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        return None

if __name__ == "__main__":
    # This block runs only when the script is executed directly
    try:
        print("Getting a new access token...")
        token = get_access_token()
        print("Successfully retrieved token.")
        
        if token:
            create_corti_interaction(token)

    except requests.exceptions.RequestException as e:
        print(f"Failed to get access token: {e}")