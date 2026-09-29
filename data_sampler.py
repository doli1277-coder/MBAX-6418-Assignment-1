import gzip
import json
import random

# File paths - ensure you have the raw .jsonl.gz file in your directory
input_file = "Gift_Cards.jsonl.gz"
output_file = "balanced_reviews.json"

# Storage for our three classes
reviews = {
    "POSITIVE": [], # 4-5 stars
    "NEUTRAL": [],  # 3 stars
    "NEGATIVE": []  # 1-2 stars
}

print(f"Reading and mapping ratings from {input_file}...")

# Stream the gzipped file line by line
with gzip.open(input_file, 'rt', encoding='utf-8') as f:
    for line in f:
        review = json.loads(line)
        
        # Ensure the required fields exist before processing
        if 'rating' in review and 'title' in review and 'text' in review:
            rating = float(review['rating'])
            
            # Map the rating to the assigned class
            if rating >= 4.0:
                classification = "POSITIVE"
            elif rating == 3.0:
                classification = "NEUTRAL"
            else:
                classification = "NEGATIVE"
                
            # Store the relevant fields for classification
            processed_review = {
                "title": review['title'],
                "text": review['text'],
                "rating": rating, # Kept strictly for final scoring, not for the LLM
                "true_class": classification
            }
            
            reviews[classification].append(processed_review)

print("Sampling 50 reviews per class...")

# Use a fixed random seed so the same 150 reviews are chosen every time
random.seed(42)

balanced_sample = []
for category in ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
    # Check if we have enough reviews in the category
    if len(reviews[category]) >= 50:
        sampled = random.sample(reviews[category], 50)
        balanced_sample.extend(sampled)
    else:
        print(f"Warning: Only found {len(reviews[category])} reviews for {category}")
        balanced_sample.extend(reviews[category])

# Save the balanced batch to a standard JSON file
with open(output_file, 'w', encoding='utf-8') as out:
    json.dump(balanced_sample, out, indent=4)

print(f"Successfully saved {len(balanced_sample)} balanced reviews to {output_file}.")