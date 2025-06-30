
# scamshield/config.py
import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Model settings
    BERT_MODEL_PATH = os.getenv("BERT_MODEL_PATH", "scambert-model-v2")
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "512"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security settings
    SCAM_THRESHOLD = float(os.getenv("SCAM_THRESHOLD", "0.5"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Feature extraction settings
    ENABLE_URL_ANALYSIS = os.getenv("ENABLE_URL_ANALYSIS", "True").lower() == "true"
    ENABLE_SENDER_ANALYSIS = os.getenv("ENABLE_SENDER_ANALYSIS", "True").lower() == "true"
    
    @classmethod
    def get_feature_weights(cls) -> Dict[str, float]:
        """Get configurable feature weights"""
        return {
            "bert_weight": float(os.getenv("BERT_WEIGHT", "0.7")),
            "rule_weight": float(os.getenv("RULE_WEIGHT", "0.3")),
        }
