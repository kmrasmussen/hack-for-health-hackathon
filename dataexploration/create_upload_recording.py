import requests
import json
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

def upload_recording(access_token: str, interaction_id: str, file_path: str) -> str | None:
    """
    Uploads a recording for a given interaction.

    Args:
        access_token: A valid Corti bearer token.
        interaction_id: The ID of the interaction to upload the recording to.
        file_path: The local path to the audio file.

    Returns:
        The recording ID if successful, otherwise None.
    """
    print(f"\nUploading recording from {file_path} to interaction ID: {interaction_id}")

    if not os.path.exists(file_path):
        print(f"Error: Audio file not found at {file_path}")
        return None

    try:
        upload_url = f"https://api.eu.corti.app/v2/interactions/{interaction_id}/recordings/"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Tenant-Name": "base",
            "Content-Type": "application/octet-stream"
        }

        with open(file_path, "rb") as audio_file:
            response = requests.post(upload_url, headers=headers, data=audio_file)
        
        response.raise_for_status()
        
        recording_data = response.json()
        recording_id = recording_data.get("recordingId")

        print("Recording uploaded successfully!")
        print(f"Recording ID: {recording_id}")
        return recording_id

    except requests.exceptions.RequestException as e:
        print(f"\nAn API error occurred while uploading recording: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        return None

# --- 3. Upload the Recording to the new Interaction ---
if interaction_id:
    audio_file_path = "../audio/kasper1.wav"
    upload_recording(access_token, interaction_id, audio_file_path)