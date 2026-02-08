"""
Synthia 4.2 - Twilio Service (Production)

Handles outbound voice calls, inbound call TwiML, WhatsApp, and SMS.
Synthia calls the user, discusses the project, then triggers the agent swarm.

Supports both Account SID/Auth Token and API Key authentication.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Twilio is optional
try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.voice_response import VoiceResponse, Connect, Stream, Say
    _twilio_available = True
except ImportError:
    _twilio_available = False
    logger.info("Twilio SDK not installed. Voice calls and WhatsApp disabled.")


class TwilioService:
    """Twilio integration for voice calls and WhatsApp."""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.api_key_sid = os.getenv("TWILIO_API_KEY_SID", "")
        self.api_key_secret = os.getenv("TWILIO_API_KEY_SECRET", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
        self.voice_webhook_url = os.getenv("VOICE_WEBHOOK_URL", "")
        self._client: Optional[object] = None

        if _twilio_available and self.account_sid:
            try:
                if self.api_key_sid and self.api_key_secret:
                    # API Key auth (preferred - more secure, revocable)
                    self._client = TwilioClient(
                        self.api_key_sid,
                        self.api_key_secret,
                        self.account_sid,
                    )
                    logger.info("Twilio client initialized with API Key (SID: %s...)", self.api_key_sid[:8])
                elif self.auth_token:
                    # Auth Token fallback
                    self._client = TwilioClient(self.account_sid, self.auth_token)
                    logger.info("Twilio client initialized with Auth Token (SID: %s...)", self.account_sid[:8])
                else:
                    logger.warning("Twilio: Account SID found but no API Key or Auth Token")
            except Exception as e:
                logger.warning("Twilio client init failed: %s", e)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def initiate_call(self, to_number: str, greeting: str = "") -> str:
        """
        Place an outbound call. Returns call SID.

        If voice_webhook_url is set and points to our WebSocket server,
        uses <Connect><Stream> for bidirectional media streaming.
        Otherwise, uses inline TwiML with <Say>.
        """
        if not self.is_available:
            raise RuntimeError("Twilio not configured")

        # Ensure E.164 format
        if not to_number.startswith("+"):
            to_number = f"+{to_number}"

        if self.voice_webhook_url and "localhost" not in self.voice_webhook_url:
            # Production: Connect to WebSocket for real-time Synthia conversation
            twiml = self._generate_stream_twiml()
        else:
            # Fallback: Simple TwiML with Say (for testing without WebSocket)
            twiml = self._generate_say_twiml(greeting)

        call = self._client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=self.phone_number,
            status_callback=f"{self.voice_webhook_url}/voice/call/status" if self.voice_webhook_url else None,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        logger.info("Call initiated: %s -> %s (SID: %s)", self.phone_number, to_number, call.sid)
        return call.sid

    def initiate_simple_call(self, to_number: str, message: str) -> str:
        """
        Place a simple outbound call with a TwiML <Say> message.
        No WebSocket needed - just speaks the message and hangs up.
        Good for test calls and notifications.
        """
        if not self.is_available:
            raise RuntimeError("Twilio not configured")

        if not to_number.startswith("+"):
            to_number = f"+{to_number}"

        twiml = self._generate_say_twiml(message)

        call = self._client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=self.phone_number,
            status_callback=f"{self.voice_webhook_url}/voice/call/status" if self.voice_webhook_url else None,
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        logger.info("Simple call initiated: %s -> %s (SID: %s)", self.phone_number, to_number, call.sid)
        return call.sid

    def _generate_stream_twiml(self) -> str:
        """Generate TwiML that connects the call to a WebSocket media stream."""
        if not _twilio_available:
            return "<Response><Say>Twilio SDK not available</Say></Response>"

        response = VoiceResponse()
        response.say(
            "Connecting you to Synthia from The Pauli Effect.",
            voice="Polly.Joanna",
        )
        response.pause(length=1)
        connect = Connect()
        ws_url = self.voice_webhook_url.replace("https://", "wss://").replace("http://", "ws://")
        stream = Stream(url=f"{ws_url}/ws/twilio-stream")
        connect.append(stream)
        response.append(connect)
        return str(response)

    def _generate_say_twiml(self, message: str = "") -> str:
        """Generate simple TwiML with <Say> verb."""
        if not _twilio_available:
            return "<Response><Say>Twilio SDK not available</Say></Response>"

        if not message:
            message = (
                "Hello! This is Synthia from The Pauli Effect agency. "
                "I'm your AI design assistant for creating Awwwards-quality websites. "
                "This is a test call to verify our voice pipeline is working. "
                "The full bidirectional voice conversation system is now active. "
                "Have a great day!"
            )

        response = VoiceResponse()
        response.say(message, voice="Polly.Joanna")
        return str(response)

    def generate_inbound_twiml(self) -> str:
        """
        Generate TwiML for handling inbound calls.
        Connects the caller to Synthia via bidirectional media stream.
        """
        if not _twilio_available:
            return "<Response><Say>System unavailable</Say></Response>"

        response = VoiceResponse()
        response.say(
            "Welcome to The Pauli Effect. Connecting you with Synthia, your AI design assistant.",
            voice="Polly.Joanna",
        )
        response.pause(length=1)
        connect = Connect()
        ws_url = self.voice_webhook_url.replace("https://", "wss://").replace("http://", "ws://")
        stream = Stream(url=f"{ws_url}/ws/twilio-stream")
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

        if not to.startswith("+"):
            to = f"+{to}"

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
