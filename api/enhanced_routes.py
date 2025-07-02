# api/enhanced_routes.py

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import os

from core.bert_classifier import BertScamClassifier
from core.advanced_features import AdvancedScamFeatureExtractor
from core.enhanced_scorer import EnhancedScamRiskScorer

# 🔐 Load environment variables if not done already
from dotenv import load_dotenv
load_dotenv()

# 🧠 Input schema
class ScanRequest(BaseModel):
    text: str
    sender: Optional[str] = ""
    metadata: Optional[Dict] = {}

# 🔧 Initialize FastAPI
app = FastAPI(
    title="ElephasAI - Scam Detection API",
    description="Enterprise-grade API to detect scams in messages, emails, links, and live input using AI.",
    version="1.0.0"
)

# ✅ Health check for Render
@app.get("/health")
def health():
    return {"status": "ok"}

# 📦 Core pipeline components
router = APIRouter()
bert_classifier = BertScamClassifier(model_path=os.getenv("HF_MODEL_NAME", "elephasai/elephas"))
feature_extractor = AdvancedScamFeatureExtractor()
risk_scorer = EnhancedScamRiskScorer(bert_classifier)

# 🧠 POST endpoint for scam detection
@router.post("/scan")
async def scan_message(body: ScanRequest):
    try:
        message = body.text.strip()
        sender = body.sender
        metadata = body.metadata or {}

        if len(message) < 3:
            return {
                "error": "Message too short to analyze.",
                "risk_score": 0.0,
                "risk_level": "low",
                "explanation": "Not enough information"
            }

        features = feature_extractor.extract(message, sender, metadata)
        risk_score, explanation, details = risk_scorer.score(
            text=message,
            features=features,
            sender=sender
        )

        return {
            "text": message,
            "sender": sender,
            "risk_score": risk_score,
            "risk_level": details.get("risk_level", "unknown"),
            "explanation": explanation,
            "confidence": details.get("bert_confidence", 0.0),
            "details": details,
            "features": features
        }

    except Exception as e:
        return {
            "error": str(e),
            "risk_score": 0.0,
            "explanation": "Failed to analyze message"
        }

# 🔁 Mount routes
app.include_router(router)