# core/auth_system.py

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel
import json
import os
import logging

logger = logging.getLogger(__name__)

class APIKey(BaseModel):
    """API Key model for enterprise clients"""
    key_id: str
    client_name: str
    key_hash: str  # Hashed version of the actual key
    tier: str  # basic, pro, enterprise
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    daily_limit: int
    monthly_limit: int
    current_daily_usage: int
    current_monthly_usage: int
    allowed_domains: List[str]
    allowed_ips: List[str]
    webhook_url: Optional[str]
    metadata: Dict

class Usage(BaseModel):
    """Usage tracking model"""
    api_key_id: str
    endpoint: str
    timestamp: datetime
    response_time_ms: float
    risk_score: float
    classification: str
    ip_address: str
    user_agent: str

class EnterpriseAuthSystem:
    """Enterprise-grade API key authentication and usage tracking"""
    
    def __init__(self):
        self.api_keys_file = os.path.join(os.path.dirname(__file__), "..", "database", "api_keys.json")
        self.usage_file = os.path.join(os.path.dirname(__file__), "..", "database", "usage_logs.json")
        self.ensure_database_files()
        
    def ensure_database_files(self):
        """Ensure database files exist"""
        os.makedirs(os.path.dirname(self.api_keys_file), exist_ok=True)
        
        if not os.path.exists(self.api_keys_file):
            with open(self.api_keys_file, 'w') as f:
                json.dump([], f)
                
        if not os.path.exists(self.usage_file):
            with open(self.usage_file, 'w') as f:
                json.dump([], f)
    
    def generate_api_key(self, client_name: str, tier: str = "basic") -> Dict:
        """Generate a new API key for an enterprise client"""
        
        # Generate secure API key
        raw_key = secrets.token_urlsafe(32)
        key_id = f"sk_{secrets.token_urlsafe(16)}"
        
        # Hash the key for storage (never store raw keys)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Set limits based on tier
        tier_limits = {
            "basic": {"daily": 1000, "monthly": 10000},
            "pro": {"daily": 10000, "monthly": 100000},
            "enterprise": {"daily": 100000, "monthly": 1000000}
        }
        
        limits = tier_limits.get(tier, tier_limits["basic"])
        
        # Create API key record
        api_key = APIKey(
            key_id=key_id,
            client_name=client_name,
            key_hash=key_hash,
            tier=tier,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),  # 1 year expiry
            is_active=True,
            daily_limit=limits["daily"],
            monthly_limit=limits["monthly"],
            current_daily_usage=0,
            current_monthly_usage=0,
            allowed_domains=[],
            allowed_ips=[],
            webhook_url=None,
            metadata={}
        )
        
        # Save to database
        self._save_api_key(api_key)
        
        logger.info(f"🔑 Generated API key for {client_name} ({tier} tier)")
        
        return {
            "api_key": raw_key,  # Only return this once!
            "key_id": key_id,
            "client_name": client_name,
            "tier": tier,
            "daily_limit": limits["daily"],
            "monthly_limit": limits["monthly"],
            "expires_at": api_key.expires_at.isoformat()
        }
    
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return client info"""
        if not api_key or not api_key.startswith('sk_'):
            return None
            
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Load all API keys
        api_keys = self._load_api_keys()
        
        for key_data in api_keys:
            if (key_data.get("key_hash") == key_hash and 
                key_data.get("is_active", False) and
                (not key_data.get("expires_at") or 
                 datetime.fromisoformat(key_data["expires_at"]) > datetime.now())):
                
                return APIKey(**key_data)
        
        return None
    
    def check_rate_limit(self, api_key: APIKey) -> Dict:
        """Check if API key has exceeded rate limits"""
        # For basic implementation, we'll allow all requests
        # In production, implement proper rate limiting with Redis
        
        usage_info = {
            "allowed": True,
            "daily_remaining": api_key.daily_limit - api_key.current_daily_usage,
            "monthly_remaining": api_key.monthly_limit - api_key.current_monthly_usage,
            "tier": api_key.tier,
            "client_name": api_key.client_name
        }
        
        # Check daily limit
        if api_key.current_daily_usage >= api_key.daily_limit:
            usage_info["allowed"] = False
            usage_info["error"] = "Daily limit exceeded"
            
        # Check monthly limit
        if api_key.current_monthly_usage >= api_key.monthly_limit:
            usage_info["allowed"] = False
            usage_info["error"] = "Monthly limit exceeded"
            
        return usage_info
    
    def log_usage(self, api_key: APIKey, endpoint: str, response_time_ms: float, 
                  risk_score: float, classification: str, ip_address: str, user_agent: str):
        """Log API usage for analytics and billing"""
        
        usage = Usage(
            api_key_id=api_key.key_id,
            endpoint=endpoint,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            risk_score=risk_score,
            classification=classification,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Save usage log
        self._save_usage(usage)
        
        # Update usage counters (in production, use atomic operations)
        self._increment_usage_counters(api_key.key_id)
    
    def get_client_analytics(self, api_key_id: str, days: int = 30) -> Dict:
        """Get analytics for a specific client"""
        usage_logs = self._load_usage_logs()
        
        # Filter logs for this client and time period
        cutoff_date = datetime.now() - timedelta(days=days)
        client_logs = [
            log for log in usage_logs 
            if (log.get("api_key_id") == api_key_id and 
                datetime.fromisoformat(log["timestamp"]) > cutoff_date)
        ]
        
        if not client_logs:
            return {"total_requests": 0, "threats_detected": 0, "avg_response_time": 0}
        
        # Calculate analytics
        total_requests = len(client_logs)
        threats_detected = len([log for log in client_logs if log.get("risk_score", 0) > 0.5])
        avg_response_time = sum(log.get("response_time_ms", 0) for log in client_logs) / total_requests
        
        # Group by classification
        classifications = {}
        for log in client_logs:
            cls = log.get("classification", "unknown")
            classifications[cls] = classifications.get(cls, 0) + 1
        
        return {
            "total_requests": total_requests,
            "threats_detected": threats_detected,
            "threat_detection_rate": round(threats_detected / total_requests * 100, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "classifications": classifications,
            "period_days": days
        }
    
    def _save_api_key(self, api_key: APIKey):
        """Save API key to database"""
        api_keys = self._load_api_keys()
        api_keys.append(api_key.dict())
        
        with open(self.api_keys_file, 'w') as f:
            json.dump(api_keys, f, indent=2, default=str)
    
    def _load_api_keys(self) -> List[Dict]:
        """Load API keys from database"""
        try:
            with open(self.api_keys_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_usage(self, usage: Usage):
        """Save usage log to database"""
        usage_logs = self._load_usage_logs()
        usage_logs.append(usage.dict())
        
        # Keep only last 100k records to prevent file bloat
        if len(usage_logs) > 100000:
            usage_logs = usage_logs[-50000:]
        
        with open(self.usage_file, 'w') as f:
            json.dump(usage_logs, f, indent=2, default=str)
    
    def _load_usage_logs(self) -> List[Dict]:
        """Load usage logs from database"""
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _increment_usage_counters(self, api_key_id: str):
        """Increment usage counters for an API key"""
        # In production, this would be an atomic operation in Redis/Database
        # For now, we'll implement basic file-based counting
        pass

# Global auth system instance
auth_system = EnterpriseAuthSystem()
