# run.py
import os
import uvicorn
from api.enhanced_routes import app  # Your FastAPI app

if __name__ == "__main__":
    # Cloud Run uses PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )