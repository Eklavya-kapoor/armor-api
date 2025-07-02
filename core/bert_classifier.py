import os
import torch
import logging
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from typing import Tuple

class BertScamClassifier:
    def __init__(self, model_path: str = "elephasai/elephas"):
        """
        Initialize BERT classifier using Hugging Face-hosted model.
        Set HF_TOKEN in your .env or Render environment.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.hf_token = os.getenv("HF_TOKEN")
        self.load_model()

    def load_model(self):
        """Load the tokenizer and model from Hugging Face"""
        try:
            self.tokenizer = BertTokenizer.from_pretrained(
                self.model_path, use_auth_token=self.hf_token
            )
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_path, use_auth_token=self.hf_token
            )
            self.model.to(self.device)
            self.model.eval()
            logging.info(f"✅ BERT model loaded from {self.model_path}")
        except Exception as e:
            logging.error(f"❌ Failed to load BERT model: {e}")
            # Optional fallback (can remove in production)
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            self.model = BertForSequenceClassification.from_pretrained(
                "bert-base-uncased", num_labels=2
            )
            self.model.to(self.device)
            self.model.eval()

    def predict(self, text: str) -> Tuple[float, float]:
        """
        Predict scam probability for given text
        Returns: (scam_probability, confidence_score)
        """
        if not self.model or not self.tokenizer:
            return 0.5, 0.0

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        scam_prob = probabilities[0][1].item()  # class 1 = scam
        confidence = torch.max(probabilities[0]).item()

        return scam_prob, confidence