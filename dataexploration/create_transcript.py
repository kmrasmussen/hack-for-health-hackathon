import requests
import json
import os

# Use relative imports for modules in the same package
from .get_corti_bearer_token import get_access_token
from .corti_create_new_interaction import create_corti_interaction
from .create_upload_recording import upload_recording

def create_transcript(access_token: str, interaction_id: str, recording_id: str) -> str | None:
    """
    Requests a transcript and returns the transcribed text.
    """
    print("\nRequesting transcript...")
    try:
        url = f"https://api.eu.corti.app/v2/interactions/{interaction_id}/transcripts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Tenant-Name": "base",
            "Content-Type": "application/json"
        }
        payload = {
            "recordingId": recording_id,
            "primaryLanguage": "da",
            "modelName": "Base",
            "diarize": False
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        transcript_data = response.json()
        print("Transcript created successfully!")
        
        if transcript_data.get("transcripts"):
            full_text = " ".join([t['text'] for t in transcript_data['transcripts']])
            print(f"\n>>> Corti Transcription: {full_text}")
            return full_text
        return "[Transcription in progress or failed]"

    except requests.exceptions.RequestException as e:
        print(f"\nAn API error occurred while creating transcript: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        return None

if __name__ == "__main__":
    # Define the audio file to be transcribed
    audio_file_path = "../audio/kasper1.wav"

    # --- Main Workflow ---
    token = get_access_token()
    if not token:
        exit()

    interaction_id = create_corti_interaction(token)
    if not interaction_id:
        exit()

    recording_id = upload_recording(token, interaction_id, audio_file_path)
    if not recording_id:
        exit()
    
    create_transcript(token, interaction_id, recording_id)