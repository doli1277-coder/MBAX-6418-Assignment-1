import json
import re
import zipfile
from collections import defaultdict

# Absolute paths based on your folder structure
input_file = "classified_reviews.json"
output_file = "final_reviews.json"
zip_path = "NRC-Emotion-Lexicon.zip"

print("Loading NRC Lexicon directly from ZIP...")
nrc_dict = defaultdict(list)
valid_emotions = {'anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust'}

try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Search the zip archive for the main word-level text file
        target_filename = None
        for name in z.namelist():
            if 'Wordlevel' in name and name.endswith('.txt'):
                target_filename = name
                break
        
        if not target_filename:
            print("Error: Could not find the expected word-level .txt file inside the ZIP.")
            exit()
            
        print(f"Found lexicon file inside zip: {target_filename}")
        
        # Read and parse the lexicon
        with z.open(target_filename) as f:
            for line in f:
                # Decode bytes to string
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) == 3:
                    word, emotion, is_associated = parts
                    # We only track the 8 primary emotions if they are associated (1)
                    if is_associated == '1' and emotion in valid_emotions:
                        nrc_dict[word].append(emotion)
except FileNotFoundError:
    print(f"Error: Could not find {zip_path}. Check the file name and location.")
    exit()

print("Loading classified reviews...")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
except FileNotFoundError:
    print(f"Error: {input_file} not found. Ensure llm_classifier.py finished successfully.")
    exit()

print("Scoring reviews against NRC Lexicon...")
for review in reviews:
    text = review.get("text", "").lower()
    
    # Extract just the words (stripping punctuation) using regex
    words = re.findall(r'\b\w+\b', text)
    
    # Initialize scores to 0 for all 8 emotions
    emotion_scores = {e: 0 for e in valid_emotions}
    
    # Tally up the emotion hits based on the lexicon
    for word in words:
        if word in nrc_dict:
            for emotion in nrc_dict[word]:
                emotion_scores[emotion] += 1
                
    # Take the highest scoring emotion as the answer
    if sum(emotion_scores.values()) == 0:
        primary_emotion = "none" # If no words matched the lexicon
    else:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
    review["nrc_emotion"] = primary_emotion

# Save the final dataset
with open(output_file, 'w', encoding='utf-8') as out:
    json.dump(reviews, out, indent=4)

print(f"Success! Final dataset with LLM and NRC emotions saved to {output_file}.")
