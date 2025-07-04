# run.py
import os
import uvicorn
from api.enhanced_routes import app  # Your FastAPI app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",                      # This is REQUIRED by Render
        port=int(os.environ.get("PORT", 8000)),  # Also required by Render
        log_level="info"
    )