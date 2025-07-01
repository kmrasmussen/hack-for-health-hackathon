from openai import OpenAI
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- 1. Setup OpenAI Client ---
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client for TTS: {e}")
    client = None

def generate_speech(text_to_speak: str) -> bytes | None:
    """
    Generates spoken audio from input text using OpenAI's TTS API.

    Args:
        text_to_speak: The text to be converted to speech.

    Returns:
        The audio data in bytes (MP3 format) if successful, otherwise None.
    """
    if not client:
        print("TTS client not initialized.")
        return None

    try:
        response = client.audio.speech.create(
            model="tts-1",  # A good balance of quality and speed
            voice="nova",   # A clear, professional female voice
            input=text_to_speak
        )
        # The response body contains the raw audio data.
        return response.content
    except Exception as e:
        print(f"An error occurred while generating speech: {e}")
        return None