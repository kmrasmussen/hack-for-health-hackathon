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
    """A structured medical case report on a given topic."""
    title: str = Field(description="A concise and fitting title for the case report.")
    patient_presentation: str = Field(description="A brief summary of the symptoms and complaints the patient presents with, in their own words or as observed initially.")
    ground_truth_diagnosis: str = Field(description="The definitive underlying medical diagnosis for the fictional patient's case.")
    single_doctor_sentence: str = Field(description="A single, standalone sentence a doctor might say that must include the topic.")
    example_doctor_report: str = Field(description="The main body of the report, written in realistic, professional prose as a doctor might write after a consultation. It should be well-structured and informative.")
    key_takeaways: List[str] = Field(description="A list of 3-5 bullet points summarizing the most critical information from the report.")

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
    You are a highly knowledgeable medical professional. Your task is to generate a fictional but realistic medical case file based on the topic: "{topic}".

    Create a complete, self-contained case. This involves inventing a patient, their symptoms, and the context of their visit.

    Please structure your response according to the provided JSON schema with the following fields:
    1.  `title`: A title for the case file.
    2.  `patient_presentation`: Describe what the patient says they are experiencing. Use layman's terms, as a real patient would.
    3.  `ground_truth_diagnosis`: State the definitive, correct medical diagnosis for the case you've invented.
    4.  `single_doctor_sentence`: A single, standalone sentence a doctor might say during a consultation that explicitly includes the topic "{topic}".
    5.  `example_doctor_report`: Write a sample report a doctor would create after the consultation. This report should be exactly four sentences, start with "The patient ...", and use professional medical terminology.
    6.  `key_takeaways`: A list of 3-5 bullet points summarizing the case.
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