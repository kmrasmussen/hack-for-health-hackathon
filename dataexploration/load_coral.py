from datasets import load_dataset

# Load the Coral dataset
# Change "read_aloud" to "conversational" to get the conversational dataset
# By specifying the split, you only download the validation data
coral_val = load_dataset("CoRal-project/coral-v2", "read_aloud", split="validation")

# Example: Accessing an audio sample and its transcription
# The returned object is the dataset itself, not a dictionary of splits
sample = coral_val[0]
audio = sample['audio']
transcription = sample['text']

print(f"Audio: {audio['array']}")
print(f"Text: {transcription}")