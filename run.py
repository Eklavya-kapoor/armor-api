# run.py
import asyncio
from main import ScamShieldOrchestrator

orchestrator = ScamShieldOrchestrator()
asyncio.run(orchestrator.start(mode="api_only"))  # Or "full" if needed