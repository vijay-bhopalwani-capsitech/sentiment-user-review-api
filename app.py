from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import List, Optional
import torch
import torch.nn.functional as F

app = FastAPI()

class SentimentInput(BaseModel):
    title: str
    description: str

class SentimentOutput(BaseModel):
    score: float
    label: str
    summary: str
    model: str
    keywords: List[str]
    isFlagged: bool
    flagReason: Optional[str]
    toxicity: dict
    spam: dict
    isShouldPublish: bool

# --- Sentiment ---
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)
sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)

LABEL_MAP = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE"
}

def generate_summary(label: str) -> str:
    return {
        "POSITIVE": "The user is satisfied and praises the product.",
        "NEUTRAL": "The user has a neutral opinion with no strong sentiment.",
        "NEGATIVE": "The user expresses dissatisfaction or criticism."
    }.get(label, "No summary available.")

def extract_keywords(text: str) -> List[str]:
    return ["performance", "design", "value"]

def check_flagged(text: str) -> bool:
    offensive_terms = ["hate", "terrible", "awful"]
    return any(term in text.lower() for term in offensive_terms)

# --- Toxicity ---
TOXICITY_MODEL = "unitary/toxic-bert"
toxicity_tokenizer = AutoTokenizer.from_pretrained(TOXICITY_MODEL)
toxicity_model = AutoModelForSequenceClassification.from_pretrained(TOXICITY_MODEL)

def predict_toxicity(text: str):
    inputs = toxicity_tokenizer(text, return_tensors="pt", truncation=True)
    outputs = toxicity_model(**inputs)
    probs = torch.sigmoid(outputs.logits).detach().numpy()[0]
    labels = list(toxicity_model.config.id2label.values())
    return dict(zip(labels, map(lambda x: round(float(x), 4), probs)))

# --- Spam ---
SPAM_MODEL = "mrm8488/bert-tiny-finetuned-sms-spam-detection"
spam_tokenizer = AutoTokenizer.from_pretrained(SPAM_MODEL)
spam_model = AutoModelForSequenceClassification.from_pretrained(SPAM_MODEL)

def predict_spam(text: str):
    inputs = spam_tokenizer(text, return_tensors="pt", truncation=True)
    outputs = spam_model(**inputs)
    probs = F.softmax(outputs.logits, dim=1).detach().numpy()[0]
    labels = ["ham", "spam"]
    return dict(zip(labels, map(lambda x: round(float(x), 4), probs)))

# --- Decision Logic for shouldPublish ---
def should_publish(toxicity: dict, spam: dict, sentiment_label: str, sentiment_score: float, is_flagged: bool) -> bool:
    if spam["spam"] > 0.5:
        return False
    if toxicity.get("toxic", 0) > 0.7:
        return False
    if toxicity.get("severe_toxic", 0) > 0.3:
        return False
    if toxicity.get("threat", 0) > 0.2:
        return False
    if toxicity.get("insult", 0) > 0.4:
        return False
    if toxicity.get("identity_hate", 0) > 0.2:
        return False
    if sentiment_label == "NEGATIVE" and sentiment_score > 0.95 and is_flagged:
        return False
    return True

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Sentiment + Toxicity + Spam API is running."}

@app.post("/analyze", response_model=SentimentOutput)
def analyze_review(data: SentimentInput):
    text = f"{data.title}. {data.description}"

    sentiment_result = sentiment_pipeline(text)[0]
    label = LABEL_MAP[sentiment_result["label"]]
    score = round(sentiment_result["score"], 4)

    keywords = extract_keywords(text)
    is_flagged = check_flagged(text)
    flag_reason = "Contains offensive language" if is_flagged else None
    toxicity_result = predict_toxicity(text)
    spam_result = predict_spam(text)
    publish_flag = should_publish(toxicity_result, spam_result, label, score, is_flagged)

    return {
        "score": score,
        "label": label.lower(),
        "summary": generate_summary(label),
        "model": SENTIMENT_MODEL,
        "keywords": keywords,
        "isFlagged": is_flagged,
        "flagReason": flag_reason,
        "toxicity": toxicity_result,
        "spam": spam_result,
        "isShouldPublish": publish_flag
    }
