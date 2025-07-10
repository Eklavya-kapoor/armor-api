import os
import torch
import logging
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from typing import Tuple

class BertScamClassifier:
    def __init__(self, model_path: str = None):
        """
        Initialize BERT classifier using a public Hugging Face model.
        Optimized for Render free tier (512MB RAM limit).
        No authentication required for public model.
        """
        self.device = torch.device("cpu")  # CPU only for memory efficiency
        self.model_path = model_path or os.getenv("MODEL_PATH", "elephasai/elephas")
        self.model = None
        self.tokenizer = None
        print(f"🌍 Initializing BERT classifier for public model: {self.model_path}")
        print(f"💾 Memory optimization enabled for free tier")
        self.load_model()

    def load_model(self):
        """Load tokenizer and model from Hugging Face (public model, no token)"""
        try:
            print(f"📦 Loading tokenizer from {self.model_path}...")
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            os.environ["OMP_NUM_THREADS"] = "1"
            self.tokenizer = BertTokenizer.from_pretrained(
                self.model_path,
                cache_dir="/tmp/transformers_cache",
                local_files_only=False
            )
            print(f"🧠 Loading model from {self.model_path} (memory optimized)...")
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_path,
                cache_dir="/tmp/transformers_cache",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                device_map="auto",
                local_files_only=False
            )
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ BERT model loaded successfully from {self.model_path}")
            print(f"💾 Running on {self.device} with memory optimizations")
        except Exception as e:
            print(f"❌ Failed to load public model: {e}")
            print("🔄 Falling back to basic BERT model...")
            self._load_fallback_model()

    def _load_fallback_model(self):
        """Load a basic public model as fallback if main model fails"""
        fallback_model = "bert-base-uncased"
        try:
            print(f"📦 Loading fallback tokenizer: {fallback_model}")
            self.tokenizer = BertTokenizer.from_pretrained(
                fallback_model,
                cache_dir="/tmp/transformers_cache",
                local_files_only=False
            )
            print(f"🧠 Loading fallback model: {fallback_model}")
            self.model = BertForSequenceClassification.from_pretrained(
                fallback_model,
                num_labels=2,
                cache_dir="/tmp/transformers_cache",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                local_files_only=False
            )
            self.model.to(self.device)
            self.model.eval()
            print("✅ Basic BERT model loaded as fallback")
        except Exception as e:
            print(f"❌ Even fallback model failed: {e}")
            raise Exception("All fallback models failed to load")

    def predict(self, text: str) -> Tuple[float, float]:
        """
        Predict scam probability for a given text.
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