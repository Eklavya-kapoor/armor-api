# api/enterprise_routes.py

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import time
import logging

from core.auth_system import auth_system, APIKey

logger = logging.getLogger(__name__)

# Enterprise API router
enterprise_router = APIRouter(prefix="/enterprise", tags=["Enterprise"])

# Security scheme
security = HTTPBearer()

class CreateAPIKeyRequest(BaseModel):
    client_name: str
    tier: str = "basic"  # basic, pro, enterprise
    contact_email: Optional[str] = None
    company_domain: Optional[str] = None

class APIKeyResponse(BaseModel):
    api_key: str
    key_id: str
    client_name: str
    tier: str
    daily_limit: int
    monthly_limit: int
    expires_at: str
    setup_instructions: Dict

class AuthenticatedRequest(BaseModel):
    """Base class for requests that require API key authentication"""
    pass

# Dependency to verify API key
async def verify_api_key(authorization: HTTPAuthorizationCredentials = Depends(security)) -> APIKey:
    """Verify API key from Authorization header"""
    if not authorization or not authorization.credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    api_key = auth_system.validate_api_key(authorization.credentials)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limits
    rate_limit_info = auth_system.check_rate_limit(api_key)
    if not rate_limit_info["allowed"]:
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded: {rate_limit_info.get('error', 'Unknown error')}"
        )
    
    return api_key

# Admin dependency (for now, just check if it's a specific admin key)
async def verify_admin_access(authorization: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify admin access for API key generation"""
    admin_key = "sk_admin_elephas_2024_secure_key_change_in_production"
    
    if not authorization or authorization.credentials != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return True

@enterprise_router.post("/create-api-key", response_model=APIKeyResponse)
async def create_enterprise_api_key(
    request: CreateAPIKeyRequest,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Create a new API key for an enterprise client (Admin only)"""
    
    try:
        # Generate API key
        key_info = auth_system.generate_api_key(
            client_name=request.client_name,
            tier=request.tier
        )
        
        # Create setup instructions
        setup_instructions = {
            "curl_example": f"""curl -X POST https://elephas-ai-api.onrender.com/scan \\
  -H "Authorization: Bearer {key_info['api_key']}" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "URGENT! Verify your account now!", "sender": "test@example.com"}}'""",
            
            "javascript_example": f"""const response = await fetch('https://elephas-ai-api.onrender.com/scan', {{
  method: 'POST',
  headers: {{
    'Authorization': 'Bearer {key_info['api_key']}',
    'Content-Type': 'application/json'
  }},
  body: JSON.stringify({{
    text: 'URGENT! Verify your account now!',
    sender: 'test@example.com'
  }})
}});""",
            
            "python_example": f"""import requests

response = requests.post(
    'https://elephas-ai-api.onrender.com/scan',
    headers={{'Authorization': 'Bearer {key_info['api_key']}'}},
    json={{'text': 'URGENT! Verify your account now!', 'sender': 'test@example.com'}}
)""",
            
            "dashboard_url": f"https://elephas-ai-api.onrender.com/dashboard/{key_info['key_id']}",
            "api_documentation": "https://elephas-ai-api.onrender.com/docs"
        }
        
        logger.info(f"✅ Created API key for {request.client_name} ({request.tier} tier)")
        
        return APIKeyResponse(
            api_key=key_info['api_key'],
            key_id=key_info['key_id'],
            client_name=key_info['client_name'],
            tier=key_info['tier'],
            daily_limit=key_info['daily_limit'],
            monthly_limit=key_info['monthly_limit'],
            expires_at=key_info['expires_at'],
            setup_instructions=setup_instructions
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@enterprise_router.get("/usage-analytics")
async def get_usage_analytics(
    days: int = 30,
    api_key: APIKey = Depends(verify_api_key)
):
    """Get usage analytics for the authenticated client"""
    
    try:
        analytics = auth_system.get_client_analytics(api_key.key_id, days)
        
        # Add current API key info
        rate_limit_info = auth_system.check_rate_limit(api_key)
        
        return {
            "client_info": {
                "client_name": api_key.client_name,
                "tier": api_key.tier,
                "key_id": api_key.key_id,
                "created_at": api_key.created_at.isoformat(),
                "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
            },
            "usage_limits": {
                "daily_limit": api_key.daily_limit,
                "monthly_limit": api_key.monthly_limit,
                "daily_remaining": rate_limit_info["daily_remaining"],
                "monthly_remaining": rate_limit_info["monthly_remaining"]
            },
            "analytics": analytics,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@enterprise_router.get("/dashboard-data")
async def get_dashboard_data(
    api_key: APIKey = Depends(verify_api_key)
):
    """Get dashboard data for the authenticated client"""
    
    try:
        # Get analytics for different periods
        daily_analytics = auth_system.get_client_analytics(api_key.key_id, 1)
        weekly_analytics = auth_system.get_client_analytics(api_key.key_id, 7)
        monthly_analytics = auth_system.get_client_analytics(api_key.key_id, 30)
        
        # Calculate trends
        daily_threats = daily_analytics.get("threats_detected", 0)
        weekly_threats = weekly_analytics.get("threats_detected", 0)
        monthly_threats = monthly_analytics.get("threats_detected", 0)
        
        return {
            "client_name": api_key.client_name,
            "tier": api_key.tier,
            "summary": {
                "threats_blocked_today": daily_threats,
                "threats_blocked_this_week": weekly_threats,
                "threats_blocked_this_month": monthly_threats,
                "total_api_calls_today": daily_analytics.get("total_requests", 0),
                "avg_response_time": monthly_analytics.get("avg_response_time_ms", 0)
            },
            "charts": {
                "threat_types": monthly_analytics.get("classifications", {}),
                "detection_rate": monthly_analytics.get("threat_detection_rate", 0)
            },
            "usage": {
                "daily_limit": api_key.daily_limit,
                "monthly_limit": api_key.monthly_limit,
                "daily_used": api_key.current_daily_usage,
                "monthly_used": api_key.current_monthly_usage
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@enterprise_router.get("/health")
async def enterprise_health():
    """Health check for enterprise endpoints"""
    return {
        "status": "healthy",
        "service": "Elephas AI Enterprise API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "API Key Authentication",
            "Usage Analytics",
            "Rate Limiting",
            "Enterprise Dashboard",
            "Multi-tenant Support"
        ]
    }
