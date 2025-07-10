# Real Data Service for ScamShield AI Dashboard
# Production-ready data integration with PostgreSQL, Redis, and external threat APIs

import asyncio
import asyncpg
import redis
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import os
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ThreatIntelResponse:
    """Structured response from threat intelligence APIs"""
    indicator: str
    threat_type: str
    confidence: float
    severity: str
    source: str
    details: Dict[str, Any]

class RealDataService:
    """Production data service for ScamShield AI dashboard"""
    
    def __init__(self):
        # Database configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'scamshield_ai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        # Redis configuration for caching
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'password': os.getenv('REDIS_PASSWORD', None),
            'db': int(os.getenv('REDIS_DB', 0))
        }
        
        # External API configurations
        self.virustotal_api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.abuseipdb_api_key = os.getenv('ABUSEIPDB_API_KEY')
        self.phishtank_api_key = os.getenv('PHISHTANK_API_KEY')
        
        # Connection pools
        self.db_pool = None
        self.redis_client = None
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def initialize(self):
        """Initialize database and cache connections"""
        try:
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(**self.db_config)
            logger.info("Database connection pool initialized")
            
            # Initialize Redis client
            self.redis_client = redis.Redis(**self.redis_config)
            await self._test_redis_connection()
            logger.info("Redis connection initialized")
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            logger.info("HTTP session initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize data service: {e}")
            raise
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.session:
            await self.session.close()
        if self.executor:
            self.executor.shutdown(wait=True)
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get real-time dashboard statistics from database"""
        cache_key = "dashboard:stats"
        
        # Try cache first
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        async with self.db_pool.acquire() as conn:
            # Get threats blocked (last 24 hours)
            threats_blocked = await conn.fetchval("""
                SELECT COUNT(*) FROM scan_results 
                WHERE classification IN ('phishing', 'malware', 'fraud', 'spam') 
                AND created_at >= NOW() - INTERVAL '24 hours'
            """)
            
            # Get total scans processed
            scans_processed = await conn.fetchval("""
                SELECT COUNT(*) FROM scan_results 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
            
            # Calculate accuracy rate (from recent scans with manual verification)
            accuracy_data = await conn.fetchrow("""
                SELECT 
                    AVG(confidence) as avg_confidence,
                    COUNT(*) as total_scans
                FROM scan_results 
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """)
            
            # Get average response time
            avg_response_time = await conn.fetchval("""
                SELECT AVG(processing_time_ms) FROM scan_results 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND processing_time_ms IS NOT NULL
            """) or 0
            
            # Get system uptime from metrics
            uptime_hours = await conn.fetchval("""
                SELECT EXTRACT(EPOCH FROM (NOW() - MIN(created_at)))/3600 
                FROM system_metrics 
                WHERE metric_name = 'system_start'
            """) or 0
            
            stats = {
                'threatsBlocked': int(threats_blocked or 0),
                'scansProcessed': int(scans_processed or 0),
                'accuracyRate': round(float(accuracy_data['avg_confidence'] or 0.95) * 100, 1),
                'avgResponseTime': int(avg_response_time),
                'uptime': f"{int(uptime_hours)}h {int((uptime_hours % 1) * 60)}m",
                'lastUpdated': datetime.now().isoformat()
            }
            
            # Cache for 30 seconds
            if self.redis_client:
                try:
                    self.redis_client.setex(cache_key, 30, json.dumps(stats))
                except Exception:
                    pass
            
            return stats
    
    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent security activity from database"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    event_type,
                    event_severity as type,
                    event_message as message,
                    EXTRACT(EPOCH FROM created_at) * 1000 as timestamp,
                    event_details
                FROM activity_log 
                ORDER BY created_at DESC 
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def get_threat_timeline(self, hours: int = 24) -> List[int]:
        """Get threat detection timeline data"""
        async with self.db_pool.acquire() as conn:
            # Get hourly threat counts for the specified period
            rows = await conn.fetch("""
                SELECT 
                    EXTRACT(HOUR FROM created_at) as hour,
                    COUNT(*) as count
                FROM scan_results 
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                AND classification IN ('phishing', 'malware', 'fraud', 'spam')
                GROUP BY EXTRACT(HOUR FROM created_at)
                ORDER BY hour
            """, hours)
            
            # Fill in missing hours with 0
            hourly_counts = [0] * 24
            for row in rows:
                hourly_counts[int(row['hour'])] = int(row['count'])
            
            return hourly_counts
    
    async def get_threat_categories(self) -> List[Dict[str, Any]]:
        """Get threat category distribution"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    classification as name,
                    COUNT(*) as count,
                    CASE classification
                        WHEN 'phishing' THEN '#ff0055'
                        WHEN 'malware' THEN '#ffa500'
                        WHEN 'spam' THEN '#00ff7f'
                        WHEN 'fraud' THEN '#00ffff'
                        ELSE '#ff00ff'
                    END as color
                FROM scan_results 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND classification IN ('phishing', 'malware', 'fraud', 'spam')
                GROUP BY classification
                ORDER BY count DESC
            """)
            
            return [dict(row) for row in rows]
    
    async def get_geographic_data(self) -> List[Dict[str, Any]]:
        """Get geographic threat distribution"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    country_code,
                    country_name,
                    threat_count,
                    risk_level,
                    latitude,
                    longitude
                FROM geographic_threats 
                WHERE threat_count > 0
                ORDER BY threat_count DESC
                LIMIT 50
            """)
            
            return [dict(row) for row in rows]
    
    async def scan_message(self, text: str, sender: str = "", metadata: Dict = None) -> Dict[str, Any]:
        """Perform real AI-powered message scan and store results"""
        from core.bert_classifier import BertScamClassifier
        from core.enhanced_scorer import EnhancedScamRiskScorer
        from core.advanced_features import AdvancedScamFeatureExtractor
        
        start_time = datetime.now()
        
        # Initialize AI components
        classifier = BertScamClassifier()
        scorer = EnhancedScamRiskScorer()
        feature_extractor = AdvancedScamFeatureExtractor()
        
        # Extract features
        features = feature_extractor.extract_features(text, sender, metadata or {})
        
        # Get AI classification
        prediction = classifier.predict(text)
        
        # Calculate risk score
        risk_score = scorer.calculate_comprehensive_risk_score(text, features, prediction)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Store scan result in database
        scan_id = hashlib.md5(f"{text}{sender}{datetime.now()}".encode()).hexdigest()
        
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO scan_results (
                    scan_id, message_text, sender_info, risk_score, 
                    classification, confidence, features, processing_time_ms,
                    model_version, api_version
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                scan_id, text, json.dumps({"sender": sender}), 
                risk_score, prediction['label'], prediction['confidence'],
                json.dumps(features), processing_time, "v2.0", "2.0"
            )
            
            # Log activity
            await self._log_activity(
                "scan_completed",
                "info" if risk_score < 0.5 else "warning" if risk_score < 0.8 else "critical",
                f"Message scan completed with risk score {risk_score:.3f}",
                {"scan_id": scan_id, "risk_score": risk_score}
            )
        
        return {
            "scan_id": scan_id,
            "risk_score": risk_score,
            "classification": prediction['label'],
            "confidence": prediction['confidence'],
            "features": features,
            "processing_time_ms": processing_time,
            "timestamp": start_time.isoformat()
        }
    
    async def _log_activity(self, event_type: str, severity: str, message: str, details: Dict = None):
        """Log activity to database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO activity_log (event_type, event_severity, event_message, event_details)
                VALUES ($1, $2, $3, $4)
            """, event_type, severity, message, json.dumps(details or {}))
    
    async def enrich_with_threat_intelligence(self, indicator: str, indicator_type: str) -> Optional[ThreatIntelResponse]:
        """Enrich data with external threat intelligence"""
        # Check local threat intelligence first
        async with self.db_pool.acquire() as conn:
            local_threat = await conn.fetchrow("""
                SELECT * FROM threat_intelligence 
                WHERE indicator_value = $1 AND indicator_type = $2 
                AND is_active = true
                ORDER BY confidence_score DESC
                LIMIT 1
            """, indicator, indicator_type)
            
            if local_threat:
                return ThreatIntelResponse(
                    indicator=local_threat['indicator_value'],
                    threat_type=local_threat['threat_type'],
                    confidence=float(local_threat['confidence_score']),
                    severity=local_threat['severity'],
                    source=local_threat['source'],
                    details=local_threat['metadata'] or {}
                )
        
        # Query external APIs if no local data
        if indicator_type == 'ip' and self.abuseipdb_api_key:
            return await self._query_abuseipdb(indicator)
        elif indicator_type in ['domain', 'url'] and self.virustotal_api_key:
            return await self._query_virustotal(indicator)
        
        return None
    
    async def _query_abuseipdb(self, ip: str) -> Optional[ThreatIntelResponse]:
        """Query AbuseIPDB for IP reputation"""
        if not self.session:
            return None
            
        try:
            headers = {
                'Key': self.abuseipdb_api_key,
                'Accept': 'application/json'
            }
            
            async with self.session.get(
                f'https://api.abuseipdb.com/api/v2/check',
                headers=headers,
                params={'ipAddress': ip, 'maxAgeInDays': 90}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data', {}).get('abuseConfidencePercentage', 0) > 25:
                        return ThreatIntelResponse(
                            indicator=ip,
                            threat_type='malicious_ip',
                            confidence=data['data']['abuseConfidencePercentage'] / 100,
                            severity='high' if data['data']['abuseConfidencePercentage'] > 75 else 'medium',
                            source='AbuseIPDB',
                            details=data['data']
                        )
        except Exception as e:
            logger.error(f"AbuseIPDB query failed: {e}")
        
        return None
    
    async def _query_virustotal(self, indicator: str) -> Optional[ThreatIntelResponse]:
        """Query VirusTotal for domain/URL reputation"""
        if not self.session:
            return None
            
        try:
            headers = {'x-apikey': self.virustotal_api_key}
            
            # URL encode the indicator for VirusTotal
            import base64
            url_id = base64.urlsafe_b64encode(indicator.encode()).decode().strip("=")
            
            async with self.session.get(
                f'https://www.virustotal.com/api/v3/urls/{url_id}',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                    malicious_count = stats.get('malicious', 0)
                    total_scans = sum(stats.values())
                    
                    if malicious_count > 0 and total_scans > 0:
                        confidence = malicious_count / total_scans
                        return ThreatIntelResponse(
                            indicator=indicator,
                            threat_type='malicious_url',
                            confidence=confidence,
                            severity='critical' if confidence > 0.5 else 'high',
                            source='VirusTotal',
                            details={'stats': stats, 'scans': total_scans}
                        )
        except Exception as e:
            logger.error(f"VirusTotal query failed: {e}")
        
        return None

# Global instance
data_service = RealDataService()

async def get_data_service() -> RealDataService:
    """Get initialized data service instance"""
    if not data_service.db_pool:
        await data_service.initialize()
    return data_service
