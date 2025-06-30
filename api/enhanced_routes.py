from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
from core.bert_classifier import BertScamClassifier
from core.advanced_features import AdvancedScamFeatureExtractor
from core.enhanced_scorer import EnhancedScamRiskScorer

class ScanRequest(BaseModel):
    text: str
    sender: Optional[str] = ""
    metadata: Optional[Dict] = {}

router = APIRouter()
bert_classifier = BertScamClassifier()
feature_extractor = AdvancedScamFeatureExtractor()
risk_scorer = EnhancedScamRiskScorer(bert_classifier)

@router.post("/scan")
async def scan_message(body: ScanRequest):
    try:
        message = body.text
        sender = body.sender
        metadata = body.metadata

        if not message or len(message.strip()) < 3:
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

app = FastAPI(
    title="ScamShield AI",
    description="API for real-time scam detection and risk analysis",
    version="1.0.0"
)

app.include_router(router)