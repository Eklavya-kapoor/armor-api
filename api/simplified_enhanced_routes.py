# api/simplified_enhanced_routes.py
# Simplified version without database dependencies for testing

from fastapi import APIRouter, FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import time
import random
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔐 Load environment variables if not done already
from dotenv import load_dotenv
load_dotenv()

# 🧠 Input schema
class ScanRequest(BaseModel):
    text: str
    sender: Optional[str] = ""
    metadata: Optional[Dict] = {}

# 📊 Dashboard Statistics Model
class DashboardStats(BaseModel):
    threats_blocked: int
    scans_processed: int
    accuracy_rate: float
    avg_response_time: int
    uptime: str
    last_updated: str

# 🎯 Activity Model
class ActivityItem(BaseModel):
    type: str
    message: str
    timestamp: int
    severity: str

# 🌍 Threat Data Model
class ThreatData(BaseModel):
    timeline: List[int]
    categories: List[Dict]
    geographic_data: List[Dict]

# 🔧 Initialize FastAPI
app = FastAPI(
    title="Elephas AI - Enterprise Security API",
    description="Enterprise-grade API to detect scams in messages, emails, links, and live input using AI.",
    version="2.0.0"
)

# Add CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🏠 Serve dashboard static files
dashboard_path = os.path.join(os.path.dirname(__file__), "..", "..", "elephas-ai-sdk", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path), name="dashboard")

# 📱 Dashboard route
@app.get("/")
async def dashboard():
    dashboard_file = os.path.join(dashboard_path, "index.html")
    if os.path.exists(dashboard_file):
        return FileResponse(dashboard_file)
    return {"message": "Elephas AI Dashboard - API is running", "status": "ok"}

# 🖼️ Serve logo files directly
logo_path = "/Users/eklavya/Documents/scamshield_flutter_app/assets/images/elephas_logo.png"

@app.get("/elephas_logo.png")
async def get_logo():
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return JSONResponse({"error": "Logo not found"}, status_code=404)

@app.get("/elephas_logo_full.png")
async def get_logo_full():
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return JSONResponse({"error": "Logo not found"}, status_code=404)

# ✅ Health check for Render and real-time monitoring
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "mock_mode",
        "cache": "disabled"
    }

# 📊 Real-time Dashboard API endpoints with fallback data
@app.get("/api/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics (fallback mode)"""
    return DashboardStats(
        threats_blocked=random.randint(2800, 3000),
        scans_processed=random.randint(150000, 160000),
        accuracy_rate=round(random.uniform(99.5, 99.9), 1),
        avg_response_time=random.randint(20, 30),
        uptime="47h 23m",
        last_updated=datetime.now().isoformat()
    )

@app.get("/api/activity", response_model=List[ActivityItem])
async def get_recent_activity():
    """Get recent security activity (fallback mode)"""
    return [
        ActivityItem(
            type="danger",
            message="High-risk phishing attempt blocked (demo mode)",
            timestamp=int(time.time() - 120) * 1000,
            severity="high"
        ),
        ActivityItem(
            type="warning", 
            message="Suspicious message pattern detected (demo mode)",
            timestamp=int(time.time() - 300) * 1000,
            severity="medium"
        ),
        ActivityItem(
            type="success",
            message="Model accuracy improved to 99.7% (demo mode)",
            timestamp=int(time.time() - 720) * 1000,
            severity="low"
        )
    ]

@app.get("/api/threats", response_model=ThreatData)
async def get_threat_data():
    """Get threat timeline and category data (fallback mode)"""
    return ThreatData(
        timeline=[45, 67, 89, 156, 234, 189, 267, 198, 145, 234, 156, 89, 67, 45, 123, 234, 156, 89, 67, 145, 234, 189, 156, 89],
        categories=[
            {"name": "Phishing", "count": random.randint(40, 60), "color": "#ff0055"},
            {"name": "Malware", "count": random.randint(20, 35), "color": "#ffa500"},
            {"name": "Spam", "count": random.randint(10, 25), "color": "#00ff7f"},
            {"name": "Fraud", "count": random.randint(5, 20), "color": "#00ffff"},
            {"name": "Other", "count": random.randint(3, 15), "color": "#ff00ff"}
        ],
        geographic_data=[
            {"country_code": "US", "country_name": "United States", "threat_count": 1247, "latitude": 39.8283, "longitude": -98.5795},
            {"country_code": "CN", "country_name": "China", "threat_count": 892, "latitude": 35.8617, "longitude": 104.1954},
            {"country_code": "RU", "country_name": "Russia", "threat_count": 756, "latitude": 61.5240, "longitude": 105.3188},
            {"country_code": "BR", "country_name": "Brazil", "threat_count": 234, "latitude": -14.2350, "longitude": -51.9253},
            {"country_code": "IN", "country_name": "India", "threat_count": 445, "latitude": 20.5937, "longitude": 78.9629}
        ]
    )

# 🧠 POST endpoint for scam detection (simplified version)
@app.post("/scan")
async def scan_message(body: ScanRequest):
    """Scan message using simplified AI processing"""
    start_time = time.time()
    
    try:
        message = body.text.strip()
        sender = body.sender or ""
        metadata = body.metadata or {}

        if len(message) < 3:
            return {
                "error": "Message too short to analyze.",
                "risk_score": 0.0,
                "risk_level": "low",
                "explanation": "Not enough information",
                "processing_time": round((time.time() - start_time) * 1000, 2)
            }

        # Simplified risk assessment based on keywords
        risk_indicators = {
            "urgent": ["urgent", "immediate", "act now", "limited time"],
            "financial": ["money", "bank", "credit card", "payment", "account", "winner", "prize"],
            "suspicious": ["click here", "verify", "confirm", "suspended", "blocked"],
            "phishing": ["login", "password", "security", "update", "verify account"]
        }
        
        risk_score = 0.0
        detected_features = {}
        
        message_lower = message.lower()
        
        for category, keywords in risk_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                detected_features[f"{category}_indicators"] = matches
                risk_score += matches * 0.15
        
        # Check for URLs
        if "http" in message_lower or "www." in message_lower:
            detected_features["contains_urls"] = True
            risk_score += 0.2
            
        # Check for suspicious sender
        if sender and any(word in sender.lower() for word in ["noreply", "admin", "security", "bank"]):
            detected_features["suspicious_sender"] = True
            risk_score += 0.1
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine classification and risk level
        if risk_score >= 0.7:
            classification = "phishing"
            risk_level = "critical"
        elif risk_score >= 0.5:
            classification = "suspicious"
            risk_level = "high"
        elif risk_score >= 0.3:
            classification = "potential_threat"
            risk_level = "medium"
        else:
            classification = "safe"
            risk_level = "low"

        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "scan_id": f"scan_{int(time.time())}_{random.randint(1000, 9999)}",
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "classification": classification,
            "confidence": min(0.95, 0.7 + (risk_score * 0.3)),
            "features": detected_features,
            "explanation": f"Detected {classification} with {len(detected_features)} risk indicators",
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "mode": "simplified_ai"
        }
        
        return response

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        processing_time = round((time.time() - start_time) * 1000, 2)
        return {
            "error": f"Analysis failed: {str(e)}",
            "risk_score": 0.0,
            "risk_level": "unknown",
            "processing_time": processing_time
        }

# 📊 Analytics endpoints
@app.get("/api/analytics")
async def get_analytics_data(period: str = "7d"):
    """Get analytics data (fallback mode)"""
    return {
        "period": period,
        "threat_timeline": [random.randint(10, 100) for _ in range(24)],
        "threat_categories": [
            {"name": "Phishing", "count": 45, "color": "#ff0055"},
            {"name": "Malware", "count": 25, "color": "#ffa500"},
            {"name": "Spam", "count": 15, "color": "#00ff7f"}
        ],
        "performance_metrics": {
            "avg_processing_time": 23.4,
            "total_scans": 15632,
            "avg_confidence": 0.94
        },
        "generated_at": datetime.now().isoformat(),
        "mode": "fallback_data"
    }

# 📄 Reports endpoint
@app.post("/api/reports")
async def generate_report(report_request: Dict):
    """Generate report (simplified version)"""
    return {
        "report_id": f"report_{int(time.time())}",
        "status": "completed",
        "report_type": report_request.get("report_type", "daily"),
        "generated_at": datetime.now().isoformat(),
        "download_url": "/api/reports/download/report_123",
        "mode": "simplified"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
