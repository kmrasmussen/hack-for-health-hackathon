import os
import shutil
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE other imports
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import contextlib

# Import DB and transcription functions
from database import get_db, init_db, Transcript, AsyncSessionLocal
from get_corti_bearer_token import get_access_token
from corti_create_new_interaction import create_corti_interaction
from create_upload_recording import upload_recording
from create_transcript import create_transcript
from create_whisper_transcript import transcribe_with_whisper
from transcript_improver import improve_transcript_with_gpt
from manuscript import generate_manuscript # <-- Import the new function

# --- App Setup ---
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, initialize the database
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

UPLOADS_DIR = "temp_uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Background Transcription Task ---
async def process_transcription_task(transcript_id: uuid.UUID, temp_file_path: str, db: AsyncSession):
    """The actual transcription logic that runs in the background."""
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

    # --- Update the database with results ---
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Transcript).where(Transcript.id == transcript_id))
        db_transcript = result.scalar_one_or_none()
        if db_transcript:
            db_transcript.whisper_transcript = whisper_result
            db_transcript.corti_transcript = corti_result
            db_transcript.status = "completed"
            await session.commit()

    # Clean up the temporary file
    os.remove(temp_file_path)

# --- API Endpoints ---
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/transcripts")
async def create_transcription_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new transcription job, saves it to DB, and starts it in the background."""
    temp_file_name = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(UPLOADS_DIR, temp_file_name)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_transcript = Transcript(original_filename=file.filename)
    db.add(new_transcript)
    await db.commit()
    await db.refresh(new_transcript)

    background_tasks.add_task(process_transcription_task, new_transcript.id, temp_file_path, db)
    return {"transcript_id": new_transcript.id, "status": new_transcript.status}

@app.get("/transcripts")
async def get_all_transcripts(db: AsyncSession = Depends(get_db)):
    """Returns a list of all transcription jobs."""
    result = await db.execute(select(Transcript).order_by(Transcript.created_at.desc()))
    return result.scalars().all()

@app.get("/transcripts/{transcript_id}")
async def get_transcript_details(transcript_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Returns the details and status of a single transcription job."""
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    transcript = result.scalar_one_or_none()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

class ImprovedTranscriptUpdate(BaseModel):
    improved_transcript: dict

@app.put("/transcripts/{transcript_id}")
async def save_improved_transcript(
    transcript_id: uuid.UUID,
    update_data: ImprovedTranscriptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Saves the user-edited improved transcript to the database."""
    result = await db.execute(select(Transcript).where(Transcript.id == transcript_id))
    db_transcript = result.scalar_one_or_none()
    if not db_transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    db_transcript.improved_transcript = update_data.improved_transcript
    await db.commit()
    return {"message": "Transcript updated successfully"}

# --- Manuscript Generation Endpoint ---
class ManuscriptRequest(BaseModel):
    topic: str

@app.post("/manuscript")
async def create_manuscript(request: ManuscriptRequest):
    """Generates a medical manuscript on a given topic."""
    manuscript_data = generate_manuscript(topic=request.topic)
    if manuscript_data:
        return manuscript_data.dict()
    else:
        raise HTTPException(status_code=500, detail="Failed to generate manuscript.")

# The /improve endpoint remains mostly the same, but is now just for processing, not saving.
class TranscriptsToImprove(BaseModel):
    whisper_transcription: str
    corti_transcription: str

@app.post("/improve")
async def improve_transcripts(transcripts: TranscriptsToImprove):
    improved_result = improve_transcript_with_gpt(
        whisper_text=transcripts.whisper_transcription,
        corti_text=transcripts.corti_transcription
    )
    if improved_result:
        return improved_result.dict()
    else:
        raise HTTPException(status_code=500, detail="Failed to generate improved transcript.")