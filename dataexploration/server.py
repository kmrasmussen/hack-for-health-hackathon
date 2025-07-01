import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import your refactored functions
from get_corti_bearer_token import get_access_token
from corti_create_new_interaction import create_corti_interaction
from create_upload_recording import upload_recording
from create_transcript import create_transcript
from create_whisper_transcript import transcribe_with_whisper

app = FastAPI()

# Create a directory for temporary uploads
UPLOADS_DIR = "temp_uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount the 'static' directory to serve index.html and index.js
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    """Serves the main HTML file."""
    return FileResponse('static/index.html')

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Receives an audio file, transcribes it with both Corti and Whisper,
    and returns the results.
    """
    # Save the uploaded file temporarily
    temp_file_name = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(UPLOADS_DIR, temp_file_name)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # --- Run Whisper Transcription ---
    whisper_result = transcribe_with_whisper(temp_file_path)

    # --- Run Corti Transcription Workflow ---
    corti_result = "[Corti transcription failed]"
    token = get_access_token()
    if token:
        interaction_id = create_corti_interaction(token)
        if interaction_id:
            recording_id = upload_recording(token, interaction_id, temp_file_path)
            if recording_id:
                corti_result = create_transcript(token, interaction_id, recording_id)

    # Clean up the temporary file
    os.remove(temp_file_path)

    return {
        "whisper_transcription": whisper_result or "Failed to get Whisper transcription.",
        "corti_transcription": corti_result or "Failed to get Corti transcription."
    }