# elephas-ai/main.py

print("🔥 STARTUP: main.py is executing...")

import asyncio
import logging
import signal
import sys
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Dict

# elephas-ai/main.py

print("🔥 STARTUP: main.py is executing...")

import asyncio
import logging
import signal
import sys
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Dict

print("🔥 STARTUP: Basic imports completed")

# Check if we're in production mode early to avoid heavy imports
if os.getenv("ENVIRONMENT") == "production":
    print("🧪 PRODUCTION MODE: Skipping heavy imports for test server")
    import uvicorn
    from fastapi import FastAPI
    
    print("🧪 PRODUCTION MODE: FastAPI imported, starting test server...")
    
    test_app = FastAPI(title="Elephas AI Test Server")
    
    @test_app.get("/")
    async def root():
        return {"message": "Elephas AI Test Server", "status": "running", "mode": "production"}
        
    @test_app.get("/health") 
    async def health():
        return {"status": "ok", "message": "Test health check", "environment": os.getenv("ENVIRONMENT")}
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 PRODUCTION: Starting test server on 0.0.0.0:{port}")
    
    try:
        uvicorn.run(
            test_app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ ERROR: Failed to start test server: {e}")
        import traceback
        traceback.print_exc()
        
else:
    # Development mode - load all components
    print("🏠 DEVELOPMENT MODE: Loading full AI components...")
    
    from core.bert_classifier import BertScamClassifier
    from core.advanced_features import AdvancedScamFeatureExtractor
    from core.enhanced_scorer import EnhancedScamRiskScorer
    from core.realtime_processor import RealtimeScamProcessor
    from integrations.android_integration import AndroidIntegration
    from mobile.optimizer import MobileModelOptimizer
    from api.enhanced_routes import app

    print("🔥 STARTUP: All imports completed")

    import uvicorn


class ElephasAIOrchestrator:
    """� Main orchestrator for Elephas AI System �"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.components = {}
        self.running = False

        self._initialize_components()

    def _setup_logging(self):
        """Configure logging for the orchestrator."""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("elephas-ai.log")
            ]
        )
        return logging.getLogger(__name__)

    def _initialize_components(self):
        """Initialize core Elephas AI modules."""
        try:
            self.logger.info("🐘 Initializing Elephas AI components...")

            self.components['bert_classifier'] = BertScamClassifier()
            self.components['feature_extractor'] = AdvancedScamFeatureExtractor()
            self.components['risk_scorer'] = EnhancedScamRiskScorer(self.components['bert_classifier'])
            self.components['realtime_processor'] = RealtimeScamProcessor(scam_detector=self)
            self.components['android_integration'] = AndroidIntegration(scam_detector=self)
            self.components['mobile_optimizer'] = MobileModelOptimizer(model_path="scambert-model-v2")

            self.logger.info("✅ Elephas AI components initialized.")
        except Exception as e:
            self.logger.error(f"❌ Initialization error: {e}")
            raise

    async def analyze_message(self, message: str, sender: str = "", message_type: str = "unknown", metadata: Dict = None) -> Dict:
        """Analyze a message and return its scam risk assessment."""
        try:
            features = self.components['feature_extractor'].extract(
                text=message,
                sender=sender,
                metadata=metadata or {}
            )

            risk_score, explanation, analysis = self.components['risk_scorer'].score(
                text=message,
                features=features,
                sender=sender
            )

            return {
                'message': message,
                'sender': sender,
                'message_type': message_type,
                'risk_score': risk_score,
                'risk_level': analysis['risk_level'],
                'confidence': analysis['bert_confidence'],
                'explanation': explanation,
                'detailed_analysis': analysis,
                'features': features
            }

        except Exception as e:
            self.logger.error(f"Message analysis failed: {e}")
            return {
                'message': message,
                'risk_score': 0.0,
                'explanation': 'Analysis failed',
                'error': str(e)
            }

    async def start(self, mode: str = "full"):
        """Start Elephas AI in the selected mode."""
        self.running = True
        self.logger.info(f"🚀 Starting Elephas AI in `{mode}` mode...")

        # Graceful shutdown on signals
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            if mode == "api_only":
                await self._start_api_server()
            elif mode == "mobile":
                await self._start_mobile_mode()
            elif mode == "full":
                await self._start_full_mode()
            else:
                raise ValueError(f"Unknown mode: {mode}")
        except Exception as e:
            self.logger.error(f"❌ Startup error: {e}")
            await self.shutdown()

    async def _start_api_server(self):
        """Run the FastAPI server only."""
        self.logger.info("🌐 Starting API server...")
        port = int(os.getenv("PORT", 8000))
        config = uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="info", loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()

    async def _start_mobile_mode(self):
        """Start real-time mobile scanner."""
        self.logger.info("📱 Starting mobile scam detection...")

        await self._optimize_for_mobile()

        tasks = [
            asyncio.create_task(self.components['realtime_processor'].start_processing()),
            asyncio.create_task(self.components['android_integration'].start_sms_monitoring())
        ]

        await asyncio.gather(*tasks)

    async def _start_full_mode(self):
        """Start full Elephas AI system including API and mobile integrations."""
        self.logger.info("🧩 Starting full system with real-time monitoring + API...")

        await self._optimize_for_mobile()

        tasks = [
            asyncio.create_task(self._start_api_server()),
            asyncio.create_task(self.components['realtime_processor'].start_processing()),
            asyncio.create_task(self.components['android_integration'].start_sms_monitoring())
        ]

        await asyncio.gather(*tasks)

    async def _optimize_for_mobile(self):
        """Run quantization and ONNX conversion for mobile model deployment."""
        optimizer: MobileModelOptimizer = self.components['mobile_optimizer']
        optimizer.quantize_model()
        optimizer.convert_to_onnx()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signal."""
        self.logger.warning(f"⚠️ Caught signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())

    async def shutdown(self):
        """Graceful shutdown of components."""
        self.logger.info("🛑 Shutting down Elephas AI system...")
        self.running = False
        # Implement cleanup logic if needed
        self.logger.info("✅ Shutdown complete.")


if __name__ == "__main__":
    print(f"🔥 MAIN: Starting with ENVIRONMENT={os.getenv('ENVIRONMENT', 'NOT_SET')}")
    
    # Production mode is handled above during imports
    if os.getenv("ENVIRONMENT") != "production":
        # Local development - use full orchestrator
        print("🏠 MAIN: Starting full orchestrator for development")
        orchestrator = ElephasAIOrchestrator()
        mode = os.getenv("DEPLOYMENT_MODE", "full")
        asyncio.run(orchestrator.start(mode=mode))
    else:
        print("🧪 MAIN: Production mode already handled above")