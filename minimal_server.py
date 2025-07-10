#!/usr/bin/env python3
"""
Ultra-minimal server for Render deployment debugging
"""
import os

print("🔥 MINIMAL: Starting minimal server...")
print(f"🔥 MINIMAL: PORT = {os.getenv('PORT', 'NOT_SET')}")
print(f"🔥 MINIMAL: ENVIRONMENT = {os.getenv('ENVIRONMENT', 'NOT_SET')}")

try:
    import uvicorn
    from fastapi import FastAPI
    
    print("🔥 MINIMAL: FastAPI imported successfully")
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"message": "Minimal server running"}
    
    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    port = int(os.getenv("PORT", 8000))
    print(f"🔥 MINIMAL: About to start uvicorn on port {port}")
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
except Exception as e:
    print(f"🔥 MINIMAL: ERROR - {e}")
    import traceback
    traceback.print_exc()
