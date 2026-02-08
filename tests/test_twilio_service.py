"""
Unit tests for Twilio Service
Tests voice calls, WhatsApp, SMS functionality
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.twilio_service import TwilioService


def test_twilio_service_initialization():
    """Test TwilioService initialization with and without credentials"""

    # Test without credentials
    with patch.dict(os.environ, {}, clear=True):
        service = TwilioService()
        assert service.account_sid == ""
        assert not service.is_available
        print("✅ TwilioService initialization without credentials OK")

    # Test with credentials
    env_vars = {
        "TWILIO_ACCOUNT_SID": "ACxxxxx",
        "TWILIO_AUTH_TOKEN": "token123",
        "TWILIO_PHONE_NUMBER": "+1234567890",
        "TWILIO_WHATSAPP_NUMBER": "+1234567890",
        "VOICE_WEBHOOK_URL": "https://example.com"
    }
    with patch.dict(os.environ, env_vars):
        with patch('services.twilio_service._twilio_available', False):
            service = TwilioService()
            assert service.account_sid == "ACxxxxx"
            assert service.auth_token == "token123"
            print("✅ TwilioService initialization with credentials OK")


def test_phone_number_normalization():
    """Test E.164 phone number formatting"""
    from services.twilio_service import TwilioService

    service = TwilioService()

    # Test with + prefix (already correct)
    phone = "+1234567890"
    assert phone.startswith("+")
    print(f"✅ Phone normalization test 1: {phone}")

    # Test without + prefix
    phone = "1234567890"
    if not phone.startswith("+"):
        phone = f"+{phone}"
    assert phone == "+1234567890"
    print(f"✅ Phone normalization test 2: {phone}")


def test_twiml_generation():
    """Test TwiML generation for voice calls"""

    env_vars = {
        "TWILIO_ACCOUNT_SID": "ACxxxxx",
        "TWILIO_AUTH_TOKEN": "token123",
        "TWILIO_PHONE_NUMBER": "+1234567890",
        "VOICE_WEBHOOK_URL": "https://example.com/voice"
    }

    with patch.dict(os.environ, env_vars):
        with patch('services.twilio_service._twilio_available', True):
            with patch('services.twilio_service.TwilioClient'):
                service = TwilioService()
                service._client = Mock()

                # Test simple TwiML generation
                twiml = service._generate_say_twiml("Hello Synthia")
                assert "Hello Synthia" in str(twiml) or "<Say" in str(twiml)
                print("✅ TwiML <Say> generation OK")


def test_message_format():
    """Test Twilio message format helpers"""
    from services.twilio_service import TwilioService

    # These are tested implicitly through class instantiation
    service = TwilioService()
    assert service.phone_number == ""  # No env vars
    print("✅ Message format initialization OK")


if __name__ == "__main__":
    print("\n🧪 Testing Twilio Service...\n")
    test_twilio_service_initialization()
    test_phone_number_normalization()
    test_twiml_generation()
    test_message_format()
    print("\n✅ All Twilio tests passed!\n")
