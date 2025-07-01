from datasets import load_dataset
import soundfile as sf
from openai import OpenAI
import os
import jiwer # <-- Add this import

# --- Setup OpenAI ---
# Make sure you have your OpenAI API key set as an environment variable
# In your terminal: export OPENAI_API_KEY='your-key-here'
# Or uncomment and set it here (less secure)
# os.environ["OPENAI_API_KEY"] = "your-key-here"
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure your OPENAI_API_KEY is set correctly.")
    exit()


# Load the Coral dataset in streaming mode
streaming_dataset = load_dataset(
    "CoRal-project/coral-v2", 
    "read_aloud", 
    split="val", 
    streaming=True
)

# The .take(N) method gives an iterable of the first N samples.
# Let's just process the first 3 to keep it quick.
first_samples = streaming_dataset.take(3)

print("Streaming and transcribing the first 3 rows from the 'val' split:")
for i, sample in enumerate(first_samples):
    print(f"\n--- Processing Sample {i+1} ---")
    
    # --- 1. Get audio data from the dataset ---
    audio_array = sample['audio']['array']
    sampling_rate = sample['audio']['sampling_rate']
    original_transcription = sample['text']

    # --- 2. Save audio to a temporary WAV file ---
    temp_audio_filename = f"temp_audio_{i+1}.wav"
    sf.write(temp_audio_filename, audio_array, sampling_rate)
    print(f"Saved temporary audio to {temp_audio_filename}")

    try:
        # --- 3. Send the file to OpenAI Whisper API ---
        with open(temp_audio_filename, "rb") as audio_file:
            print("Sending to Whisper API for transcription...")
            whisper_transcription = client.audio.transcriptions.create(
              model="whisper-1", # or "gpt-4o-transcribe"
              file=audio_file
            )
        
        # --- 4. Compare results and calculate WER ---
        whisper_text = whisper_transcription.text
        print(f"Original Text : {original_transcription}")
        print(f"Whisper Text  : {whisper_text}")

        # Calculate Word Error Rate (WER). Lower is better.
        error = jiwer.wer(original_transcription, whisper_text)
        print(f"Word Error Rate (WER): {error:.2f}")

    except Exception as e:
        print(f"An error occurred with the API call: {e}")

    finally:
        # --- 5. Clean up the temporary file ---
        if os.path.exists(temp_audio_filename):
            os.remove(temp_audio_filename)
            print(f"Removed temporary file: {temp_audio_filename}")