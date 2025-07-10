"""
Optimized BERT model loader specifically designed for private models on constrained environments
This loader uses aggressive memory optimization and error recovery
"""

import os
import torch
import logging
import gc
import time
from transformers import BertTokenizer, BertForSequenceClassification
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class OptimizedPrivateBertLoader:
    """Ultra-optimized loader for private BERT models on memory-constrained environments"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.device = torch.device("cpu")  # Force CPU for memory efficiency
        
        # Aggressive memory settings
        os.environ.update({
            "TOKENIZERS_PARALLELISM": "false",
            "OMP_NUM_THREADS": "1", 
            "MKL_NUM_THREADS": "1",
            "TORCH_NUM_THREADS": "1",
            "PYTORCH_TRANSFORMERS_CACHE": "/tmp/transformers_cache",
            "HF_HOME": "/tmp/huggingface",
            "TRANSFORMERS_OFFLINE": "0"
        })
        
        # Clear any existing cache
        self._clear_cache()
    
    def _clear_cache(self):
        """Aggressively clear caches and free memory"""
        try:
            import shutil
            cache_dirs = ["/tmp/transformers_cache", "/tmp/huggingface", "/tmp/torch"]
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir, ignore_errors=True)
                os.makedirs(cache_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"Cache clearing failed: {e}")
        
        # Force garbage collection
        gc.collect()
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def load_model_with_retries(self, max_retries: int = 3) -> Tuple[Optional[BertTokenizer], Optional[BertForSequenceClassification]]:
        """Load model with multiple retry strategies"""
        
        strategies = [
            self._load_strategy_minimal,
            self._load_strategy_reduced_precision,
            self._load_strategy_cpu_offload
        ]
        
        for attempt in range(max_retries):
            for i, strategy in enumerate(strategies):
                logger.info(f"🔄 Attempt {attempt + 1}, Strategy {i + 1}: {strategy.__name__}")
                try:
                    self._clear_cache()  # Clear cache before each attempt
                    tokenizer, model = strategy()
                    if tokenizer and model:
                        logger.info(f"✅ Model loaded successfully with {strategy.__name__}")
                        return tokenizer, model
                except Exception as e:
                    logger.warning(f"❌ Strategy {i + 1} failed: {e}")
                    self._clear_cache()
                    time.sleep(2)  # Brief pause between attempts
        
        logger.error("❌ All loading strategies failed")
        return None, None
    
    def _load_strategy_minimal(self) -> Tuple[BertTokenizer, BertForSequenceClassification]:
        """Strategy 1: Minimal memory footprint"""
        logger.info("📦 Loading with minimal memory strategy...")
        
        # Load tokenizer first (smaller memory footprint)
        tokenizer = BertTokenizer.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache",
            local_files_only=False,
            force_download=False,
            resume_download=True
        )
        
        # Force garbage collection after tokenizer
        gc.collect()
        
        # Load model with aggressive memory optimization
        model = BertForSequenceClassification.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache",
            torch_dtype=torch.float16,  # Half precision
            low_cpu_mem_usage=True,
            device_map="cpu",
            local_files_only=False,
            force_download=False,
            resume_download=True,
            use_safetensors=True,
            trust_remote_code=False
        )
        
        model.to(self.device)
        model.eval()
        
        # Final memory cleanup
        gc.collect()
        
        return tokenizer, model
    
    def _load_strategy_reduced_precision(self) -> Tuple[BertTokenizer, BertForSequenceClassification]:
        """Strategy 2: Ultra-reduced precision for memory saving"""
        logger.info("📦 Loading with reduced precision strategy...")
        
        tokenizer = BertTokenizer.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache",
            model_max_length=128  # Reduce max length
        )
        
        gc.collect()
        
        # Try to load with even more aggressive settings
        model = BertForSequenceClassification.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="cpu",
            use_safetensors=True,
            attn_implementation="eager"  # Use eager attention (more memory efficient)
        )
        
        # Quantize to int8 for even more memory savings
        try:
            import torch.quantization
            model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear}, dtype=torch.qint8
            )
        except Exception:
            pass  # Quantization not available, continue without it
        
        model.to(self.device)
        model.eval()
        gc.collect()
        
        return tokenizer, model
    
    def _load_strategy_cpu_offload(self) -> Tuple[BertTokenizer, BertForSequenceClassification]:
        """Strategy 3: CPU offloading with disk caching"""
        logger.info("📦 Loading with CPU offload strategy...")
        
        tokenizer = BertTokenizer.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache"
        )
        
        # Load with disk offloading
        model = BertForSequenceClassification.from_pretrained(
            self.model_path,
            cache_dir="/tmp/transformers_cache",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto",
            offload_folder="/tmp/offload",
            offload_state_dict=True
        )
        
        model.eval()
        gc.collect()
        
        return tokenizer, model

def load_optimized_private_model(model_path: str) -> Tuple[Optional[BertTokenizer], Optional[BertForSequenceClassification]]:
    """
    Main function to load a private BERT model with maximum optimization
    Returns (tokenizer, model) or (None, None) if failed
    """
    logger.info(f"🚀 Starting optimized loading for private model: {model_path}")
    
    loader = OptimizedPrivateBertLoader(model_path)
    tokenizer, model = loader.load_model_with_retries(max_retries=2)
    
    if tokenizer and model:
        logger.info("✅ Optimized private model loading successful!")
        return tokenizer, model
    else:
        logger.error("❌ Optimized private model loading failed")
        return None, None
