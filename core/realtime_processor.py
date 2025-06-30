# core/realtime_processor.py

import asyncio
import logging
from typing import Optional

class RealtimeScamProcessor:
    """
    🔄 Background task that listens for new messages (from queue or stream)
    and processes them using the ScamShieldOrchestrator's detection pipeline.
    """

    def __init__(self, scam_detector):
        self.logger = logging.getLogger(__name__)
        self.scam_detector = scam_detector
        self.running = False
        self.message_queue = asyncio.Queue()

    async def start_processing(self):
        """Begin processing messages from the queue in real time."""
        self.logger.info("🔍 Realtime scam processor started.")
        self.running = True
        while self.running:
            try:
                message = await self.message_queue.get()
                await self._handle_message(message)
            except Exception as e:
                self.logger.error(f"⚠️ Error in realtime processing: {e}")

    async def _handle_message(self, message: dict):
        """Handle and analyze an incoming message dict."""
        text = message.get("text", "")
        sender = message.get("sender", "")
        metadata = message.get("metadata", {})

        if not text.strip():
            self.logger.warning("🚫 Empty message received, skipping.")
            return

        result = await self.scam_detector.analyze_message(
            message=text,
            sender=sender,
            message_type=metadata.get("message_type", "unknown"),
            metadata=metadata
        )

        self.logger.info(f"✅ Processed message | Risk: {result.get('risk_level')} | Sender: {sender}")

    def submit_message(self, text: str, sender: str = "", metadata: Optional[dict] = None):
        """Submit a message to the queue from another thread or integration."""
        if metadata is None:
            metadata = {}
        message = {
            "text": text,
            "sender": sender,
            "metadata": metadata
        }
        if self.running:
            asyncio.create_task(self.message_queue.put(message))