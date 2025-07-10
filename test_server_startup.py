#!/usr/bin/env python3
"""
Simple test to verify FastAPI server can start without AI components
"""

import uvicorn
import os
from fastapi import FastAPI

# Simple test app
test_app = FastAPI(title="Test Server")

@test_app.get("/")
async def root():
    return {"message": "Server is running", "status": "ok"}

@test_app.get("/health")
async def health():
    return {"status": "ok", "message": "Simple health check"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting test server on port {port}")
    uvicorn.run(test_app, host="0.0.0.0", port=port, log_level="info")
