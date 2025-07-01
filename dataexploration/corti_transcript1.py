import os
import requests
import json
from datasets import load_dataset
import soundfile as sf
import time
from dotenv import load_dotenv # <-- Add this import

# Load variables from .env file into environment
load_dotenv() # <-- Add this line

# --- 1. Configuration ---
# Get credentials and settings from environment variables
# The script will now read these from your .env file
API_KEY = os.getenv("CORTI_API_KEY")
TENANT_NAME = os.getenv("CORTI_TENANT_NAME")
ENVIRONMENT = os.getenv("CORTI_ENVIRONMENT")

if not all([API_KEY, TENANT_NAME, ENVIRONMENT]):
    print("Error: Please set CORTI_API_KEY, CORTI_TENANT_NAME, and CORTI_ENVIRONMENT environment variables.")
    exit()

BASE_URL = f"https://api.{ENVIRONMENT}.corti.app/v2"
AUTH_HEADER = {"Authorization": f"Bearer {API_KEY}", "Tenant-Name": TENANT_NAME}

# --- 2. Get an Audio Sample ---
print("Fetching an audio sample from the CoRal dataset...")
try:
    streaming_dataset = load_dataset("CoRal-project/coral-v2", "read_aloud", split="val", streaming=True)
    sample = next(iter(streaming_dataset)) # Get the very first sample
    
    audio_array = sample['audio']['array']
    sampling_rate = sample['audio']['sampling_rate']
    original_transcription = sample['text']

    temp_audio_filename = "temp_corti_audio.wav"
    sf.write(temp_audio_filename, audio_array, sampling_rate)
    print(f"Saved temporary audio file: {temp_audio_filename}")
    print(f"Original Transcription: {original_transcription}")

except Exception as e:
    print(f"Failed to load dataset or save audio: {e}")
    exit()

# --- 3. Use the Corti API ---
interaction_id = None
try:
    # Step 1: Create an Interaction
    print("\nStep 1: Creating Corti Interaction...")
    interaction_payload = { "assignedUserId": "hackathon-user-1" }
    response = requests.post(
        f"{BASE_URL}/interactions",
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
        json=interaction_payload
    )
    response.raise_for_status()
    interaction_id = response.json()["interactionId"]
    print(f"Successfully created interaction with ID: {interaction_id}")

    # Step 2: Upload Recording
    print("\nStep 2: Uploading Recording...")
    with open(temp_audio_filename, "rb") as audio_file:
        response = requests.post(
            f"{BASE_URL}/interactions/{interaction_id}/recordings",
            headers={**AUTH_HEADER, "Content-Type": "application/octet-stream"},
            data=audio_file
        )
    response.raise_for_status()
    recording_id = response.json()["recordingId"]
    print(f"Successfully uploaded recording with ID: {recording_id}")

    # Step 3: Create Transcript
    print("\nStep 3: Requesting Transcript...")
    # Note: Transcription can take time. We might need to poll for the result later.
    # This call initiates the transcription process.
    transcript_payload = {
        "recordingId": recording_id,
        "tenantName": "base",
        "primaryLanguage": "en", # Danish
        "modelName": "enhanced", # or "base", "premier"
        "diarize": False # The sample has only one speaker
    }
    response = requests.post(
        f"{BASE_URL}/interactions/{interaction_id}/transcripts",
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
        json=transcript_payload
    )
    response.raise_for_status()
    transcript_data = response.json()
    print("\nSuccessfully initiated transcription.")
    print("Full transcript response:")
    print(json.dumps(transcript_data, indent=2))

    # Extract and print the text
    if transcript_data.get("transcripts"):
        full_text = " ".join([t['text'] for t in transcript_data['transcripts']])
        print(f"\nCorti Transcription: {full_text}")
    else:
        print("\nTranscription is processing. The response did not contain the final text yet.")
        print("You may need to poll the GET /transcripts/{id} endpoint to get the result.")


except requests.exceptions.RequestException as e:
    print(f"\nAn API error occurred: {e}")
    if e.response is not None:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Body: {e.response.text}")

finally:
    # --- 4. Cleanup ---
    if os.path.exists(temp_audio_filename):
        os.remove(temp_audio_filename)
        print(f"\nCleaned up temporary file: {temp_audio_filename}")

