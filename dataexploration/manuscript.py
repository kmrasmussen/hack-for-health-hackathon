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
    client = None

# --- 2. Define the desired JSON output structure using Pydantic ---
class Manuscript(BaseModel):
    """A structured medical manuscript on a given topic."""
    title: str = Field(description="A concise and fitting title for the manuscript.")
    prose: str = Field(description="The main body of the manuscript, written in realistic, professional prose as a doctor might explain the topic. It should be well-structured and informative.")
    key_takeaways: List[str] = Field(description="A list of 3-5 bullet points summarizing the most critical information from the prose.")

# --- 3. Create the function to call the chat model ---
def generate_manuscript(topic: str) -> Manuscript | None:
    """
    Uses a chat model to generate a structured medical manuscript about a topic.
    """
    if not client:
        print("OpenAI client not initialized.")
        return None

    print(f"\nAsking OpenAI to generate a manuscript on: {topic}...")

    system_prompt = f"""
    You are a highly knowledgeable medical professional and a skilled writer. Your task is to generate a clear, concise, and informative manuscript on the given topic: "{topic}".

    The manuscript should be written in realistic prose, as if a doctor were explaining the concept to a colleague or a medical student. It must be accurate and professionally toned.

    The text should be written as if you are a doctor that has just had a consultation and is using a lot of prose. The goal is that we cover a lot of vocabulary in its right context, a lot of medical terms.
    Make it more like a description of a concrete case, it is fine to imagine what the patients etc presented of symptoms etc, more than an encyclopedic article.

    Make the manuscript exactly four sentences and start the first sentence with "The patient ...".
    
    Please structure your response according to the provided JSON schema, including a title, the main prose, and a list of key takeaways.
    """

    try:
        response = client.responses.parse(
            model="gpt-4o",
            input=[
                {"role": "system", "content": system_prompt},
            ],
            text_format=Manuscript
        )
        print("Successfully generated manuscript.")
        return response.output_parsed
    except Exception as e:
        print(f"An error occurred while generating the manuscript: {e}")
        return None