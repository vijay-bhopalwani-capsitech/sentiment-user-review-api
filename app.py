from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import List, Optional

# Model config
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
LABEL_MAP = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE"
}

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# FastAPI app
app = FastAPI()

# Input schema
class SentimentInput(BaseModel):
    title: str
    description: str

# Output schema (updated)
class SentimentOutput(BaseModel):
    score: float
    label: str
    summary: str
    model: str
    keywords: List[str]
    isFlagged: bool
    flagReason: Optional[str] = None

# Helper function to generate a summary based on sentiment
def generate_summary(label: str) -> str:
    summaries = {
        "POSITIVE": "The user is satisfied and praises the product.",
        "NEUTRAL": "The user has a neutral opinion with no strong sentiment.",
        "NEGATIVE": "The user expresses dissatisfaction or criticism."
    }
    return summaries.get(label, "No summary available.")

# Helper function to extract keywords (mock implementation)
def extract_keywords(text: str) -> List[str]:
    # Replace with actual NLP keyword extraction (e.g., RAKE, YAKE, Spacy)
    mock_keywords = ["performance", "design", "value"]  # Placeholder
    return mock_keywords

# Helper function to check if the review should be flagged
def check_flagged(text: str) -> bool:
    # Replace with actual moderation logic (e.g., profanity filter)
    offensive_terms = ["hate", "terrible", "awful"]  # Placeholder
    return any(term in text.lower() for term in offensive_terms)

@app.get("/")
def read_root():
    return {"message": "3-Class Sentiment API is running."}

@app.post("/analyze", response_model=SentimentOutput)
def analyze_sentiment(data: SentimentInput):
    text = f"{data.title}. {data.description}"
    result = classifier(text)[0]

    # Map label
    label = LABEL_MAP[result["label"]]
    score = round(result["score"], 4)

    # Generate additional fields
    summary = generate_summary(label)
    keywords = extract_keywords(text)
    isFlagged = check_flagged(text)
    flagReason = "Contains offensive language" if isFlagged else None

    return {
        "score": score,
        "label": label.lower(),  # "positive" instead of "POSITIVE"
        "summary": summary,
        "model": "cardiffnlp/twitter-roberta-base-sentiment",
        "keywords": keywords,
        "isFlagged": isFlagged,
        "flagReason": flagReason
    }