import os
import torch
import logging
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
from typing import Tuple

class BertScamClassifier:
    def __init__(self, model_path: str = None):
        """
        Initialize BERT classifier using a private Hugging Face-hosted model.
        Optimized for Render free tier (512MB RAM limit).
        Requires HF_TOKEN as environment variable.
        """
        # Memory optimization: Force CPU usage for free tier
        self.device = torch.device("cpu")  # CPU only for memory efficiency
        self.model_path = model_path or os.getenv("MODEL_PATH", "elephasai/elephas")
        self.hf_token = os.getenv("HF_TOKEN")  # ✅ Ensure it's set in Render
        self.model = None
        self.tokenizer = None
        
        print(f"🔐 Initializing BERT classifier for private model: {self.model_path}")
        print(f"💾 Memory optimization enabled for free tier")
        
        self.load_model()

    def load_model(self):
        """Load tokenizer and model from Hugging Face using auth token with memory optimization"""
        try:
            print(f"📦 Loading tokenizer from {self.model_path}...")
            self.tokenizer = BertTokenizer.from_pretrained(
                self.model_path,
                token=self.hf_token,  # ✅ Use new token arg
                cache_dir="/tmp/transformers_cache"  # Use temp directory
            )
            
            print(f"🧠 Loading model from {self.model_path} (memory optimized)...")
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_path,
                token=self.hf_token,
                cache_dir="/tmp/transformers_cache",
                torch_dtype=torch.float16,  # Half precision (50% memory reduction)
                low_cpu_mem_usage=True,     # Enable memory optimization
                device_map="auto"           # Automatic device placement
            )
            
            # Move to CPU and set eval mode for memory efficiency
            self.model.to(self.device)
            self.model.eval()
            
            # Force garbage collection to free memory
            import gc
            gc.collect()
            
            print(f"✅ BERT model loaded successfully from {self.model_path}")
            print(f"💾 Running on {self.device} with memory optimizations")
            
        except Exception as e:
            print(f"❌ Failed to load private model: {e}")
            print("🔄 Falling back to public model...")
            
            # Fallback to public model if private fails
            self.tokenizer = BertTokenizer.from_pretrained(
                "bert-base-uncased",
                cache_dir="/tmp/transformers_cache"
            )
            self.model = BertForSequenceClassification.from_pretrained(
                "bert-base-uncased", 
                num_labels=2,
                cache_dir="/tmp/transformers_cache",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            self.model.to(self.device)
            self.model.eval()
            print("✅ Fallback model loaded successfully")

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