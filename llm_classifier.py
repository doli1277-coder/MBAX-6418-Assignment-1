import json
import requests

API_BASE = "http://dobolyi.com:9001/v1/chat/completions"
API_KEY = "6418"
MODEL_NAME = "cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit"

# Updated paths to match your folder name exactly
input_file = "balanced_reviews.json"
output_file = "classified_reviews.json"

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
except FileNotFoundError:
    print(f"Error: {input_file} not found. Run data_sampler.py first.")
    exit()

classified_data = []
print(f"Starting classification of {len(reviews)} reviews...")

for i, review in enumerate(reviews):
    title = review.get("title", "")
    text = review.get("text", "")
    
    prompt = f"""You are a helpful review analysis assistant.
Analyze the following review title and text. Provide two things:
1. The Sentiment: strictly classify as POSITIVE, NEUTRAL, or NEGATIVE.
2. The Primary Emotion: strictly pick ONE from the following list (anger, anticipation, disgust, fear, joy, sadness, surprise, trust).

Review Title: {title}
Review Text: {text}

Provide your response in exact JSON format like this, with no extra text:
{{"sentiment": "POSITIVE", "emotion": "joy"}}
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a precise JSON-outputting review classifier."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0 
    }

    try:
        response = requests.post(API_BASE, headers=headers, json=payload, timeout=30)
        response_json = response.json()
        
        model_output = response_json['choices'][0]['message']['content']
        cleaned_output = model_output.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(cleaned_output)
        
        review["predicted_sentiment"] = result_dict.get("sentiment", "UNKNOWN").upper()
        review["llm_emotion"] = result_dict.get("emotion", "UNKNOWN").lower()
        
    except Exception as e:
        print(f"Error on review {i+1}: {e}")
        review["predicted_sentiment"] = "ERROR"
        review["llm_emotion"] = "ERROR"
        
    classified_data.append(review)
    print(f"Processed {i+1}/{len(reviews)}: True={review['true_class']}, Pred={review.get('predicted_sentiment')}")

with open(output_file, 'w', encoding='utf-8') as out:
    json.dump(classified_data, out, indent=4)

print(f"Classification complete! Results saved to {output_file}.")