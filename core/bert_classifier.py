import torch
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
from typing import Tuple, Dict
import logging

class BertScamClassifier:
    def __init__(self, model_path: str = "scambert-model-v2"):
        """Initialize BERT classifier with trained model"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.load_model()
        
    def load_model(self):
        """Load the trained BERT model and tokenizer"""
        try:
            self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            logging.info(f"✅ BERT model loaded from {self.model_path}")
        except Exception as e:
            logging.error(f"❌ Failed to load BERT model: {e}")
            # Fallback to pre-trained model
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            self.model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
            self.model.to(self.device)
            self.model.eval()
            
    def predict(self, text: str) -> Tuple[float, float]:
        """
        Predict scam probability for given text
        Returns: (scam_probability, confidence_score)
        """
        if not self.model or not self.tokenizer:
            return 0.5, 0.0
            
        # Tokenize input
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Extract scam probability (class 1) and confidence
        scam_prob = probabilities[0][1].item()
        confidence = torch.max(probabilities[0]).item()
        
        return scam_prob, confidence
