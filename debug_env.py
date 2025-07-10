import os
print("=== ENVIRONMENT VARIABLES DEBUG ===")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'NOT_SET')}")
print(f"PORT: {os.getenv('PORT', 'NOT_SET')}")
print(f"MODEL_PATH: {os.getenv('MODEL_PATH', 'NOT_SET')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'NOT_SET')}")
print("=== ALL ENV VARS ===")
for key, value in os.environ.items():
    if not key.startswith('_'):
        print(f"{key}: {value}")
print("=== END DEBUG ===")

# Start simple server
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Debug server", "env_count": len(os.environ)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/env")
def env_debug():
    return {key: value for key, value in os.environ.items() if not key.startswith('_')}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting debug server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
