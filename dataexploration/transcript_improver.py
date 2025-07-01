import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- 1. Setup OpenAI Client ---
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    # In a real app, you'd want more robust error handling
    client = None

# --- 2. Define the desired JSON output structure using Pydantic ---
class Sentence(BaseModel):
    """A single sentence from the final transcript."""
    #reasoning: str = Field(description="Discuss shortly which of the sentences make more sense, and use context etc and think also about medical stuff.")
    text: str = Field(description="The corrected and finalized sentence.")
    is_uncertain: bool = Field(description="Set to true if the model is uncertain about the accuracy of this sentence, for example if the two source transcripts disagree significantly.")
    has_medical_terminology: bool = Field(description="Set to true if the sentence contains specialist medical terminology, and false if just usual conversation that everyone understands.")
    specific_uncertain_word: List[str] = Field(description="If uncertain in general, list specific words you are especially uncertain about and make them be verbatim exact matches to the words you used in the text field.")

class ImprovedTranscript(BaseModel):
    """The final, improved transcript composed of a list of sentences."""
    sentences: List[Sentence]

# --- 3. Create the function to call the chat model ---
def improve_transcript_with_gpt(whisper_text: str, corti_text: str) -> ImprovedTranscript | None:
    """
    Uses a chat model to combine two transcripts into a single, improved, structured transcript.
    """
    if not client:
        print("OpenAI client not initialized.")
        return None

    print("\nAsking OpenAI to improve and combine transcripts...")

    # This prompt guides the model to perform the specific task
    system_prompt = """
    You are an expert assistant tasked with creating a single, high-quality transcript from two different sources.
    Your goal is to produce the most accurate and coherent final version.
    - Analyze both the Whisper transcript and the Corti transcript.
    - Where they agree, use that text.
    - Where they disagree, use your best judgment to determine the most likely correct phrasing.
    - If you are still uncertain about a sentence because of a significant disagreement, mark it as uncertain.
    - Combine the results into a single, logical transcript.
    - The final output must be structured as a list of sentences.
    """

    user_prompt = f"""
    Here are the two transcripts to analyze:

    <whisper_transcript>
    {whisper_text}
    </whisper_transcript>

    <corti_transcript>
    {corti_text}
    </corti_transcript>

    Please generate the improved, structured transcript now.
    """

    try:
        response = client.responses.parse(
            model="o4-mini", # Or another capable model like gpt-4-turbo
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=ImprovedTranscript # This enforces the Pydantic schema
        )
        print("Successfully generated improved transcript.")
        print('response', response)
        return response.output_parsed
        #return response
    except Exception as e:
        print(f"An error occurred while improving the transcript: {e}")
        return None