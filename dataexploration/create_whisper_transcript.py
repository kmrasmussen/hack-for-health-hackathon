import os
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- 1. Setup OpenAI Client ---
# The script will read the OPENAI_API_KEY from your .env file
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure your OPENAI_API_KEY is set correctly in the .env file.")
    exit()

def transcribe_with_whisper(file_path: str):
    """
    Transcribes the given audio file using OpenAI's Whisper API.
    """
    print(f"\nTranscribing {file_path} with Whisper...")

    if not os.path.exists(file_path):
        print(f"Error: Audio file not found at {file_path}")
        return

    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
              model="whisper-1", # You can also use "gpt-4o-transcribe"
              file=audio_file
            )
        
        print("Whisper transcription successful!")
        print(f"\n>>> Final Transcription: {transcription.text}")

    except Exception as e:
        print(f"An error occurred with the Whisper API call: {e}")


if __name__ == "__main__":
    # Define the audio file to be transcribed
    audio_file_path = "../audio/kasper1.wav"
    
    # --- Main Workflow ---
    transcribe_with_whisper(audio_file_path)