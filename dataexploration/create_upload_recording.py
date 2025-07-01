import requests
import json
import uuid
import os
from get_corti_bearer_token import get_access_token
from corti_create_new_interaction import create_corti_interaction # <-- Import the new function

# --- 1. Get a fresh access token ---
try:
    print("Getting a new access token...")
    access_token = get_access_token()
    print("Successfully retrieved token.")
except requests.exceptions.RequestException as e:
    print(f"Failed to get access token: {e}")
    exit()

# --- 2. Create a new Interaction using the function ---
interaction_id = create_corti_interaction(access_token)

# --- 3. Upload the Recording to the new Interaction ---
if interaction_id:
    print(f"\nUploading recording to interaction ID: {interaction_id}")
    
    # The user specified the path /audio/kasper1.wav.
    # We assume this is relative to the project root.
    audio_file_path = "../audio/kasper1.wav"

    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        exit()

    try:
        upload_url = f"https://api.eu.corti.app/v2/interactions/{interaction_id}/recordings/"
        
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Tenant-Name": "base",
            "Content-Type": "application/octet-stream"
        }

        with open(audio_file_path, "rb") as audio_file:
            response = requests.post(upload_url, headers=upload_headers, data=audio_file)
        
        response.raise_for_status()
        
        print("Recording uploaded successfully!")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

    except requests.exceptions.RequestException as e:
        print(f"\nAn API error occurred while uploading recording: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")