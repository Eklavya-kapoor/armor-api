#!/usr/bin/env python3
"""
Simplified server startup for Render deployment
Separates server startup from AI initialization to prevent deployment failures
"""

import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI server with proper configuration for Render"""
    
    # Get port from environment (Render sets this automatically)
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Required for Render
    
    logger.info(f"🚀 Starting Elephas AI API server on {host}:{port}")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Import the FastAPI app
    try:
        from api.enhanced_routes import app
        logger.info("✅ FastAPI app imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import FastAPI app: {e}")
        sys.exit(1)
    
    # Configure server
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        workers=1,  # Single worker to conserve memory on free tier
        timeout_keep_alive=30,
        timeout_graceful_shutdown=10
    )
    
    # Start server
    server = uvicorn.Server(config)
    
    try:
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info(f"📊 Dashboard available at: http://{host}:{port}/dashboard")
        logger.info(f"🔍 Health check: http://{host}:{port}/health")
        server.run()
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
