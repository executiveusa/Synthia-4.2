"""
Synthia 4.2 - Twilio Service

Handles outbound voice calls and WhatsApp messaging.
Synthia calls the user, discusses the project, then triggers the agent swarm.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Twilio is optional
try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
    _twilio_available = True
except ImportError:
    _twilio_available = False
    logger.info("Twilio SDK not installed. Voice calls and WhatsApp disabled.")


class TwilioService:
    """Twilio integration for voice calls and WhatsApp."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
        self.voice_webhook_url = os.getenv("VOICE_WEBHOOK_URL", "")
        self._client: Optional[object] = None

        if _twilio_available and self.account_sid and self.auth_token:
            try:
                self._client = TwilioClient(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.warning("Twilio client init failed: %s", e)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def initiate_call(self, to_number: str) -> str:
        """Place an outbound call. Returns call SID."""
        if not self.is_available:
            raise RuntimeError("Twilio not configured")

        # Generate TwiML that connects to our WebSocket for real-time audio
        twiml = self._generate_stream_twiml()

        call = self._client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=self.phone_number,
            status_callback=f"{self.voice_webhook_url}/voice/call/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        logger.info("Call initiated: %s -> %s (SID: %s)", self.phone_number, to_number, call.sid)
        return call.sid

    def _generate_stream_twiml(self) -> str:
        """Generate TwiML that connects the call to a WebSocket media stream."""
        if not _twilio_available:
            return "<Response><Say>Twilio SDK not available</Say></Response>"

        response = VoiceResponse()
        response.say(
            "Hi, this is Synthia from The Pauli Effect. Connecting you now.",
            voice="Polly.Joanna",
        )
        connect = Connect()
        stream = Stream(url=f"wss://{self.voice_webhook_url.replace('https://', '')}/ws/twilio-stream")
        connect.append(stream)
        response.append(connect)
        return str(response)

    def send_whatsapp(self, to: str, message: str, media_url: Optional[str] = None) -> str:
        """Send a WhatsApp message. Returns message SID."""
        if not self.is_available:
            raise RuntimeError("Twilio not configured")

        kwargs = {
            "body": message,
            "from_": f"whatsapp:{self.whatsapp_number}",
            "to": f"whatsapp:{to}",
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        msg = self._client.messages.create(**kwargs)
        logger.info("WhatsApp sent to %s (SID: %s)", to, msg.sid)
        return msg.sid

    def send_sms(self, to: str, message: str) -> str:
        """Send an SMS. Returns message SID."""
        if not self.is_available:
            raise RuntimeError("Twilio not configured")

        msg = self._client.messages.create(
            body=message,
            from_=self.phone_number,
            to=to,
        )
        return msg.sid


# Singleton
_twilio_service: Optional[TwilioService] = None


def get_twilio_service() -> TwilioService:
    global _twilio_service
    if _twilio_service is None:
        _twilio_service = TwilioService()
    return _twilio_service


__all__ = ["TwilioService", "get_twilio_service"]
